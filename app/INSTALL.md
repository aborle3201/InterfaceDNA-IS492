# InterfaceDNA CP3 — Local setup

Requirements: Python 3.10+ and your own Groq API key (free at https://console.groq.com/keys). SQLite ships with Python.

**What is real and what is not:** university rules, course data, class schedules and degree requirements are quoted from real UIUC documents in `University docs/`. Student records (names, transcripts, visa status, holds) are synthetic, and every action is simulated. Nothing connects to a university system. The interface itself is written as a working portal for presentations and does not say this on screen; see *Presentation mode* in `docs/safety_privacy.md`.

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

Visit http://127.0.0.1:8000, pick a student and enter a goal. `GET /health` shows whether a model key is configured and which date the rules use; it does NOT prove API access. The server intentionally returns an error rather than faking an LLM reply when no key or quota is available.

**How a request flows:** Groq extracts only the intent (`drop`, `graduation`, `hold`, `unknown`) and the course code the student typed; a course code is discarded unless it appears in the student's own text. `rules.py` reads the student's synthetic record and the real policy facts, and reports each check with its source. Anything the sources do not cover is shown as **Not verified** rather than guessed. `/api/confirm` reruns every rule before recording a simulated action.

## Data

| File | Contents | Real or synthetic |
|---|---|---|
| `sources/courses.json` | 362 courses: CS and IS listings plus supporting courses from the 2026-2027 catalog, with source page | Real, extracted |
| `sources/policies.json` | ISSS full-time rules, tuition ranges and refunds, withdrawal, Graduate College registration rules, holds, 2026-2027 calendar, and the Registrar's Fall 2026 deadlines (drop without a W and refund deadlines by part of term, graduation application, Spring 2027 registration); each with a verbatim quote and page | Real, quoted |
| Terms | Fall 2025 and Spring 2026 (2025-2026 Senate calendar), Fall 2026 and Spring 2027 (full Registrar calendars), Winter 2027 (Registrar winter calendar), Summer 2027 (2026-2027 Senate calendar). The term picker in the page header switches the schedule, key dates, directory hours and drop checks | Real, quoted |
| `sources/offerings.json` | Courses offered in Fall 2026 and Spring 2027 for CS, IS, CSE and TE (Course Explorer) | Real, extracted |
| `sources/programs.json` | Computer Science BS and Information Sciences BS requirements (2026-2027 catalog); CS MCS and Information Management MS names | Real, quoted |
| `generate_students.py` | 254 students (4 featured + 250 generated), seeded so every build is identical; current CS/IS enrollments use only courses offered in Fall 2026, and 203 students also have Spring 2027 registrations from the Spring 2027 schedules (none for students with holds or in their final semester) | Synthetic |

Featured students: **S00001 Alex Morgan** (CS BS, F-1, 14 hours — course drop blocked by ISSS rule), **S00002 Maya Patel** (IS BS, final semester — graduation), **S00003 Jordan Lee** (CS BS, two holds — registration), **S00004 Sam Rivera** (CS MCS, 12 hours — a drop that can be confirmed before the graduate deadlines).

`db.py` loads all of this into SQLite. Rerun `python db.py` after changing any source or the generator; this also clears stored sessions and actions. Inspect with `sqlite3 data/interfacedna.db`.

## Updating the university sources

The PDFs in `University docs/` are the source of truth. After adding or replacing documents:

```bash
python tools/extract_courses.py   # regenerate sources/courses.json
python tools/extract_offerings.py # regenerate sources/offerings.json from the *Schedule*.pdf files
python tools/verify_sources.py    # check every quote appears on its cited page
python db.py
```

Add policy facts to `sources/policies.json` only with a verbatim quote, the source and the page, and run `verify_sources.py`; it also checks that every dated value appears in its quote. Known gap: the class schedules list courses but not each section's part of term (POT). When the no-W deadlines differ by POT (for undergraduates between October 17 and November 13, 2026), the drop is reported as **depends on the course's part of term** and cannot be confirmed.

## Tests and evaluation

**Tests:** from the repository root, `python -m pytest tests -q`. Tests use a temporary database and never call the real LLM.

**Model evaluation:** from `app/`, `python eval_intents.py` sends the 28 cases in `prompts/intent_eval.json` (typical, edge and adversarial) to the live model and reports accuracy by category. This is prompt engineering plus evaluation, not fine-tuning.

**Simulated date:** rules use the server's date unless `INTERFACEDNA_TODAY=YYYY-MM-DD` is set in `.env`. Disclose a simulated date whenever it is used in a demo.

**Deployment:** Existing Vercel prototype is a static CP2 demo, not this server. Deploy `/app` to a Python-capable hosting service, supply the API key only as a server-side environment variable, and update the demo URL.
