"""Checkpoint 3 API: live model classification + deterministic verified demo workflows.
Only synthetic student data and simulated university actions are supported.
"""
from __future__ import annotations

import json
import logging
import os
import pathlib
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
DATA = json.loads((BASE / 'demo_data.json').read_text())
SYSTEM = (BASE / 'prompts' / 'system.txt').read_text()
SETTINGS = json.loads((BASE / 'prompts' / 'settings.json').read_text())

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)
log = logging.getLogger('interfacedna')
SESSIONS = {}
GUARD = Lock()


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
    """Classify using a real Groq API call; never silently substitute a mock response."""
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
    if intent not in ('drop', 'graduation', 'hold', 'unknown'):
        raise RuntimeError('Model produced an invalid task classification.')
    return (
        intent,
        str(output.get('explanation', ''))[:500],
        {
            'model': resp.model,
            'input_tokens': getattr(resp.usage, 'prompt_tokens', None),
            'output_tokens': getattr(resp.usage, 'completion_tokens', None),
        },
    )


app = FastAPI(title='InterfaceDNA CP3', version='0.1.0')

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
    }


@app.post('/api/start')
def start(body: Start):
    tic = time.perf_counter()
    try:
        intent, explanation, usage = classify_live(body.message)
    except Exception as exc:
        log.exception('Groq model call failed')
        raise HTTPException(
            503,
            detail=(
                'Live model unavailable. Check the server configuration/API '
                'quota and retry. No task was submitted.'
            ),
        ) from exc

    result = facts(intent, body.persona)
    sid = str(uuid.uuid4())
    state = 'review' if result['status'] == 'ready' else 'blocked'
    with GUARD:
        SESSIONS[sid] = {
            'intent': intent,
            'persona': body.persona,
            'state': state,
            'fault': 'none',
        }
    log.info(
        'inference intent=%s model=%s input_tokens=%s output_tokens=%s latency_ms=%.0f',
        intent,
        usage['model'],
        usage['input_tokens'],
        usage['output_tokens'],
        (time.perf_counter() - tic) * 1000,
    )
    return {
        'session_id': sid,
        'intent': intent,
        'interpretation': explanation,
        'model_usage': usage,
        'result': result,
        'state': state,
    }


@app.post('/api/fault')
def fault(body: Fault):
    with GUARD:
        sess = SESSIONS.get(body.session_id)
        if not sess:
            raise HTTPException(404, 'Session not found')
        if sess['state'] == 'completed':
            raise HTTPException(409, 'Cannot mutate completed session')
        sess['fault'] = body.mode
        result = facts(sess['intent'], sess['persona'], body.mode)
        sess['state'] = 'review' if result['status'] == 'ready' else 'blocked'
        return {
            'state': sess['state'],
            'result': result,
            'session_id': body.session_id,
        }


@app.post('/api/confirm')
def confirm(body: Confirm):
    with GUARD:
        sess = SESSIONS.get(body.session_id)
        if not sess:
            raise HTTPException(404, 'Session not found')
        if not body.confirmation:
            raise HTTPException(400, 'Explicit confirmation required')
        if sess['state'] != 'review':
            raise HTTPException(
                409, 'Task is not confirmable in current state')
        current = facts(sess['intent'], sess['persona'], sess['fault'])
        if current['status'] != 'ready':
            raise HTTPException(409, 'Source validation failed')
        # Synthetic backend action only; no university connectivity or enrollment changes.
        sess['state'] = 'completed'
        return {
            'state': 'completed',
            'receipt': str(uuid.uuid4()),
            'description': current['action'],
            'synthetic': True,
            'message': (
                'Synthetic backend action recorded. '
                'No university system was changed.'
            ),
        }
