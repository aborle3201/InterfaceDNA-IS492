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

## Failure and Recovery Tests

InterfaceDNA includes controlled failure scenarios to evaluate how the application responds when verified student information is missing, policy sources conflict, or supporting services become unavailable. These tests focus on safe state transitions, preventing unsupported AI-generated conclusions, and ensuring that blocked actions cannot generate simulated receipts.

All scenarios use synthetic student records; the university policies shown are real and quoted from UIUC sources, and every failure is simulated. Failures are introduced through the application's **Failure / edge case** selector after initializing a session.

---

### F-01 — Conflicting Course-Drop Policies

- **Persona:** Alex
- **Input:** `Can I drop CS 411?`
- **Failure mode:** `policy_conflict`
- **Expected:** The application blocks the request when the simulated fault reports two conflicting versions of the drop rules, and advises the student to consult the Registrar. No conflicting dates are invented.
- **Safeguard:** No confirmation action or receipt is permitted while the workflow is blocked.
- **Verification:** Covered by automated backend testing. The conflict scenario was also observed in earlier Checkpoint 3 testing.
  
---

### F-02 — Missing Graduation Audit (Maya)

- **Persona:** Maya
- **Input:** `What do I still need to graduate?`
- **Failure mode:** `missing_record`

**Test procedure:**
1. Select **J2 Graduation** with the failure setting `None`.
2. Analyze Maya's graduation question using live Groq inference.
3. Verify that the degree requirements are displayed with individual names, statuses, and supporting details.
4. Open **Test scenarios** and select **Record unavailable**.
5. Verify that the system enters a blocked state.
6. Confirm that the acknowledgment and confirmation controls are unavailable.
7. Verify that no simulated receipt is generated.

**Expected behavior:** The system displays `Your degree audit is unavailable right now, so graduation status can’t be determined. Please try again later.` and prevents the workflow from proceeding without verified degree-audit information.

**Automated verification:** `test_maya_missing_audit_recovery` confirms that `/api/fault` returns a blocked state and `/api/confirm` rejects the action with HTTP `409 Conflict`, without producing a receipt.

---

### F-03 — Synthetic Records-Service Outage (Jordan)

- **Persona:** Jordan
- **Input:** `Why can't I register?`
- **Failure mode:** `service_outage`

**Test procedure:**
1. Select **J3 Registration hold** with the failure setting `None`.
2. Analyze Jordan's registration question.
3. Verify that the two synthetic holds are displayed.
4. Open **Test scenarios** and select **Service outage**.
5. Verify that the application displays the service-unavailable warning.
6. Confirm that the workflow becomes blocked and confirmation is unavailable.
7. Verify that no simulated receipt is generated.

**Expected behavior:** The system displays `The student records service is unavailable. Please try again later; no action was taken.` and prevents any simulated advising-review request while the outage condition remains active.

**Automated verification:** `test_confirm_flow` (Jordan) verifies the blocked state and confirms that attempting to call `/api/confirm` returns HTTP `409 Conflict`, without a receipt.

---

### F-04 — Recovery After Clearing an Injected Failure

**Objective:** Verify that the application can restore a previously blocked workflow once the simulated failure is cleared.

**Test procedure:**
1. Start a valid Maya or Jordan workflow.
2. Introduce the corresponding failure through the dropdown.
3. Confirm the workflow enters the blocked state.
4. Change **Failure / edge case** back to `None` without resetting the session.
5. Verify that the original synthetic student information returns.
6. Confirm that explicit acknowledgment is still required before performing a simulated action.

**Expected recovery behavior:**

- **Maya:** The verified graduation requirements reappear with their individual names, statuses, and details.
- **Jordan:** Both registration holds reappear with the Spring 2027 registration dates.
- **Workflow state:** The backend transitions from `blocked` to `review`.
- **Human confirmation:** The application does not automatically execute an action when the failure is cleared.

**Automated verification:** `test_maya_missing_audit_recovery` and `test_confirm_flow` confirm that clearing the fault restores the `review` state, and both verify successful synthetic confirmation after recovery.

---

### F-05 — Backend Confirmation Protection

**Objective:** Ensure that blocked actions cannot bypass frontend restrictions through direct API calls.

**Test procedure:**
1. Create a valid session using `POST /api/start`.
2. Inject a missing-record or service-outage condition using `POST /api/fault`.
3. Confirm that the backend session state is `blocked`.
4. Attempt to confirm the blocked session through `POST /api/confirm` with `confirmation: true`.
5. Inspect the HTTP response and verify that no receipt was returned.

**Expected behavior:**
- HTTP status: `409 Conflict`
- Error: `Task is not confirmable in current state`
- No receipt generated
- No transition to a completed state

**Automated verification:** Both the Maya and Jordan recovery tests validate these confirmation safeguards. A blocked request cannot be completed until the failure condition is cleared and the backend returns to the review state.

---

### F-06 — Live Model Unavailability

- **Scenario:** Groq model inference fails or becomes unavailable.
- **Expected:** The backend returns HTTP `503 Service Unavailable`, displays an appropriate error message, and does not silently substitute a fabricated model response.
- **Verification status:** Covered by a mocked unit test (`test_model_failure_creates_no_session`). A live provider outage was not tested.

---

### Automated Test Results

Automated regression testing was conducted using pytest and FastAPI's TestClient to verify InterfaceDNA's backend workflows, policy evaluation, session transitions, confirmation safeguards, and error-recovery behavior.

The current implementation uses a SQLite database containing synthetic student records and course information derived from real UIUC sources. Tests exercise the deterministic application logic without requiring live Groq inference. Model responses are mocked where necessary to isolate backend behavior from external API availability.

**Command executed:**

```bash
python -m pytest tests -q
```

**Latest locally observed result (November 5, 2026):**

```text
25 passed, 1 warning in 1.24s
```

The warning concerns the deprecated Starlette TestClient import path and does not indicate a failed test.

The latest result was obtained after integrating the updated `live_demo` backend and test suite. Earlier screenshots showing 8 or 10 passing tests belong to the previous prototype implementation and are retained as historical development evidence.

| Test category | Verification coverage | Result |
|---|---|---|
| Course and policy data | Catalog data, policy references, and source-backed facts | Passed |
| Synthetic student generation | Deterministic generation and validity of student records | Passed |
| Course-drop validation | Credit consequences, enrollment eligibility, and full-time requirements | Passed |
| Deadline enforcement | Registrar deadlines and graduate petition restrictions | Passed |
| Graduation readiness | Undergraduate degree requirements and incomplete checks | Passed |
| Registration holds | Synthetic hold records and associated rule evaluation | Passed |
| Model-output validation | Course normalization and accepted intent/entity values | Passed |
| Confirmation safeguards | Explicit confirmation, blocked requests, and duplicate prevention | Passed |
| Missing-record recovery | Blocked graduation review, restoration, and confirmation | Passed |
| Service-outage recovery | Blocked workflow and restoration after clearing the fault | Passed |
| Policy source traceability | Citations and quoted source references | Passed |
| Model failure handling | Rejection of failed inference without creating a valid session | Passed |

**Verification scope:** These results establish that the tested backend behavior passed the locally executed regression suite. They do not independently establish browser usability, live provider reliability, or integration with university systems.

### Verification Summary

| Scenario | Expected outcome | Automated test status |
|---|---|---|
| Conflicting course-drop policies | Block unsafe request | Passed |
| Maya missing graduation audit | Block request and reject confirmation | Passed |
| Jordan records-service outage | Block request and reject confirmation | Passed |
| Maya recovery after selecting `None` | Restore verified graduation review | Passed |
| Jordan recovery after selecting `None` | Restore two registration-hold records | Passed |
| Confirmation during blocked state | HTTP 409; no receipt | Passed |
| Successful confirmation after recovery | Synthetic action permitted | Passed |
| Groq model-provider failure | HTTP 503; no fabricated response | Passed (mocked) |

### Safety Considerations and Limitations

* The error-recovery tests demonstrate that InterfaceDNA separates AI-based intent interpretation from deterministic validation of synthetic student records against quoted university rules. When critical information is missing or supporting services become unavailable, the backend blocks the workflow instead of allowing unsupported conclusions or actions.
* The system enforces a confirmation boundary at the backend, meaning blocked actions cannot generate simulated receipts even when confirmation is attempted directly through the API. Once the injected failure is removed, the application restores the verified review state without automatically executing an action.
* These tests use fictional student records and application-controlled fault injection. They validate the implementation's state transitions and safeguards but do not establish production resilience against actual university-system outages. No real university records are accessed or modified during testing.

### Correct fault-injection procedure
**Analyze first, inject the failure second.** The `/api/start` call creates the session. The fault selector then calls `/api/fault` using its `session_id`; without a session there is nothing to mutate. This is correct behavior for an **interactive fault-injection demonstration**, but does not establish the system can withstand real third-party outages in production.

---

## Automated Verification

The latest locally executed Checkpoint 3 regression suite reported **25 passing tests** on November 5, 2026, following integration of the redesigned backend.

The suite covers synthetic student records, real source-backed policy facts, course-drop rules, graduation checks, registration holds, confirmation safeguards, fault injection, recovery, and API behavior.

The system also includes a separate source-verification process implemented in `app/tools/verify_sources.py`. The documented source-verification run checked 49 policy and program quotations against their cited PDF pages and verified the consistency of extracted deadline values.

Automated application tests use mocked model responses where required. Live Groq inference and the 38-case intent evaluation are separate verification activities.

The earlier 8-test and 10-test screenshots remain available in `validation/checkpoint3/` as historical evidence of the previous prototype.

**Limitation:** Passing automated tests validates the scenarios included in the test suite; it does not establish that every UI workflow has been manually tested in the final redesigned portal.

---

## Proposed CP4 benchmark alignment
Compare the **same Alex/Maya/Jordan tasks** across (A) human-only policy portal, (B) general AI-only chatbot without verified records, (C) InterfaceDNA hybrid. Pre-register participant count and task order. Collect correct next-action rate, unsupported claims, completion time, clicks/steps, and explicit confirmation compliance. The actual participant count and benchmark results are not available yet.
