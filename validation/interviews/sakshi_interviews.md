# Sakshi - User Interviews

## Interview 1

**Participant:** Participant 1

**Student type:** Student who prefers simple, low-clutter digital interfaces

**Date:** 2026-10-07

### Current experience
The participant said the main problem with university systems isn’t finding information but understanding it quickly. Student portals often use office jargon that students don’t fully understand, and that’s worst in stressful moments like registering, dealing with holds, meeting deadlines, or checking graduation progress. Even when the right information is there, it can feel too technical, too packed, or too hard to skim.

### Accuracy
The participant said accuracy is important, but the system should also explain important information in plain language.
For example, instead of only showing:
“Reduced Course Load authorization required”
the system should briefly explain what that means and why it matters.
They said a technically correct answer would still be unhelpful if the student cannot understand it.

### Reliability
The participant said reliability also means being predictable in how the interface behaves.
They would not want the layout to change dramatically every time they ask a similar question.
For example, if warnings appear in one place for one task and somewhere completely different for another task, it could make the system harder to learn.
They preferred some consistent interface patterns even if the content itself changes dynamically.

### Latency
The participant said they would rather see the interface appear quickly with partial verified information than wait for the entire result to load at once.
They suggested a staged experience where the system could first show basic confirmed information and then fill in additional policy details as they are retrieved.

### UX Friction
This participant focused strongly on visual and cognitive overload.
They said they would not want InterfaceDNA to generate a very different or complicated screen every time.

Their preference was for a small set of familiar components such as:
* summary card;
* warning card;
* required action;
* optional explanation;
* confirmation button.

They also said too many warnings could become ineffective because students may start ignoring them.

### Safety

The participant said safety information should be prioritized rather than showing every possible risk equally.
For example, if dropping a course definitely affects full-time status, that warning should be visually stronger than a minor or unlikely consequence.

They felt the system should distinguish:
critical;
important;
informational.

### Cost
The participant said they would not personally evaluate the system based on technical cost, but they would notice if the interface felt unnecessarily slow or complicated.
They felt that efficiency should include reducing mental effort, not only reducing the number of clicks.

### Suggested Improvement
The participant suggested using a progressive disclosure approach.

The first screen should show only the most important information, with optional controls such as:
* “Show details”
* “Why does this matter?”
* “View policy source”

This would let students choose how much explanation they need.

### Main Finding
The participant values clarity, consistency, and reduced cognitive overload, not simply personalization.

### 
Changed: We initially assumed that generating a highly customized interface for every goal would always improve usability. 
This interview suggests that too much variation could itself create confusion. InterfaceDNA should therefore generate task-specific content within a stable and familiar component structure.

---

**Participant:** Participant 2

**Student type:** Student who frequently communicates with academic advisors and support offices

**Date:** 2026-10-07

### Current experience
The participant said that many complicated university issues eventually require human help.
They explained that when a problem cannot be resolved through the portal, students often email an advisor and then have to explain the entire situation again from the beginning.
If the issue moves from one office to another, the student may repeat the same context several times.

### Accuracy
The participant said they would want InterfaceDNA to summarize the situation accurately before handing it to a staff member.

For example, if the system determines that a registration hold cannot be resolved automatically, it should generate a short summary containing:
* the student's goal;
* relevant account state;
* what has already been checked;
* unresolved issue;
* applicable policy;
* requested next action.

They felt this could reduce misunderstandings between students and university staff.

### Reliability
The participant said the system should preserve a history of what has already happened.
For example, if they already contacted the Registrar and were told to speak with their department, InterfaceDNA should remember that workflow state instead of sending them back to the Registrar again.
They described repeated or circular referrals as one of the most frustrating parts of current administrative processes.

### Latency
The participant said response time becomes less important once a task involves escalation to a human.
In that situation, they would rather have a complete and accurate case summary than a very fast answer.
They also said the system should clearly show when the process is waiting on a university office rather than making it seem like the AI is still processing.

### UX Friction
The participant's main frustration was handoff friction.

They said current systems often treat each interaction as separate:
* student checks portal;
* emails advisor;
* advisor redirects to Registrar;
* Registrar asks for more information;
* student repeats context.

They wanted InterfaceDNA to carry the relevant context forward across these steps.

### Safety
The participant said the AI should know when to stop trying to solve the issue and escalate it.

They felt the system should not continue generating more recommendations when:
* policies conflict;
* required approval is missing;
* the issue involves an exception;
* the student's record contains an unusual condition.

In those cases, they wanted the system to explicitly say:
“This requires human review.”

### Cost
The participant felt the strongest efficiency benefit might actually be for university staff.
If InterfaceDNA could send a structured case summary instead of an unorganized student email, advisors could understand the problem faster and spend less time asking basic follow-up questions.

### Suggested Improvement
The participant suggested adding a handoff mode.

When the AI cannot safely resolve a case, the system could generate a structured summary and route the student to the correct office.
The summary might include:
* student goal;
* relevant facts;
* policies checked;
* unresolved conflict;
* actions already attempted;
* reason for escalation.

### Main Finding
The participant values continuity and effective human handoff, not only automated answers.

### Assumption confirmed or changed
Changed and expanded: We originally focused on helping the student complete tasks inside the interface. 
This interview suggests that a strong system also needs to support unresolved cases by preserving context and coordinating the transition from AI assistance to human support.

---

## Combined Findings
These interviews introduced two different gaps that were not as prominent in the earlier interviews.
* Students do not necessarily want every generated screen to look completely different. They still want some consistency so the interface feels familiar and easy to use.
* Too much information at once can be overwhelming, even if it is personalized. Students preferred seeing the most important details first and having the option to expand for more explanation.
* Warnings should not all be treated the same. More serious consequences should stand out clearly from lower-priority information.
* Some university problems are too complex to be fully handled by AI and should be passed to a human advisor or office when needed.
* Students do not want to repeat the same information every time they are redirected to a different office.
* Keeping track of what has already been checked or attempted would make the overall process feel much smoother.
* A structured handoff from the AI to a human could reduce confusion for both the student and university staff.

## Design Implications
Based on these interviews, InterfaceDNA should:
* keep a consistent overall layout while still adapting the content to the student's goal;
* show the most important information first and allow students to open additional details only when needed;
* make high-risk warnings more noticeable than minor informational messages;
* recognize when a problem cannot be safely resolved by the AI alone;
* preserve important context and previous steps across the student's workflow;
* avoid sending students back to offices or steps they have already completed;
* provide a clear handoff summary when human support is required; and
* make the transition between AI assistance and university staff feel continuous rather than like starting the process again.
