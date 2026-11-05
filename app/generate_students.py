"""Generate synthetic student records for InterfaceDNA.

Only the students are fictional: names, IDs, visa status, grades, holds and
course histories. Every course code, title and credit range comes from
sources/courses.json (real UIUC catalog data), and the semester plans follow the
2026-2027 catalog requirements in sources/programs.json. Current-term CS and IS
enrollments use only courses on the Fall 2026 Course Explorer schedules
(sources/offerings.json). Generation is seeded, so every run produces the same
students.

Preview:  python generate_students.py
"""
from __future__ import annotations

import collections
import json
import pathlib
import random

BASE = pathlib.Path(__file__).parent
SEED = 492
COUNTS = {'CS_BS': 110, 'IS_BS': 100, 'CS_MCS': 20, 'IM_MS': 20}
CURRENT_TERM = 'Fall 2026'
PAST_TERMS = ['Spring 2026', 'Fall 2025', 'Spring 2025', 'Fall 2024',
              'Spring 2024', 'Fall 2023', 'Spring 2023']  # most recent first

# 4.00 = A per the catalog; the remaining steps follow the standard 4-point scale.
GRADES = [('A', 4.0), ('A-', 3.67), ('B+', 3.33), ('B', 3.0), ('B-', 2.67),
          ('C+', 2.33), ('C', 2.0), ('C-', 1.67), ('D', 1.0), ('F', 0.0)]

GEN = ['ECON 103', 'PSYC 100', 'SOC 100', 'ANTH 101', 'CMN 101', 'LING 100',
       'MUS 132', 'GLBL 100', 'AAS 100', 'AFRO 100', 'LLS 100', 'IB 150',
       'GEOL 107', 'PHIL 103']
ELEC = GEN + ['STAT 207', 'ACCY 201', 'BADM 310', 'MATH 225', 'MATH 227',
              'ECON 102', 'STAT 400']
CS_TE = ['CS 410', 'CS 411', 'CS 412', 'CS 414', 'CS 416', 'CS 418', 'CS 419',
         'CS 425', 'CS 427', 'CS 428', 'CS 431', 'CS 433', 'CS 435', 'CS 437',
         'CS 438', 'CS 440', 'CS 441', 'CS 444', 'CS 446', 'CS 447', 'CS 450',
         'CS 461', 'CS 463', 'CS 467', 'CS 473', 'CS 475', 'CS 477']
IS_E = ['IS 226', 'IS 236', 'IS 305', 'IS 310', 'IS 316', 'IS 324', 'IS 327',
        'IS 340', 'IS 357', 'IS 364', 'IS 401', 'IS 407', 'IS 424', 'IS 439',
        'IS 445', 'IS 455', 'IS 457', 'IS 467', 'IS 477']
RANDOM = object()  # sentinel: let the generator choose
POOLS = {'GEN': GEN, 'ELEC': ELEC, 'TE': CS_TE, 'ISE': IS_E,
         'IS_CULT': ['IS 308', 'IS 309']}

PLANS = {
    'CS_BS': [
        ['CS 124', 'MATH 221', 'ENG 100', 'ECON 102', 'CHEM 102', 'CHEM 103'],
        ['CS 128', 'CS 173', 'MATH 231', 'PHYS 211', 'GEN'],
        ['CS 222', 'CS 225', 'MATH 241', 'PHYS 212', 'GEN'],
        ['CS 233', 'CS 361', 'MATH 257', 'CS 210', 'GEN'],
        ['CS 341', 'CS 357', 'CS 374', 'GEN', 'GEN'],
        ['CS 421', 'TE', 'TE', 'GEN', 'GEN'],
        ['TE', 'TE', 'STAT 400', 'GEN', 'GEN'],
        ['TE', 'TE', 'GEN', 'GEN', 'ELEC'],
    ],
    'IS_BS': [
        ['IS 101', 'IS 107', 'GEN', 'GEN', 'GEN'],
        ['IS 202', 'IS 203', 'GEN', 'GEN', 'GEN'],
        ['IS 204', 'IS 205', 'ELEC', 'GEN', 'GEN'],
        ['IS 206', 'IS_CULT', 'ISE', 'GEN', 'GEN'],
        ['ISE', 'ISE', 'ELEC', 'ELEC', 'GEN'],
        ['ISE', 'ISE', 'ISE', 'ELEC', 'ELEC'],
        ['ISE', 'ISE', 'ELEC', 'ELEC', 'ELEC'],
        ['ISE', 'ISE', 'ISE', 'ELEC', 'ELEC'],
    ],
}
GRAD_POOLS = {
    'CS_MCS': CS_TE + ['CS 511', 'CS 512', 'CS 519', 'CS 521', 'CS 525'],
    'IM_MS': ['IS 501', 'IS 504', 'IS 505', 'IS 507', 'IS 509', 'IS 510',
              'IS 514', 'IS 515', 'IS 517', 'IS 518', 'IS 519', 'IS 525',
              'IS 534', 'IS 455', 'IS 445', 'IS 467', 'IS 477'],
}

# Hold categories are the common reasons listed in the Graduate College
# Handbook 2026-2027; the per-student details are synthetic.
HOLDS = {
    'Immunization requirement': 'Required immunization records are not on file.',
    'Financial encumbrance': 'Unpaid balance on the student account.',
    'Departmental deficiency': 'Department requires a completed advising check-in.',
    'Missing transcripts': 'Final transcript from a previous institution has not been received.',
}
LOW_GPA_HOLD = ('Low GPA', 'Cumulative GPA is below the level required by the college.')

FIRST = ['Aarav', 'Abena', 'Aiden', 'Amara', 'Ana', 'Arjun', 'Ayesha', 'Ben',
         'Camila', 'Chen', 'Chloe', 'Daniel', 'Deja', 'Diego', 'Elena', 'Eli',
         'Fatima', 'Grace', 'Hana', 'Ibrahim', 'Isabel', 'Jamal', 'Ji-woo',
         'Kai', 'Kavya', 'Liam', 'Lucia', 'Malik', 'Mei', 'Mohammed', 'Nadia',
         'Noah', 'Olivia', 'Omar', 'Priya', 'Rafael', 'Rhea', 'Samir', 'Sara',
         'Sofia', 'Tariq', 'Thanh', 'Tomas', 'Valentina', 'Wei', 'Yara',
         'Yusuf', 'Zoe']
LAST = ['Abara', 'Alvarez', 'Bakshi', 'Boateng', 'Castillo', 'Chowdhury',
        'Dang', 'Delgado', 'Ekwueme', 'Fischer', 'Gallagher', 'Haddad', 'Hsu',
        'Iyer', 'Jensen', 'Kaur', 'Kowalski', 'Lindqvist', 'Mahmoud', 'Marsh',
        'Mensah', 'Nakamura', 'Novak', 'Okafor', 'Oyelaran', 'Park', 'Quinn',
        'Ramaswamy', 'Reyes', 'Sato', 'Schmidt', 'Shah', 'Sorensen', 'Tan',
        'Thornton', 'Udeh', 'Varga', 'Whitfield', 'Xu', 'Yilmaz', 'Zamora']


def load_courses():
    data = json.loads((BASE / 'sources' / 'courses.json').read_text())
    return {c['code']: c for c in data}


def load_offered(term=CURRENT_TERM):
    """Subjects with a schedule for the term, and the courses they offer."""
    data = json.loads((BASE / 'sources' / 'offerings.json').read_text())[term]
    return set(data), {c for s in data.values() for c in s['courses']}


class Generator:
    def __init__(self, courses, seed=SEED):
        self.courses = courses
        self.rng = random.Random(seed)
        self.ids = (f'S{n:05d}' for n in range(1, 100000))
        self.names = set()
        self.scheduled, self.offered = load_offered()
        for pool in [*POOLS.values(), *GRAD_POOLS.values()]:
            for code in pool:
                self.course(code)

    def course(self, code):
        if code not in self.courses:
            raise KeyError(f'{code} is not in sources/courses.json')
        return self.courses[code]

    def name(self):
        while True:
            name = f'{self.rng.choice(FIRST)} {self.rng.choice(LAST)}'
            if name not in self.names:
                self.names.add(name)
                return name

    def credits(self, code, level):
        c = self.course(code)
        lo, hi = max(c['credits_min'], 1), c['credits_max']
        if lo == hi:
            return lo
        return hi if level == 'GR' or self.rng.random() < 0.3 else max(lo, 3 if hi >= 3 else lo)

    def grade(self, ability):
        weights = [max(0.02, 1 - abs(ability + 0.25 - pts) / 1.4) for _, pts in GRADES]
        weights[-1] = 0.015  # F
        return self.rng.choices(GRADES, weights)[0][0]

    def offered_now(self, code):
        return code.split()[0] not in self.scheduled or code in self.offered

    def resolve(self, slot, taken, current=False):
        if slot not in POOLS:
            if current and not self.offered_now(slot):
                raise ValueError(f'{slot} is not offered in {CURRENT_TERM}')
            return slot
        options = [c for c in POOLS[slot] if c not in taken
                   and (not current or self.offered_now(c))]
        return self.rng.choice(options)

    def semester(self, slots, taken, current=False):
        codes = []
        for slot in slots:
            code = self.resolve(slot, taken, current)
            taken.add(code)
            codes.append(code)
        return codes

    def student(self, program, *, sid=None, name=None, visa=RANDOM, done=None,
                ability=None, current=None, holds=None, assistantship=None,
                load='normal'):
        rng = self.rng
        level = 'GR' if program in GRAD_POOLS else 'UG'
        visa = visa if visa is not RANDOM else rng.choices(
            ['F-1', 'J-1', None],
            [0.55, 0.05, 0.40] if level == 'GR' else [0.18, 0.02, 0.80])[0]
        ability = ability if ability is not None else min(4.0, max(1.6, rng.gauss(3.25, 0.45)))
        taken, records = set(), []

        if level == 'UG':
            plan = PLANS[program]
            done = done if done is not None else rng.randint(0, 6)
            for i in range(done):
                for code in self.semester(plan[i], taken):
                    records.append(self._record(code, PAST_TERMS[done - 1 - i], level, ability))
            current = current or self.semester(plan[done], taken, current=True)
        else:
            pool = GRAD_POOLS[program]
            done = done if done is not None else rng.randint(0, 3)
            for i in range(done):
                for code in rng.sample([c for c in pool if c not in taken], 3):
                    taken.add(code)
                    records.append(self._record(code, PAST_TERMS[done - 1 - i], level, ability))
            current = current or rng.sample(
                [c for c in pool if c not in taken and self.offered_now(c)],
                rng.choice([2, 3, 3]))
            taken.update(current)

        if load == 'part_time':
            current = current[:2]
        elif load == 'single':
            current = current[:1]
        elif load == 'heavy' and level == 'UG':
            current = current + [self.resolve('GEN', taken, current=True)]

        enrolled = [{'code': c, 'term': CURRENT_TERM, 'credits': self.credits(c, level),
                     'status': 'Enrolled', 'grade': None} for c in current]

        sid = sid or next(self.ids)
        student = {
            'id': sid,
            'name': name or self.name(),
            'level': level,
            'program': program,
            'visa': visa,
            'assistantship': bool(assistantship if assistantship is not None
                                  else level == 'GR' and rng.random() < 0.3),
            'admit_term': PAST_TERMS[done - 1] if done else CURRENT_TERM,
            'enrollments': records + enrolled,
            'holds': [],
        }
        gpa = self.gpa(records)
        if holds is None:
            holds = []
            if rng.random() < 0.15:
                holds = rng.sample(sorted(HOLDS), rng.choice([1, 1, 2]))
            if gpa is not None and gpa < 2.0:
                holds.append(LOW_GPA_HOLD[0])
        details = dict(HOLDS, **{LOW_GPA_HOLD[0]: LOW_GPA_HOLD[1]})
        student['holds'] = [{'type': h, 'detail': details[h], 'placed_term': CURRENT_TERM}
                            for h in holds]
        return student

    def _record(self, code, term, level, ability):
        return {'code': code, 'term': term, 'credits': self.credits(code, level),
                'status': 'Completed', 'grade': self.grade(ability)}

    @staticmethod
    def gpa(records):
        points = dict(GRADES)
        graded = [(r['credits'], points[r['grade']]) for r in records if r['grade']]
        hours = sum(h for h, _ in graded)
        return round(sum(h * p for h, p in graded) / hours, 2) if hours else None


def featured(gen):
    """Four fixed students used in the demo journeys."""
    alex = gen.student(
        'CS_BS', sid='S00001', name='Alex Morgan', visa='F-1', done=4, ability=3.6,
        current=['CS 341', 'CS 357', 'CS 374', 'CS 411'], holds=[])
    for e in alex['enrollments']:
        if e['code'] == 'CS 411':
            e['credits'] = 3  # 14 hours total; dropping CS 411 leaves 11

    maya = gen.student('IS_BS', sid='S00002', name='Maya Patel', visa=None, done=7,
                       ability=3.7, holds=[])
    # Final semester: top up with real electives until the 123-hour total is met.
    total = sum(e['credits'] for e in maya['enrollments'] if e['grade'] != 'F')
    taken = {e['code'] for e in maya['enrollments']}
    while total < 123:
        code = gen.resolve('ELEC', taken, current=True)
        taken.add(code)
        credits = gen.credits(code, 'UG')
        maya['enrollments'].append({'code': code, 'term': CURRENT_TERM, 'credits': credits,
                                    'status': 'Enrolled', 'grade': None})
        total += credits
    for e in maya['enrollments']:
        if e['grade'] == 'F':
            e['grade'] = 'B'

    jordan = gen.student(
        'CS_BS', sid='S00003', name='Jordan Lee', visa=None, done=2, ability=3.1,
        holds=['Immunization requirement', 'Financial encumbrance'])
    sam = gen.student(
        'CS_MCS', sid='S00004', name='Sam Rivera', visa=None, done=1, ability=3.5,
        current=['CS 411', 'CS 412', 'CS 440'], holds=[], assistantship=False)
    for s in (alex, maya, jordan, sam):
        gen.names.add(s['name'])
    return [alex, maya, jordan, sam]


def generate(seed=SEED):
    gen = Generator(load_courses(), seed)
    students = featured(gen)
    for _ in range(4):
        next(gen.ids)  # S00001-S00004 are the featured students
    for program, count in COUNTS.items():
        for _ in range(count):
            load = gen.rng.choices(['normal', 'part_time', 'single', 'heavy'],
                                   [0.80, 0.07, 0.03, 0.10])[0]
            students.append(gen.student(program, load=load))
    for s in students:
        s['gpa'] = Generator.gpa([e for e in s['enrollments'] if e['status'] == 'Completed'])
    return students


if __name__ == '__main__':
    students = generate()
    by = collections.Counter((s['program'], s['visa'] or 'domestic') for s in students)
    print(f'{len(students)} synthetic students')
    for k, v in sorted(by.items(), key=str):
        print(f'  {k[0]:7} {k[1]:9} {v}')
    loads = [sum(e['credits'] for e in s['enrollments'] if e['status'] == 'Enrolled')
             for s in students]
    print('current credits: min', min(loads), 'max', max(loads),
          'below 12:', sum(x < 12 for x in loads))
    print('with holds:', sum(bool(s['holds']) for s in students))
    for s in students[:3]:
        cur = [(e['code'], e['credits']) for e in s['enrollments'] if e['status'] == 'Enrolled']
        print(s['id'], s['name'], s['program'], s['visa'], s['gpa'], cur, [h['type'] for h in s['holds']])
