"""SQLite store for InterfaceDNA.

Real UIUC data: courses (sources/courses.json), policy facts with verbatim
quotes (sources/policies.json) and degree requirements (sources/programs.json).
Synthetic data: students, transcripts, enrollments and holds (generate_students.py).
Also stores sessions and simulated actions.

Rebuild the database:  python db.py
"""
from __future__ import annotations

import json
import os
import pathlib
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

import generate_students

BASE = pathlib.Path(__file__).parent
SOURCES = BASE / 'sources'
DB_PATH = pathlib.Path(
    os.getenv('INTERFACEDNA_DB', BASE / 'data' / 'interfacedna.db'))
CURRENT_TERM = generate_students.CURRENT_TERM

SCHEMA = """
CREATE TABLE courses (
    code TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    credits_text TEXT NOT NULL,
    credits_min INTEGER NOT NULL,
    credits_max INTEGER NOT NULL,
    prerequisite TEXT,
    source_document TEXT NOT NULL,
    source_page INTEGER
);
CREATE TABLE programs (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    level TEXT NOT NULL,
    data TEXT NOT NULL      -- JSON from sources/programs.json
);
CREATE TABLE policy_sources (
    key TEXT PRIMARY KEY,
    data TEXT NOT NULL      -- JSON: title, publisher, url, document, retrieved
);
CREATE TABLE policy_facts (
    key TEXT PRIMARY KEY,
    source TEXT NOT NULL REFERENCES policy_sources(key),
    page INTEGER,
    quote TEXT NOT NULL,
    vals TEXT               -- JSON
);
CREATE TABLE students (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    level TEXT NOT NULL CHECK (level IN ('UG', 'GR')),
    program TEXT NOT NULL REFERENCES programs(code),
    visa TEXT,
    assistantship INTEGER NOT NULL DEFAULT 0,
    admit_term TEXT NOT NULL,
    gpa REAL
);
CREATE TABLE enrollments (
    student_id TEXT NOT NULL REFERENCES students(id),
    course_code TEXT NOT NULL REFERENCES courses(code),
    term TEXT NOT NULL,
    credits INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Enrolled', 'Completed', 'Registered')),
    grade TEXT,
    PRIMARY KEY (student_id, course_code, term)
);
CREATE TABLE holds (
    id INTEGER PRIMARY KEY,
    student_id TEXT NOT NULL REFERENCES students(id),
    hold_type TEXT NOT NULL,
    detail TEXT,
    placed_term TEXT,
    active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL REFERENCES students(id),
    intent TEXT NOT NULL,
    term TEXT NOT NULL,
    entities TEXT NOT NULL, -- JSON object
    state TEXT NOT NULL CHECK (state IN ('review', 'blocked', 'completed')),
    fault TEXT NOT NULL DEFAULT 'none',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE actions (
    receipt TEXT PRIMARY KEY,
    session_id TEXT NOT NULL UNIQUE REFERENCES sessions(id),
    action_type TEXT NOT NULL,
    status TEXT NOT NULL,
    details TEXT NOT NULL,  -- JSON object
    created_at TEXT NOT NULL
);
"""


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


@contextmanager
def transaction():
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def load(name):
    return json.loads((SOURCES / name).read_text())


def seed(conn):
    for c in load('courses.json'):
        conn.execute(
            'INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (c['code'], c['title'], c['credits_text'], c['credits_min'],
             c['credits_max'], c['prerequisite'], c['source']['document'],
             c['source']['page']),
        )
    for code, p in load('programs.json')['programs'].items():
        conn.execute('INSERT INTO programs VALUES (?, ?, ?, ?)',
                     (code, p['name'], p['level'], json.dumps(p)))
    policies = load('policies.json')
    for key, s in policies['sources'].items():
        conn.execute('INSERT INTO policy_sources VALUES (?, ?)', (key, json.dumps(s)))
    for key, f in policies['facts'].items():
        conn.execute('INSERT INTO policy_facts VALUES (?, ?, ?, ?, ?)',
                     (key, f['source'], f['page'], f['quote'],
                      json.dumps(f.get('values'))))

    for s in generate_students.generate():
        conn.execute(
            'INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (s['id'], s['name'], s['level'], s['program'], s['visa'],
             int(s['assistantship']), s['admit_term'], s['gpa']),
        )
        for e in s['enrollments']:
            conn.execute(
                'INSERT INTO enrollments VALUES (?, ?, ?, ?, ?, ?)',
                (s['id'], e['code'], e['term'], e['credits'], e['status'], e['grade']),
            )
        for h in s['holds']:
            conn.execute(
                'INSERT INTO holds (student_id, hold_type, detail, placed_term)'
                ' VALUES (?, ?, ?, ?)',
                (s['id'], h['type'], h['detail'], h['placed_term']),
            )


def reset():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.unlink(missing_ok=True)
    with transaction() as conn:
        conn.executescript(SCHEMA)
        seed(conn)


def ensure():
    if not DB_PATH.exists():
        reset()


# ---- Real university data ---------------------------------------------------

def get_fact(key):
    """A policy fact with its quote and full source citation."""
    with transaction() as conn:
        row = conn.execute(
            'SELECT f.*, s.data AS source_data FROM policy_facts f'
            ' JOIN policy_sources s ON s.key = f.source WHERE f.key = ?',
            (key,)).fetchone()
        if not row:
            return None
        return {
            'key': row['key'],
            'quote': row['quote'],
            'page': row['page'],
            'values': json.loads(row['vals']) if row['vals'] else None,
            **json.loads(row['source_data']),
        }


def list_facts():
    with transaction() as conn:
        keys = [r['key'] for r in conn.execute('SELECT key FROM policy_facts ORDER BY key')]
    return [get_fact(k) for k in keys]


def get_dated(kind, level, term=None):
    """Dated entries of one kind (e.g. 'no_w', 'refund') that apply to a level
    (and term, if given), each with the key of the fact that quotes it."""
    with transaction() as conn:
        rows = conn.execute(
            "SELECT key, vals FROM policy_facts WHERE vals LIKE '[%'").fetchall()
    return [dict(v, key=row['key']) for row in rows for v in json.loads(row['vals'])
            if v.get('kind') == kind and level in v.get('levels', ())
            and (term is None or v.get('term') == term)]


def get_terms():
    """Terms that have a quoted calendar, oldest first, with that calendar's values."""
    with transaction() as conn:
        rows = conn.execute("SELECT key, vals FROM policy_facts WHERE vals LIKE '{%'").fetchall()
    terms = [dict(json.loads(r['vals']), key=r['key']) for r in rows]
    return sorted((t for t in terms if 'instruction_begins' in t),
                  key=lambda t: t['instruction_begins'])


def list_programs():
    with transaction() as conn:
        return [json.loads(r['data']) for r in conn.execute('SELECT data FROM programs ORDER BY level DESC, name')]


def subjects():
    with transaction() as conn:
        return {r[0].split()[0] for r in conn.execute('SELECT code FROM courses')} | set(
            subject for term in load('offerings.json').values() for subject in term)


def get_offerings(term):
    """Course Explorer listing for a term: {subject: {courses, titles, url, ...}}."""
    return load('offerings.json').get(term, {})


def get_program(code):
    with transaction() as conn:
        row = conn.execute('SELECT data FROM programs WHERE code = ?', (code,)).fetchone()
        return json.loads(row['data']) if row else None


def list_courses():
    with transaction() as conn:
        return [dict(r) for r in conn.execute('SELECT code, title FROM courses')]


def get_course(code):
    with transaction() as conn:
        row = conn.execute('SELECT * FROM courses WHERE code = ?', (code,)).fetchone()
        return dict(row) if row else None


# ---- Synthetic student records ----------------------------------------------

def get_student(student_id):
    with transaction() as conn:
        row = conn.execute(
            'SELECT s.*, p.name AS program_name FROM students s'
            ' JOIN programs p ON p.code = s.program WHERE s.id = ?',
            (student_id,)).fetchone()
        return dict(row, assistantship=bool(row['assistantship'])) if row else None


def list_students(term=CURRENT_TERM):
    with transaction() as conn:
        rows = conn.execute(
            'SELECT s.id, s.name, s.level, s.program, p.name AS program_name, s.visa, s.gpa,'
            ' (SELECT COUNT(*) FROM holds h WHERE h.student_id = s.id AND h.active = 1) AS holds,'
            ' (SELECT COALESCE(SUM(e.credits), 0) FROM enrollments e WHERE e.student_id = s.id'
            '  AND e.term = ?) AS term_credits'
            ' FROM students s JOIN programs p ON p.code = s.program ORDER BY s.id',
            (term,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_records(student_id):
    """Every enrollment row (completed and current) joined with course data."""
    with transaction() as conn:
        rows = conn.execute(
            'SELECT e.course_code AS code, c.title, e.term, e.credits, e.status, e.grade'
            ' FROM enrollments e JOIN courses c ON c.code = e.course_code'
            ' WHERE e.student_id = ? ORDER BY e.term, e.course_code',
            (student_id,)).fetchall()
        return [dict(r) for r in rows]


def get_current(student_id):
    return get_term_courses(student_id, CURRENT_TERM)


def get_term_courses(student_id, term):
    """A student's courses in one term: completed, enrolled or registered."""
    return [r for r in get_records(student_id) if r['term'] == term]


def get_enrollment(student_id, course_code):
    return next((r for r in get_current(student_id) if r['code'] == course_code), None)


def get_active_holds(student_id):
    with transaction() as conn:
        rows = conn.execute(
            'SELECT hold_type AS type, detail, placed_term FROM holds'
            ' WHERE student_id = ? AND active = 1 ORDER BY id',
            (student_id,)).fetchall()
        return [dict(r) for r in rows]


# ---- Sessions and simulated actions -----------------------------------------

def _session_row(row):
    return dict(row, entities=json.loads(row['entities'])) if row else None


def create_session(session_id, student_id, intent, term, entities, state):
    stamp = now()
    with transaction() as conn:
        conn.execute(
            "INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, 'none', ?, ?)",
            (session_id, student_id, intent, term, json.dumps(entities), state,
             stamp, stamp),
        )


def get_session(session_id):
    with transaction() as conn:
        return _session_row(conn.execute(
            'SELECT * FROM sessions WHERE id = ?', (session_id,)).fetchone())


def update_session(session_id, state, fault):
    """Change an uncompleted session. Returns False if it is completed or missing."""
    with transaction() as conn:
        cur = conn.execute(
            "UPDATE sessions SET state = ?, fault = ?, updated_at = ?"
            " WHERE id = ? AND state != 'completed'",
            (state, fault, now(), session_id),
        )
        return cur.rowcount == 1


def complete_session(session_id, receipt, action_type, details):
    """Atomically move a session from review to completed and record its action.
    Returns False if the session was not in review (e.g. already confirmed)."""
    stamp = now()
    with transaction() as conn:
        cur = conn.execute(
            "UPDATE sessions SET state = 'completed', updated_at = ?"
            " WHERE id = ? AND state = 'review'",
            (stamp, session_id),
        )
        if cur.rowcount != 1:
            return False
        conn.execute(
            "INSERT INTO actions VALUES (?, ?, ?, 'simulated_success', ?, ?)",
            (receipt, session_id, action_type, json.dumps(details), stamp),
        )
        return True


def list_requests(student_id, active=False):
    """A student's confirmed requests, newest first; `active` leaves out cancelled ones."""
    with transaction() as conn:
        rows = conn.execute(
            'SELECT a.receipt, a.action_type AS intent, a.status, a.details, a.created_at,'
            ' s.term, s.entities FROM actions a JOIN sessions s ON s.id = a.session_id'
            ' WHERE s.student_id = ? ORDER BY a.created_at DESC',
            (student_id,)).fetchall()
    out = [dict(r, details=json.loads(r['details']), entities=json.loads(r['entities']))
           for r in rows]
    return [r for r in out if r['status'] != 'cancelled'] if active else out


def cancel_request(student_id, receipt):
    """Cancel one of the student's active requests. Returns the request, or None
    if it doesn't exist, belongs to someone else or is already cancelled."""
    stamp = now()
    with transaction() as conn:
        row = conn.execute(
            'SELECT a.details FROM actions a JOIN sessions s ON s.id = a.session_id'
            " WHERE a.receipt = ? AND s.student_id = ? AND a.status != 'cancelled'",
            (receipt, student_id)).fetchone()
        if not row:
            return None
        details = dict(json.loads(row['details']), cancelled_at=stamp)
        conn.execute("UPDATE actions SET status = 'cancelled', details = ? WHERE receipt = ?",
                     (json.dumps(details), receipt))
    return next(r for r in list_requests(student_id) if r['receipt'] == receipt)


def find_request(student_id, intent, term, entities):
    """An already-confirmed request for the same task, if any."""
    return next((r for r in list_requests(student_id, active=True)
                 if r['intent'] == intent and r['term'] == term
                 and r['entities'].get('course_code') == entities.get('course_code')),
                None)


def get_action(session_id):
    with transaction() as conn:
        row = conn.execute(
            'SELECT * FROM actions WHERE session_id = ?', (session_id,)).fetchone()
        return dict(row, details=json.loads(row['details'])) if row else None


if __name__ == '__main__':
    reset()
    with transaction() as conn:
        for table in ('courses', 'programs', 'policy_facts', 'students',
                      'enrollments', 'holds'):
            count = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
            print(f'{table:14} {count}')
    print(f'Seeded {DB_PATH}')
