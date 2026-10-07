# Theory Lens

# InterfaceDNA — Theory Lens

## Part 1 — Human–AI Complementarity

InterfaceDNA uses the human–AI complementarity framework from Gonzalez et al. (2026).

The main idea is that simply combining a human and an AI does not automatically lead to better results. A good human–AI system should achieve something that neither the human nor the AI can do as well alone.

For InterfaceDNA:

- A student alone may have to search across several university pages, policies, and systems.
- A general-purpose AI can organize information quickly, but may lack verified student context or reliable policy grounding.
- InterfaceDNA combines AI-assisted retrieval and organization with student judgment and final decision-making control.

### Working Theory Claim

> Our human–AI hybrid should outperform both students navigating university systems alone and AI assistants working alone at completing complex university tasks because students retain personal judgment and final decision-making authority, while AI organizes relevant student information, retrieves policies, and assembles a focused interface around their goals.

### Core Workflow

Student goal → interpret goal → retrieve student context and approved policies → organize steps → present a focused interface → student reviews → student confirms any consequential action.

---

## Part 2 — Human vs. AI Responsibilities

| Dimension | AI Responsibility | Student Responsibility |
|---|---|---|
| **Reasoning** | Organize information, identify dependencies, and explain possible consequences. | Evaluate whether the recommendation makes sense for their goals and situation. |
| **Memory** | Retrieve relevant student records and approved university policies. | Confirm that personal context is correct and provide information the system does not know. |
| **Attention** | Surface the most relevant deadlines, warnings, requirements, and next steps. | Focus on the trade-offs that matter and decide what to do. |
| **Meta-coordination** | Manage the workflow, identify uncertainty, and escalate when information cannot be verified. | Decide whether to continue, ask for clarification, or contact a human authority. |
| **Decision rights** | Prepare and explain an action, but never silently execute a consequential decision. | Retain final authority and explicitly confirm consequential actions. |

### Trust Cues

InterfaceDNA should consistently show three trust cues:

1. **Student confirmation before consequential actions**
2. **Visible policy sources**
3. **An “I’m not sure” state when information cannot be verified**

The goal is not to replace student judgment, but to reduce the amount of searching and coordination the student has to do.

---

## Part 3 — Evidence → Theory → Design



---

## Part 4 — Committed Design Principle

### Principle

**InterfaceDNA should help students understand and coordinate a decision, but it should not make consequential decisions for them.**

The AI can retrieve information, organize policies, calculate consequences, and highlight uncertainty. However:

- important claims should be tied to verified sources;
- conflicting information should be shown rather than silently resolved;
- uncertainty should trigger an “I’m not sure” or escalation state; and
- consequential actions should always require explicit student confirmation.

This division keeps the strengths of AI in information retrieval and organization while keeping judgment and decision authority with the student.

---

## Checkpoint 3 Test Plan

In Checkpoint 3, we will test whether the hybrid system actually provides complementarity rather than assuming that it does.

We will compare three conditions:

### 1. Student Alone

The student completes the task using the available university information and systems without AI assistance.

### 2. AI Alone

The student uses a general-purpose AI assistant to help complete the same task.

### 3. InterfaceDNA Hybrid

InterfaceDNA retrieves relevant student context and verified policies, presents the important consequences in one focused interface, and keeps the student in control of the final decision.

### Tasks

We will compare the three conditions across the main InterfaceDNA scenarios:

- course drop;
- graduation readiness; and
- registration or hold resolution.

### What We Will Measure

We will look at:

- **Accuracy:** Did the student reach the correct conclusion?
- **Reliability:** Were claims based on the correct information and sources?
- **Latency:** How long did the task take?
- **UX friction:** How many pages, systems, or manual steps were needed?
- **Safety:** Were consequential actions and uncertainty handled correctly?
- **User confidence:** Did the student understand why the recommendation was made?

The hybrid should only be considered successful if it performs better than both the student-alone and AI-alone conditions on the overall task, not simply because it uses AI.