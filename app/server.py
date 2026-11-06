"""Checkpoint 3 API: live model intent/entity extraction + deterministic verified workflows.
University facts are quoted from real UIUC sources; student records are synthetic
and university actions are simulated.
"""
from __future__ import annotations

import json
import logging
import os
import pathlib
import re
import time
import uuid
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE = pathlib.Path(__file__).parent
load_dotenv(BASE / '.env')

import db  # noqa: E402  (reads INTERFACEDNA_DB from .env)
import rules  # noqa: E402

SYSTEM = (BASE / 'prompts' / 'system.txt').read_text()
SETTINGS = json.loads((BASE / 'prompts' / 'settings.json').read_text())
INTENTS = ('drop', 'graduation', 'hold', 'record', 'course_search', 'course_info', 'policy', 'unknown')
TERM = re.compile(r'\b(fall|spring|summer|winter)\s+(\d{4})\b', re.I)
TOPICS = ('full_time', 'deadlines', 'refunds', 'withdrawal', 'registration',
          'graduation_application', 'winter_session', 'holds')
COURSE = re.compile(r'\b([A-Za-z]{2,4})\s*-?\s*(\d{3})\b')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)
log = logging.getLogger('interfacedna')


class Start(BaseModel):
    message: str = Field(min_length=3, max_length=1000)
    student_id: str = Field(pattern=r'^S\d{5}$')
    term: str = Field(default=db.CURRENT_TERM, pattern=r'^(Fall|Spring|Summer|Winter) \d{4}$')


class Confirm(BaseModel):
    session_id: str
    confirmation: bool


class Cancel(BaseModel):
    student_id: str = Field(pattern=r'^S\d{5}$')
    receipt: str = Field(min_length=8, max_length=64)
    confirmation: bool


class Fault(BaseModel):
    session_id: str
    mode: str = Field(
        pattern=r'^(none|policy_conflict|missing_record|service_outage)$')


def normalize_course(raw, message):
    """Model entities are untrusted: keep a course code only if it is well-formed
    and the student actually typed it."""
    if not isinstance(raw, str):
        return None
    m = COURSE.fullmatch(raw.strip())
    if not m:
        return None
    code = f'{m[1].upper()} {m[2]}'
    typed = {f'{a.upper()} {b}' for a, b in COURSE.findall(message)}
    return code if code in typed else None


def normalize_term(raw, message):
    """A term the student typed, e.g. 'spring 2027' -> 'Spring 2027'."""
    m = TERM.fullmatch(raw.strip()) if isinstance(raw, str) else None
    if not m:
        return None
    term = f'{m[1].title()} {m[2]}'
    typed = set(typed_terms(message))
    return term if term in typed and rules.term_info(term) else None


def as_int(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value)
    return None


RELATIVE = re.compile(r'\b(this|next|coming|upcoming|last|previous)\s+(fall|spring|summer|winter|semester|term)\b', re.I)


def typed_terms(message):
    """Terms the student named: 'spring 2027', or relative ones like 'next
    spring', 'this fall' or 'next semester', resolved against today's date."""
    out = [f'{a.title()} {b}' for a, b in TERM.findall(message)]
    terms = rules.terms()
    for when, what in RELATIVE.findall(message):
        what = what.lower()
        if when.lower() in ('last', 'previous'):  # the most recent finished term
            pool = [t for t in reversed(terms) if t['status'] == 'past'
                    and (rules.full_term(t['term']) if what in ('semester', 'term')
                         else t['term'].lower().startswith(what))]
        elif when.lower() == 'this' and what in ('semester', 'term'):
            pool = [t for t in terms if t['status'] == 'current']
        elif what in ('semester', 'term'):  # the next Fall or Spring semester
            pool = [t for t in terms if t['status'] == 'upcoming' and rules.full_term(t['term'])]
        else:
            pool = [t for t in terms if t['term'].lower().startswith(what)
                    and (t['status'] == 'upcoming' or (when.lower() == 'this' and t['status'] == 'current'))]
        out.append(pool[0]['term'] if pool else f'{when.lower()} {what}')  # unknown -> reported
    return out


def precheck(intent, message):
    """Reasons to stop before the rules run, based on what the student typed."""

    # Detect hypothetical course-failure questions before evaluating
    # the student's current graduation record.
    text = message.lower()

    hypothetical = re.search(
        r'\b(?:what if|if i|if one|if my|suppose|assuming|imagine)\b',
        text
    )

    course_failure = re.search(
        r'\b(?:fail|fails|failed|failing)\b',
        text
    )

    if intent == 'graduation' and hypothetical and course_failure:
        return (
            'This is a hypothetical graduation scenario. '
            'InterfaceDNA cannot currently recalculate degree '
            'requirements based on a course that might be failed. '
            'The normal credit projection assumes current courses '
            'are passed, so it should not be used to determine '
            'eligibility under this scenario. '
            'Failing a course could affect earned credits, '
            'required courses, or GPA. '
            'Please discuss the specific course and its impact '
            'with your academic advisor. '
            'No graduation decision or simulated request has '
            'been recorded.'
        )

    codes = {f'{a.upper()} {b}' for a, b in COURSE.findall(message)}
    wants_drop = intent == 'drop' or (intent == 'unknown' and any(
        w in message.lower() for w in ('drop', 'withdraw')))
    if wants_drop and len(codes) > 1:
        return (f'Please ask about one course at a time. You mentioned '
                f'{", ".join(sorted(codes))}.')
    terms = typed_terms(message)
    if intent != 'graduation' and terms and not any(rules.term_info(t) for t in terms):
        available = ', '.join(t['term'] for t in rules.terms())
        return f'Information for {terms[0]} isn’t available. Available terms: {available}.'
    return None


def resolve_name(intent, student_id, entities, term):
    """Turn 'my database class' into a course code using the student's own
    courses (or, for course details, the catalog). Never guesses between several."""
    own = [r for r in db.get_records(student_id) if intent == 'course_info' or r['term'] == term]
    codes = rules.resolve_course_name(entities['course_name'], own)
    if not codes and intent == 'course_info':
        codes = rules.resolve_course_name(entities['course_name'], db.list_courses())
    if len(codes) == 1:
        entities['course_code'] = codes[0]
        return None
    if len(codes) > 1:
        shown = ', '.join(codes[:8]) + (' …' if len(codes) > 8 else '')
        return f'“{entities["course_name"]}” matches several courses ({shown}). Which one do you mean?'
    return None


def clean_entities(intent, raw, message):
    """Keep only well-formed entities that fit the intent; the model's output
    is untrusted, so typed values (course, term, keyword) must be in the text."""
    out = {}
    if intent in ('drop', 'course_info'):
        out['course_code'] = normalize_course(raw.get('course_code'), message)
        name = str(raw.get('course_name') or '').strip()
        if not out['course_code'] and 2 < len(name) <= 60 and name.lower() in message.lower():
            out['course_name'] = name
    if intent in ('drop', 'record', 'course_search', 'course_info', 'policy'):
        # A single term the student typed is used even if the model missed it.
        known = [t for t in dict.fromkeys(typed_terms(message)) if rules.term_info(t)]
        out['term'] = normalize_term(raw.get('term'), message) or (known[0] if len(known) == 1 else None)
    if intent == 'course_search':
        subject = str(raw.get('subject') or '').strip().upper()
        out['subject'] = subject if subject in db.subjects() else None
        credits, level = as_int(raw.get('credits')), as_int(raw.get('level'))
        out['credits'] = credits if isinstance(credits, int) and 0 < credits <= 6 else None
        out['level'] = level if level in (100, 200, 300, 400, 500) else None
        keyword = str(raw.get('keyword') or '').strip().lower()
        out['keyword'] = keyword if 2 <= len(keyword) <= 40 and keyword in message.lower() else None
    if intent == 'policy':
        out['topic'] = raw.get('topic') if raw.get('topic') in TOPICS else None
    # A drop always carries its course key so duplicate requests compare equal.
    return {k: v for k, v in out.items() if v is not None or k == 'course_code'}


def groq_api_key():
    key = os.getenv('GROQ_API_KEY', '').strip()
    if not key or key == 'gsk_your_actual_api_key_here':
        raise RuntimeError(
            'Set GROQ_API_KEY in app/.env to enable live model inference.')
    return key


def classify_live(message):
    """Extract intent and entities using a real Groq API call; never silently
    substitute a mock response."""
    from openai import OpenAI  # Groq provides an OpenAI-compatible API.

    client = OpenAI(
        api_key=groq_api_key(),
        base_url='https://api.groq.com/openai/v1',
        timeout=30,
        max_retries=1,
    )
    resp = client.chat.completions.create(
        model=os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b'),
        temperature=SETTINGS['temperature'],
        response_format={'type': 'json_object'},
        messages=[
            {'role': 'system', 'content': SYSTEM},
            {'role': 'user', 'content': message},
        ],
        max_tokens=SETTINGS['max_output_tokens'],
    )
    output = json.loads(resp.choices[0].message.content or '{}')
    intent = output.get('intent', 'unknown')
    if intent not in INTENTS:
        raise RuntimeError('Model produced an invalid task classification.')
    entities = output.get('entities')
    entities = entities if isinstance(entities, dict) else {}
    return (
        intent,
        clean_entities(intent, entities, message),
        str(output.get('explanation', ''))[:500],
        {
            'model': resp.model,
            'input_tokens': getattr(resp.usage, 'prompt_tokens', None),
            'output_tokens': getattr(resp.usage, 'completion_tokens', None),
        },
    )


@asynccontextmanager
async def lifespan(_app):
    db.ensure()
    log.info('database=%s rules_date=%s', db.DB_PATH, rules.today())
    yield


app = FastAPI(title='InterfaceDNA CP3', version='0.2.0', lifespan=lifespan)

# Serve the original InterfaceDNA frontend CSS and JavaScript.
app.mount('/assets', StaticFiles(directory=BASE / 'assets'), name='assets')


@app.middleware('http')
async def telemetry(req: Request, call_next):
    start = time.perf_counter()
    try:
        res = await call_next(req)
        if req.url.path == '/' or req.url.path.startswith('/assets/'):
            res.headers['Cache-Control'] = 'no-cache'  # always pick up UI updates
        log.info(
            'path=%s status=%d latency_ms=%.0f',
            req.url.path,
            res.status_code,
            (time.perf_counter() - start) * 1000,
        )
        return res
    except Exception:
        log.exception(
            'path=%s error latency_ms=%.0f',
            req.url.path,
            (time.perf_counter() - start) * 1000,
        )
        raise


@app.get('/')
def home():
    return FileResponse(BASE / 'index.html')


@app.get('/health')
def health():
    key = os.getenv('GROQ_API_KEY', '').strip()
    return {
        'status': 'ok',
        'model_configured': bool(key) and key != 'gsk_your_actual_api_key_here',
        'provider': 'Groq',
        'model': os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b'),
        'database': db.DB_PATH.name,
        'rules_date': rules.today().isoformat(),
    }


def known_term(term):
    if not rules.term_info(term):
        raise HTTPException(404, f'No calendar for {term}')
    return term


@app.get('/api/terms')
def terms():
    return {'current': db.CURRENT_TERM,
            'terms': [dict(t, key_dates=rules.key_dates('UG', t['term']))
                      for t in rules.terms()]}


@app.get('/api/students')
def students(term: str = db.CURRENT_TERM):
    return db.list_students(known_term(term))


@app.get('/api/sources')
def sources():
    return {
        'facts': db.list_facts(),
        'programs': db.list_programs(),
        'schedules': json.loads((BASE / 'sources' / 'offerings.json').read_text()),
        'term_dates': rules.key_dates('UG', db.CURRENT_TERM),
    }


@app.get('/api/students/{student_id}')
def student(student_id: str, term: str = db.CURRENT_TERM):
    s = db.get_student(student_id)
    if not s:
        raise HTTPException(404, 'Student not found')
    courses = db.get_term_courses(student_id, known_term(term))
    return {
        **s,
        'term': term,
        'term_info': rules.term_info(term),
        'term_courses': courses,
        'term_credits': sum(c['credits'] for c in courses),
        'holds': db.get_active_holds(student_id),
        'requests': db.list_requests(student_id),
        'important': rules.important(student_id, term),
        'key_dates': rules.key_dates(s['level'], term),
        'rules_date': rules.today().isoformat(),
    }


@app.post('/api/start')
def start(body: Start):
    tic = time.perf_counter()
    try:
        intent, entities, explanation, usage = classify_live(body.message)
    except Exception as exc:
        log.exception('Groq model call failed')
        busy = getattr(exc, 'status_code', None) == 429
        raise HTTPException(
            503,
            detail=(
                'The assistant is busy right now. Please wait a minute and try '
                'again. No task was submitted.' if busy else
                'Live model unavailable. Check the server configuration/API '
                'quota and retry. No task was submitted.'
            ),
        ) from exc

    if not db.get_student(body.student_id):
        raise HTTPException(404, 'Student not found')
    term = entities.get('term') or known_term(body.term)  # a term in the question wins
    stop = precheck(intent, body.message)
    if not stop and intent in ('drop', 'course_info') and entities.get('course_name'):
        stop = resolve_name(intent, body.student_id, entities, term)
    result = (rules.blocked(stop) if stop else
              rules.evaluate(intent, body.student_id, entities, term=term))
    sid = str(uuid.uuid4())
    state = 'review' if result['status'] == 'ready' else 'blocked'
    db.create_session(sid, body.student_id, intent, term, entities, state)
    log.info(
        'inference intent=%s entities=%s model=%s input_tokens=%s '
        'output_tokens=%s latency_ms=%.0f',
        intent,
        entities,
        usage['model'],
        usage['input_tokens'],
        usage['output_tokens'],
        (time.perf_counter() - tic) * 1000,
    )
    result['important'] = rules.important(body.student_id, term)
    return {
        'session_id': sid,
        'term': term,
        'intent': intent,
        'entities': entities,
        'interpretation': explanation,
        'model_usage': usage,
        'result': result,
        'state': state,
    }


@app.post('/api/requests/cancel')
def cancel(body: Cancel):
    if not body.confirmation:
        raise HTTPException(400, 'Explicit confirmation required')
    request = db.cancel_request(body.student_id, body.receipt)
    if not request:
        raise HTTPException(409, 'This request is not active, so it cannot be cancelled')
    return {'receipt': body.receipt, 'status': 'cancelled', 'description': request['details']['description'],
            'message': 'Request cancelled.'}


@app.post('/api/fault')
def fault(body: Fault):
    sess = db.get_session(body.session_id)
    if not sess:
        raise HTTPException(404, 'Session not found')
    if sess['state'] == 'completed':
        raise HTTPException(409, 'Cannot mutate completed session')
    result = rules.evaluate(
        sess['intent'], sess['student_id'], sess['entities'], body.mode,
        term=sess['term'])
    state = 'review' if result['status'] == 'ready' else 'blocked'
    if body.mode not in ('missing_record', 'service_outage'):  # needs the student record
        result['important'] = rules.important(sess['student_id'], sess['term'])
    if not db.update_session(body.session_id, state, body.mode):
        raise HTTPException(409, 'Cannot mutate completed session')
    return {'state': state, 'result': result, 'session_id': body.session_id}


@app.post('/api/confirm')
def confirm(body: Confirm):
    sess = db.get_session(body.session_id)
    if not sess:
        raise HTTPException(404, 'Session not found')
    if not body.confirmation:
        raise HTTPException(400, 'Explicit confirmation required')
    if sess['state'] != 'review':
        raise HTTPException(409, 'Task is not confirmable in current state')
    # Recheck every fact at confirmation time (deadline, enrollment, faults).
    current = rules.evaluate(
        sess['intent'], sess['student_id'], sess['entities'], sess['fault'],
        term=sess['term'])
    if current['status'] != 'ready':
        db.update_session(body.session_id, 'blocked', sess['fault'])
        raise HTTPException(
            409, f'Source validation failed: {current.get("reason", "not confirmable")}')
    # Synthetic backend action only; no university connectivity or enrollment changes.
    receipt = str(uuid.uuid4())
    if not db.complete_session(
            body.session_id, receipt, sess['intent'],
            {'description': current['action'], **sess['entities']}):
        raise HTTPException(409, 'Task is not confirmable in current state')
    return {
        'state': 'completed',
        'receipt': receipt,
        'description': current['action'],
        'synthetic': True,
        'message': (
            'Request recorded.'
        ),
    }
