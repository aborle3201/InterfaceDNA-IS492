# InterfaceDNA
## Goal-Adaptive Interfaces for Complex Digital Systems

### Problem Significance

Digital systems often make users solve two problems at once: understand what they want to accomplish, then figure out how the system expects them to do it. In institutional portals, one goal can depend on several policies, records, deadlines, and account states. The difficult part is not always finding a page; it is translating a real-world goal into the system’s structure and knowing which information matters at that moment.

InterfaceDNA treats this “goal-to-system translation” as the main design problem. Fixed workflows work for predictable cases, but become difficult when the same request changes based on user state, timing, eligibility, or policy conditions. An AI-native approach is useful because natural-language goals are variable and context-dependent. GenAI can interpret the request, connect it with relevant context, and help form a task-specific plan without requiring the user to understand the portal first.

### Prior Work & Gaps

The papers in our literature review show that natural-language web interaction is possible, but reliable task completion is still difficult. Mind2Web evaluates more than 2,000 tasks across 137 real websites and shows that generalizing to unseen websites and interaction patterns remains challenging (Deng et al., 2023). WebArena reports a large gap between human and agent performance on realistic long-horizon tasks, especially when planning, state tracking, and error recovery are required (Zhou et al., 2023). WorkArena finds similar limitations in enterprise software, where agents can solve some ServiceNow tasks but remain far from dependable automation (Drouin et al., 2024). WebVoyager shows that visual reasoning can improve web interaction, but the agent still works within an interface that already exists (He et al., 2024).

Generative Interfaces for Language Models asks a different question: whether AI can generate an interface better suited to the current task, and reports benefits for structured, information-dense interactions (Chen et al., 2026). This is closest to InterfaceDNA, but our project places the idea in a more constrained institutional setting where policies, permissions, and valid actions matter. The gap we want to explore is whether a generative interface can stay useful while remaining grounded in system state and limited to actions the system actually supports.

### Proposed Technical Approach

We will build the prototype around a simulated university portal using synthetic student records and a controlled institutional policy corpus. Initial scenarios will include course drops, registration preparation, graduation readiness, account holds, and meal-plan changes.

A natural-language request is first converted into a structured task representation containing the goal, relevant entities, missing information, and confidence. Retrieval then supplies the student state and policy information needed for that task. A planning prompt identifies required steps, dependencies, warnings, and possible actions. The interface-composition stage maps that plan to a fixed library of trusted components such as status cards, policy notices, forms, links, and confirmation controls.

GenAI handles interpretation, planning, and component selection. Agentic behavior is intentionally bounded: the model may propose what should happen next, but deterministic software decides whether an action exists, whether it is permitted, and whether confirmation is required. The model will not directly change student data or generate unrestricted executable code.

### Checkpoint 2 Validation Plan

Checkpoint 2 will test both the individual prompt chains and the full goal-to-interface pipeline using approximately 25–30 controlled scenarios. Scenarios will vary by wording, missing information, policy conditions, conflicting states, and unsupported requests. Each case will have a known expected intent, required context, valid actions, warnings, dependencies, and confirmation rules.

We will measure intent-recognition accuracy, policy-grounding accuracy, required-information coverage, irrelevant-information rate, valid-action selection, interface completeness, and confirmation compliance. We will also record where an error first appears—interpretation, retrieval, planning, or composition—so failures can be traced to a specific stage. A smaller comparison with a chat-only baseline will examine task-completion steps, correct-next-action rate, and perceived user effort.

### Risk Analysis & Mitigation

The main risks are privacy exposure, hallucinated policies or actions, prompt injection, unsafe automation, biased or toxic outputs, and inaccessible generated views. Synthetic records will be used during development. Policy-dependent outputs will be grounded in the controlled corpus, structured outputs will be schema-validated, and actions outside the approved backend function set will be rejected.

Low-confidence or unsupported requests will fall back to a normal informational response instead of forcing a generated interface. Adversarial cases will test prompt injection, bias, and toxicity, and generated views will be reviewed for basic accessibility. Consequential actions will always require explicit confirmation, keeping the model in an assistive role rather than allowing it to act silently on the user’s behalf.