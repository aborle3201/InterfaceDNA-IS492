# Design Spec

# InterfaceDNA — Design Specification

## 1. Design Goal

InterfaceDNA turns a student's university goal into a focused task-specific interface.

Instead of making the student search across portals, policies, and emails, the system retrieves relevant information, organizes the decision, and keeps the student in control of consequential actions.

---

# Part A — User and Interaction Design

## 2. Primary Persona

### University Student

A student trying to complete an academic or administrative task such as:

- dropping a course;
- checking graduation readiness; or
- resolving a registration hold.

### Main Needs

The student needs:

- accurate student-specific information;
- official university policies;
- a clear explanation of consequences;
- fewer systems to navigate;
- visible uncertainty; and
- control over final decisions.

---

## 3. Mental Model

Students do not usually think:

> “Which university system should I open?”

They think in goals:

> “Can I drop this course?”

> “What do I still need to graduate?”

> “Why can’t I register?”

InterfaceDNA should therefore begin with the student's goal and assemble the relevant interface around it.

---

## 4. Decision Rights

### AI can

- retrieve authorized student context;
- retrieve approved university policies;
- calculate simple consequences;
- organize relevant information;
- identify missing information;
- highlight conflicts or uncertainty; and
- prepare a possible next action.

### Student must

- review the consequences;
- evaluate whether the recommendation fits their situation;
- resolve unclear personal context when needed; and
- explicitly confirm consequential actions.

### AI must not

- silently change enrollment;
- claim an action succeeded before system confirmation;
- invent missing policy information; or
- override student confirmation.

---

## 5. Trust Cues

Every important workflow should include three trust cues.

### Source Visibility

Important policy information should show where it came from.

### Uncertainty State

If information cannot be verified, the system should say:

> “I’m not sure.”

It should then explain what information is missing or which office should be contacted.

### Explicit Confirmation

The student must confirm before any permanent action.

---

# 6. Task Flows

## Course Drop

Student asks:

> “Can I drop CS 411?”

Flow:

1. Interpret the course-drop goal.
2. Retrieve course and credit information.
3. Retrieve relevant drop policy.
4. Calculate the student's post-drop credit load.
5. Show relevant consequences.
6. Flag uncertainty or conflicts.
7. Student reviews sources and consequences.
8. Student explicitly confirms if they choose to continue.

---

## Graduation Readiness

Student asks:

> “What do I still need to graduate?”

Flow:

1. Retrieve degree requirements.
2. Retrieve completed and current courses.
3. Compare student record with requirements.
4. Group requirements into:
   - completed;
   - in progress; and
   - still required.
5. Highlight possible blockers.
6. Show policy/degree-rule sources.
7. Escalate unclear requirement mappings to an advisor.

---

## Registration Hold

Student asks:

> “Why can’t I register?”

Flow:

1. Retrieve current hold information.
2. Identify the office responsible.
3. Retrieve the relevant requirement or message.
4. Show what the hold blocks.
5. Show the next required action.
6. Provide the appropriate office if human review is needed.
7. Verify when the hold has been resolved.

---

# Part B — Interface Design

## 7. Main Interface Structure

Each generated task interface should include:

### Goal Header

Shows the student's current goal.

Example:

> Course Drop — CS 411

### Student Context

Shows only the student information relevant to the task.

Example:

- Current credits: 16
- CS 411 credits: 4
- Credits after drop: 12

### Consequence Summary

Shows the most important effects in short cards rather than a long AI response.

### Sources

Shows verified policy and student-record sources.

### Warning / Uncertainty Area

Used when:

- policies conflict;
- required information is missing; or
- human approval is required.

### Action Area

Shows the next permitted action.

Any consequential action requires explicit confirmation.

---

## 8. Interaction States

### Loading

The system should indicate that it is:

- retrieving student information;
- checking university policies; and
- calculating consequences.

### Verified

Information from an approved source should be visibly marked as verified.

### Uncertain

If the system cannot verify an answer, it should show:

> “I’m not sure.”

The interface should explain why.

### Confirmation

Before a permanent action:

> “Review the consequences before continuing.”

The student then chooses:

- Cancel
- Confirm

### Completed

An action should only be shown as completed after confirmation from the connected university system.

---

## 9. Design-System Alignment

The interface should follow established design-system principles such as Material 3, Carbon, or Apple HIG.

Key principles include:

- clear visual hierarchy;
- consistent components;
- accessible contrast;
- readable typography;
- clear status and warning states;
- obvious primary and secondary actions; and
- confirmation for destructive or consequential actions.

---

## 10. Evidence Traceability

Every major interface element should correspond to a finding from the prompting study or interviews.

| Interface Element | Evidence |
|---|---|
| Visible policy source | Students wanted verified and traceable information |
| “I’m not sure” state | Conflicting or uncertain policy findings |
| Consequence summary | Interviews preferred concise, relevant information |
| Student context card | Existing AI required manual record gathering |
| Explicit confirmation | Safety tests and interviews supported student control |
| Office escalation | Students currently need multiple offices for complex cases |

No feature should be included only because it seems useful; it should trace back to evidence from validation.