# InterfaceDNA — Checkpoint 3 Observability

## What the current code records
- Every HTTP request: route path, HTTP status, elapsed latency in milliseconds (FastAPI middleware).
- Successful LLM call: classified intent, model name, prompt/input tokens, completion/output tokens, inference latency.
- Failed model call: exception category; most recent corrected server variant logs exception tracebacks in the server console. **Review traces before sharing**, as remote errors can contain sensitive metadata.
- Browser displays model name and token counts for observed successful calls.

## How to reproduce and debug
1. In `app/`, run `python -m uvicorn server:app --reload`.
2. Visit `/health`: confirms whether a key is configured; **does not** confirm model availability.
3. Analyze a student question and verify `/api/start` returns HTTP 200 and logs model usage.
4. Inject a fault and inspect `/api/fault` (expected block state).
5. Attempt confirmation while blocked and verify no receipt appears; clearing fault should permit review again.
6. If `/api/start` gives 503, check the server traceback; validate `.env`, model ID, rate limits and Groq access without exposing the credential.

## Cost accounting (not yet automated)
The code currently logs token counts, **not dollar cost**. To estimate cost per request, use the Groq provider's current price schedule and compute:
`estimated_usd = input_tokens / 1_000_000 * input_price_per_million + output_tokens / 1_000_000 * output_price_per_million`.
Do not claim measured spending unless current prices and usage were reconciled.

## Current limitations and additions
No distributed traces, trace IDs, durable metrics, per-user budget, structured event log, or dashboard are present. Before public release, add privacy-preserving request IDs, counters for error classes, retention rules, alerting and cost monitoring.

---

## Checkpoint 3 — Verification and Interpretation of Logs

The integrated application was tested locally using pytest and FastAPI's TestClient, with 25 tests passing in the latest observed run on November 5, 2026.

The automated tests use mocked model interpretation where appropriate, allowing deterministic validation of backend behavior without relying on Groq API availability.

Live inference is evaluated separately through the model evaluation workflow and interactive application testing.

### Verification Levels

| Verification level | Evidence | Limitation |
|---|---|---|
| Backend regression | pytest and TestClient | Does not independently validate browser usability |
| Policy-source verification | Source quotations and deadline-value checks | Source documents may become outdated |
| Live model evaluation | Intent-classification evaluation cases | Model output may vary between runs |
| UI evidence | Checkpoint 3 screenshots | Earlier screenshots reflect the previous prototype |
| Operational logging | HTTP outcomes, latency, model usage, and errors | Not a production monitoring system |

### Operational Interpretation

A successful API response indicates that an application request completed according to the implemented code path. It does not establish that a university transaction occurred.

Likewise, a synthetic confirmation receipt indicates a completed local workflow, not a modification to a real student information system.

Observability remains focused on local debugging and classroom evaluation. Production deployment would require trace correlation, durable metrics, controlled log retention, and additional security review.
