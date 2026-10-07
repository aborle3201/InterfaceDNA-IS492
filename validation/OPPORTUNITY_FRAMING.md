# Opportunity Framing

# InterfaceDNA — Opportunity Framing

## What We Originally Assumed

In Checkpoint 1, we assumed that the main problem was that students have to navigate too many university systems and policies to complete one task.

We expected InterfaceDNA to reduce this friction by understanding a student's goal, retrieving relevant information, and presenting a focused interface.

## What We Found

Our prompting study and interviews mostly confirmed the problem, but also made it more specific.

### 1. Good AI reasoning is not enough

Existing AI tools were often able to explain what a student should check, but they still depended on the student to find records, verify policies, or move between university systems.

**What changed:**  
The value of InterfaceDNA is not just better explanations. It is bringing verified student context and policy information into the same workflow.

### 2. Source verification matters

In the prompting study, models generally handled uncertainty well, but we also saw cases where unrelated context or retrieval appeared.

Students also said they would trust the system more if important claims were clearly tied to official university sources.

**What changed:**  
Source visibility and provenance should be part of the interface, not hidden in the backend.

### 3. Students prefer reliability over instant responses

Both interviews showed that students were willing to wait slightly longer if the system was checking official information.

**What changed:**  
We should prioritize verified results over the fastest possible response.

### 4. Consequential actions need clear boundaries

The safety tests showed that general-purpose AI can refuse unauthorized actions, but students also strongly wanted permanent actions to require explicit confirmation.

**What changed:**  
Confirmation should be enforced by the system design rather than depending only on model behavior.

---

## Prioritized Features

### Verified Student Context

InterfaceDNA should retrieve relevant student information such as current credits, degree requirements, course status, and holds from authorized sources.

**Evidence:** Students currently have to repeatedly find or provide information the university already has.

**Complementarity gap:** AI cannot give personalized guidance without reliable context.

**Design principle:** Let AI organize verified information while the student retains judgment.

---

### Visible Policy Sources

Important deadlines, requirements, and restrictions should show the official source they came from.

**Evidence:** Interview participants said they would double-check AI-generated answers if the source was not visible.

**Complementarity gap:** AI-generated explanations can sound confident even when provenance is unclear.

**Design principle:** Verified information should be visible and traceable.

---

### Uncertainty and Conflict State

If two sources conflict or information cannot be verified, InterfaceDNA should clearly say so.

**Evidence:** E02 showed that conflicting deadlines should remain unresolved until an authoritative source is available.

**Complementarity gap:** AI should not silently choose between uncertain alternatives.

**Design principle:** Use an “I’m not sure” state and escalate when needed.

---

### Personalized Consequence Summary

Instead of returning a long general checklist, InterfaceDNA should show only the consequences that apply to the current student.

Examples:

- credit-load change;
- degree impact;
- important deadlines;
- enrollment requirements; and
- required approvals.

**Evidence:** Interviews favored short consequence summaries over long explanations.

**Complementarity gap:** General-purpose AI often gives broad advice that the student still has to interpret.

**Design principle:** AI focuses attention; the student evaluates the trade-offs.

---

### Explicit Confirmation

No permanent academic action should happen without student confirmation.

**Evidence:** Both the prompting study and interviews supported keeping final decision rights with the student.

**Complementarity gap:** Automation becomes risky when decision ownership is unclear.

**Design principle:** The AI prepares the action; the student authorizes it.

---

## Current Opportunity

InterfaceDNA is not intended to replace advisors or student judgment.

The opportunity is to reduce the work between a student's goal and an informed decision by combining:

**verified context + official policy + focused consequences + clear uncertainty + student control**

This is the main direction we will carry into Checkpoint 3.