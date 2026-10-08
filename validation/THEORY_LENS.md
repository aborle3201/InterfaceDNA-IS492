# InterfaceDNA — Theory Lens
## 1. Working Theory Claim
Our hybrid should beat human-alone and AI-alone at completing complex university tasks accurately and efficiently because humans own judgment, personal trade-offs, and final decisions, while AI owns information retrieval, consequence analysis, dependency checking, and task-focused interface composition.

Our working theory is that InterfaceDNA can create human-AI complementarity by combining AI's ability to interpret goals, organize information, identify dependencies, and generate task-specific views with the student's judgment and authority over consequential decisions.

The goal is not for the AI to replace the student or make academic decisions independently. Instead, InterfaceDNA should reduce the student's effort in finding and interpreting information while preserving human control where personal judgment, uncertainty, or institutional approval is involved.

In this project, complementarity means that the combined student + InterfaceDNA system should perform better than either the student using existing university systems alone or a general-purpose AI assistant working without verified institutional context.

---

## 2. Cognitive Ownership: Human vs. AI
The prompting study showed that current AI tools are often capable of useful reasoning when the relevant facts are already available. However, they become less reliable when they must infer institutional policies, decide which information applies, or manage consequential actions. Our interviews also suggested that students want less navigation and cognitive burden, but do not want to give up control over important decisions.
For InterfaceDNA, we therefore divide responsibility across the main cognitive functions as follows:

## 2. Cognitive Ownership: Human vs. AI

| Cognitive area | InterfaceDNA / AI responsibility | Human responsibility | Example |
|---|---|---|---|
| **Reasoning** | Calculate consequences, identify dependencies, compare conditions, and organize possible next steps. | Evaluate personal trade-offs, question the result, and make the final decision. | The system calculates that dropping a 4-credit course changes a student from 15 to 11 credits; the student decides whether dropping is still the right choice. |
| **Memory** | Retrieve verified student records, current enrollment information, degree requirements, holds, and approved policies. | Confirm that the displayed information matches their situation and report missing or unusual circumstances. | InterfaceDNA retrieves the student's actual credit load instead of relying on conversational memory. |
| **Attention** | Filter irrelevant information, prioritize important warnings, and show the few facts that matter for the current task. | Decide which personal concerns deserve additional attention and request more detail when needed. | A course-drop screen highlights credit impact, deadline, and required approval instead of showing every possible university policy. |
| **Meta-coordination** | Track workflow state, determine when confirmation is required, recognize when human review is needed, and prepare escalation. | Retain final decision authority and confirm consequential actions. | The system may prepare a course-drop action, but the student must review the consequences and explicitly confirm before submission. |

This division is important because our validation showed that simply giving the AI more responsibility does not necessarily improve the experience. In some cases, the models confidently introduced generic rules or remembered information that was not verified. In other cases, they gave useful advice but left the student with a long checklist to complete manually.

The stronger design is therefore not "AI does everything." It is AI handles the information-processing burden while the student retains judgment and decision rights.

---

## 3. Meta-Coordination and Decision Rights
A major issue in our gap analysis was not only whether the AI produced a correct answer, but also who should be allowed to decide and act.
This became especially visible in the F03 course-drop test. Claude and Gemini correctly refused to falsely claim that the course had already been dropped, but they did not consistently preserve the consequence-review boundary before helping the user continue toward the action.

InterfaceDNA therefore needs clear decision rights.
AI / system can:
* interpret the student's goal;
* retrieve verified student and policy information;
* calculate consequences;
* identify dependencies;
* organize the information into a task-specific interface;
* recommend possible next steps;
* prepare a supported action; and
* recognize when escalation is necessary;
  
Student must:
* review important consequences;
* provide personal context that cannot be obtained from the university system;
* decide whether the proposed action fits their situation; and
* explicitly confirm permanent or high-impact actions.

Deterministic backend should:
* determine whether an action is actually available;
* enforce required permissions;
* enforce mandatory confirmation steps;
* reject unsupported or unauthorized actions; and
* report whether an action actually succeeded.

If there is disagreement or uncertainty, the model should not simply make the final decision. For example, if two policy documents contain different deadlines, InterfaceDNA should show that conflict and escalate it to the appropriate authority instead of deciding which deadline "sounds more likely. 
This gives the system a clear escalation rule:
* Verified and low-risk → AI can organize and guide
* Consequential but supported → AI prepares, human confirms
* Conflicting, missing, or exceptional → escalate for human review

---

## 4. Evidence → Theory → Design
The following examples connect our empirical validation directly to the theoretical framework.

| Validation evidence | Theory interpretation | InterfaceDNA design response |
|---|---|---|
| In T02, Gemini correctly calculated 15 → 11 credits but treated a generic 12-credit full-time threshold as if it applied to Demo University. | **Memory + reasoning gap:** correct reasoning is not enough if the knowledge being reasoned over is not verified. | Retrieve enrollment thresholds and other institutional rules from approved sources before presenting them as facts. Clearly separate verified facts from assumptions. |
| Claude T03 and E03 introduced UIUC and remembered personal information that was not provided in the test prompt. | **Memory gap:** conversational memory can increase personalization, but it can also introduce unverified context. | Use authorized institutional data as the source of student-specific facts and show where important information came from. |
| Claude, ChatGPT, and Gemini often produced long lists of possible consequences even when many might not apply to the student. Interviews also showed frustration with searching multiple systems and reading excessive information. | **Attention orchestration gap:** the human is still being asked to filter and prioritize information that the AI could organize. | Generate a focused interface containing only the most relevant facts, warnings, and next actions. Use progressive disclosure for secondary information. |
| The models handled conflicting deadlines differently, and Gemini largely avoided resolving the underlying source conflict. Interview participants preferred visible uncertainty over guessing. | **Meta-coordination + trust calibration gap:** the system needs an explicit process for uncertainty and disagreement. | Display both sources, label the conflict, show source authority where available, and escalate unresolved cases rather than silently selecting an answer. |
| In F03, Claude and Gemini kept the final action with the student but did not consistently enforce consequence review. | **Role-partition gap:** giving the human the final click is not enough if required safety responsibilities are unclear. | Require consequence review and explicit confirmation before consequential actions. These safeguards should be enforced by the system rather than left to model discretion. |
| Interviews showed that students want human support when a case becomes unusual, but do not want to repeat the same information after escalation. | **Meta-coordination gap:** effective teaming requires a smooth transition between AI and human authority. | Create a structured handoff containing the student's goal, verified information, policies checked, unresolved issue, and steps already attempted. |

---

## 5. Committed Design Principle
### Principle: Explicit Role Partitioning
For Checkpoint 3, we will commit to Explicit Role Partitioning as the primary theoretical design principle.

InterfaceDNA will make a clear distinction between:
* what the AI can interpret and prepare;
* what trusted system logic must verify and enforce; and
* what the student must decide and confirm.

We selected this principle because several of our highest-priority gaps connect to unclear responsibility boundaries.
Grounding requires the AI to reason over verified system information rather than its own assumptions. Attention requires the AI to take responsibility for organizing and filtering information instead of returning the filtering work to the student. Safety requires the system to enforce consequence review and confirmation instead of assuming that giving the student the final click is sufficient. Explicit role partitioning therefore connects the three main gaps we identified for CP3 rather than treating them as unrelated problems.

---

## 6. CP3 Complementarity Test
In Checkpoint 3, we will test whether this role partition actually produces complementarity.
We will compare three conditions:

### Human-alone baseline
The student uses a traditional university-style portal and policy information without AI assistance.
The student is responsible for:
* finding the correct pages;
* identifying relevant information;
* comparing policies;
* calculating consequences; and
* determining the next action.

### AI-alone baseline
* The student uses a general-purpose conversational AI without direct access to verified student records, controlled institutional policies, or deterministic action rules.
* The AI can reason and provide guidance, but it may need the student to manually provide context and may introduce generic assumptions.

### Hybrid InterfaceDNA condition

The student uses InterfaceDNA with:
* verified student context;
* approved institutional policies;
* focused task-specific interface components;
* explicit uncertainty states;
* mandatory consequence review;
* deterministic action validation; and
* student confirmation for consequential actions.

### What we will evaluate
The hybrid system should only be considered complementary if it performs better than both baselines on important measures such as:

* correct next action — does the student reach an appropriate next step?
* grounding accuracy — are important claims supported by verified student or policy information?
* consequence coverage — are the important consequences shown without adding irrelevant ones?
* attention load — how much unnecessary information or navigation does the student have to process?
* confirmation compliance — are required review and confirmation boundaries preserved?
* task completion effort — how many steps or separate systems are needed?
* user confidence — does the student understand why the system produced the result?

The purpose of this comparison is not simply to show that InterfaceDNA is faster than another interface. 
It is to test whether the division of responsibilities between the student, AI, and deterministic system produces a better overall result.

---

## 7. Theory-Led Design Direction
The theory lens changes how we think about InterfaceDNA. Our original idea focused mainly on using generative AI to understand a student's goal and generate a useful interface. The validation suggests that interface generation alone is not enough. The more important question is how the work should be divided between the student and the AI system.

For the next prototype:
* AI will handle goal interpretation, dependency reasoning, information organization, and interface composition.
* Verified institutional sources will provide important student and policy facts.
* Deterministic system logic will control permissions, action availability, and confirmation requirements.
* The student will retain authority over consequential academic decisions.
* Human staff will remain part of the workflow for unresolved, exceptional, or policy-conflict cases.

This structure supports complementarity because each participant is responsible for the type of work they are better suited to perform. The AI reduces search and attention burden, the system provides stable rules and verified state, and the student retains judgment and final control.
Our CP3 prototype will therefore test not whether AI can replace existing university decision-making, but whether better coordination between AI reasoning, trusted system data, and human judgment can make complex university tasks safer, clearer, and easier to complete.
