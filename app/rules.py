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


def evaluate(intent, student_id, entities, fault='none', on=None, term=None):
    on = on or today()
    term = term or db.CURRENT_TERM
    if fault == 'service_outage':
        return blocked(
            'The student records service is unavailable. '
            'Please try again later; no action was taken.')
    student = db.get_student(student_id)
    if not student:
        return blocked('No record exists for this student.')
    if intent == 'drop':
        return drop(student, entities, fault, on, term)
    if intent == 'graduation':
        return graduation(student, fault, on)
    if intent == 'hold':
        return hold(student, fault, on)
    return blocked(
        'Please ask about dropping a course, graduation requirements, '
        'or registration holds.')


# ---- Terms and Registrar deadlines -------------------------------------------

def terms(on=None):
    """Every term with a quoted calendar, oldest first, with its status on `on`."""
    on = on or today()
    out = []
    for t in db.get_terms():
        begins, ends = date.fromisoformat(t['instruction_begins']), date.fromisoformat(t['finals_end'])
        out.append({
            'term': t['term'], 'calendar': t['key'],
            'begins': t['instruction_begins'], 'ends': t['finals_end'],
            'display': f'{fmt(begins).rsplit(",", 1)[0]} – {fmt(ends)}',
            'status': 'past' if on > ends else 'upcoming' if on < begins else 'current',
            'levels': t.get('levels', ['UG', 'GR']),
            'note': db.get_fact(t['key'])['quote'] if t['key'].startswith('w27') else None,
        })
    return out


def term_info(term):
    return next((t for t in terms() if t['term'] == term), None)


def full_term(term):
    """Fall and Spring semesters carry ISSS full-time rules and tuition ranges."""
    return term.split()[0] in ('Fall', 'Spring')


def by_pot(kind, level, term=None):
    """The deadline for each part of term. An entry for one level (e.g. GRAD)
    overrides one that applies to ALL students."""
    out = {}
    for v in sorted(db.get_dated(kind, level, term), key=lambda v: -len(v['levels'])):
        out[v['pot']] = v
    return out


def dated(kind, level, term=None):
    entries = db.get_dated(kind, level, term)
    return entries[0] if entries else None


def parts_of_term(term):
    with db.transaction() as conn:
        row = conn.execute(
            "SELECT key FROM policy_facts WHERE key LIKE '%parts_of_term' AND vals LIKE ?",
            (f'%"term": "{term}"%',)).fetchone()
    return db.get_fact(row['key']) if row else None


def possible_pots(on, term, begins):
    """Parts of term a course can be in on `on`. Before the term starts all are
    possible; once POT A ends (per the Registrar), only POT 1 and B remain."""
    parts = parts_of_term(term)
    a_end = date.fromisoformat(parts['values']['A_ends_approx'])
    if on < begins or on <= a_end:
        return ['1', 'A', 'B'], parts
    return ['1', 'B'], parts


def pot_dates(deadlines, pots):
    return '; '.join(f'{POT[p]}: {fmt(deadlines[p]["date"])}' for p in pots)


def date_label(v, term):
    kind = v['kind']
    if kind in ('event', 'cancel'):
        return v['label']
    return {
        'refund': f'Last day to drop a {POT.get(v.get("pot"), "")} course with a tuition refund',
        'no_w': f'Last day to drop a {POT.get(v.get("pot"), "")} course without a W',
        'withdraw_no_w': f'Last day to withdraw from {term} without a W',
        'apply_graduate': f'Deadline to apply to graduate in {v.get("conferral", "")}',
        'spring_priority_registration': 'Spring 2027 priority registration begins',
        'spring_graduation_application_opens': 'Spring 2027 graduation application opens',
        'spring_open_registration': 'Spring 2027 open registration begins',
        'grad_petition_after': 'Last day to add/drop without a Graduate College petition',
    }.get(kind)


def key_dates(level, term=None, on=None):
    """Dates for one term that apply to a student level, oldest first, each with
    its quoted source: the term's calendar plus any Registrar deadlines."""
    on, term = on or today(), term or db.CURRENT_TERM
    info = term_info(term)
    if not info or level not in info['levels']:
        return []

    def entry(d, label, key):
        f = db.get_fact(key)
        return {'date': d, 'display': fmt(d), 'label': label,
                'past': on > date.fromisoformat(d),
                'source': {'title': f['title'], 'publisher': f['publisher'],
                           'url': f['url'], 'page': f['page'], 'quote': f['quote']}}

    cal = db.get_fact(info['calendar'])['values']
    dates = [entry(cal['instruction_begins'], 'First day of instruction', info['calendar']),
             entry(cal['finals_end'], 'Final examinations end', info['calendar'])]
    with db.transaction() as conn:
        keys = [r['key'] for r in conn.execute("SELECT key FROM policy_facts WHERE vals LIKE '[%'")]
    seen = set()
    for key in keys:
        for v in db.get_fact(key)['values']:
            if v.get('term') != term or level not in v.get('levels', ()):
                continue
            label = date_label(v, term)
            if v['kind'] in ('refund', 'no_w'):
                best = by_pot(v['kind'], level, term).get(v['pot'])
                if not best or (best['date'], best['levels']) != (v['date'], v['levels']):
                    continue  # superseded by a level-specific deadline
            if label and (label, v['date']) not in seen:
                seen.add((label, v['date']))
                dates.append(entry(v['date'], label, key))
    return sorted(dates, key=lambda d: d['date'])


# ---- Course drop ------------------------------------------------------------

def tuition_range(hours, ranges):
    for r in ranges:
        if hours >= r['min'] and (r['max'] is None or hours <= r['max']):
            return r['name']
    return None


def drop(student, entities, fault, on, term):
    code = entities.get('course_code')
    if not code:
        return blocked(
            'Which course? Name the course you want to drop, '
            'for example “Can I drop CS 411?”.')
    if fault == 'missing_record':
        return blocked(
            'Your enrollment record is unavailable right now, so your '
            'credits can’t be verified. Please try again later.')
    info = term_info(term)
    if not info:
        return blocked(f'Course information for {term} isn’t available.')
    courses = db.get_term_courses(student['id'], term)
    course = next((c for c in courses if c['code'] == code), None)
    if not course:
        return blocked(
            f'Your {term} schedule does not include {code}, '
            'so there is nothing to drop. No action has been enabled.')
    if fault == 'policy_conflict':
        return blocked(
            'Two different versions of the drop rules were returned, so I’m not '
            'sure which applies. Ask the Office of the Registrar before proceeding.')

    r = Report()
    level = student['level']
    begins, ends = date.fromisoformat(info['begins']), date.fromisoformat(info['ends'])
    started = on >= begins
    registered = course['status'] == 'Registered'
    before = sum(c['credits'] for c in courses)
    after = before - course['credits']
    r.metric('Course', f'{code} · {course["title"]} · {course["credits"]} hours')
    r.metric(f'{term} hours {"registered" if registered else "now"}', before)
    r.metric('Hours after drop', after)
    r.fact(info['calendar'])

    if course['status'] == 'Completed' or on > ends:
        r.check('block', f'{term} has ended',
                f'Final examinations ended {fmt(ends)}.', [info['calendar']])
        return r.result(f'{term} has ended, so {code} can no longer be dropped.', None)

    if len(courses) == 1 and not started:
        cancel = dated('cancel', level, term)
        if cancel:
            r.check('info', 'Dropping your only course cancels your registration',
                    f'{code} is your only {term} course. {cancel["label"]}: '
                    f'{fmt(cancel["date"])}.', [cancel['key']])
    elif len(courses) == 1:
        cites, extra = ['single_course_withdrawal'], ''
        wd = dated('withdraw_no_w', level, term)
        if wd:
            cites.append(wd['key'])
            extra = (f' The deadline for undergraduates to withdraw from {term} '
                     f'without a grade of W {"is" if on <= date.fromisoformat(wd["date"]) else "was"} '
                     f'{fmt(wd["date"])}.')
        r.check('block', 'Dropping your only course is a withdrawal',
                f'{code} is your only {term} course. Dropping it after '
                'the term starts requires withdrawing from the university.' + extra,
                cites)

    petition = dated('grad_petition_after', level, term)
    if petition and on > date.fromisoformat(petition['date']):
        r.check('block', 'Graduate add/drop now requires a petition',
                'The last day for graduate students to add or drop POT 1 or POT B '
                'courses without petitioning the Graduate College was '
                f'{fmt(petition["date"])}.',
                [petition['key']])

    if full_term(term) and student['visa'] in VISAS:
        minimum = db.get_fact('isss_full_time')['values'][level]
        r.metric(f'{student["visa"]} full-time minimum', minimum)
        if after < minimum:
            cites = ['isss_full_time', 'isss_before_dropping']
            if level == 'GR':
                cites.append('grad_isss_prior_approval')
            r.check('block', 'Contact ISSS before dropping below full time',
                    f'Dropping {code} leaves {after} hours, below the {minimum}-hour '
                    f'minimum for {student["visa"]} {LEVEL_WORD[level]} '
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
                    f'{student["visa"]} {LEVEL_WORD[level]} students.',
                    ['isss_full_time'])

    parts = parts_of_term(term)
    pots = possible_pots(on, term, begins)[0] if parts else []
    refunds = by_pot('refund', level, term)
    if full_term(term) and refunds and pots:
        ranges = r.fact('tuition_ranges')['values']
        rb, ra = tuition_range(before, ranges), tuition_range(after, ranges)
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
        if level == 'GR':
            r.check('info', 'Per-credit-hour programs',
                    'If your program bills per credit hour, billing hours can be '
                    'reduced only by the drop deadline for the course’s part of term.',
                    ['per_credit_hour_programs'])
    r.check('info', 'Other effects to review',
            'Registration changes may affect tuition assessment, financial aid, '
            'waiver eligibility and other aspects of student standing.',
            ['registration_change_impacts'])

    no_w = by_pot('no_w', level, term)
    if not (parts and no_w):
        r.check('unknown', 'Drop deadline not available',
                f'Drop deadlines for {term} aren’t available here. Check the '
                'Registrar’s academic calendar.', [])
    else:
        cites = [parts['key'], *sorted({no_w[p]['key'] for p in pots})]
        still_open = [p for p in pots if on <= date.fromisoformat(no_w[p]['date'])]
        dates = (f'Deadlines for {LEVEL_WORD[level]} students to drop '
                 f'without a grade of W: {pot_dates(no_w, pots)}.')
        if 'A' not in pots:
            dates += (f' First-8-week (POT A) courses ended around '
                      f'{fmt(parts["values"]["A_ends_approx"])}, so a course still in '
                      'progress is POT 1 or POT B.')
        if len(still_open) == len(pots):
            r.check('ok', 'Within the deadline to drop without a W', dates, cites)
        elif not still_open:
            r.check('block', 'The deadline to drop without a W has passed',
                    dates + ' To ask about dropping after these dates, contact your '
                    'college office.', cites)
        else:
            r.check('unknown', 'Drop deadline depends on the course’s part of term',
                    f'{code} is on the {term} class schedule, but its part of '
                    'term isn’t available here. ' + dates + ' Check the Section Details on '
                    'Course Explorer.', cites + ['drop_deadlines_by_part_of_term'])

    summary = (f'Dropping {code} would take your {term} registration from {before} to {after} hours.'
               if registered else
               f'Dropping {code} would take you from {before} to {after} credit hours.')
    return r.result(summary, f'Submit course-drop request for {code} ({term})')


# ---- Graduation -------------------------------------------------------------

def course_level(code):
    return int(code.split()[1])


def graduation(student, fault, on):
    if fault == 'missing_record':
        return blocked(
            'Your degree audit is unavailable right now, so graduation '
            'status can’t be determined. Please try again later.')
    prog = db.get_program(student['program'])
    r = Report()
    r.program(student['program'], prog)
    if not prog['audit_supported']:
        return blocked(
            f'Degree checks for {prog["name"]} aren’t available online yet. '
            'Contact your graduate program office.', r)

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

    apply = dated('apply_graduate', student['level'], db.CURRENT_TERM)
    if apply and not missing and now_hours and done_hours + now_hours >= prog['total_hours']:
        deadline = date.fromisoformat(apply['date'])
        r.check('info' if on <= deadline else 'warn', f'Apply to graduate in {apply["conferral"]}',
                (f'Apply via Student Self-Service by {fmt(deadline)}.' if on <= deadline else
                 f'The deadline to apply to graduate in {apply["conferral"]} was {fmt(deadline)}; '
                 'after that date, contact your Academic Office.')
                + ' Applications are made through Student Self-Service.',
                [apply['key']], blocks=False)

    for item in prog['not_evaluated']:
        r.check('unknown', item,
                'Not included in this check; confirm with your academic advisor.',
                blocks=False)

    summary = (
        f'{missing} checked requirement(s) not yet covered by completed or current courses.'
        if missing else
        'Every checked requirement is met or in progress; on track if current courses are passed.')
    return r.result(summary, 'Save graduation review plan')


# ---- Registration holds -----------------------------------------------------

def hold(student, fault, on):
    if fault == 'missing_record':
        return blocked(
            'Hold records are unavailable right now, so registration status '
            'can’t be determined. Please try again later.')
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
        r.check('ok', 'No active holds', 'You have no active holds.',
                blocks=False)
        return r.result('You have no active holds.',
                        None, status='info')
    for h in holds:
        r.check('warn', h['type'], f'{h["detail"]} Placed {h["placed_term"]}.',
                blocks=False)
    r.check('info', 'What holds can block',
            'Holds may prohibit registration changes, receiving a transcript or '
            'graduating, and appear in the Registration section of Self-Service.'
            + (' This description is from the Graduate College Handbook; '
               'undergraduate procedures may differ.' if student['level'] == 'UG' else ''),
            ['holds_general'])
    r.check('unknown', 'Which office clears each hold',
            'Check the hold details in the Registration section of Student '
            'Self-Service.', blocks=False)
    return r.result(
        f'{len(holds)} active hold(s) on your record may block '
        f'{spring["term"]} registration.',
        f'Save a reminder to resolve {len(holds)} hold(s) before {spring["term"]}')
