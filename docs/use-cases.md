# InterfaceDNA — Checkpoint 3 Use Cases and Live Test Scripts

**University rules are real; students are synthetic.** Policies, course data and degree requirements are quoted from UIUC documents in `University docs/` (retrieved November 4, 2026), each shown with its source and page. Student records and all actions are synthetic. These scripts document actual code paths; the status of hands-on checks is specified separately.

## UC-01 — Alex Morgan (S00001): Can I drop CS 411?

- **Setup:** Journey J1, student S00001, failure `None`. Alex is a synthetic F-1 Computer Science BS student enrolled in 14 hours for Fall 2026 (CS 341, CS 357, CS 374, CS 411).
- **Input:** `Can I drop CS 411?`
- **Live action:** Click **Analyze using live AI**. Groq extracts intent `drop` and course `CS 411`; the backend checks Alex's synthetic schedule against the real policy facts.
- **Expected:** 14 hours now, 11 after the drop; CS 411 shown with its catalog title, *Database Systems*.
  - **Blocks action — Contact ISSS before dropping below full time:** 11 is below the 12-hour minimum for F-1 undergraduates (ISSS, *Maintaining F-1/J-1 Status*, p. 2).
  - **Note — Other effects to review** (Graduate College Handbook, p. 12).
  - **Note — Tuition range changes from Range I to Range II, but no refund applies:** the refund deadlines (September 4 for POT 1, October 23 for POT B) have passed (Registrar, *Fall 2026 Academic Calendar*).
  - **Not verified — Drop deadline depends on the course's part of term:** the undergraduate no-W deadline was October 16 for POT 1 and is November 13 for POT B; the class schedule does not give CS 411's part of term.
- **Confirmation:** Not available.
- **Observed (November 5, 2026):** Live Groq inference extracted `drop` / `CS 411`; the API returned `blocked` with the ISSS and part-of-term checks. Browser check pending.

## UC-01b — Sam Rivera (S00004): I want to drop CS 440

- **Setup:** Journey J1, student S00004. Sam is a synthetic domestic CS MCS student enrolled in CS 411, CS 412 and CS 440 (12 hours).
- **Expected (November 5, 2026):** 12 → 8 hours; **Verified — Within the deadline to drop without a W** (graduate deadlines: November 13 for POT 1, December 4 for POT B); no refund because the refund deadlines have passed. Status `review`.
- **Confirmation:** Check the acknowledgment and confirm; a synthetic receipt is recorded. After December 10, 2026 the same request is blocked because graduate add/drop requires a Graduate College petition.
- **Observed (November 5, 2026):** Live Groq inference extracted `drop` / `CS 440`; review state; confirmation returned a synthetic receipt. Browser check pending.

## UC-02 — Maya Patel (S00002): What do I still need to graduate?

- **Setup:** Journey J2, student S00002. Maya is a synthetic Information Sciences BS student in her final semester.
- **Input:** `What do I still need to graduate?`
- **Expected:** `graduation` intent; 113 hours completed, 17 in progress, 123 required (catalog p. 471). **Needs attention — Apply to graduate in December:** the undergraduate deadline was September 4, 2026; after that date, contact your Academic Office. Every IS core course, the 51 School hours and both 2.50 GPA minimums are checked. Items the prototype cannot check (gen eds, programming proficiency, approved non-IS courses, catalog year) are listed as **Not verified** with a pointer to the academic advisor.
- **Confirmation:** Save a **synthetic review plan**, not graduation approval.
- **Observed (November 5, 2026):** Live classification and an on-track result through the API. Browser check pending.

## UC-03 — Jordan Lee (S00003): Why can't I register?

- **Setup:** Journey J3, student S00003. Jordan is a synthetic Computer Science BS student with two synthetic holds.
- **Input:** `Why can't I register?`
- **Expected:** `hold` intent; *Immunization requirement* and *Financial encumbrance* holds (categories from the Graduate College Handbook, p. 15); what holds can block, with the note that this description comes from the Graduate College Handbook; Spring 2027 instruction begins January 19, 2027 (2026-2027 Academic Calendar); priority registration began November 2 and open registration begins November 19, 2026 (Registrar, *Fall 2026 Academic Calendar*). Which office clears each hold is shown as **Not verified**, because the sources do not say.
- **Confirmation:** Save a **synthetic reminder**; do not claim that any hold was cleared.
- **Observed (November 5, 2026):** Live classification and both holds through the API. Browser check pending.

## Failure and recovery tests
| Case | Session prerequisite | Fault selection | Expected result | Evidence status |
|---|---|---|---|---|
| F-01 Conflicting policy versions | Analyze Alex first | `policy_conflict` | State `blocked`; message says the conflict is simulated; no university facts are invented | Unit test |
| F-02 Record unavailable | Analyze Maya first | `missing_record` | State `blocked`; do not infer graduation status | Unit test; browser check pending |
| F-03 Records service outage | Analyze Jordan first | `service_outage` | State `blocked`; no simulated action performed | Unit test; browser check pending |
| F-04 Recover to review | Any uncompleted blocked session | Return to `none` | Restore the verified view; confirmation still requires acknowledgment | Unit test (`test_confirm_flow`); browser check pending |
| F-05 Model failure | Remove API key in *private local copy* or simulate denied credentials | Analyze | HTTP 503; transparent error, no invented output | Unit test |

### Correct fault-injection procedure
**Analyze first, inject the failure second.** The `/api/start` call creates the session. The fault selector then calls `/api/fault` using its `session_id`; without a session there is nothing to mutate. This is correct behavior for an **interactive fault-injection demonstration**, but does not establish the system can withstand real third-party outages in production.

## Automated verification
`tests/test_api.py`: 20 tests passed (November 5, 2026). They include every one of the 254 synthetic students run through all three journeys, with each check's citation resolving to a quoted source, and no-W deadline outcomes on several dates. `app/tools/verify_sources.py`: all 49 policy and program quotes found verbatim on their cited pages, and every deadline date found in its quote.

## Proposed CP4 benchmark alignment
Compare the **same Alex/Maya/Jordan tasks** across (A) human-only policy portal, (B) general AI-only chatbot without verified records, (C) InterfaceDNA hybrid. Pre-register participant count and task order. Collect correct next-action rate, unsupported claims, completion time, clicks/steps, and explicit confirmation compliance. The actual participant count and benchmark results are not available yet.
