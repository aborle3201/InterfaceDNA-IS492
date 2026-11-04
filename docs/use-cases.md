# InterfaceDNA — Checkpoint 3 Use Cases and Live Test Scripts

**All student and policy data are fictional.** These scripts document actual code paths; the status of hands-on checks is specified separately.

## UC-01 — Alex: Can I drop CS 411?

## UC-01 — Alex: Can I drop CS 411?

- **Setup:** Journey J1, persona Alex, failure `None`.
- **Input:** `Can I drop CS 411?`
- **Live action:** Click **Analyze using live AI**. The frontend calls `/api/start`, Groq classifies the intent as `drop`, and the backend checks the synthetic course-drop policy and student records.
- **Synthetic policy deadline:** September 30, 2026.
- **Expected behavior before deadline:** The system calculates the consequences of dropping CS 411: 16 credits before, 12 after, and a 12-credit full-time threshold. The student can review and explicitly confirm a simulated request.
- **Expected behavior on deadline:** Requests dated September 30, 2026, remain eligible for review.
- **Expected behavior after deadline:** Requests are blocked. The interface displays the expired-deadline warning, provides the synthetic policy source, and prevents confirmation.
- **Confirmation safeguard:** The backend rechecks the deadline before recording any simulated action. An expired request cannot generate a receipt.
- **Observed (November 3, 2026):** Live Groq inference successfully classified Alex's request as `drop`. The backend blocked the action because the September 30 deadline had passed. The interface displayed the policy warning and no confirmation controls were available.
- **Automated verification:** All 8 tests passed, including checks for requests before, on, and after the deadline, and confirmation-time validation.
- **Limitation:** The deadline is fictional and is evaluated against the server's local calendar date. No real university enrollment system is accessed.

---

## UC-02 — Maya: What do I still need to graduate?
- **Setup:** Journey J2, persona Maya, failure `None`.
- **Input:** `What do I still need to graduate?`
- **Expected:** `graduation` intent; 112 completed credits, 12 in progress, 120 required; 0 potentially remaining **if in-progress classes pass**, plus requirement status and source.
- **Confirmation:** Save a **synthetic review plan**, not graduation approval.
- **Observed:** Live model classification, progress data, and a simulated receipt were shown in screenshots.
- **UI follow-up:** Requirement details currently appear as JSON-like text in some cards; improve rendering.

## UC-03 — Jordan: Why can't I register?
- **Setup:** Journey J3, persona Jordan, failure `None`.
- **Input:** `Why can't I register?`
- **Expected:** `hold` intent and two synthetic holds: Academic Advising (semester planning check-in) and Student Accounts (outstanding account review). Offices and next actions should be distinct.
- **Confirmation:** Submit simulated advising-review request; **do not** claim that either hold was cleared.
- **Observed:** Both cards displayed in user's integrated UI screenshot; synthetic receipt previously shown in older CP3 UI.

## Failure and recovery tests
| Case | Session prerequisite | Fault selection | Expected result | Evidence status |
|---|---|---|---|---|
| F-01 Conflicting policy | Analyze Alex first | `policy_conflict` / Conflicting drop policies | State `blocked`; conflicting source warning; no confirm action | **Observed** in screenshot |
| F-02 Missing graduation audit | Analyze Maya first | `missing_record` / Missing degree audit | State `blocked`; do not infer graduation readiness | Code path present; hands-on verification pending |
| F-03 Synthetic records outage | Analyze Jordan first | `service_outage` | State `blocked`; no simulated action performed | Code path present; hands-on verification pending |
| F-04 Recover to review | Any uncompleted blocked session | Return to `none` | Restore verified view; confirmation still requires acknowledgment | Code path present; hands-on verification pending |
| F-05 Model failure | Remove API key in *private local copy* or simulate denied credentials | Analyze | HTTP 503; transparent error, no invented output | Code path present; avoid exposing actual key |

### Correct fault-injection procedure
**Analyze first, inject the failure second.** The `/api/start` call creates the session. The fault selector then calls `/api/fault` using its `session_id`; without a session there is nothing to mutate. This is correct behavior for an **interactive fault-injection demonstration**, but does not establish the system can withstand real third-party outages in production.

## Proposed CP4 benchmark alignment
Compare the **same Alex/Maya/Jordan tasks** across (A) human-only policy portal, (B) general AI-only chatbot without verified records, (C) InterfaceDNA hybrid. Pre-register participant count and task order. Collect correct next-action rate, unsupported claims, completion time, clicks/steps, and explicit confirmation compliance. The actual participant count and benchmark results are not available yet.
