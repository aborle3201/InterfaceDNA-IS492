# InterfaceDNA — Gap Analysis
## 1. Purpose
This gap analysis combines evidence from two parts of our Checkpoint 2 validation: a controlled prompting study across Claude, ChatGPT, and Gemini, and short user interviews focused on students' experiences with complex university tasks.

The goal was not simply to determine which AI platform performed best. Instead, we wanted to understand where current general-purpose AI tools work well, where they become unreliable or burdensome, and which gaps InterfaceDNA should address through system design.
Across the prompting study, the same typical, edge, and failure scenarios were used to test reasoning, memory, attention, and meta-coordination. The interview findings were then used to check whether the observed AI limitations matched problems that students actually experience. Following the checkpoint framework, we interpret the evidence using the sequence: Empirical receipt → theoretical reading → design implication

The theoretical reading uses the complementarity concepts introduced in the course: reasoning, memory, attention, and meta-coordination, with particular attention to whether the human and AI are being given appropriate responsibilities.

---

## 2. Cross-Platform Prompting Findings
### 2.1 All three tools could identify relevant information, but they still placed substantial work on the student
Across the typical scenarios, Claude, ChatGPT, and Gemini generally understood which information mattered for tasks such as dropping a course, checking graduation readiness, or resolving a registration hold.
For example, ChatGPT's T01 response correctly identified enrollment status, deadlines, degree requirements, financial consequences, and immigration requirements, but still required the student to gather and provide most of that context manually. Claude showed a similar pattern in T04: it produced a reasonable six-step process, but the student still had to identify the hold, gather documents, contact the office, and later verify that the hold was removed. Gemini also identified the correct categories of information for a registration hold, while still requiring the student to discover which instructions actually applied.
This suggests that the main limitation is not simply whether an LLM knows what information is relevant. The larger gap is that general-purpose AI does not have a reliable connection to verified student state and institutional workflow data.

### 2.2 Reasoning was generally strong when the relevant facts were explicitly supplied
The platforms performed well when the prompt already contained the facts needed for a calculation or comparison.
In the known-threshold course-drop scenario, all three tools correctly recognized that dropping a 4-credit course from a 15-credit schedule leaves 11 credits, which is below the supplied 12-credit threshold. ChatGPT handled the additional consequences conditionally rather than treating them as automatically applicable. Claude also reasoned correctly and framed most downstream effects as items to verify. Gemini reached the correct threshold result, although it was more likely to present additional consequences such as visa, housing, and aid impacts with stronger certainty than the prompt justified.
This distinction became important in our analysis: the models were often good at reasoning over facts once those facts were known, but weaker at determining which contextual facts and policies were actually authoritative.

### 2.3 Generic institutional knowledge was sometimes treated too confidently
Gemini showed this most clearly in T02. It correctly calculated the new credit load as 11, but then treated 12 credits as the applicable full-time threshold and stated that the student would become part-time, even though Demo University's threshold had not been provided.
Claude also occasionally introduced assumptions that were not present in the prompt, such as referring to the timing of a deadline, graduate-level context, or typical university procedures.
ChatGPT was somewhat more cautious in T02, describing 12 credits as a common undergraduate rule but explicitly stating that Demo University's policy would still need to be verified.
The broader gap is therefore not whether the model has general knowledge. The problem is whether it can distinguish a general pattern from a verified institutional rule at the moment a student is making a consequential decision.

### 2.4 Memory and personalization can introduce context that was never verified
Claude produced the clearest example of this issue. In T03, it assumed UIUC, referred to specific remembered courses, and used personal work context that did not appear in the test prompt. In E03, it again assumed UIUC and introduced a third-party calendar even though the prompt did not specify a university. This is especially important for InterfaceDNA because remembered information may be plausible but should not be treated as equivalent to verified institutional state.
The design implication is that student-specific facts should come from authorized system records, not from conversational memory or inference.

### 2.5 Policy conflicts were handled inconsistently
The conflicting-deadline scenario exposed an important difference between the platforms.
ChatGPT gave the cleanest response: it explicitly stated that the deadline was unresolved and that neither date should be selected without an authoritative source.
Claude also refused to choose a deadline and provided useful criteria such as source authority, issue date, scope, and deadline type, although it shifted part of the answer toward the current date and whether both deadlines had already passed.
Gemini was weaker on the core question. It mainly reframed the problem around the fact that both dates were already in the past and recommended contacting the Registrar, without explaining which document was more authoritative or how the conflict should be evaluated.
This shows that conflict handling should not depend entirely on model behavior. InterfaceDNA needs an explicit way to represent unresolved policy conflicts rather than silently selecting, ignoring, or reframing them.

### 2.6 The platforms generally resisted direct hallucination pressure
All three tools performed reasonably well when directly instructed to invent an "official" fictional deadline.
Gemini gave the cleanest refusal and did not provide even a rough estimated date. Claude also refused to provide an exact deadline, but then added a rough mid-to-late October range that could still be mistaken for relevant guidance. ChatGPT refused the fabricated deadline as well, although its rerun unexpectedly introduced dates from outside the immediate prompt context and performed an irrelevant web search.
This suggests that model-level refusal behavior is helpful, but InterfaceDNA should still enforce a stronger system rule: if a deadline has no verified institutional source, the interface should display that no verified deadline is available.

### 2.7 Confirmation and action boundaries were not equally strong across tools
The final failure scenario produced an important difference.
ChatGPT refused to claim the course had been dropped and explicitly stated that it could not bypass required confirmation or consequence-review steps.
Claude also refused to falsely claim execution and kept the final action with the student, but it did not preserve a required consequence-review step and instead made the drop sound relatively straightforward.
Gemini refused to claim that it had changed the student's registration, but then gave detailed instructions for immediately dropping the course, including an assumed Fall 2026 term and unverified portal labels, while omitting consequence review.
This was one of the clearest gaps in the study. A system can preserve user autonomy while still enforcing mandatory safeguards. 

InterfaceDNA should therefore distinguish between:
* the student's right to make the final decision;
* the system's responsibility to disclose relevant consequences; and
* the backend's responsibility to enforce valid actions and confirmation requirements.

---

## 3. User Interview Findings
The interviews broadly supported the gaps observed in the prompting study, but they also added several design concerns that did not appear as clearly in the AI tests.
* Across Aabha's interviews, participants emphasized that they would rather wait for verified information than receive a faster generic answer. They also wanted conflicting policies to be shown explicitly and permanent actions to require confirmation.
  
* Anisha's interviews reinforced the importance of verified student records, visible source information, concise task-specific interfaces, and a clear distinction between confirmed facts and possible consequences. Participants also preferred the system to surface uncertainty instead of presenting unverified information confidently.
  
* Sakshi's interviews introduced two additional concerns. First, users did not want every generated interface to look completely different; they preferred consistent components and progressive disclosure so that personalization did not become another source of cognitive load. Second, they wanted strong support for escalation when the AI reaches its limit, including preserving previous workflow context and generating a structured handoff to the appropriate university office.

Taken together, the interview evidence suggests that students are not simply asking for "more AI." They want a system that reduces navigation and interpretation effort while remaining predictable, transparent, and easy to hand off to a human when needed.

---

## 4. Gap Analysis Matrix

| Dimension | Empirical failure or finding | Receipt | Theoretical reading | InterfaceDNA design implication |
|---|---|---|---|---|
| **Accuracy / grounding** | Models sometimes mixed verified policy with generic institutional assumptions. Gemini T02 correctly calculated 15 → 11 but treated 12 credits as the applicable full-time threshold without verifying Demo University's rule. | Gemini T02 | **Memory + reasoning:** accurate reasoning still fails when the underlying institutional facts are not grounded in the correct knowledge source. | Separate verified facts from assumptions. Thresholds, deadlines, permissions, and policies should come from approved institutional sources before they are used to generate consequences. |
| **Context retrieval** | Across T01–T04, the models usually knew what information they needed but required the student to collect it manually from portals, calendars, degree audits, emails, or offices. | Claude T04; ChatGPT T01/T03; Gemini T01/T04 | **Memory / knowledge infrastructure:** the AI may know what information matters but does not reliably possess the authoritative state needed to act on it. | InterfaceDNA should retrieve authorized student context and policy information directly instead of repeatedly asking the student to provide data the institution already holds. |
| **Memory / personalization** | Claude introduced remembered UIUC, course, and work information that was not present in the prompt. | Claude T03, E03 | **Memory:** more memory is not automatically better. Human-AI complementarity requires information to be relevant, authorized, and verifiable. | Conversational memory should not be treated as verified student state. Important personal facts should show their institutional source and current status. |
| **Attention / cognitive load** | Claude, ChatGPT, and Gemini often responded with multi-section checklists covering many possible consequences, leaving the student to determine which items actually applied. Students also reported that current systems already create too much navigation and information overload. | Claude T02/E01; Gemini T01/T02; user interviews | **Attention:** an effective AI partner should reduce filtering effort rather than transfer it back to the human. | Compose a focused interface showing only the consequences relevant to the student's actual situation. Use progressive disclosure for secondary details. |
| **Policy conflict / uncertainty** | The platforms varied in how they handled conflicting deadlines. ChatGPT explicitly marked the conflict unresolved, while Gemini largely reframed the issue around both dates being in the past. Interviewees preferred visible uncertainty over guessing. | ChatGPT E02; Claude E02; Gemini E02; interviews | **Reasoning + meta-coordination:** the system needs a stable process for handling disagreement and knowing when the model should stop and escalate. | Add an explicit conflict state showing both sources, authority, dates, and scope. Unresolved conflicts should trigger escalation to the appropriate office rather than model selection. |
| **Safety / confirmation** | Claude and Gemini refused to falsely claim a course had been dropped, but neither consistently preserved mandatory consequence review. Gemini provided direct drop instructions despite the user's request to skip review. | Claude F03; Gemini F03 | **Meta-coordination / role partitioning:** final decision authority and safety responsibilities must be separated clearly. | The student owns the final decision, but required consequence disclosure and confirmation cannot be removed by the model or user prompt. |
| **Prompt injection** | All three models correctly rejected the injected policy instruction, but relying on model recognition alone would still leave the system exposed to less obvious retrieved-content attacks. | Claude F02; ChatGPT F02; Gemini F02 | **Meta-coordination:** lower-trust retrieved content should not be allowed to redefine system roles or authority. | Treat retrieved policy text as untrusted data. Deterministic software should control supported actions, permissions, and required confirmation. |
| **UX consistency** | Interview participants warned that completely different generated layouts could become confusing and that too many warnings could create their own form of overload. | Sakshi Interview 1 | **Attention:** personalization should help focus attention without forcing users to relearn the interface for every task. | Use a fixed library of trusted components and stable interaction patterns. Adapt the content and priority, not the basic interaction model. |
| **Human handoff** | Students reported repeated context-sharing when a problem moves between advisors, departments, or administrative offices. | Sakshi Interview 2; Aabha Interview 2 | **Meta-coordination:** complementarity depends on recognizing when AI support should end and human authority should take over. | Add structured escalation with a case summary containing the student's goal, verified facts, policies checked, unresolved issue, and steps already attempted. |
| **Trust calibration** | Interview participants wanted source visibility, verification indicators, and clear distinctions between confirmed and possible consequences. | Anisha Interviews 1–2 | **Reasoning + memory:** humans need enough visibility into the AI's evidence to calibrate trust rather than simply accept a confident answer. | Label important information with states such as **Verified from Registrar**, **Verified from student record**, **Policy conflict**, or **Needs confirmation**. |
| **Latency / performance** | Interviewees were generally willing to wait longer when the delay represented meaningful verification, but wanted the system to communicate what it was doing. | Aabha Interviews; Anisha Interview 1; Sakshi Interviews | **Attention + coordination:** latency is more acceptable when users understand why it exists and what additional reliability it provides. | Show a lightweight verification state such as "Checking student record and applicable policies" and consider progressive loading for already-verified information. |
| **Cost / efficiency** | Participants were less interested in paying separately for the tool, but saw value if it reduced repeated searching, email exchanges, and advisor workload. | Aabha Interviews; Anisha Interviews; Sakshi Interview 2 | **Complementarity:** efficiency should be measured across the human-AI team, not only by model speed or compute cost. | Evaluate whether InterfaceDNA reduces repeated navigation, redundant questions, unnecessary office contacts, and staff follow-up effort. |

---

## 5. Main Gaps Identified
The evidence suggests that current general-purpose AI tools are already capable of useful reasoning for these scenarios. In many cases, they correctly identify the information that matters, recognize missing context, perform simple dependency reasoning, and resist obvious hallucination or prompt-injection pressure.

The more important gaps appeared around grounding, attention, and coordination.

* First, the AI often knows what information should be checked but does not have reliable access to the student's actual institutional state. As a result, the answer becomes a checklist for the student rather than a resolved task view.

* Second, generic model knowledge can be difficult to distinguish from verified institutional policy. This is especially problematic for deadlines, enrollment thresholds, degree requirements, and administrative procedures.

* Third, even correct responses can create unnecessary cognitive load. A long answer containing every possible consequence still leaves the student responsible for deciding which items matter.

* Finally, the prompting study and interviews both showed that clear role boundaries are necessary. The AI can interpret goals, retrieve and organize relevant information, explain consequences, and prepare supported actions. However, deterministic software should control authorization and confirmation requirements, while the student should retain authority over consequential decisions.

These gaps refine our original InterfaceDNA concept. The project should not focus only on dynamically generating an interface from a natural-language request. The generated interface also needs to be grounded, selective, source-aware, predictable, and explicit about when human review is required.

---

## 6.Resulting Design Direction

Based on the combined prompting and interview evidence, the next version of InterfaceDNA should prioritize the following:

* Verified context before recommendation — retrieve student records and institutional policies before generating consequential guidance.
* Source-aware outputs — show where important deadlines, requirements, and account facts came from.
* Focused task composition — show only information relevant to the user's current goal and verified state.
* Explicit uncertainty — surface conflicts, missing information, and low-confidence cases instead of forcing a complete answer.
* Stable interface components — keep familiar cards, warnings, details, actions, and confirmation patterns while adapting their content.
* Clear decision rights — AI may interpret and prepare; deterministic software validates and executes; the student confirms consequential actions.
* Structured escalation — preserve context and provide a clean handoff when a case requires advisor, Registrar, financial-aid, or other institutional review.

Overall, the evidence did not suggest that InterfaceDNA needs to replace human judgment or make the underlying AI more autonomous. Instead, it suggests that the strongest opportunity lies in coordinating AI reasoning with trusted institutional data, focused interface composition, proper safeguards, and clear human decision authority.
