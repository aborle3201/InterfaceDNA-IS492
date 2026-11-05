"""Deterministic rules for InterfaceDNA's three workflows.

Student facts come from the synthetic database. University facts come only from
policy facts and catalog requirements quoted from real UIUC documents
(sources/policies.json, sources/programs.json). When the sources do not answer
a question, the check is reported as unverified instead of guessed. The model
only supplies the intent and the entities the student typed.

Each result has: status ('ready' | 'blocked' | 'info'), summary, optional reason,
metrics, checks (level ok | info | warn | block | unknown), cited sources, and
an action only when status is 'ready'.
"""
from __future__ import annotations

import os
from datetime import date

import db
from generate_students import GRADES

VISAS = ('F-1', 'J-1')
LEVEL_WORD = {'UG': 'undergraduate', 'GR': 'graduate'}
POT = {'1': 'full semester (POT 1)', 'A': 'first 8 weeks (POT A)',
       'B': 'second 8 weeks (POT B)'}


def today():
    """The date rules are evaluated on. INTERFACEDNA_TODAY=YYYY-MM-DD pins a
    simulated date for demos; otherwise the server's local date."""
    override = os.getenv('INTERFACEDNA_TODAY', '').strip()
    return date.fromisoformat(override) if override else date.today()


def fmt(d):
    d = date.fromisoformat(d) if isinstance(d, str) else d
    return f'{d:%B} {d.day}, {d.year}'


class Report:
    def __init__(self):
        self.metrics, self.checks, self.sources = [], [], {}

    def metric(self, label, value):
        self.metrics.append({'label': label, 'value': value})

    def fact(self, key):
        f = db.get_fact(key)
        self.sources[key] = {
            'key': key, 'title': f['title'], 'publisher': f['publisher'], 'url': f['url'],
            'document': f['document'], 'page': f['page'], 'quote': f['quote'],
            'retrieved': f['retrieved'], 'synthetic': False,
        }
        return f

    def program(self, code, prog):
        quote = prog['quotes'][0]
        self.sources[f'program:{code}'] = {
            'key': f'program:{code}', 'title': f'{prog["name"]} — Academic Catalog {prog["catalog"]}',
            'publisher': 'University of Illinois Urbana-Champaign',
            'url': 'http://catalog.illinois.edu/',
            'document': 'UIUC catalog 2026-2027.pdf', 'page': prog['pages'],
            'quote': quote['quote'], 'retrieved': '2026-11-04', 'synthetic': False,
        }

    def check(self, level, title, text, cites=(), blocks=None):
        for key in cites:
            self.fact(key)
        self.checks.append({
            'level': level, 'title': title, 'text': text, 'cites': list(cites),
            'blocks': level in ('block', 'unknown') if blocks is None else blocks,
        })

    def result(self, summary, action, status=None):
        blocking = [c for c in self.checks if c['blocks']]
        status = status or ('blocked' if blocking else 'ready')
        out = {
            'status': status,
            'summary': summary,
            'metrics': self.metrics,
            'checks': self.checks,
            'sources': list(self.sources.values()),
            'action': action if status == 'ready' else None,
        }
        if blocking:
            out['reason'] = ' '.join(f'{c["title"]}.' for c in blocking)
        return out


def blocked(reason, report=None):
    out = (report or Report()).result(reason, None, status='blocked')
    out['reason'] = reason
    return out


def evaluate(intent, student_id, entities, fault='none', on=None):
    on = on or today()
    if fault == 'service_outage':
        return blocked(
            'Simulated fault: the student records service is unavailable. '
            'Retry later; no action executed.')
    student = db.get_student(student_id)
    if not student:
        return blocked('No synthetic record exists for this student.')
    if intent == 'drop':
        return drop(student, entities, fault, on)
    if intent == 'graduation':
        return graduation(student, fault, on)
    if intent == 'hold':
        return hold(student, fault, on)
    return blocked(
        'Please ask about dropping a course, graduation requirements, '
        'or registration holds.')


# ---- Registrar deadlines -----------------------------------------------------

def by_pot(kind, level):
    """The deadline for each part of term. An entry for one level (e.g. GRAD)
    overrides one that applies to ALL students."""
    out = {}
    for v in sorted(db.get_dated(kind, level), key=lambda v: -len(v['levels'])):
        out[v['pot']] = v
    return out


def dated(kind, level):
    entries = db.get_dated(kind, level)
    return entries[0] if entries else None


def possible_pots(on):
    """Parts of term a course still in progress on `on` can be in. POT A ends
    around October 16 per the Registrar, so later only POT 1 and B remain."""
    a_end = db.get_fact('f26_parts_of_term')['values']['A_ends_approx']
    return ['1', 'B'] + (['A'] if on <= date.fromisoformat(a_end) else [])


def pot_dates(deadlines, pots):
    return '; '.join(f'{POT[p]}: {fmt(deadlines[p]["date"])}' for p in pots)


# ---- Course drop ------------------------------------------------------------

def tuition_range(hours, ranges):
    for r in ranges:
        if hours >= r['min'] and (r['max'] is None or hours <= r['max']):
            return r['name']
    return None


def drop(student, entities, fault, on):
    code = entities.get('course_code')
    if not code:
        return blocked(
            'Which course? Name the course you want to drop, '
            'for example “Can I drop CS 411?”.')
    if fault == 'missing_record':
        return blocked(
            'Simulated fault: the enrollment record is unavailable. '
            'Do not infer enrollment or credits.')
    current = db.get_current(student['id'])
    course = next((c for c in current if c['code'] == code), None)
    if not course:
        return blocked(
            f'Your {db.CURRENT_TERM} schedule does not include {code}, '
            'so there is nothing to drop. No action has been enabled.')
    if fault == 'policy_conflict':
        return blocked(
            'Simulated fault: the policy store returned two different versions '
            'of the drop rules. I’m not sure which applies; ask the Office of '
            'the Registrar before proceeding.')

    r = Report()
    before = sum(c['credits'] for c in current)
    after = before - course['credits']
    r.metric('Course', f'{code} · {course["title"]} · {course["credits"]} hours')
    r.metric('Hours now', before)
    r.metric('Hours after drop', after)

    cal = r.fact('calendar_fall_2026')['values']
    if on > date.fromisoformat(cal['finals_end']):
        r.check('block', f'{cal["term"]} has ended',
                f'Final examinations ended {fmt(cal["finals_end"])}.',
                ['calendar_fall_2026'])

    if len(current) == 1:
        cites, extra = ['single_course_withdrawal'], ''
        wd = dated('withdraw_no_w', student['level'])
        if wd:
            cites.append(wd['key'])
            extra = (f' The deadline for undergraduates to withdraw from '
                     f'{db.CURRENT_TERM} without a grade of W '
                     f'{"is" if on <= date.fromisoformat(wd["date"]) else "was"} '
                     f'{fmt(wd["date"])}.')
        r.check('block', 'Dropping your only course is a withdrawal',
                f'{code} is your only {db.CURRENT_TERM} course. Dropping it after '
                'the term starts requires withdrawing from the university.' + extra,
                cites)

    petition = dated('grad_petition_after', student['level'])
    if petition and on > date.fromisoformat(petition['date']):
        r.check('block', 'Graduate add/drop now requires a petition',
                'The last day for graduate students to add or drop POT 1 or POT B '
                'courses without petitioning the Graduate College was '
                f'{fmt(petition["date"])}.',
                [petition['key']])

    if student['visa'] in VISAS:
        minimum = db.get_fact('isss_full_time')['values'][student['level']]
        r.metric(f'{student["visa"]} full-time minimum', minimum)
        if after < minimum:
            cites = ['isss_full_time', 'isss_before_dropping']
            if student['level'] == 'GR':
                cites.append('grad_isss_prior_approval')
            r.check('block', 'Contact ISSS before dropping below full time',
                    f'Dropping {code} leaves {after} hours, below the {minimum}-hour '
                    f'minimum for {student["visa"]} {LEVEL_WORD[student["level"]]} '
                    'students. ISSS must be contacted first; failing to do so may '
                    'result in termination of immigration status.',
                    cites)
            if student['assistantship']:
                r.check('info', 'Possible exception',
                        'ISSS lists automatic exceptions for some students with '
                        'assistantships; only ISSS can confirm whether one applies.',
                        ['isss_exceptions'])
        else:
            r.check('ok', 'Stays at or above the visa full-time minimum',
                    f'{after} hours meets the {minimum}-hour minimum for '
                    f'{student["visa"]} {LEVEL_WORD[student["level"]]} students.',
                    ['isss_full_time'])

    pots = possible_pots(on)
    ranges = r.fact('tuition_ranges')['values']
    rb, ra = tuition_range(before, ranges), tuition_range(after, ranges)
    refunds = by_pot('refund', student['level'])
    refund_cites = ['tuition_ranges', 'tuition_range_refund',
                    *sorted({refunds[p]['key'] for p in pots})]
    refund_open = [p for p in pots if on <= date.fromisoformat(refunds[p]['date'])]
    if rb != ra and not refund_open:
        r.check('info', f'Tuition range changes from {rb} to {ra}, but no refund applies',
                'A refund for a lower range requires dropping by the refund deadline '
                f'for the course’s part of term ({pot_dates(refunds, pots)}), and '
                'those dates have passed.',
                refund_cites + ['drop_deadlines_by_part_of_term'])
    elif rb != ra:
        r.check('info', f'Tuition range changes from {rb} to {ra}',
                'In range-based tuition programs, the refund is the full difference '
                'between the two ranges if the drop is made by the refund deadline '
                f'for the course’s part of term ({pot_dates(refunds, pots)}).',
                refund_cites)
    else:
        r.check('info', f'Tuition range stays {rb}',
                'In range-based tuition programs, no refund is available for '
                'reducing hours within the same range.',
                ['tuition_ranges', 'tuition_range_refund'])
    if student['level'] == 'GR':
        r.check('info', 'Per-credit-hour programs',
                'If your program bills per credit hour, billing hours can be '
                'reduced only by the drop deadline for the course’s part of term.',
                ['per_credit_hour_programs'])
    r.check('info', 'Other effects to review',
            'Registration changes may affect tuition assessment, financial aid, '
            'waiver eligibility and other aspects of student standing.',
            ['registration_change_impacts'])

    no_w = by_pot('no_w', student['level'])
    cites = ['f26_parts_of_term', *sorted({no_w[p]['key'] for p in pots})]
    still_open = [p for p in pots if on <= date.fromisoformat(no_w[p]['date'])]
    dates = (f'Deadlines for {LEVEL_WORD[student["level"]]} students to drop '
             f'without a grade of W: {pot_dates(no_w, pots)}.')
    if 'A' not in pots:
        dates += (' First-8-week (POT A) courses ended around October 16, so a '
                  'course still in progress is POT 1 or POT B.')
    if len(still_open) == len(pots):
        r.check('ok', 'Within the deadline to drop without a W', dates, cites)
    elif not still_open:
        r.check('block', 'The deadline to drop without a W has passed',
                dates + ' The loaded sources do not cover dropping after these '
                'dates; contact your college office.', cites)
    else:
        r.check('unknown', 'Drop deadline depends on the course’s part of term',
                f'The loaded class schedules list {code} for {db.CURRENT_TERM} but '
                'not its part of term. ' + dates + ' Check the Section Details on '
                'Course Explorer.', cites + ['drop_deadlines_by_part_of_term'])

    return r.result(
        f'Dropping {code} would take you from {before} to {after} credit hours.',
        f'Submit synthetic course-drop request for {code}')


# ---- Graduation -------------------------------------------------------------

def course_level(code):
    return int(code.split()[1])


def graduation(student, fault, on):
    if fault == 'missing_record':
        return blocked(
            'Simulated fault: the degree audit is unavailable. '
            'Do not infer graduation status.')
    prog = db.get_program(student['program'])
    r = Report()
    r.program(student['program'], prog)
    if not prog['audit_supported']:
        return blocked(
            f'Degree checks for {prog["name"]} are not supported in this '
            'prototype. Contact your graduate program office.', r)

    records = db.get_records(student['id'])
    passed = [x for x in records if x['status'] == 'Completed' and x['grade'] != 'F']
    current = [x for x in records if x['status'] == 'Enrolled']
    done_codes = {x['code'] for x in passed}
    now_codes = {x['code'] for x in current}
    done_hours = sum(x['credits'] for x in passed)
    now_hours = sum(x['credits'] for x in current)

    r.metric('Hours completed', done_hours)
    r.metric('Hours in progress', now_hours)
    r.metric('Hours required', prog['total_hours'])

    missing = 0

    def threshold(title, done, now, need, unit='hours'):
        nonlocal missing
        if done >= need:
            r.check('ok', title, f'{done} of {need} {unit} completed.', blocks=False)
        elif done + now >= need:
            r.check('info', title,
                    f'{done} of {need} {unit} completed; met if current courses are passed.',
                    blocks=False)
        else:
            missing += 1
            r.check('warn', title,
                    f'{done} completed + {now} in progress of {need} {unit}; '
                    f'{need - done - now} still needed.', blocks=False)

    threshold('Total hours', done_hours, now_hours, prog['total_hours'])

    for req in prog['required']:
        hit = [c for c in req['any_of'] if c in done_codes]
        if hit:
            r.check('ok', req['label'], f'Completed ({hit[0]}).', blocks=False)
        elif any(c in now_codes for c in req['any_of']):
            now = next(c for c in req['any_of'] if c in now_codes)
            r.check('info', req['label'], f'In progress ({now}).', blocks=False)
        else:
            missing += 1
            r.check('warn', req['label'],
                    f'Not found in completed or current courses '
                    f'(any of: {", ".join(req["any_of"])}).', blocks=False)

    if 'upper_division_hours' in prog:
        upper = lambda rows: sum(x['credits'] for x in rows if course_level(x['code']) >= 300)
        threshold('Upper-division hours (300/400-level)', upper(passed), upper(current),
                  prog['upper_division_hours'])

    te = prog.get('technical_electives')
    if te:
        def eligible(x):
            return (x['code'] in te['also_eligible']
                    or (x['code'].startswith(te['subject'] + ' ')
                        and course_level(x['code']) // 100 * 100 in te['levels']
                        and x['code'] not in te['excluded']))
        core = {c for req in prog['required'] for c in req['any_of']}
        done_te = [x for x in passed if eligible(x) and x['code'] not in core]
        now_te = [x for x in current if eligible(x) and x['code'] not in core]
        threshold('Technical electives (courses)', len(done_te), len(now_te),
                  te['min_courses'], 'courses')
        threshold('Technical electives (hours)', sum(x['credits'] for x in done_te),
                  sum(x['credits'] for x in now_te), te['min_hours'])
        team = [x for x in done_te + now_te if x['code'] in te['team_project']
                and x['credits'] >= te['team_project_min_credits'].get(x['code'], 0)]
        if team:
            r.check('ok' if team[0] in done_te else 'info', 'Team project course',
                    f'{team[0]["code"]} ' + ('completed.' if team[0] in done_te
                                             else 'in progress.'), blocks=False)
        else:
            missing += 1
            r.check('warn', 'Team project course',
                    'None of the technical electives is on the team project list.',
                    blocks=False)

    if 'school_hours' in prog:
        subj = prog['school_subject'] + ' '
        school = lambda rows: sum(x['credits'] for x in rows if x['code'].startswith(subj))
        threshold(f'{prog["school_subject"]} hours (School of Information Sciences)',
                  school(passed), school(current), prog['school_hours'])

    if 'min_gpa' in prog:
        points = dict(GRADES)
        graded = [x for x in records if x['status'] == 'Completed' and x['grade']]
        for title, rows, need in [
                ('Cumulative GPA', graded, prog['min_gpa']),
                ('GPA in School courses',
                 [x for x in graded if x['code'].startswith(prog['school_subject'] + ' ')],
                 prog['min_school_gpa'])]:
            hours = sum(x['credits'] for x in rows)
            gpa = round(sum(x['credits'] * points[x['grade']] for x in rows) / hours, 2) if hours else None
            if gpa is None:
                r.check('unknown', title, 'No graded courses yet.', blocks=False)
            elif gpa >= need:
                r.check('ok', title, f'{gpa:.2f} (minimum {need:.2f}).', blocks=False)
            else:
                missing += 1
                r.check('warn', title, f'{gpa:.2f}, below the {need:.2f} minimum.',
                        blocks=False)

    apply = dated('apply_graduate_december', student['level'])
    if apply and not missing and now_hours and done_hours + now_hours >= prog['total_hours']:
        deadline = date.fromisoformat(apply['date'])
        r.check('info' if on <= deadline else 'warn', 'Apply to graduate in December',
                (f'Apply via Student Self-Service by {fmt(deadline)}.' if on <= deadline else
                 f'The deadline to apply to graduate in December was {fmt(deadline)}; '
                 'after that date, contact your Academic Office.')
                + ' This synthetic record does not show whether you already applied.',
                [apply['key']], blocks=False)

    for item in prog['not_evaluated']:
        r.check('unknown', item,
                'Not checked by this prototype; confirm with your academic advisor.',
                blocks=False)

    summary = (
        f'{missing} checked requirement(s) not yet covered by completed or current courses.'
        if missing else
        'Every checked requirement is met or in progress; on track if current courses are passed.')
    return r.result(summary, 'Save synthetic graduation review plan')


# ---- Registration holds -----------------------------------------------------

def hold(student, fault, on):
    if fault == 'missing_record':
        return blocked(
            'Simulated fault: hold records are unavailable. '
            'Do not infer registration status.')
    holds = db.get_active_holds(student['id'])
    r = Report()
    spring = r.fact('calendar_spring_2027')['values']
    r.metric('Active holds', len(holds))
    r.metric('Next term', f'{spring["term"]} (instruction begins {fmt(spring["instruction_begins"])})')
    priority = dated('spring_priority_registration', student['level'])
    open_reg = dated('spring_open_registration', student['level'])
    if priority and open_reg:
        verb = lambda d: 'began' if on >= date.fromisoformat(d) else 'begins'
        r.check('info', f'{spring["term"]} registration dates',
                f'Priority registration {verb(priority["date"])} {fmt(priority["date"])}; '
                f'open registration {verb(open_reg["date"])} {fmt(open_reg["date"])}.',
                [priority['key'], open_reg['key']], blocks=False)
    if not holds:
        r.check('ok', 'No active holds', 'This synthetic record has no active holds.',
                blocks=False)
        return r.result('No active holds were found on this synthetic record.',
                        None, status='info')
    for h in holds:
        r.check('warn', h['type'], f'{h["detail"]} (Synthetic record, placed {h["placed_term"]}.)',
                blocks=False)
    r.check('info', 'What holds can block',
            'Holds may prohibit registration changes, receiving a transcript or '
            'graduating, and appear in the Registration section of Self-Service.'
            + (' This description is from the Graduate College Handbook; '
               'undergraduate procedures may differ.' if student['level'] == 'UG' else ''),
            ['holds_general'])
    r.check('unknown', 'Which office clears each hold',
            'The loaded sources do not say which office handles each hold type; '
            'check the hold details in Self-Service.', blocks=False)
    return r.result(
        f'{len(holds)} active hold(s) on this synthetic record may block '
        f'{spring["term"]} registration.',
        f'Save synthetic reminder to resolve {len(holds)} hold(s) before {spring["term"]}')
