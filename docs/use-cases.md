# InterfaceDNA — Checkpoint 3 Use Cases and Test Scripts

**University rules are real; students are synthetic.** Policies, deadlines, course data, class schedules and degree requirements are quoted from UIUC documents in `University docs/` (retrieved November 4–5, 2026), each shown with its source and page. Student records and all actions are synthetic. Expected results below are taken from the current code, evaluated on November 5–6, 2026 with the term picker on **Fall 2026** unless stated.

**How to run a scenario:** open http://127.0.0.1:8000, choose the student in the directory, set the term, then pick a service tile (or *Something else*) and enter the input. Press **Build my page**. Every result page starts with **Important for you**: the student's holds, the selected term's upcoming deadlines, the F-1/J-1 minimum, registration status, the graduation application and recorded requests. Items the sources can't verify show **Where to check**.

---

## Core journeys

### UC-01 — Alex Morgan (S00001): Can I drop CS 411?
- **Setup:** S00001, a synthetic F-1 CS BS student with 14 hours in Fall 2026 (CS 341, CS 357, CS 374, CS 411). Tile: *Drop a course*.
- **Expected:** 14 → 11 hours; CS 411 *Database Systems*. Status `blocked`.
  - **Blocks action — Contact ISSS before dropping below full time:** 11 is below the 12-hour F-1 undergraduate minimum (ISSS, p. 2). Where to check: ISSS.
  - **Not verified — Drop deadline depends on the course's part of term:** the no-W deadline was October 16 for POT 1 and is November 13 for POT B. Where to check: *CS 411 section details on Course Explorer* (link).
  - **Note — Tuition range changes from Range I to Range II, but no refund applies:** refund deadlines (Sept 4, Oct 23) have passed. Where to check: Registrar refund schedules.
- **Confirmation:** not available.

### UC-01b — Sam Rivera (S00004): I want to drop CS 440
- **Setup:** S00004, a domestic CS MCS student with CS 411, CS 412 and CS 440 (12 hours).
- **Expected:** 12 → 8 hours; **Verified — Within the deadline to drop without a W** (graduate deadlines: Nov 13 for POT 1, Dec 4 for POT B); no refund. Status `review`.
- **Confirmation:** tick the acknowledgment and confirm, which records a receipt. The request then appears under *My requests* on the dashboard, and CS 440 shows **Drop requested** in the schedule. After December 10, 2026 the same request is blocked: graduate add/drop needs a Graduate College petition.

### UC-01c — Alex Morgan, term Spring 2027: Can I drop CS 441?
- **Setup:** term picker on **Spring 2027**, or ask "Can I drop CS 441 in spring 2027?" with the picker on Fall (a term in the question overrides the picker).
- **Expected:** "Dropping CS 441 would take your Spring 2027 registration from 16 to 13 hours." Stays at the F-1 minimum; within every Spring deadline because the term has not started; tuition range stays Range I. Status `review`. *Important for you* shows Spring items only: open registration Nov 19, cancellation Jan 18, refund deadlines, and the F-1 check against 16 registered hours.

### UC-02 — Maya Patel (S00002): What do I still need to graduate?
- **Setup:** S00002, IS BS, final semester. Tile: *Graduation check*.
- **Expected:** 113 hours completed since Spring 2023, 17 in progress, 0 remaining after current courses (of the 123 required, catalog p. 471). Every IS core course, the 51 School hours and both 2.50 GPA minimums are checked. The summary opens with **"Graduation is not guaranteed."**, gives the credit projection (130 hours if current courses are passed), and says to confirm with the academic advisor or Academic Office. Unchecked items (gen eds, programming proficiency, approved non-IS courses, catalog year) are *Not verified* with *Where to check: Your academic advisor*. **Important for you:** *Apply to graduate in December*: the deadline was September 4, 2026; contact your Academic Office.
- **Confirmation:** save a graduation review plan (not graduation approval).

### UC-03 — Jordan Lee (S00003): Why can't I register?
- **Setup:** S00003, CS BS with two synthetic holds and no Spring 2027 registration.
- **Expected:** *Immunization requirement* and *Financial encumbrance* holds; Spring 2027 registration dates (priority began Nov 2, open Nov 19); what holds can block (Graduate College Handbook, labelled for undergraduates). *Which office clears each hold* is *Not verified* with *Where to check: Registration section of Student Self-Service*. The status banner says the holds are still active and that the portal cannot verify a payment or remove a hold.
- **Confirmation:** save a reminder; no hold is cleared.

## Question types beyond the core journeys

| ID | Student / term | Input | Expected |
|---|---|---|---|
| UC-03b | Alex | "What courses do I have?" | *Your courses · Fall 2026*: CS 341, CS 357, CS 374, CS 411 (14 hours), 63 hours completed, GPA 3.38. "what did I take last semester" shows Spring 2026 with grades; "what am I registered for next semester" shows Spring 2027 |
| UC-04 | Any, Spring 2027 | "Show me 3 credit courses I can take in spring 2027" | *Courses for Spring 2027*: about 140 courses from the CS, IS, CSE and TE schedules that list 3 credit hours, with prerequisites and *Available* or the student's record. Sources: the Course Explorer schedules |
| UC-05 | Alex | "any AI courses next spring" | *next spring* → Spring 2027; *AI* matches CS 440 *Artificial Intelligence* and TE 468 *Transforming Marketing with AI* |
| UC-06 | Alex | "What are the prerequisites for CS 425?" | Course details: prerequisites (catalog), offered Fall 2026 and Spring 2027, not taken, eligible CS BS technical elective on the team-project list |
| UC-07 | Alex | "can I quit my database class?" | Course name resolved from Alex's own schedule to CS 411; same result as UC-01 |
| UC-08 | Any | "How many credits do international students need?" | Policy answer quoting the ISSS full-time rule, the ISSS exceptions and the tuition ranges |
| UC-09 | Jordan | "Where can I get a parking permit?" | *Here's where to look*: Jordan's important items plus a guide to ISSS, refunds, both Registrar calendars, Course Explorer, the catalog, Self-Service and the academic advisor |
| UC-10 | Alex | "what if I fail CS 374, can I still graduate?" | Stopped before the rules: "This is a hypothetical graduation scenario…", with advice to discuss it with the academic advisor; no projection or request |

## Edge cases

| ID | Input / action | Expected |
|---|---|---|
| UC-02b | S00235 Aarav Marsh (Information Management MS): "What do I still need to graduate?" | Graduate check: 40-hour total, IS 504, IS 507, IS 515 or IS 455, 28 IS hours, 12 500-level hours, at most 4 research/independent-study hours, 2.75 program GPA; programming competency points to the graduate program office |
| E-01 | "drop CS 411 and CS 425" | "Please ask about one course at a time." |
| E-02 | "show me IS courses for fall 2030" | "Information for Fall 2030 isn't available", plus the available terms |
| E-03 | "courses next fall" | "Information for next fall isn't available" (Fall 2027 has no calendar) |
| E-04 | Alex on Fall: "Can I drop CS 441?" | "Your Fall 2026 schedule does not include CS 441… CS 441 is on your Spring 2027 registration; choose Spring 2027 in the term picker or name the term in your question." |
| E-05 | Sam: confirm the CS 440 drop, then ask to drop CS 412 | Counts from 8 hours, not 12 (8 → 4), with *Includes your pending drop request* |
| E-06 | Sam: ask to drop CS 440 again | "You already requested to drop CS 440 for Fall 2026 (receipt …)" |
| E-06b | Sam: under *My requests*, choose **Cancel** on the CS 440 request, then **Yes, cancel it** | The request shows *Cancelled*; CS 440 returns to *Enrolled*; asking to drop CS 440 again is allowed. Cancel is also offered on the receipt page |
| E-07 | Empty or over-1,000-character question | "Please describe your goal in 3 to 1,000 characters." |
| E-08 | Free-tier rate limit hit | "The assistant is busy right now. Please wait a minute and try again." |
| E-09 | S00085 (only CS 128): "Can I drop CS 128?" | *Dropping your only course is a withdrawal*, with the October 16 deadline |
| E-10 | Any student, term Fall 2025: drop a course taken then | "Fall 2025 has ended" |

---

## Failure and recovery tests

Failures are introduced through the **Test scenarios** panel (collapsed at the bottom of a result page) after a page has been built. Every failure is simulated.

### F-01 — Conflicting policy versions
- **Persona:** Alex. **Input:** `Can I drop CS 411?` **Scenario:** *Conflicting policy versions*.
- **Expected:** blocked: "Two different versions of the drop rules were returned, so I'm not sure which applies. Ask the Office of the Registrar before proceeding." No conflicting dates are invented. The same scenario on a policy question blocks the policy answer.
- **Verification:** `test_failures_block`, `test_edge_faults_on_new_question_types`.

### F-02 — Record unavailable (Maya)
**Test procedure:**
1. As Maya, build the graduation page (*Test scenarios* set to *None*).
2. Verify the requirement cards show names, statuses and details.
3. Choose **Record unavailable**.
4. Verify the page is blocked, confirmation controls are gone and no receipt is created.

**Expected:** "Your degree audit is unavailable right now, so graduation status can't be determined. Please try again later." The same scenario also blocks course search and course details, because they use the student's record.

**Verification:** `test_maya_missing_audit_recovery` (blocked state, HTTP 409 on confirm, no receipt).

### F-03 — Records-service outage (Jordan)
**Test procedure:**
1. As Jordan, build the holds page.
2. Choose **Service outage**.
3. Verify the outage message appears, confirmation is unavailable and no receipt is created.

**Expected:** "The student records service is unavailable. Please try again later; no action was taken."

**Verification:** `test_confirm_flow` (blocked, HTTP 409, no receipt).

### F-04 — Recovery after clearing a failure
**Test procedure:**
1. After F-02 or F-03, set the scenario back to **None** without rebuilding the page.
2. Verify the original page returns.
3. Verify the acknowledgment is required again before confirming.

**Expected:** the backend moves from `blocked` to `review`; nothing is executed automatically.

**Verification:** `test_maya_missing_audit_recovery`, `test_confirm_flow`.

### F-05 — Backend confirmation protection
**Test procedure:** create a session with `POST /api/start`, inject a failure with `POST /api/fault`, then call `POST /api/confirm` with `confirmation: true`.

**Expected:** HTTP 409; no receipt; no completed state. `confirmation: false` gives HTTP 400, and a repeated confirmation gives HTTP 409.

**Verification:** `test_confirm_flow`, `test_unverified_drop_cannot_be_confirmed`.

### F-06 — Live model unavailable
- **Expected:** HTTP 503 with "Live model unavailable… No task was submitted." (or the *busy* message on a rate limit); no fabricated response and no session.
- **Verification:** `test_model_failure_creates_no_session`, `test_edge_rate_limit_message` (mocked). A live provider outage was not tested.

**Procedure note:** build the page first, then inject the failure. `/api/start` creates the session that `/api/fault` changes. This demonstrates the safeguards, not resilience against real outages.

---

## Automated verification

```bash
python -m pytest tests -q
```

**Result (November 6, 2026):** `51 passed, 1 warning`. The warning concerns the deprecated Starlette TestClient import path.

| Test category | Coverage |
|---|---|
| Real data | Catalog courses (including extraction fixes), policy facts, every student × every journey cited to a quoted source |
| Synthetic students | Deterministic generation; credits within catalog ranges; current enrollments on the Fall 2026 schedules |
| Drops | ISSS minimum, enrollment by term, withdrawal, no-W and refund deadlines on several dates, graduate petition, Spring registration drops, past terms, pending drops, duplicates |
| Record | Courses by term with grades, registrations, last/this/next semester |
| Graduation and holds | CS BS / IS BS checks, "not guaranteed" summary, hypothetical failure stop, holds and registration dates |
| New question types | Course search with synonyms, course details, policy answers as quotes |
| Input handling | Entity cleaning, typed and relative terms, course names, multi-course drops, unknown terms, numeric text |
| Important items | Per student and per selected term; directions on unverified items; out-of-scope guide |
| Safeguards | Request cancellation (confirmation, ownership, already-cancelled), explicit confirmation, blocked confirmation, recovery, test scenarios on every question type, model failure and rate limit |

Source verification (`app/tools/verify_sources.py`) separately checks all **81** policy and program quotations against their cited PDF pages and every deadline date against its quote. The live intent evaluation (37/38 on the 38-case run; the 4 later record cases passed) is separate from these tests.

**Screenshots:** `validation/checkpoint3/` holds the earlier 8- and 10-test runs from the previous prototype, plus Anisha's prompt-test screenshots from November 5. Some of those file names contain `validation:checkpoint3:` as part of the name.

**Limitation:** passing tests validates the scenarios in the suite; the browser checks covered the main flows but not every combination.

---

## Proposed CP4 benchmark alignment
Compare the **same Alex/Maya/Jordan/Sam tasks** across:

| Condition | Description |
|---|---|
| (A) Human only | The policy portal alone |
| (B) AI only | A general chatbot without verified records |
| (C) Hybrid | InterfaceDNA |

Pre-register the participant count and task order. Collect:
- correct next-action rate
- unsupported claims
- completion time
- clicks/steps
- explicit confirmation compliance

The participant count and benchmark results are not available yet.
