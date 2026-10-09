# InterfaceDNA — Checkpoint 2 Interactive Prototype

A standalone HTML/CSS/JavaScript proof-of-concept for **InterfaceDNA: Goal-Adaptive Interfaces for Complex Digital Systems**.

The prototype demonstrates the full Checkpoint 2 interaction model across three student journeys:

1. **Course drop** — verified student context + approved policy → personalized consequence summary → explicit confirmation.
2. **Graduation readiness** — degree audit + catalog provenance → requirement-level explanation → student-approved plan.
3. **Registration hold** — hold ownership + office routing → safe next steps → confirmation only for an action the student may initiate.

> **Important:** This is a fixed-scenario simulation using fictional **Demo University** data. It does not access a real student record, university system, or policy source, and it never submits a real action.

## Live prototype

**Hosted demo:** https://interfacedna-is492-prototype.vercel.app/

The hosted version is the recommended way to review and demo the prototype.

You can also run the prototype locally by opening `index.html` directly in a browser. No build step or package installation is required.

Alternatively, serve it with any static server, for example:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## Prototype controls

The dark bar at the top is deliberately outside the product UI so the team can quickly demo required scenarios in class.

### Journey

- **J1 Course drop**
- **J2 Graduation**
- **J3 Registration hold**

### Play as

The three synthetic personas map to the three core journeys:

- **Alex** — enrollment-sensitive student
- **Maya** — graduating senior
- **Jordan** — student with registration holds

The right rail gives each persona a short task list and success criterion.

### Failure / edge case

The prototype has three explicit failure states so the team can demonstrate trust calibration instead of only the happy path:

- **Conflicting drop policies** → “I’m not sure” + Registrar escalation
- **Missing degree-audit record** → provisional answer + no hallucinated requirement status
- **University service unavailable** → verification stops + retry/fallback

### Theme

Use **Dark / Light** to switch themes.

## What to look for

| Requirement | Where it appears |
|---|---|
| **Decision rights** | Course-drop confirmation gate; graduation plan disclaimer; advising-request confirmation; cancel paths |
| **Interrogation moments** | “Why?” on course-drop consequences, graduation requirement rows, office ownership, and failure states |
| **Trust calibration** | Visible source/version badges, synthetic-data banner, conditional language, no false completion claim |
| **Uncertainty** | Policy conflict, missing academic record, and university service outage states |
| **Provenance** | Approved policy source cards and student-record verification rows |
| **Role partitioning** | Right-rail Human–AI role split plus action-specific permission boundaries |
| **Attention support** | Goal-specific summaries instead of a general chat transcript or full portal dump |
| **Meta-coordination** | Escalation to Registrar/Advising/Student Accounts and explicit student confirmation |

## What works vs. what is simulated

| Capability | Prototype status |
|---|---|
| Journey navigation | **Works** |
| Persona switching | **Works** |
| Failure-state switching | **Works** |
| Light/dark theme | **Works** |
| “Why?” interrogation panels | **Works** |
| Confirmation checkbox gates | **Works** |
| Safe cancel paths | **Works** |
| Credit arithmetic and requirement display | **Works over the synthetic fixture** |
| Student-record retrieval | **Simulated** |
| Policy retrieval / policy versions | **Simulated** |
| Registrar clarification | **Simulated** |
| Degree-audit refresh | **Simulated** |
| Hold-clearance request | **Simulated** |
| Course drop submission | **Simulated** |
| Any real university system integration | **Not implemented** |

## The three trust cues

The prototype makes the team’s three trust cues visible:

1. **Student confirmation before consequential action**
2. **Policy / record source shown near important claims**
3. **“I’m not sure” fallback when information cannot be verified**

## Evidence → theory → design traceability

The prototype is grounded in the Checkpoint 2 validation findings rather than adding features only because they look useful.

| Receipt / finding | Theory interpretation | Prototype decision |
|---|---|---|
| **F01:** the assistant safely refused to invent an official deadline but still introduced irrelevant/unreliable context | Memory / provenance failures can undermine trust even when the final conclusion is safe | Important policy claims are tied to approved source/version cards |
| **E02:** conflicting fictional policy dates could not be resolved from the supplied documents alone | Weak shared institutional memory requires escalation, not confident guessing | Dedicated “I’m not sure” conflict state with Registrar escalation |
| **T03/T04:** useful AI explanations still left the student to gather records and navigate multiple systems | Attention + memory coordination breaks when the student remains the integration layer | Goal-specific screen combines relevant student context, policy, consequence, and next step |
| **F02:** the model resisted prompt injection inside a policy excerpt | Retrieved documents should be treated as data, while permissions are controlled separately | Policy content never grants action authority; role boundaries stay explicit |
| **F03:** the model refused to pretend a course was dropped without confirmation/execution | Meta-coordination requires explicit decision rights and truthful action status | Confirmation gate + simulated system response; no “done” state before confirmation |
| Student interviews favored verified information over instant answers for consequential decisions | Reliability is more important than raw latency in high-stakes academic workflows | Verification stage is visible and the system stops when authoritative context is unavailable |

See `EVIDENCE_MAP.md` for a compact screen-to-evidence map.

## Files

| File | Purpose |
|---|---|
| `index.html` | Prototype shell and demo controls |
| `styles.css` | Responsive light/dark design system |
| `app.js` | Journey state machine, interactions, failure flows, and confirmation gates |
| `data/run.json` | Synthetic Demo University fixture |
| `data/run.js` | Same fixture as a browser script so the prototype works when opened directly from the file system |
| `EVIDENCE_MAP.md` | Receipt → theory → prototype traceability |


