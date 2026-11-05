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
from threading import Lock

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
INTENTS = ('drop', 'graduation', 'hold', 'unknown')
COURSE = re.compile(r'\b([A-Za-z]{2,4})\s*-?\s*(\d{3})\b')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)
log = logging.getLogger('interfacedna')

def policy_today():
    """Return the server's current calendar date for policy validation."""
    return date.today()


class Start(BaseModel):
    message: str = Field(min_length=3, max_length=1000)
    student_id: str = Field(pattern=r'^S\d{5}$')
    term: str = Field(default=db.CURRENT_TERM, pattern=r'^(Fall|Spring|Summer|Winter) \d{4}$')


class Confirm(BaseModel):
    session_id: str
    confirmation: bool


class Fault(BaseModel):
    session_id: str
    mode: str = Field(
        pattern=r'^(none|policy_conflict|missing_record|service_outage)$')


def facts(intent, persona, fault='none'):
    st = DATA['students'][persona]
    if fault == 'service_outage':
        return {
            'status': 'blocked',
            'reason': 'Synthetic records service unavailable. Retry later; no action executed.',
            'sources': [],
        }

    if intent == 'drop':
        if fault == 'policy_conflict':
            return {
                'status': 'blocked',
                'reason': 'Two synthetic policy sources conflict. Ask the registrar before proceeding.',
                'sources': [DATA['policies']['courseDropConflict']],
            }
        course = next(
            (
                c for c in st.get('courses', [])
                if c['code'] == 'CS 411' and c['status'] == 'Enrolled'
            ),
            None,
        )
        if not course:
            return {
                'status': 'blocked',
                'reason': 'CS 411 not enrolled for this persona.',
                'sources': [],
            }
        policy = DATA['policies']['courseDrop']
        remaining = st['currentCredits'] - course['credits']
        return {
            'status': 'ready',
            'summary': (
                f'Dropping CS 411 changes enrolled credits from '
                f'{st["currentCredits"]} to {remaining}.'
            ),
            'details': {
                'before_credits': st['currentCredits'],
                'after_credits': remaining,
                'full_time_threshold': policy['threshold'],
                'below_threshold': remaining < policy['threshold'],
                'policy_deadline': policy['deadline'],
            },
            'sources': [{
                'title': policy['title'],
                'source': policy['source'],
                'version': policy['version'],
                'synthetic': True,
            }],
            'action': 'Submit synthetic course-drop request',
        }

    if intent == 'graduation':
        if fault == 'missing_record':
            return {
                'status': 'blocked',
                'reason': 'Synthetic degree audit unavailable. Do not infer graduation status.',
                'sources': [],
            }
        grad = st.get('graduation')
        if not grad:
            return {
                'status': 'blocked',
                'reason': 'No degree audit for this persona.',
                'sources': [],
            }
        policy = DATA['policies']['graduation']
        return {
            'status': 'ready',
            'summary': (
                f'{grad["completed"]} credits completed; '
                f'{grad["inProgress"]} in progress; '
                f'{grad["totalRequired"]} required.'
            ),
            'details': {
                'requirements': grad['requirements'],
                'remaining_if_in_progress_pass': max(
                    0,
                    grad['totalRequired'] -
                    grad['completed'] - grad['inProgress'],
                ),
            },
            'sources': [{
                'title': policy['title'],
                'source': policy['source'],
                'version': policy['version'],
                'synthetic': True,
            }],
            'action': 'Save synthetic graduation review plan',
        }

    if intent == 'hold':
        holds = st.get('holds', [])
        if not holds:
            return {
                'status': 'blocked',
                'reason': 'No holds found for this synthetic student.',
                'sources': [],
            }
        policy = DATA['policies']['registration']
        return {
            'status': 'ready',
            'summary': (
                f'{len(holds)} active synthetic registration hold(s). '
                'Review the responsible offices.'
            ),
            'details': {'holds': holds},
            'sources': [{
                'title': policy['title'],
                'source': policy['source'],
                'version': policy['version'],
                'synthetic': True,
            }],
            'action': 'Submit synthetic advising-review request',
        }

    return {
        'status': 'blocked',
        'reason': (
            'Please ask about dropping CS 411, graduation readiness, '
            'or registration holds.'
        ),
        'sources': [],
    }


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
    course = normalize_course(entities.get('course_code'), message)
    return (
        intent,
        {'course_code': course} if intent == 'drop' else {},
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
        raise HTTPException(
            503,
            detail=(
                'Live model unavailable. Check the server configuration/API '
                'quota and retry. No task was submitted.'
            ),
        ) from exc

    if not db.get_student(body.student_id):
        raise HTTPException(404, 'Student not found')
    term = known_term(body.term)
    result = rules.evaluate(intent, body.student_id, entities, term=term)
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
