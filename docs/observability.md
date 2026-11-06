# InterfaceDNA — Checkpoint 3 Observability

## What the current code records
- **At startup:** the database path and the date the rules are evaluated on (the server date, or `INTERFACEDNA_TODAY` if set).
- **Every HTTP request:** route path, HTTP status and elapsed latency in milliseconds (FastAPI middleware). Exceptions are logged with a traceback.
- **Every successful model call:** classified intent, validated entities (course code, term, filters), model name, prompt and completion tokens, and inference latency.
- **Every failed model call:** the exception with its traceback, labelled "Groq model call failed". The client sees a *busy* message for a rate limit (HTTP 429 from the provider) and an *unavailable* message otherwise. **Review traces before sharing**, as remote errors can contain sensitive metadata.
- **In the browser:** the result page shows the model name next to the AI interpretation, the extracted intent, term and course.
- **In the database:** sessions (intent, term, entities, state, active test scenario, timestamps) and confirmed actions (receipt, type, details, timestamp) persist in `app/data/interfacedna.db`, and the dashboard shows them under *My requests*.

## How to reproduce and debug
1. In `app/`, run `python -m uvicorn server:app --reload`, then check the startup log line for the database and rules date.
2. Visit `/health`. It confirms whether a key is configured and the rules date; it **does not** confirm model availability.
3. Build a page in the portal and verify `/api/start` returns HTTP 200 and logs an `inference intent=… entities=…` line.
4. Open **Test scenarios**, inject a failure and check `/api/fault` returns a blocked state.
5. Attempt confirmation while blocked and verify no receipt appears; clearing the scenario should permit review again.
6. If `/api/start` gives 503, check the server traceback. Validate `.env`, the model ID, rate limits and Groq access without exposing the credential. On the free tier, wait a minute after a rate limit.
7. Inspect stored state with `sqlite3 data/interfacedna.db "select * from sessions order by created_at desc limit 5;"`.

## Cost accounting (not yet automated)
The code logs token counts, **not dollar cost**. A model call with the current system prompt uses about 1,380 input tokens plus a variable number of output tokens (observed roughly 60 to 500, depending on how much the model reasons). To estimate cost per request, use the Groq provider's current price schedule:
`estimated_usd = input_tokens / 1_000_000 * input_price_per_million + output_tokens / 1_000_000 * output_price_per_million`.
Do not claim measured spending unless current prices and usage were reconciled.

## Current limitations and additions
There are no distributed traces, trace IDs, durable metrics, per-user budget, structured event log or dashboard. Before public release, add:
- privacy-preserving request IDs
- counters for error classes
- retention rules
- alerting
- cost monitoring

---

## Checkpoint 3 — Verification and Interpretation of Logs

The application is tested locally with pytest and FastAPI's TestClient: **51 tests pass** (November 6, 2026). The tests mock model interpretation, so backend behavior is validated without depending on Groq availability. Live inference is evaluated separately through `app/eval_intents.py` (37/38 on the 38-case run; 4 later record cases passed) and interactive testing.

### Verification levels

| Verification level | Evidence | Limitation |
|---|---|---|
| Backend regression | pytest and TestClient (51 tests) | Does not independently validate browser usability |
| Policy-source verification | `tools/verify_sources.py`: 81 quotations and every deadline date | Source documents may become outdated |
| Live model evaluation | 42 intent-classification cases | Model output may vary between runs |
| Browser checks | Headless-browser walkthroughs of the main flows, phone width and dark mode | Not every combination of student, term and question |
| UI evidence | `validation/checkpoint3/` screenshots | Some reflect the previous prototype |
| Operational logging | HTTP outcomes, latency, intent, entities, model usage and errors | Not a production monitoring system |

### Operational interpretation
A successful API response means an application request completed according to the implemented code path. It does not mean a university transaction occurred. Likewise, a receipt indicates a completed local workflow, not a change to a real student information system.

Observability is focused on local debugging and classroom evaluation. Production deployment would require trace correlation, durable metrics, controlled log retention and additional security review.
