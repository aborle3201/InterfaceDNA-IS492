# InterfaceDNA CP3 — Local setup

Requirements: Python 3.10+ and your own Groq API key (free at https://console.groq.com/keys). SQLite ships with Python. Only fictional university data is used.

```bash
cd app
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env     # Windows: copy .env.example .env
# Edit .env: set GROQ_API_KEY, and optionally INTERFACEDNA_TODAY (see below)
python db.py             # build data/interfacedna.db from demo_data.json
uvicorn server:app --reload
```

Visit http://127.0.0.1:8000 and enter a goal. `GET /health` shows whether a model key is configured and which date the rules use; it does NOT prove API access. A live request is required for that. The server intentionally returns an error rather than faking an LLM reply when no key or quota is available.

**How a request flows:** Groq extracts only the intent (`drop`, `graduation`, `hold`, `unknown`) and the course code the student typed. The course code is discarded unless it appears in the student's own text. `rules.py` then reads every fact (enrollment, credits, deadlines, holds, degree audit, policy versions) from SQLite and decides whether the task is `review` or `blocked`. `/api/confirm` rechecks all rules before recording a simulated action.

**Database:** `db.py` defines the schema (students, courses, enrollments, holds, degree audits/requirements, policies, sessions, actions) and seeds it from `demo_data.json`. Edit the JSON and rerun `python db.py` to change the synthetic data; this also clears stored sessions and actions. Inspect it with `sqlite3 data/interfacedna.db`.

**Drop deadline:** the synthetic deadline is September 30, 2026, inclusive. Rules use the server's date unless `INTERFACEDNA_TODAY=YYYY-MM-DD` is set, so after that date Alex's drop is blocked. For a classroom demo of the eligible path, set e.g. `INTERFACEDNA_TODAY=2026-09-15` and say on screen that the date is simulated.

**Tests:** from the repository root, `python -m pytest tests -q`. Tests use a temporary database and never call the real LLM.

**Model evaluation:** from `app/`, `python eval_intents.py` sends the 28 cases in `prompts/intent_eval.json` (typical, edge and adversarial) to the live model and reports accuracy by category. This is prompt engineering plus evaluation, not fine-tuning.

**Deployment:** Existing Vercel prototype is a static CP2 demo, not this server. Deploy `/app` to a Python-capable hosting service, supply the API key only as a server-side environment variable, and update the demo URL.

**Integrated UI:** The original Checkpoint 2 visual styling is reused at `/`. Its new JavaScript lives in `app/assets/live.js` and makes real backend calls to `/api/start`, `/api/fault`, and `/api/confirm`. It is not the original scripted prototype.
