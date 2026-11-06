# InterfaceDNA — Checkpoint 3 Safety, Privacy and Guardrails

## Scope
University rules, course data and degree requirements are quoted from real UIUC documents. Student records are synthetic. The app does not authenticate real students, contact UIUC systems, modify university records, remove holds or grant graduation approval.

**Presentation mode.** For the class presentation, the interface is written as a working student portal: it does not label students as synthetic, actions as simulated, or itself as a prototype. This is disclosed here, in `app/INSTALL.md` and to the instructor. The interface is branded InterfaceDNA, not as the university, credits UIUC only as the policy source, and keeps "confirm important decisions with the office cited" in the footer. **If the app is ever hosted where real students could reach it, restore a visible notice that records are fictional and requests are not submitted to the university.**

## Implemented safeguards
| Risk | Current mitigation | Evidence / verification |
|---|---|---|
| Fabricated or misquoted university policy | University facts come only from `sources/policies.json` and `sources/programs.json`; each has a verbatim quote, source and page, and the UI shows the quote. The model never supplies facts | `tools/verify_sources.py`: 49/49 quotes found on their cited pages and every deadline date found in its quote; `test_every_student_and_journey_is_cited` |
| Questions the sources do not answer | Reported as **Not verified** instead of guessed (drop deadline, which office clears a hold, gen eds and other unchecked degree items) | Unit tests; live API run |
| Acting without a verified deadline | No-W and refund deadlines come from the Registrar's Fall 2026 calendar by part of term and student level; if the outcome depends on a part of term the sources do not give, the action is blocked | `test_ug_no_w_deadlines_by_date`; `test_unverified_drop_cannot_be_confirmed`; `test_grad_drop_confirm` |
| Visa-status harm | F-1/J-1 students dropping below the ISSS minimum (12 UG, 8 GR) are blocked and told to contact ISSS first | `test_drop_f1_below_full_time_blocks`; live API run |
| Rules applied to the wrong students | Deadlines carry the student levels they apply to (ALL, UG or GRAD); graduate-only rules such as the December 10 petition cutoff apply to graduate students only; hold guidance from the Graduate College Handbook is labelled as such for undergraduates | `test_grad_petition_after_dec_10`; source inspection |
| Model-invented course | A course code is kept only if the student typed it, and only a current enrollment can proceed | test_normalize_course; test_drop_requires_enrolled_named_course |
| Invalid model intent | Allowlist of `drop`, `graduation`, `hold`, `unknown`; unknown task blocks | Source inspection; automated classification-path test is mocked |
| Action without consent | Explicit checkbox and server confirmation flag; `review` state required; every rule rechecked at confirmation | `test_confirm_flow` |
| Missing record / outage | `missing_record` and `service_outage` block instead of inferring | `test_failures_block` |
| Model failure | `/api/start` emits 503 and no session/action | `test_model_failure_creates_no_session` |
| Secrets exposure | Key in server-only `.env`; `.env.example` placeholder and `.gitignore` | Inspect repository ignore patterns before pushing |
| Large prompts | Pydantic `message` length maximum 1,000 characters | Source inspection; boundary test pending |

## Important limitations / known risks
- **Sources can go out of date.** Policies were retrieved November 4, 2026, and the catalog is current as of June 2026. The prototype does not check for newer versions; re-extract and re-verify when documents change.
- **Coverage is partial.** Only Computer Science BS and Information Sciences BS requirements are checked; graduate degree audits are not supported. Gen eds, focus areas, technical GPA, residency and catalog-year differences are listed as not checked.
- **Course part of term is unknown.** Undergraduate drops between October 17 and November 13, 2026 cannot be confirmed, because the deadline depends on the part of term. The Registrar also marks its calendar dates as tentative until close to the semester.
- **Synthetic grades use the standard 4-point scale.** The catalog confirms only A = 4.00.
- **PII sanitization is not fully implemented.** The user-entered goal text is sent to the Groq API; students must not enter real identifiers or personal records. Production deployment requires input redaction, authentication, consent and a retention policy.
- **Rate limiting and abuse protection are not implemented.** The 1,000-character limit does not prevent repeated requests.
- **Prompt-injection defenses are partial.** The model only extracts intent and a course code and cannot invoke university tools. One adversarial evaluation case (A06) can still steer the extracted course; the rules then block it because the course is not an enrollment.
- Sessions and simulated receipts are stored in a local SQLite file (`app/data/interfacedna.db`); it has no access control or retention policy, and rebuilding the database clears it.
- A simulated successful receipt is **not** proof of a real-world action.
- **No UIUC branding.** The interface cites UIUC sources but must not use UIUC logos or present itself as an official university service.
- **Receipts are not real.** The portal shows "Request recorded" with a receipt number, but nothing is sent to the university (see Presentation mode above).
  
---

## Checkpoint 3 — Verification Boundaries and Responsible Demonstration

### Separation of Responsibilities

InterfaceDNA separates AI interpretation, institutional rule evaluation, and user authorization.

The language model interprets the student's request and extracts relevant entities, but it does not independently determine institutional policy outcomes or execute university actions.

Deterministic backend rules evaluate the available student and policy information. The interface communicates relevant findings, citations, and uncertainty to the student.

Eligible simulated actions require explicit acknowledgment and server-side revalidation before recording a receipt.

### Synthetic Records and Simulated Actions

The implementation combines real, quoted UIUC policy information with fictional student records.

The following are simulated:

- Student profiles, transcripts, and enrollment histories.
- Registration holds and individual student circumstances.
- Action confirmation and receipt generation.
- Policy conflicts, missing-record conditions, and service outages introduced through fault injection.

A simulated receipt indicates only that the application recorded a local action. It is not evidence of a submitted course drop, cleared registration hold, approved graduation, or completed university transaction.

### Presentation and Deployment Boundary

The controlled classroom demonstration uses a student-portal-style interface to evaluate usability and workflow realism.

The distinction between the prototype and an official university service must be disclosed to evaluators. If the application becomes publicly accessible, it should visibly identify its student records and transactions as simulated, rather than relying only on repository documentation.

Real student information should not be entered into the prototype.

### Interpretation of Automated Tests

The integrated backend's latest locally observed regression suite passed 25 tests on November 5, 2026.

These results support the implemented behaviors tested by the suite, including rule evaluation, blocked confirmation, duplicate-action prevention, and simulated recovery.

The tests do not independently establish:

- Reliability during real university-system outages.
- Protection of real institutional records.
- Production authentication or authorization.
- Security against every prompt-injection attempt.
- Compliance with all accessibility requirements.
- Safe execution of actual university transactions.

### Recovery and Confirmation Safeguards

A blocked session cannot be completed through the normal confirmation endpoint.

Clearing a simulated failure restores eligibility for review only when the deterministic rules permit it. Recovery does not itself constitute authorization or trigger execution.

The backend revalidates applicable rules at confirmation time, reducing the risk of acting on an earlier eligibility decision after relevant conditions have changed.

### Remaining Work

Before any real-world integration, the project would require authentication, authorization, input sanitization, secure data handling, stronger operational monitoring, access-controlled persistence, and a formal review of institutional policies and integration permissions.

---

## Required tests before submission
1. Confirm false -> HTTP 400; blocked state -> HTTP 409; repeated confirmation -> HTTP 409.
2. Show conflicting policy, missing record, outage and return-to-normal on the integrated interface.
3. Test unexpected intent, very long input, no key/invalid key, and model rate limit response without leaking secrets.
4. Verify no `.env`, credentials or real student data appear in the repository or screenshots.
5. Run `tools/verify_sources.py` after any change to the policy or program files.
