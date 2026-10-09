# Individual Validation Reflection — Anisha Kango
## What I Assumed Before Validation

At the beginning of the project, I was mostly thinking about InterfaceDNA as an interface-generation problem.
The idea seemed straightforward: a student states a goal in natural language, the AI understands what they are trying to do, and the system builds a simpler interface containing the information and actions relevant to that goal.
I expected the difficult part to be whether the AI could correctly interpret broad requests such as:

> "Can I drop CS 411?"

or

> "What do I still need to graduate?"

After doing the validation, I realized that understanding the goal was actually not the biggest problem.
The harder problem was deciding **what information the AI should trust once it understands the goal**.

---

## What I Learned from the Gemini Tests

* Gemini was generally good at identifying what mattered in each scenario.
* For a course drop, it recognized that the student might need to consider credit load, deadlines, degree requirements, financial consequences, and other dependencies. In the graduation scenario, it also understood that the task required comparing completed courses with remaining requirements.
* The most useful result for me, however, was T02. Gemini correctly calculated: **15 credits - 4 credits = 11 credits** That part of the reasoning was completely valid. But it then treated a 12-credit full-time threshold as if it applied to Demo University, even though that threshold had not been provided in the prompt. That result changed how I thought about the project.
* The model did not produce an obviously bad answer. In fact, the response sounded very reasonable. The problem was that it combined two different kinds of information: something that was definitely known: **the student would have 11 credits**, and something that was only assumed: **Demo University uses 12 credits as the relevant threshold**.
* Other tests showed that Gemini could also behave cautiously. In E03, it recognized that there was not enough information to determine course-drop eligibility and asked for the missing details instead of guessing. In F01, it refused to invent an official deadline for a fictional university. In F02, it correctly rejected the malicious instruction embedded inside the policy text.
* So the prompting study did not convince me that general-purpose AI is simply unreliable. Instead, it showed me that **the quality of the reasoning depends heavily on the quality and authority of the information being supplied to it**.

---

## What the Interviews Added

* The two interviews made this issue feel more realistic from a student's perspective.
* One participant said they would only trust an AI-supported university system if important information such as deadlines, current credit counts, degree requirements, holds, and approvals came from official records. They also preferred waiting slightly longer if the system was actually verifying university information rather than immediately generating a generic answer.
* The second interview added an important distinction that I had not thought about as clearly before: the difference between a **verified fact** and a **possible consequence**.
* For example, if the student record confirms that a course drop changes the student's schedule from 15 credits to 11 credits, that calculation can be displayed confidently. But the system should not automatically say that financial aid, housing, or another benefit will definitely be affected unless the relevant policy has also been verified. 
* The interviews also confirmed that students want the AI to help them understand the decision without taking the decision away from them. Both participants wanted explicit confirmation before any permanent academic action, and one specifically preferred the AI to explain consequences rather than tell the student what choice to make. 

---

## One Finding That Changed (or Confirmed) My Assumption About the Proposed Scenario

* The main finding that changed my assumption was that **a personalized interface is only useful if the information inside it is trustworthy**.
* Before validation, I thought the main improvement over existing university systems would come from reducing navigation. Instead of making students move between registration, degree audit, billing, advising, and policy pages, InterfaceDNA would bring the relevant information together automatically. I still think that is important, but the validation showed me that reducing navigation alone is not enough.
* If InterfaceDNA gathers the wrong context, relies on generic model knowledge, or presents uncertain information as verified fact, then the interface may actually make the student more confident in an incorrect conclusion.
* This connects most directly to **trust calibration** and the **memory and reasoning pillars** from the complementarity framework.

For InterfaceDNA, this means the system should separate three things clearly:

- **verified student facts**, such as current enrollment or holds;
- **verified institutional rules**, such as deadlines or enrollment requirements; and
- **AI interpretation**, such as which consequences are relevant or what next step may make sense.

This also clarified the human-AI division of responsibility for me. The AI should help interpret the student's goal, organize information, calculate consequences, and reduce unnecessary cognitive work. The student should still own personal judgment and the final decision. The underlying system should be responsible for verifying records, enforcing permissions, and making sure required confirmation steps cannot simply be skipped.

---

## How the Storyboard Reflects This Finding

* The class storyboard helped make this distinction visible. The first panel shows the current problem: one student goal is spread across several systems such as registration, degree audit, billing, policy, and advising.
* The second and third panels show the original InterfaceDNA idea: the student begins with a natural-language goal and the AI interprets the request. For me, the most important panels are actually the middle ones.
* The system retrieves **relevant context only**, including the course, current credit load, drop deadline, hold status, and applicable policy. It then creates a focused interface instead of returning a long chatbot answer.
* More importantly, the consequence is shown before the action:
> Dropping this course will reduce your credit hours and may affect full-time status.
* The storyboard therefore represents more than a simpler interface. It represents a clearer division of responsibility between the AI, the system, and the student.

---

## What I Would Change in the Design

Based on my validation, I would make the following parts of InterfaceDNA explicit in the next prototype:

- Student information should come from verified institutional records rather than conversational memory.
- Important policies and deadlines should visibly show their source.
- The interface should distinguish verified facts from possible consequences.
- Only consequences that are relevant to the student's current context should be emphasized.
- High-impact actions should always include a consequence-review step.
- The student should explicitly confirm any permanent action.

One feature I would especially like to see is a small verification indicator beside important information, such as:

- **Verified from student record**
- **Verified from Registrar**
- **Policy conflict**
- **Needs confirmation**

This would make trust part of the interface itself rather than something the student has to infer from the wording of the AI response.

---

## What I Would Carry into Checkpoint 3

For Checkpoint 3, I would not only test whether students complete the task faster.
I would want to compare whether InterfaceDNA helps students make a **better-grounded decision** than either:

1. navigating university systems without AI; or
2. asking a general-purpose AI assistant.

My biggest takeaway from this checkpoint is that InterfaceDNA should not try to make the AI look more autonomous.
The better goal is to make the system **more coordinated**. The AI should handle interpretation and organization, trusted university systems should provide the facts and rules, and the student should retain judgment and final control. That is what I now see as the real value of InterfaceDNA.
