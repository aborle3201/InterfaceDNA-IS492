"""Checkpoint 3 API: live model intent/entity extraction + deterministic verified workflows.
Only synthetic student data and simulated university actions are supported.
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
INTENTS = ('drop', 'graduation', 'hold', 'unknown')
COURSE = re.compile(r'\b([A-Za-z]{2,4})\s*-?\s*(\d{3})\b')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)
log = logging.getLogger('interfacedna')


class Start(BaseModel):
    message: str = Field(min_length=3, max_length=1000)
    persona: str = Field(pattern=r'^(alex|maya|jordan)$')


class Confirm(BaseModel):
    session_id: str
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

    result = rules.evaluate(intent, body.persona, entities)
    sid = str(uuid.uuid4())
    state = 'review' if result['status'] == 'ready' else 'blocked'
    db.create_session(sid, body.persona, intent, entities, state)
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
        sess['intent'], sess['student_id'], sess['entities'], body.mode)
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
        sess['intent'], sess['student_id'], sess['entities'], sess['fault'])
    if current['status'] != 'ready':
        db.update_session(body.session_id, 'blocked', sess['fault'])
        raise HTTPException(
            409, f'Source validation failed: {current["reason"]}')
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
            'Synthetic backend action recorded. '
            'No university system was changed.'
        ),
    }
