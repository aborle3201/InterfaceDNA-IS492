# InterfaceDNA — Checkpoint 3 Safety, Privacy and Guardrails

## Scope
This classroom demonstration operates entirely on fictional Demo University profiles/policies. The app does not authenticate real students, contact UIUC systems, modify university records, remove holds or grant graduation approval.

## Implemented safeguards
| Risk | Current mitigation | Evidence / verification |
|---|---|---|
| Fabricated university policy | Groq extracts only intent and the typed course code; academic values and policies are read from the synthetic SQLite database and calculated by deterministic code in `rules.py` | Alex's credits and Jordan's hold details visible in UI; test_credit_math |
| Model-invented course | A course code is kept only if the student typed it, and only an active enrollment can proceed | test_normalize_course; test_drop_uses_requested_course; live CS 500 request blocked |
| Expired drop deadline | Deadline (inclusive) checked when the task starts and again at confirmation | test_drop_deadline; test_confirm_rechecks_deadline; live request on November 4, 2026 blocked |
| Invalid model intent | Allowlist of `drop`, `graduation`, `hold`, `unknown`; unknown task blocks | Source inspection; automated classification-path test is mocked |
| Action without consent | Explicit checkbox and server confirmation flag; `review` state required | API rejects `confirmation: false`; repeated confirmation rejected in test |
| Conflicting evidence | `policy_conflict` blocks course-drop action | User-observed live failure screen |
| Missing academic audit | `missing_record` blocks graduation evaluation | Code and unit test; manual integrated UI check pending |
| Service unavailable | `service_outage` blocks action instead of inventing record | Code and unit test; manual integrated UI check pending |
| Model failure | `/api/start` emits 503 and no session/action | Source inspection; direct failure injection should be documented |
| Secrets exposure | Key in server-only `.env`; `.env.example` placeholder and `.gitignore` | Inspect repository ignore patterns before pushing |
| Large prompts | Pydantic `message` length maximum 1,000 characters | Source inspection; boundary test pending |

## Important limitations / known risks
- **PII sanitization is not fully implemented.** The user-entered goal text is sent to the Groq API; students must not enter real identifiers or personal records. Production deployment requires input redaction, authentication, consent and a retention policy.
- **Rate limiting and abuse protection are not implemented.** The 1,000-character limit does not prevent repeated requests.
- **The demo date may be simulated.** The synthetic course-drop deadline (September 30, 2026) has passed, so the eligible drop path is only reachable with `INTERFACEDNA_TODAY` set to an earlier date. Disclose this whenever it is used.
- **Prompt-injection defenses are partial.** The model only selects intents and cannot directly invoke university tools, but classification robustness against malicious instructions is not yet systematically benchmarked.
- Sessions and simulated receipts are stored in a local SQLite file (`app/data/interfacedna.db`); it has no access control or retention policy, and rebuilding the database clears it.
- A simulated successful receipt is **not** proof of a real-world action.

## Required tests before submission
1. Confirm false -> HTTP 400; blocked state -> HTTP 409; repeated confirmation -> HTTP 409.
2. Show conflicting policy, missing audit, outage and return-to-normal on the integrated interface.
3. Test unexpected intent, very long input, no key/invalid key, and model rate limit response without leaking secrets.
4. Verify no `.env`, credentials or real student data appear in the repository or screenshots.
5. Decide whether to implement a deterministic deadline guard or set and label a historical synthetic scenario date.
