# InterfaceDNA — Local setup

Requirements: Python 3.10+ and your own Groq API key (free at https://console.groq.com/keys). SQLite ships with Python.

**What is real and what is not:** university rules, course data, class schedules, academic calendars and degree requirements are quoted from real UIUC documents in `University docs/`. Student records (names, transcripts, visa status, holds, registrations) are synthetic, and every action is simulated. Nothing connects to a university system. The interface is written as a working portal for presentations and does not say this on most screens; see *Presentation mode* in `docs/safety_privacy.md`.

```bash
cd app
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env     # Windows: copy .env.example .env
# Edit .env: set GROQ_API_KEY
python db.py             # build data/interfacedna.db
uvicorn server:app --reload
```

Visit http://127.0.0.1:8000, choose a student and a term, pick a service or describe a goal. `GET /health` shows whether a model key is configured and which date the rules use; it does NOT prove API access. The server returns an error rather than faking an LLM reply when no key or quota is available, and a "busy, try again in a minute" message when the free-tier rate limit is hit.

## How a request flows

1. **The model extracts only what was asked.** Groq returns an intent (`drop`, `graduation`, `hold`, `record`, `course_search`, `course_info`, `policy`, `unknown`) and the details the student typed: course code or course name, term, subject, credit hours, level, keyword or policy topic.
2. **The server validates those details** (`clean_entities()` and `precheck()` in `server.py`). Course codes, terms and keywords must appear in the student's own text. Relative terms such as "next spring" or "last semester" are resolved from today's date, and a term named in the question overrides the term picker. A course name such as "my database class" is matched only against the student's own courses (or, for course details, the catalog). The server stops early, with an explanation, on:
   - a drop that names more than one course;
   - a term with no calendar;
   - a hypothetical "what if I fail…" graduation question.
3. **The rules decide** (`rules.py`). They read the student's synthetic record and the quoted policy facts, and report each check with its source. A check the sources can't settle is marked *Not verified* and carries a **Where to check** direction (for example, the course's Course Explorer page, the Registrar refund schedules, ISSS or Student Self-Service).
4. **Every page also lists what matters for the student.** Holds, the selected term's upcoming deadlines, the F-1/J-1 minimum, missing registration, the graduation application and recorded requests.
5. **Confirmation is checked again.** `/api/confirm` reruns every rule before recording a simulated action. Confirmed requests appear under *My requests*, where each can be cancelled (after a confirmation step); a cancelled request stays listed as *Cancelled*, its course counts again, and the request can be made again. A repeat of an active request is blocked.

## Data

| File | Contents | Real or synthetic |
|---|---|---|
| `sources/courses.json` | 378 courses: CS and IS catalog listings plus supporting and TE courses from the 2026-2027 catalog tables, with source page | Real, extracted |
| `sources/offerings.json` | Courses offered in Fall 2026 and Spring 2027 for CS, IS, CSE and TE, with titles (Course Explorer) | Real, extracted |
| `sources/policies.json` | 48 facts from 9 sources: ISSS full-time rules, tuition ranges and refunds, withdrawal, Graduate College registration rules and holds, the 2025-2026 and 2026-2027 Senate calendars, and the Registrar's Fall 2026, Spring 2027 and Winter 2027 calendars (drop and refund deadlines by part of term and level, cancellation, graduation applications, registration dates); each with a verbatim quote and page | Real, quoted |
| `sources/programs.json` | Requirements for Computer Science BS, Information Sciences BS, CS MCS and Information Management MS (checked) and Innovation, Leadership & Engineering Entrepreneurship (ILEE) BS (listed) | Real, quoted |
| `generate_students.py` | 254 students (4 featured + 250 generated), seeded so every build is identical. Fall 2026 CS/IS enrollments use only courses offered in Fall 2026; 203 students also have Spring 2027 registrations from the Spring 2027 schedules (none for students with holds or in their final semester) | Synthetic |

Terms in the term picker: Fall 2025 and Spring 2026 (past; 2025-2026 Senate calendar), Fall 2026 (current), Winter 2027 (undergraduates only), Spring 2027 (Registrar calendar) and Summer 2027 (session dates only).

Featured students:
- **S00001 Alex Morgan:** CS BS, F-1, 14 hours. A Fall drop of CS 411 is blocked by the ISSS rule; a Spring 2027 drop of CS 441 can be confirmed.
- **S00002 Maya Patel:** IS BS, final semester. Shows the graduation check and the missed December application.
- **S00003 Jordan Lee:** CS BS with two holds, so no Spring registration.
- **S00004 Sam Rivera:** CS MCS, 12 hours. A Fall drop that can be confirmed before the graduate deadlines.

`db.py` loads all of this into SQLite. Rerun `python db.py` after changing any source or the generator; this also clears stored sessions and requests. Inspect with `sqlite3 data/interfacedna.db`.

## Updating the university sources

The PDFs in `University docs/` are the source of truth. After adding or replacing documents:

```bash
python tools/extract_courses.py   # regenerate sources/courses.json
python tools/extract_offerings.py # regenerate sources/offerings.json from the *Schedule*.pdf files
python tools/verify_sources.py    # check every quote appears on its cited page (currently 81/81)
python db.py
```

Add policy facts to `sources/policies.json` only with a verbatim quote, the source and the page, and run `verify_sources.py`; it also checks that every dated value appears in its quote.

Known gap: the class schedules list courses but not each section's part of term (POT). When the no-W deadlines differ by POT (for undergraduates between October 17 and November 13, 2026), the drop is reported as *depends on the course's part of term*, links to the course's Course Explorer page, and cannot be confirmed.

## Tests and evaluation

**Tests:** from the repository root, `python -m pytest tests -q` (51 tests). Tests use a temporary database and never call the real LLM.

**Model evaluation:** from `app/`, `python eval_intents.py` sends the 42 cases in `prompts/intent_eval.json` (typical, edge and adversarial, including filters such as term, credits and topic) to the live model and reports accuracy by category. The full 38-case run scored 37/38; the four record cases added later (R01–R04) passed live. This is prompt engineering plus evaluation, not fine-tuning. The script waits 12 seconds between calls to stay under the free-tier rate limit.

**Simulated date:** rules use the server's date unless `INTERFACEDNA_TODAY=YYYY-MM-DD` is set in `.env`. Disclose a simulated date whenever it is used in a demo.

**Deployment:** The existing Vercel prototype is a static CP2 demo, not this server. Deploy `/app` to a Python-capable hosting service, supply the API key only as a server-side environment variable, and restore a visible notice that records are fictional (see `docs/safety_privacy.md`).
