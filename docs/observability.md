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
