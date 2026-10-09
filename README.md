# InterfaceDNA

### Goal-Adaptive Interfaces for Complex Digital Systems

**InterfaceDNA** is a Generative AI system that transforms a user's natural-language goal into a focused, task-specific interface and brings together the information, warnings, policies, and actions that actually matter for that task.

## Team Members

| Team Member     | Role                      | Responsibilities                                                          | Contact              |
| ---             | ---                       | ---                                                                       | ---                  |
| Aabha Borle     | Backend & Evaluation Lead | Backend APIs, synthetic data, policy handling, testing, and evaluation    | aborle2@illinois.edu |
| Anisha Kango    | Frontend & UI/UX Lead     | Adaptive UI, user flows, usability, and accessibility                     | kango2@illinois.edu  |
| Sakshi Katolkar | GenAI & Agent Logic Lead  | Intent interpretation, prompt workflows, task planning, and AI evaluation | srk12@illinois.edu   |

**Course:** IS 492: Generative AI & Human-AI Systems  
**Semester:** Fall 2026  
**GitHub Repository:** https://github.com/aborle3201/InterfaceDNA-IS492

## Problem Statement & Motivation

Complex institutional websites are often organized around departments and system structure rather than what users are actually trying to accomplish.

For example, a university student asking, **“What do I still need to graduate?”** may need to check degree requirements, completed courses, academic policies, registration information, advising resources, and account holds across multiple pages or systems.

Similarly, a student trying to drop a course may need to determine deadlines, eligibility, academic consequences, policies, and the correct action to take before they can complete what initially seems like a simple task.

The problem is therefore not just navigation. Users must understand which information matters, connect information across different systems, interpret policies, and determine the correct next step.

InterfaceDNA explores whether Generative AI can reduce this gap by allowing users to express their goals naturally and dynamically creating an interface around what they are trying to accomplish.

## Target Users

Our initial target users are university students interacting with complex institutional portals.

University systems provide a useful environment for testing InterfaceDNA because students regularly complete tasks that require information from multiple systems, policies, and sources.

### Core User Tasks

#### 1. Graduation Readiness

**User Goal:** “What do I still need to graduate?”

**Desired Outcome:** The student receives a focused view showing completed requirements, remaining requirements, relevant warnings, and recommended next steps.

#### 2. Course Drop

**User Goal:** “Can I drop CS 411?”

**Desired Outcome:** The student sees the relevant deadline, eligibility requirements, possible consequences, applicable policies, and available actions in one place.

#### 3. Registration Preparation

**User Goal:** “Help me prepare for registration.”

**Desired Outcome:** The system identifies relevant holds, prerequisites, degree requirements, registration information, and actions the student may need to complete.

## Competitive Landscape

### Traditional University Portals

University portals provide access to important services such as registration, degree progress, billing, advising, and student records.

However, these systems are often separated into different pages or services. Users must understand the system structure before they can successfully complete their actual goal.

### Conversational AI Assistants

AI assistants make it easier for users to ask questions using natural language.

However, a conversational response may still leave users with instructions that they must manually translate into actions across an existing interface.

### AI Web Agents

Research systems such as **Mind2Web, WebArena, WorkArena, and WebVoyager** explore how language models can understand natural-language instructions and interact with existing websites.

These systems demonstrate the potential of AI-driven web interaction, but research also shows continuing challenges involving generalization, grounding, reliability, and successful execution of multi-step tasks.

Most existing work focuses on helping AI operate interfaces that already exist.

**InterfaceDNA explores a complementary question:** If AI understands the user's goal, can the interface itself adapt around that goal?

## Initial Concept

Instead of requiring users to navigate through a fixed website structure, InterfaceDNA begins with the user's goal.

For example: **“I want to drop CS 411.”**

The system would interpret the request, retrieve relevant user information and institutional policies, identify required steps and dependencies, and generate a focused interface containing only the information and actions relevant to that task.

### System Flow

```text
User expresses a goal
        ↓
Intent Interpretation
        ↓
Context & Policy Retrieval
        ↓
Task Planning
        ↓
Interface Composition
        ↓
Focused Task-Specific Interface
        ↓
User Reviews and Confirms Actions
```

The initial system follows four primary stages:

1. **Intent Interpretation**  
   Convert the user's natural-language request into a structured goal.

2. **Context Retrieval**  
   Retrieve relevant student information, system state, and institutional policies.

3. **Task Planning**  
   Determine the required steps, dependencies, warnings, and available actions.

4. **Interface Composition**  
   Assemble a temporary task-specific interface using predefined components such as status cards, warnings, forms, links, and action buttons.

## Why Generative AI?

Generative AI is a functional part of InterfaceDNA rather than an additional chatbot layer.

User goals can be open-ended, context-dependent, and expressed in many different ways. It would be difficult to manually create a fixed workflow for every possible combination of requests, policies, and user states.

GenAI allows InterfaceDNA to:

- Interpret natural-language goals.
- Understand the user's intent.
- Determine what context is relevant.
- Connect user information with applicable policies.
- Plan the steps required to complete a task.
- Decide which interface components are appropriate for the current goal.

Deterministic software will continue to control permissions, validation, and execution of actions.

## Safety and User Control

InterfaceDNA will not allow the language model to freely execute actions or generate unrestricted executable code.

State-changing operations will use controlled backend functions.

Important or consequential actions will require explicit user confirmation before execution.

Additional safeguards include:

- Using synthetic student data during prototype development.
- Grounding policy-related responses in a controlled policy corpus.
- Schema-validating model outputs.
- Restricting executable actions to approved backend functions.
- Falling back to informational responses for unsupported or low-confidence requests.
- Testing against prompt injection and adversarial inputs.
- Reviewing generated interfaces for accessibility.
- Evaluating bias and potentially harmful outputs.

## Prototype Scope

The initial prototype will use a simulated university portal with synthetic student records and a controlled institutional policy corpus.

Initial scenarios will include:

- Course drops
- Registration preparation
- Graduation readiness
- Account holds
- Meal-plan changes

Simple informational questions may remain conversational, while more complex or multi-step goals will trigger an adaptive interface.

## Literature Foundation

InterfaceDNA is informed by research in web agents, multimodal interface interaction, grounding, and generative interfaces.

Our initial literature corpus includes research such as:

- **Mind2Web** - General-purpose web agents and cross-website generalization.
- **WebArena** - Realistic multi-step web interaction.
- **WorkArena** - Enterprise and knowledge-work web tasks.
- **WebVoyager** - Multimodal web interaction using visual and textual information.
- **Generative Interfaces for Language Models** - Dynamically generated task-specific interfaces.
- **SUPPLE: Automatically Generating User Interfaces** - Automatic and adaptive interface generation.
- **Exploring the Design Space for Adaptive Graphical User Interfaces** - How adaptive UI changes affect usability and user satisfaction.
- **Guidelines for Human-AI Interaction** - Principles for transparency, correction, user control, and trustworthy AI interaction.

Together, these works highlight several recurring challenges:

1. Understanding user intent does not guarantee correct execution.
2. Grounding model decisions in valid interface actions remains difficult.
3. Real-world tasks frequently require reasoning across multiple steps and sources.
4. Visual and contextual information are important for interface interaction.
5. Generative interfaces offer an alternative to purely conversational interaction.

InterfaceDNA builds on these findings by exploring whether AI can adapt the interface itself rather than only navigating a fixed interface.

## Checkpoint 2 Validation Plan

Checkpoint 2 will focus on validating the **goal-to-interface pipeline**.

We plan to evaluate approximately **25-30 controlled scenarios**, where each scenario defines:

- User goal
- Required context
- Applicable policy
- Expected actions
- Dependencies
- Warnings
- Confirmation requirements

### Evaluation Metrics

We will evaluate:

- Intent-recognition accuracy
- Required-information coverage
- Irrelevant-information rate
- Policy-grounding accuracy
- Valid-action selection
- Interface completeness
- Confirmation compliance

We also plan to compare InterfaceDNA against a chat-only baseline using:

- Number of task-completion steps
- Correct-next-action rate
- Perceived user effort

The goal is to determine whether adaptive interfaces improve task completion rather than simply presenting the same information differently.

## Project Roadmap

| Checkpoint | Timeline | Primary Goal | Planned Deliverables |
| --- | --- | --- | --- |
| **Checkpoint 1** | **Sept. 17, 2026** | Project definition and research foundation | Problem definition, literature review, proposal, repository setup, GitHub project management, initial concept |
| **Checkpoint 2** | **Oct. 8, 2026** | Validate the core goal-to-interface pipeline | Intent/prompt logic, controlled scenarios, synthetic data, prototype components, initial evaluation |
| **Checkpoint 3** | **Nov. 5, 2026** | Expand and integrate the prototype | Integrated InterfaceDNA workflow, broader task coverage, safety testing, usability testing |
| **Checkpoint 4** | **Dec. 3, 2026** | Final evaluation and refinement | Refined prototype, evaluation results, limitations, final presentation |

## Repository Structure

```text
InterfaceDNA/
│
├── README.md
│
├── literature/
│   ├── BIBLIOGRAPHY.md
│   └── [research papers]
│
├── reflections/
│   ├── lastname_firstname.md
│   └── ...
│
├── proposal/
│   └── PROPOSAL.md
│
└── slides/
    └── InterfaceDNA_Checkpoint1.pptx
```

## Current Project Status

### Checkpoint 1

- Project concept selected
- Problem and motivation defined
- Initial technical approach designed
- Checkpoint 2 validation strategy defined
- Complete literature corpus
- Complete individual paper reflections
- Set up GitHub Issues
- Set up GitHub Project Board
- Finalize Checkpoint 1 presentation

### Checkpoint 2

- Completed controlled prompting study across ChatGPT, Claude, and Gemini.
- Completed six short user interviews.
- Documented cross-platform prompting results and failure cases.
- Completed `GAP_ANALYSIS.md`.
- Completed `THEORY_LENS.md`.
- Identified the top three gaps for Checkpoint 3.
- Refined the human-AI role partition and confirmation boundaries.
- Developed the updated InterfaceDNA storyboard.
- Completed individual validation reflections.

---

## Checkpoint 2 Outcomes

Checkpoint 2 shifted the project from an initial concept into an evidence-informed design direction.
The team completed a controlled prompting study across **ChatGPT, Claude, and Gemini**, using the same typical, edge, and failure scenarios to examine reasoning, grounding, memory, attention, uncertainty handling, and action boundaries.
The team also conducted **six short student interviews** to understand how students currently experience complex academic tasks and what they would need in order to trust an AI-supported university interface.

The combined validation produced several important findings:

- General-purpose AI tools were usually good at identifying what information mattered, but they often still required the student to manually gather information from multiple systems.
- Reasoning was generally stronger when all relevant facts were explicitly provided.
- Models sometimes mixed verified facts with generic institutional assumptions.
- Conversational memory or personalization could introduce context that had not been verified against the student's current institutional record.
- Conflicting policies were not handled consistently across models.
- Long chatbot-style responses often created additional cognitive load rather than reducing it.
- Students consistently preferred verified information, visible uncertainty, and clear source information over fast but generic answers.
- Consequential actions such as dropping a course should remain under student control and require consequence review and explicit confirmation.
- Students also valued consistent interface patterns and clear escalation to a human when the system could not safely resolve a case.

These findings refined the original InterfaceDNA concept. The project is no longer focused only on generating a personalized interface from a natural-language goal. The interface must also be **grounded, selective, source-aware, predictable, and explicit about uncertainty and decision rights**.

### Checkpoint 2 Priority Gaps

Three gaps were selected as the highest priority for the next checkpoint:

1. **Grounding in verified student state and institutional policy**  
   InterfaceDNA should distinguish between verified institutional facts and general model knowledge. Student status, deadlines, thresholds, holds, and policy rules should come from controlled and traceable sources.

2. **Confirmation and consequence-review boundaries**  
   The student should remain the final decision-maker, while the system must preserve required consequence review and explicit confirmation before consequential actions.

3. **Attention load and focused interface composition**  
   Instead of presenting every possible consequence, InterfaceDNA should use verified student context to show only the most relevant information, warnings, and next actions.

---

## Checkpoint 3 Direction

Checkpoint 3 will focus on turning the validated design principles into a more integrated InterfaceDNA prototype.

The next prototype will test whether a hybrid system can outperform both:

- a student navigating a traditional university-style interface without AI support; and
- a student using a general-purpose AI assistant without verified institutional context.

### Planned Checkpoint 3 Focus

The team plans to implement and evaluate:

- verified retrieval of synthetic student records and controlled policy data;
- task-specific interface generation using a fixed library of trusted components;
- visible source and verification indicators;
- explicit handling of missing or conflicting information;
- consequence summaries that prioritize only relevant risks;
- mandatory review and confirmation before state-changing actions;
- deterministic backend validation for permissions and execution;
- structured escalation when human review is required; and
- consistent interface patterns across different student goals.

### Checkpoint 3 Evaluation

The Checkpoint 3 evaluation will compare:

1. **Human-alone baseline**  
   Student completes the task using a traditional portal-style workflow.

2. **AI-alone baseline**  
   Student uses a general-purpose conversational AI without verified student records or controlled institutional policies.

3. **Hybrid InterfaceDNA condition**  
   Student uses InterfaceDNA with verified context, focused interface composition, explicit uncertainty states, and controlled action              boundaries.

The goal for Checkpoint 3 is not simply to make InterfaceDNA more autonomous. It is to test whether a clearer division of responsibility between the **AI, trusted system logic, and the student** creates a safer and more useful experience.

## Project Vision

InterfaceDNA explores a different way of thinking about digital interfaces.

Instead of requiring users to understand how a complex system is organized before they can accomplish something, the system attempts to understand what the user wants to accomplish first and adapts the interface around that goal.

Our central research question is:

> **Can Generative AI transform a natural-language goal and current system state into a more direct, understandable, and actionable interface while preserving user control?**
