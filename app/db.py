"""SQLite store for InterfaceDNA: synthetic university records, sessions and simulated actions.
Seeded from demo_data.json. Every record is fictional.

Rebuild the database:  python db.py
"""
from __future__ import annotations

import json
import os
import pathlib
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

BASE = pathlib.Path(__file__).parent
SEED = BASE / 'demo_data.json'
DB_PATH = pathlib.Path(
    os.getenv('INTERFACEDNA_DB', BASE / 'data' / 'interfacedna.db'))

SCHEMA = """
CREATE TABLE students (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    persona TEXT,
    major TEXT,
    catalog_year TEXT,
    completed_credits INTEGER NOT NULL,
    gpa REAL
);
CREATE TABLE courses (
    code TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    credits INTEGER NOT NULL
);
CREATE TABLE enrollments (
    student_id TEXT NOT NULL REFERENCES students(id),
    course_code TEXT NOT NULL REFERENCES courses(code),
    term TEXT NOT NULL,
    status TEXT NOT NULL,
    requirement TEXT,
    PRIMARY KEY (student_id, course_code, term)
);
CREATE TABLE holds (
    id INTEGER PRIMARY KEY,
    student_id TEXT NOT NULL REFERENCES students(id),
    hold_type TEXT NOT NULL,
    office TEXT NOT NULL,
    reason TEXT,
    status TEXT,
    can_request INTEGER NOT NULL DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE degree_audits (
    student_id TEXT PRIMARY KEY REFERENCES students(id),
    total_required INTEGER NOT NULL,
    completed INTEGER NOT NULL,
    in_progress INTEGER NOT NULL
);
CREATE TABLE degree_requirements (
    id INTEGER PRIMARY KEY,
    student_id TEXT NOT NULL REFERENCES students(id),
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    detail TEXT
);
CREATE TABLE policies (
    key TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    version TEXT NOT NULL,
    url_label TEXT,
    deadline TEXT,          -- ISO date, inclusive
    threshold INTEGER,
    notes TEXT              -- JSON list
);
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL REFERENCES students(id),
    intent TEXT NOT NULL,
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

# demo_data.json policy name -> database key
POLICY_KEYS = {
    'courseDrop': 'course_drop',
    'graduation': 'graduation',
    'registration': 'registration',
}


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


def seed(conn, data):
    term = data['meta']['term']
    for sid, st in data['students'].items():
        conn.execute(
            'INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)',
            (sid, st['name'], st['persona'], st['major'], st['catalogYear'],
             st['completedCredits'], st['gpa']),
        )
        for c in st.get('courses', []):
            conn.execute(
                'INSERT OR IGNORE INTO courses VALUES (?, ?, ?)',
                (c['code'], c['title'], c['credits']),
            )
            conn.execute(
                'INSERT INTO enrollments VALUES (?, ?, ?, ?, ?)',
                (sid, c['code'], term, c['status'], c['requirement']),
            )
        for h in st.get('holds', []):
            conn.execute(
                'INSERT INTO holds (student_id, hold_type, office, reason, status, can_request)'
                ' VALUES (?, ?, ?, ?, ?, ?)',
                (sid, h['type'], h['office'], h['reason'], h['status'],
                 int(h['canRequest'])),
            )
        grad = st.get('graduation')
        if grad:
            conn.execute(
                'INSERT INTO degree_audits VALUES (?, ?, ?, ?)',
                (sid, grad['totalRequired'], grad['completed'], grad['inProgress']),
            )
            for r in grad['requirements']:
                conn.execute(
                    'INSERT INTO degree_requirements (student_id, name, status, detail)'
                    ' VALUES (?, ?, ?, ?)',
                    (sid, r['name'], r['status'], r['detail']),
                )

    policies = data['policies']
    for name, key in POLICY_KEYS.items():
        p = policies[name]
        conn.execute(
            'INSERT INTO policies VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (key, p['title'], p['source'], p['version'], p.get('urlLabel'),
             p.get('deadline'), p.get('threshold'), json.dumps(p.get('notes', []))),
        )
    # The older calendar edition is stored but only consulted by the
    # policy_conflict demonstration fault.
    cal = policies['courseDropConflict']['sourceA']
    conn.execute(
        'INSERT INTO policies VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        ('course_drop_calendar', cal['title'], cal['source'], cal['version'],
         None, cal['date'], None, '[]'),
    )


def reset():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.unlink(missing_ok=True)
    with transaction() as conn:
        conn.executescript(SCHEMA)
        seed(conn, json.loads(SEED.read_text()))


def ensure():
    if not DB_PATH.exists():
        reset()


# ---- Synthetic university records -------------------------------------------

def get_student(student_id):
    with transaction() as conn:
        row = conn.execute(
            'SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
        return dict(row) if row else None


def get_enrollment(student_id, course_code):
    with transaction() as conn:
        row = conn.execute(
            'SELECT e.course_code AS code, c.title, c.credits, e.term, e.status, e.requirement'
            ' FROM enrollments e JOIN courses c ON c.code = e.course_code'
            " WHERE e.student_id = ? AND e.course_code = ? AND e.status = 'Enrolled'",
            (student_id, course_code),
        ).fetchone()
        return dict(row) if row else None


def current_credits(student_id):
    with transaction() as conn:
        return conn.execute(
            'SELECT COALESCE(SUM(c.credits), 0) FROM enrollments e'
            ' JOIN courses c ON c.code = e.course_code'
            " WHERE e.student_id = ? AND e.status = 'Enrolled'",
            (student_id,),
        ).fetchone()[0]


def get_active_holds(student_id):
    with transaction() as conn:
        rows = conn.execute(
            'SELECT hold_type AS type, office, reason, status, can_request'
            ' FROM holds WHERE student_id = ? AND active = 1 ORDER BY id',
            (student_id,),
        ).fetchall()
        return [dict(r, canRequest=bool(r['can_request'])) for r in rows]


def get_degree_audit(student_id):
    with transaction() as conn:
        audit = conn.execute(
            'SELECT * FROM degree_audits WHERE student_id = ?',
            (student_id,)).fetchone()
        if not audit:
            return None
        reqs = conn.execute(
            'SELECT name, status, detail FROM degree_requirements'
            ' WHERE student_id = ? ORDER BY id',
            (student_id,),
        ).fetchall()
        return dict(audit, requirements=[dict(r) for r in reqs])


def get_policy(key):
    with transaction() as conn:
        row = conn.execute(
            'SELECT * FROM policies WHERE key = ?', (key,)).fetchone()
        if not row:
            return None
        return dict(row, notes=json.loads(row['notes'] or '[]'))


# ---- Sessions and simulated actions -----------------------------------------

def _session_row(row):
    return dict(row, entities=json.loads(row['entities'])) if row else None


def create_session(session_id, student_id, intent, entities, state):
    stamp = now()
    with transaction() as conn:
        conn.execute(
            "INSERT INTO sessions VALUES (?, ?, ?, ?, ?, 'none', ?, ?)",
            (session_id, student_id, intent, json.dumps(entities), state,
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


def get_action(session_id):
    with transaction() as conn:
        row = conn.execute(
            'SELECT * FROM actions WHERE session_id = ?', (session_id,)).fetchone()
        return dict(row, details=json.loads(row['details'])) if row else None


if __name__ == '__main__':
    reset()
    with transaction() as conn:
        for table in ('students', 'courses', 'enrollments', 'holds',
                      'degree_requirements', 'policies'):
            count = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
            print(f'{table:20} {count}')
    print(f'Seeded {DB_PATH}')
