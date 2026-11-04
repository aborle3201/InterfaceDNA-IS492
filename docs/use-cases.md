# InterfaceDNA — Checkpoint 3 Use Cases and Live Test Scripts

**All student and policy data are fictional.** These scripts document actual code paths; the status of hands-on checks is specified separately.

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
- **Automated verification:** All 11 tests in `tests/test_api.py` passed (November 4, 2026), including checks for requests before, on, and after the deadline, and confirmation-time validation.
- **Limitation:** The deadline is fictional and is evaluated against the server's local calendar date. No real university enrollment system is accessed.

---

## UC-02 — Maya: What do I still need to graduate?
- **Setup:** Journey J2, persona Maya, failure `None`.
- **Input:** `What do I still need to graduate?`
- **Expected:** `graduation` intent; 112 completed credits, 12 in progress, 120 required; 0 potentially remaining **if in-progress classes pass**, plus requirement status and source.
- **Confirmation:** Save a **synthetic review plan**, not graduation approval.
- **Observed:** Live model classification, progress data, and a simulated receipt were shown in screenshots.
- **UI:** Each requirement card shows its name, status and detail.

## UC-03 — Jordan: Why can't I register?
- **Setup:** Journey J3, persona Jordan, failure `None`.
- **Input:** `Why can't I register?`
- **Expected:** `hold` intent and two synthetic holds: Academic Advising (semester planning check-in) and Student Accounts (outstanding account review). Offices and next actions should be distinct.
- **Confirmation:** Submit simulated advising-review request; **do not** claim that either hold was cleared.
- **Observed:** Both cards displayed in user's integrated UI screenshot; synthetic receipt previously shown in older CP3 UI.


## Failure and Recovery Tests

InterfaceDNA includes controlled failure scenarios to evaluate how the application responds when verified student information is missing, policy sources conflict, or supporting services become unavailable. These tests focus on safe state transitions, preventing unsupported AI-generated conclusions, and ensuring that blocked actions cannot generate simulated receipts.

All scenarios use fictional university records and synthetic policies. Failures are introduced through the application's **Failure / edge case** selector after initializing a session.

---

### F-01 — Conflicting Course-Drop Policies

- **Persona:** Alex
- **Input:** `Can I drop CS 411?`
- **Failure mode:** `policy_conflict`
- **Expected:** The application blocks the request when synthetic course-drop policies conflict and advises the student to consult the registrar.
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
4. Select **Missing degree audit** from the failure dropdown.
5. Verify that the system enters a blocked state.
6. Confirm that the acknowledgment and confirmation controls are unavailable.
7. Verify that no simulated receipt is generated.

**Expected behavior:** The system displays `Synthetic degree audit unavailable. Do not infer graduation status.` and prevents the workflow from proceeding without verified degree-audit information.

**Automated verification:** The missing-audit test confirms that `/api/fault` returns a blocked state and `/api/confirm` rejects the action with HTTP `409 Conflict`, without producing a receipt.

---

### F-03 — Synthetic Records-Service Outage (Jordan)

- **Persona:** Jordan
- **Input:** `Why can't I register?`
- **Failure mode:** `service_outage`

**Test procedure:**
1. Select **J3 Registration hold** with the failure setting `None`.
2. Analyze Jordan's registration question.
3. Verify that the two synthetic holds are displayed with their responsible offices.
4. Select **Service outage** from the failure dropdown.
5. Verify that the application displays the service-unavailable warning.
6. Confirm that the workflow becomes blocked and confirmation is unavailable.
7. Verify that no simulated receipt is generated.

**Expected behavior:** The system displays `Synthetic records service unavailable. Retry later; no action executed.` and prevents any simulated advising-review request while the outage condition remains active.

**Automated verification:** The service-outage test verifies the blocked state and confirms that attempting to call `/api/confirm` returns HTTP `409 Conflict`, without a receipt.

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
- **Jordan:** Both registration holds reappear with their respective offices and next actions.
- **Workflow state:** The backend transitions from `blocked` to `review`.
- **Human confirmation:** The application does not automatically execute an action when the failure is cleared.

**Automated verification:** Both recovery tests confirm that clearing the fault restores the `review` state. The Maya test additionally verifies successful synthetic confirmation after recovery.

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
- **Verification status:** The fallback behavior is implemented in `app/server.py`. A separate live provider-failure test was not included in this verification cycle.

### Automated Test Results

Automated regression tests were executed using the FastAPI test client and pytest. Model classification was mocked for deterministic backend testing, while the application continued to use the actual session-management, validation, fault-injection, and confirmation logic.

**Command executed:**

```bash
python -m pytest tests -q
```

**Result:**

```text
10 passed
```

The completed suite includes the original eight tests and two additional tests specifically covering error recovery.

---

| Test category | Verification coverage | Result |
|---|---|---|
| Credit calculations | Correct course-drop credit consequences | Passed |
| Graduation and registration holds | Synthetic student record calculations | Passed |
| Failure handling | Conflicting policies, missing records, and service outage | Passed |
| Live model API path (mocked) | Session initialization, confirmation and recovery | Passed |
| Deadline validation | Before, on, and after synthetic deadline | Passed |
| Confirmation deadline revalidation | Reject confirmation after deadline expiration | Passed |
| Maya missing-audit recovery | Block, deny confirmation, restore, and confirm | Passed |
| Jordan service-outage recovery | Block, deny confirmation, restore, and confirm | Passed |

**Evidence:** `validation/checkpoint3/error_recovery_tests_passed.png`

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
| Groq model-provider failure | HTTP 503; no fabricated response | Not separately tested |

### Safety Considerations and Limitations

* The error-recovery tests demonstrate that InterfaceDNA separates AI-based intent interpretation from deterministic validation of synthetic university records. When critical information is missing or supporting services become unavailable, the backend blocks the workflow instead of allowing unsupported conclusions or actions.
* The system enforces a confirmation boundary at the backend, meaning blocked actions cannot generate simulated receipts even when confirmation is attempted directly through the API. Once the injected failure is removed, the application restores the verified review state without automatically executing an action.
* These tests use fictional student records and application-controlled fault injection. They validate the implementation's state transitions and safeguards but do not establish production resilience against actual university-system outages. No real university records are accessed or modified during testing.


## Proposed CP4 benchmark alignment
Compare the **same Alex/Maya/Jordan tasks** across (A) human-only policy portal, (B) general AI-only chatbot without verified records, (C) InterfaceDNA hybrid. Pre-register participant count and task order. Collect correct next-action rate, unsupported claims, completion time, clicks/steps, and explicit confirmation compliance. The actual participant count and benchmark results are not available yet.
