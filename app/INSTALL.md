# InterfaceDNA CP3 — Local setup

Requirements: Python 3.10+ and your own Groq API key. Only fictional university data is used.

```bash
cd app
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env     # Windows: copy .env.example .env
# Edit .env, set GROQ_API_KEY to a valid key, and choose an available GROQ_MODEL
uvicorn server:app --reload
```

Visit http://127.0.0.1:8000 and enter a goal. `GET /health` shows whether a model key is configured; it does NOT prove API access. A live request is required for that. The server intentionally returns an error rather than faking an LLM reply when no key or quota is available.

Run tests from repository root: `python -m pytest tests -q` (install dependencies above first). No test calls the real LLM; use the UI to validate inference with your own key.

**Deployment:** Existing Vercel prototype is a static CP2 demo, not this server. Deploy `/app` to a Python-capable hosting service, supply the API key only as a server-side environment variable, and update the demo URL. Sessions are stored in memory for the classroom demonstration only; restart clears them.

**Integrated UI:** The original Checkpoint 2 visual styling is reused at `/`. Its new JavaScript lives in `app/assets/live.js` and makes real backend calls to `/api/start`, `/api/fault`, and `/api/confirm`. It is not the original scripted prototype.
