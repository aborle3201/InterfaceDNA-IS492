"""Deterministic rules for InterfaceDNA's three workflows.
Every fact comes from the synthetic database. The model only supplies the intent
and the entities the student typed; it never supplies credits, deadlines or policy.
"""
from __future__ import annotations

import os
from datetime import date

import db


def today():
    """The date rules are evaluated on. INTERFACEDNA_TODAY=YYYY-MM-DD pins a
    simulated date for classroom demos; otherwise the server's local date."""
    override = os.getenv('INTERFACEDNA_TODAY', '').strip()
    return date.fromisoformat(override) if override else date.today()


def fmt(d):
    d = date.fromisoformat(d) if isinstance(d, str) else d
    return f'{d:%B} {d.day}, {d.year}'


def cite(policy, **extra):
    return {
        'title': policy['title'],
        'source': policy['source'],
        'version': policy['version'],
        'synthetic': True,
        **extra,
    }


def blocked(reason, sources=()):
    return {'status': 'blocked', 'reason': reason, 'sources': list(sources)}


def evaluate(intent, student_id, entities, fault='none', on=None):
    on = on or today()
    if fault == 'service_outage':
        return blocked(
            'Synthetic records service unavailable. Retry later; no action executed.')
    if not db.get_student(student_id):
        return blocked('No synthetic record exists for this student.')
    if intent == 'drop':
        return drop(student_id, entities, fault, on)
    if intent == 'graduation':
        return graduation(student_id, fault)
    if intent == 'hold':
        return hold(student_id, fault)
    return blocked(
        'Please ask about dropping a course, graduation readiness, '
        'or registration holds.')


def drop(student_id, entities, fault, on):
    code = entities.get('course_code')
    if not code:
        return blocked(
            'Which course? Name the course you want to drop, '
            'for example “Can I drop CS 411?”.')
    if fault == 'missing_record':
        return blocked(
            'Synthetic enrollment record unavailable. '
            'Do not infer enrollment or credits.')
    enrollment = db.get_enrollment(student_id, code)
    if not enrollment:
        return blocked(
            f'We could not verify that you are enrolled in {code}. '
            'No action has been enabled.')

    policy = db.get_policy('course_drop')
    if fault == 'policy_conflict':
        calendar = db.get_policy('course_drop_calendar')
        return blocked(
            'I’m not sure which drop deadline applies. Two synthetic sources '
            f'conflict: {calendar["title"]} says {fmt(calendar["deadline"])}; '
            f'{policy["title"]} says {fmt(policy["deadline"])}. '
            'Ask the Registrar before proceeding.',
            [cite(calendar, date=fmt(calendar['deadline'])),
             cite(policy, date=fmt(policy['deadline']))],
        )

    deadline = date.fromisoformat(policy['deadline'])
    if on > deadline:
        return blocked(
            f'The synthetic drop deadline ({fmt(deadline)}) has passed as of '
            f'{fmt(on)}. Contact the Registrar about late-drop options; '
            'no action has been enabled.',
            [cite(policy, date=fmt(deadline))],
        )

    before = db.current_credits(student_id)
    after = before - enrollment['credits']
    return {
        'status': 'ready',
        'summary': (
            f'Dropping {code} ({enrollment["title"]}) changes enrolled credits '
            f'from {before} to {after}.'
        ),
        'details': {
            'course_code': code,
            'course_title': enrollment['title'],
            'course_credits': enrollment['credits'],
            'requirement': enrollment['requirement'],
            'before_credits': before,
            'after_credits': after,
            'full_time_threshold': policy['threshold'],
            'below_threshold': after < policy['threshold'],
            'policy_deadline': fmt(deadline),
            'as_of': fmt(on),
        },
        'sources': [cite(policy, date=fmt(deadline))],
        'action': f'Submit synthetic course-drop request for {code}',
    }


def graduation(student_id, fault):
    if fault == 'missing_record':
        return blocked(
            'Synthetic degree audit unavailable. Do not infer graduation status.')
    audit = db.get_degree_audit(student_id)
    if not audit:
        return blocked('No degree audit exists for this student.')
    policy = db.get_policy('graduation')
    return {
        'status': 'ready',
        'summary': (
            f'{audit["completed"]} credits completed; '
            f'{audit["in_progress"]} in progress; '
            f'{audit["total_required"]} required.'
        ),
        'details': {
            'requirements': audit['requirements'],
            'remaining_if_in_progress_pass': max(
                0,
                audit['total_required'] - audit['completed'] - audit['in_progress'],
            ),
        },
        'sources': [cite(policy)],
        'action': 'Save synthetic graduation review plan',
    }


def hold(student_id, fault):
    if fault == 'missing_record':
        return blocked(
            'Synthetic hold records unavailable. Do not infer registration status.')
    holds = db.get_active_holds(student_id)
    if not holds:
        return blocked('No active holds found for this synthetic student.')
    policy = db.get_policy('registration')
    requestable = [h['office'] for h in holds if h['canRequest']]
    result = {
        'status': 'ready',
        'summary': (
            f'{len(holds)} active synthetic registration hold(s). '
            'Review the responsible offices.'
        ),
        'details': {'holds': holds},
        'sources': [cite(policy)],
        'action': (
            f'Submit synthetic review request to {", ".join(requestable)}'
        ),
    }
    if not requestable:
        result.update(
            status='blocked',
            reason=(
                'Every active hold must be cleared by its office directly; '
                'this interface cannot request a review.'
            ),
        )
    return result
