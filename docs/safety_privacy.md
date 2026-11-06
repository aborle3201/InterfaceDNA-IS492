# InterfaceDNA — Checkpoint 3 Safety, Privacy and Guardrails

## Scope
University rules, deadlines, course data, class schedules and degree requirements are quoted from real UIUC documents. Student records are synthetic. The app does not authenticate real students, contact UIUC systems, modify university records, remove holds or grant graduation approval.

**Presentation mode.** For the class presentation, the interface is written as a working student portal. It does not label students as synthetic or call itself a prototype, and receipts read "Request recorded". The confirmation banner on result pages does describe the action as *simulated*, and the holds banner says the portal cannot verify payments or remove holds. This is disclosed here, in `app/INSTALL.md` and to the instructor. The interface is branded InterfaceDNA, not as the university, and credits UIUC only as the policy source. Its footer keeps "Confirm important decisions with the office cited". **If the app is ever hosted where real students could reach it, restore a visible notice that records are fictional and requests are not submitted to the university.**

## Implemented safeguards
| Risk | Current mitigation | Evidence / verification |
|---|---|---|
| Fabricated or misquoted university policy | University facts come only from `sources/policies.json`, `sources/programs.json`, the catalog course data and the Course Explorer schedules. Each policy fact has a verbatim quote, source and page, and the UI shows the quote. The model never supplies facts | `tools/verify_sources.py`: 81/81 quotes found on their cited pages, and every deadline date found in its quote; `test_every_student_and_journey_is_cited`; `test_policy_answers_are_quotes` |
| Questions the sources do not answer | Marked *Not verified* with a **Where to check** direction (Course Explorer course page, Registrar refund schedules, ISSS, Student Self-Service, college office, academic advisor). Out-of-scope questions get a guide to official pages instead of a guess | `test_unverified_items_have_directions`; `test_unanswerable_question_points_somewhere` |
| Acting without a verified deadline | No-W and refund deadlines come from the Registrar's Fall 2026 and Spring 2027 calendars, by part of term and student level; if the outcome depends on a part of term the sources do not give, the action is blocked | `test_ug_no_w_deadlines_by_date`; `test_unverified_drop_cannot_be_confirmed`; `test_grad_drop_confirm`; `test_spring_registration_drop` |
| Visa-status harm | F-1/J-1 students dropping below the ISSS minimum (12 UG, 8 GR) in Fall or Spring are blocked and pointed to ISSS; the minimum is also shown under *Important for you* | `test_drop_f1_below_full_time_blocks`; `test_important_follows_selected_term` |
| Hours counted wrongly after an earlier drop | Courses with a recorded drop request no longer count toward hours; a repeat of the same request is blocked with its receipt | `test_edge_pending_drop_counts`; `test_requests_listed_and_duplicates_blocked` |
| Cancelling a request | Cancellation needs explicit confirmation, works only on the student's own active requests, and keeps the request listed as *Cancelled* | `test_cancel_request` |
| Over-promising graduation | Graduation results open with "Graduation is not guaranteed" and point to the advisor or Academic Office; hypothetical "what if I fail…" questions are stopped before any projection | `test_graduation_summary_does_not_guarantee_approval`; `test_hypothetical_course_failure_is_blocked` |
| Rules applied to the wrong students or term | Deadlines carry the levels and term they apply to; graduate-only rules (e.g. the petition cutoff) apply to graduate students only; Winter applies to undergraduates only; important items follow the selected term | `test_grad_petition_after_dec_10`; `test_terms_and_key_dates`; `test_important_follows_selected_term` |
| Model-invented course, term or filter | Course codes, terms and keywords are kept only if the student typed them; course names are resolved only against the student's own courses or the catalog, and the portal asks when several match; subjects, credits, levels and topics must be from fixed sets | `test_normalize_course`; `test_clean_entities`; `test_course_name_resolution`; `test_edge_numbers_as_text` |
| Ambiguous or out-of-range requests | A drop naming several courses asks for one at a time; a term with no calendar is reported as unavailable rather than answered for another term | `test_edge_one_course_at_a_time`; `test_edge_unknown_term_in_question`; `test_relative_terms_and_short_keywords` |
| Invalid model intent | Allowlist of eight intents; anything else is rejected with HTTP 503 and no session | Source inspection; `test_model_failure_creates_no_session` |
| Action without consent | Explicit checkbox and server confirmation flag; `review` state required; every rule rechecked at confirmation; one action per session | `test_confirm_flow` |
| Missing record / outage / conflict | Test scenarios block drops, graduation, holds, course search, course details and policy answers instead of inferring | `test_failures_block`; `test_edge_faults_on_new_question_types` |
| Model failure or rate limit | `/api/start` returns 503 with a clear message and creates no session | `test_model_failure_creates_no_session`; `test_edge_rate_limit_message` |
| Secrets exposure | Key in server-only `.env`; `.env.example` placeholder; `.env` and the database are git-ignored | Inspect repository ignore patterns before pushing |
| Large prompts | Pydantic `message` length 3–1,000 characters; the UI explains the limit | Source inspection; browser check |

## Important limitations / known risks
- **Sources can go out of date.** Policies were retrieved November 4–5, 2026, and the catalog is current as of June 2026. The app does not check for newer versions; re-extract and re-verify when documents change. The Registrar marks its calendar dates as tentative until close to each semester.
- **Coverage is partial.**
  - CS BS, IS BS, CS MCS and Information Management MS requirements are checked; the ILEE check is not supported, and the MCS breadth requirement is not checked.
  - Gen eds, focus areas, technical GPA, residency and catalog-year differences are not checked.
  - Prerequisites are shown but not checked against transcripts.
- **Course part of term is unknown.** Undergraduate drops between October 17 and November 13, 2026 cannot be confirmed; the page links to the course's Course Explorer page.
- **Synthetic grades use the standard 4-point scale.** The catalog confirms only A = 4.00.
- **PII sanitization is not fully implemented.** The goal text is sent to the Groq API; students must not enter real identifiers or personal records. Production deployment requires input redaction, authentication, consent and a retention policy.
- **Rate limiting and abuse protection are not implemented** on the server; only the provider's free-tier limit applies.
- **Prompt-injection defenses are partial.** The model only extracts an intent and entities and cannot invoke university tools. One adversarial evaluation case (A06) can still steer the extracted course; the rules then block it because the course is not an enrollment.
- **Local data store.** Sessions and receipts are stored in a local SQLite file (`app/data/interfacedna.db`) with no access control or retention policy; rebuilding the database clears them.
- **Receipts are not real.** The portal shows "Request recorded" with a receipt number, but nothing is sent to the university.
- **No UIUC branding.** The interface cites UIUC sources but must not use UIUC logos or present itself as an official university service.

---

## Checkpoint 3 — Verification Boundaries and Responsible Demonstration

### Separation of responsibilities
InterfaceDNA separates AI interpretation, institutional rule evaluation and user authorization:
- **The language model** interprets the request and extracts entities. It does not determine policy outcomes or execute actions.
- **Deterministic backend rules** evaluate the student's record and the policy information. They communicate findings, citations, uncertainty and where to check.
- **The student** must explicitly acknowledge an eligible simulated action, and the server revalidates it before recording a receipt.

### Synthetic records and simulated actions
The implementation combines real, quoted UIUC policy information with fictional student records. The following are simulated:

- Student profiles, transcripts, enrollments and Spring 2027 registrations.
- Registration holds and individual student circumstances.
- Action confirmation, receipts, cancellations and the *My requests* list.
- Policy conflicts, missing-record conditions and service outages introduced through test scenarios.

A receipt indicates only that the application recorded a local action. It is not evidence of a submitted course drop, cleared registration hold, approved graduation or completed university transaction.

### Presentation and deployment boundary
The classroom demonstration uses a student-portal interface to evaluate usability and workflow realism. Evaluators must be told that it is a prototype and not an official university service. If the application becomes publicly accessible, it should visibly identify its records and transactions as simulated. Real student information should not be entered.

### Interpretation of automated tests
The regression suite passes 51 tests (November 6, 2026). These cover the implemented behaviours:
- rule evaluation and blocked confirmation;
- duplicate prevention and pending drops;
- important items and directions;
- input handling and simulated recovery.

The tests do not establish:
- reliability during real university-system outages;
- protection of real institutional records;
- production authentication or authorization;
- security against every prompt-injection attempt;
- compliance with all accessibility requirements;
- safe execution of actual university transactions.

### Recovery and confirmation safeguards
A blocked session cannot be completed through the confirmation endpoint. Clearing a simulated failure restores review only when the rules permit it; recovery does not authorize or execute anything. The backend revalidates the rules at confirmation time, reducing the risk of acting on an earlier eligibility decision after conditions changed.

### Remaining work
Before any real-world integration, the project would require:
- authentication and authorization;
- input sanitization and secure data handling;
- operational monitoring and access-controlled persistence;
- a formal review of institutional policies and integration permissions.

---

## Required checks before submission
1. Confirm false → HTTP 400; blocked state → HTTP 409; repeated confirmation → HTTP 409; repeated request → blocked with its receipt.
2. Show conflicting policy, record unavailable, service outage and return-to-normal in the browser.
3. Test an unexpected intent, very long input, no key or an invalid key, and a rate limit without leaking secrets.
4. Verify no `.env`, credentials or real student data appear in the repository or screenshots.
5. Run `tools/verify_sources.py` after any change to the policy or program files.
