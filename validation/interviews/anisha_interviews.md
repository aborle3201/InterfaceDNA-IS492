# Anisha — User Interviews

## Interview 1

**Participant:** Participant 5

**Student type:** International student 

**Date:** 2026-10-07

### Current experience
The participant said university systems work fine for simple tasks but get hard when one decision depends on several things. Dropping a class, for example, can mean checking the deadline, their current credit load, degree requirements, money effects, and sometimes getting approval from an advisor or another office. The most frustrating part is that this information is almost never in one place. They might have to jump between the student portal, the academic calendar, department pages, the degree audit, and their email before they feel sure enough to act.

### Accuracy
The participant said they would only trust an AI-supported university system if the important information was clearly based on official university records.

They specifically mentioned that the following information should never be guessed:
* course-drop and registration deadlines;
* current credit count;
* degree and graduation requirements;
* registration holds;
* financial consequences; and
* whether an action requires approval.

They also said it would be helpful if the interface showed where important information came from, such as the Registrar, student record, degree audit, or department policy.

### Reliability
The participant said that inconsistent answers would quickly reduce their trust in the system. If they asked the same question twice using the same information, they would expect the result to remain consistent.
If two university policies conflict, they would prefer InterfaceDNA to show both sources and clearly state that the information cannot yet be resolved. They felt the system should then direct the student to the correct office rather than choosing one policy without enough evidence.

### Latency
The participant said they would be comfortable waiting approximately 10–20 seconds if the system was using that time to retrieve official university information and personalize the response.
They preferred a slightly slower but verified answer over an immediate response that was based only on generic knowledge.

### UX Friction
The participant said the biggest advantage of InterfaceDNA would be reducing unnecessary navigation.
They described current university systems as fragmented because students often need to search several pages just to answer one question. They also disliked repeatedly entering information that the university already has, such as their major, credit load, completed courses, or registration status.
They preferred a task-specific interface that shows only the most relevant information rather than a long chatbot response.

For example, for a course-drop request, they would want to immediately see:
* current credits;
* credits after dropping;
* relevant deadline;
* important consequences;
* required approval; and
* next action.

### Safety
The participant said permanent academic actions should always require explicit confirmation.

They specifically said the AI should not automatically:
* drop a course;
* register for a course;
* submit a petition;
* make a payment; or
* change another important student record.

The participant preferred the AI to prepare the information and explain consequences, while the student remains responsible for the final decision.

### Cost
The participant said they would be more likely to use InterfaceDNA if it were integrated into the university's existing digital services.
They said they would probably not pay separately for the system unless it offered a major improvement over current student tools, such as significantly reducing the amount of time spent searching, emailing different offices, or interpreting policies.

### Suggested improvement
The participant suggested adding a simple “Why does this matter?” option next to important warnings.
This would allow the main interface to stay concise while still giving students access to additional explanation when needed.

### Main finding
The participant values verified information, reduced navigation, clear source visibility, and a concise task-specific interface.

### Assumption confirmed or changed
Confirmed and refined: The interview supported the assumption that students would benefit from an interface that combines student-specific information with official university policies. It also suggested that provenance and source visibility should be treated as important trust features rather than optional details.

---

## Interview 2

**Participant:** Participant 6

**Student type:** Graduate student

**Date:** 2026-10-07

### Current experience
The participant said that many academic tasks are difficult because the student has to understand both the university process and the consequences of the decision.
For example, if a student wants to drop a course, it may not be enough to know whether the portal allows the drop. The student may also need to understand whether the course is required for graduation, whether dropping changes full-time enrollment status, whether another course depends on it as a prerequisite, and whether approval is needed.
They said students often have to interpret these dependencies themselves, even though most of the relevant data already exists somewhere in the university system.

### Accuracy
The participant said InterfaceDNA would need to correctly distinguish between facts that are definitely known and consequences that are only possible.
For example, if the system knows that a student will move from 15 credits to 11 credits, it can show that calculation confidently. However, it should not say that financial aid, housing, or another benefit will definitely be affected unless the applicable policy has actually been verified.
They said this distinction would make the system feel more trustworthy.

### Latency
The participant said the system should be comfortable saying “I cannot verify this” when information is missing or conflicting.

They felt that uncertainty should be visible rather than hidden.

If a deadline or policy cannot be confirmed, they would prefer the interface to:
 * identify the uncertainty;
 * show the available sources;
 * avoid presenting an unverified answer as fact; and
 * direct the student to the correct university office.

They said this would be preferable to a confident answer that might later turn out to be wrong.

### UX Friction
The participant liked the idea that InterfaceDNA could generate different views depending on the student's goal.
They said current chatbots often provide similar long-form answers regardless of the task, while university tasks require different kinds of information.

For example:
* a course drop should emphasize deadlines, credit impact, and consequences;
* a registration hold should emphasize the hold type, responsible office, and resolution steps;
* a graduation check should emphasize completed requirements, missing requirements, and prerequisite dependencies.

They felt this task-specific structure would be easier to understand than a long conversational response.

### Safety
The participant strongly preferred the student to retain control over consequential decisions.

They said the system should be allowed to:
* retrieve information;
* calculate consequences;
* explain policies;
* identify dependencies; and
* prepare an action.

However, it should not make the final decision on the student's behalf.
For example, they preferred:
“Dropping this course will leave you with 11 credits and may affect your enrollment status.”
instead of:
“You should not drop this course.”

They also said mandatory confirmation should not disappear simply because the user asks the AI to skip it.

### Cost
The participant said the system's value would come mainly from reducing repeated administrative work.
They felt InterfaceDNA could save time if it reduced the need to:
* search multiple university websites;
* contact several offices for the same issue;
* manually compare policies;
* repeatedly provide the same student information; and
* interpret complex university requirements independently.

They said this efficiency would make the system worthwhile even if it required more computation than a normal chatbot response.

### Suggested Improvement
The participant suggested adding a confidence or verification indicator for important information.
For example:
* Verified from Registrar
* Verified from student record
* Needs confirmation
* Policy conflict detected

They felt this would make it easier for students to understand how much they should trust each part of the generated interface.

### Main finding
The participant values clear uncertainty handling, personalized consequences, task-specific interface generation, and strong human decision rights.

### Assumption confirmed or changed
Confirmed and expanded: The interview supported the idea that InterfaceDNA should reduce the student's cognitive burden, but also showed that simply generating a personalized interface is not enough. 
The system must distinguish verified facts from uncertain information and clearly communicate when human review is required.

---

## Combined Findings
Both interviews strongly supported the core InterfaceDNA concept, while also highlighting several requirements that should be treated as essential rather than optional.

* Students prefer verified information over immediate generic answers.
* The system should use actual student records and applicable institutional policies instead of asking students to manually provide information the university already has.
* Important information should show its source or verification status.
* Conflicting policies should be surfaced clearly rather than silently resolved by the AI.
* Students prefer short, task-specific interfaces over long chatbot responses.
* The AI should distinguish between confirmed consequences and possible consequences.
* Permanent or high-impact actions should always require explicit student confirmation.
* Students are willing to accept slightly longer response times when the system is performing meaningful verification.
* Both participants preferred InterfaceDNA to be integrated with and officially supported by the university rather than functioning as an independent third-party assistant.

## Design Implications
Based on the two interviews, InterfaceDNA should:

* retrieve student-specific information from verified institutional records;
* ground deadlines, requirements, and permissions in official university sources;
* show provenance or verification status for important information;
* distinguish confirmed facts from possible consequences;
* explicitly display policy conflicts or uncertainty;
* generate different interface structures for different student goals;
* prioritize short consequence summaries with optional deeper explanations;
* escalate unresolved cases to the correct university office;
* show high-impact warnings prominently;
* preserve student decision rights; and
* require explicit confirmation before any permanent academic or administrative action.
