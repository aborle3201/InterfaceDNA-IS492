# InterfaceDNA — Checkpoint 3 Safety, Privacy and Guardrails

## Scope
This classroom demonstration operates entirely on fictional Demo University profiles/policies. The app does not authenticate real students, contact UIUC systems, modify university records, remove holds or grant graduation approval.

## Implemented safeguards
| Risk | Current mitigation | Evidence / verification |
|---|---|---|
| Fabricated university policy | Groq classifies intent; academic values and policies are retrieved from `demo_data.json` and calculated by deterministic code | Alex's credits and Jordan's hold details visible in UI; test_credit_math |
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
- **Deadline enforcement is not implemented.** Sample course-drop deadline (September 30, 2026) is in the past as of the CP3 snapshot; do not present an unrestricted drop action as if policy-compliant.
- **Prompt-injection defenses are partial.** The model only selects intents and cannot directly invoke university tools, but classification robustness against malicious instructions is not yet systematically benchmarked.
- Sessions and simulated receipts live only in process memory; there is no durable audit database.
- A simulated successful receipt is **not** proof of a real-world action.

## Required tests before submission
1. Confirm false -> HTTP 400; blocked state -> HTTP 409; repeated confirmation -> HTTP 409.
2. Show conflicting policy, missing audit, outage and return-to-normal on the integrated interface.
3. Test unexpected intent, very long input, no key/invalid key, and model rate limit response without leaking secrets.
4. Verify no `.env`, credentials or real student data appear in the repository or screenshots.
5. Decide whether to implement a deterministic deadline guard or set and label a historical synthetic scenario date.
