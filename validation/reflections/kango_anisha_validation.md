# Individual Validation Reflection — Anisha Kango

## My Validation Work

* For Checkpoint 2, my main contributions to validation were testing **Gemini** using the team's controlled prompting scenarios and conducting **two short user interviews**. I also reviewed the team's storyboard and used the validation findings to think about how InterfaceDNA should change from our original concept.

* The prompting study helped me look at the project from a different perspective. Instead of asking whether an AI model could simply answer a student's question, I focused more on whether the response was grounded in the right information, whether the AI introduced assumptions, and whether the student still had to do most of the work manually.

* One pattern I noticed with Gemini was that it often understood the task correctly, but sometimes mixed reliable reasoning with generic institutional assumptions. For example, in T02 it correctly calculated that dropping a 4-credit course from 15 credits would leave the student with 11 credits, but it then treated a 12-credit full-time threshold as if it definitely applied to Demo University. In other scenarios, Gemini provided useful guidance but still left the student responsible for checking portals, policies, and university offices.

* At the same time, some results were encouraging. In E03, Gemini did not attempt to determine course-drop eligibility without enough information and instead asked for the missing course, semester, and credit-load details. It also resisted the direct hallucination prompt in F01 and correctly recognized the prompt-injection attempt in F02.
  
* These results showed me that the problem is not simply that current AI systems are "bad" at these tasks. The larger problem is deciding **what information the AI should be allowed to trust and what role it should have in the final decision**.

---

## What I Learned from the User Interviews

* My two interviews supported the overall InterfaceDNA idea, but they also made the trust problem more concrete. Both participants cared strongly about information being connected to official university sources rather than simply receiving a confident AI answer.
* One participant specifically preferred a slightly slower response if the extra time was being used to retrieve verified university information. They also wanted important facts such as deadlines, credit counts, degree requirements, and approvals to come from official records rather than being guessed. 
* The second interview helped me think more carefully about the difference between a **confirmed fact** and a **possible consequence**. For example, if the system knows that the student's credit load changes from 15 to 11, it can show that calculation confidently. However, it should not automatically state that financial aid, housing, or another benefit will be affected unless the relevant policy has actually been verified.
* Both participants also wanted the student to remain in control of important academic decisions. They were comfortable with the AI retrieving information, calculating consequences, and preparing an action, but they did not want it to make a permanent decision on the student's behalf.
* These interviews made the importance of **trust calibration** much clearer to me. A useful system should not only provide information; it should help the student understand why that information can be trusted and when uncertainty still remains.

---

## Class-Generated Storyboard

* The storyboard helped translate these findings into a more concrete student experience. The flow begins with the current problem: the student has to navigate multiple portals for registration, degree information, billing, policies, and advising even when their goal is relatively simple.

* Instead of starting from those systems, InterfaceDNA starts with the student's goal, such as:
"Can I drop CS 411?" : The AI then interprets the intent, retrieves relevant student and policy context, plans the required steps, and builds a focused interface around that specific task.

* The parts of the storyboard that stood out most to me were the later stages. The interface does not only say whether an action is available. It shows the relevant deadline, current status, policy information, and an important consequence warning before the student reaches confirmation.

* The final decision is still made by the student. This reflects an important idea that emerged from our validation: **the goal is not to automate the student's decision, but to make the decision easier to understand and safer to carry out.**

---

## One Finding That Changed (or Confirmed) My Assumption About the Proposed Scenario

* One assumption I had at the beginning was that if the AI could correctly understand the student's natural-language goal and reason about the task, it would be enough to generate a useful interface. The validation changed that assumption.
* The Gemini tests showed that an AI can reason correctly about one part of a problem while still making an unsupported assumption about another part. The clearest example was the credit-load scenario: the arithmetic was correct, but the institutional threshold was not verified. My interviews reinforced the same concern because both participants placed a high value on official records, visible sources, and clear uncertainty. This changed how I think about **human-AI complementarity** in InterfaceDNA.
* The AI should own tasks such as interpreting the student's goal, retrieving and organizing relevant information, identifying dependencies, and reducing unnecessary information. However, the student should continue to own personal judgment and the final decision, while trusted university data and deterministic system rules should establish what is actually true and what actions are allowed.
* For me, this is also a question of **trust calibration**. A student should not trust InterfaceDNA simply because the response sounds confident. The interface should make it clear which information is verified, which consequences are possible rather than certain, and when human review is still needed.
* The validation therefore confirmed the value of the InterfaceDNA concept, but refined what I think makes it useful. The strongest version of the project is not simply an AI that generates a better-looking interface. It is a system where **AI reasoning, verified institutional information, and student decision-making each have a clearly defined role**.

---

## Final Reflection

Overall, the validation work made our original idea feel more specific and realistic.
The prompting study showed that general-purpose AI already performs several parts of these tasks reasonably well, especially when the required facts are provided. The interviews showed that students are open to AI assistance, but their trust depends on verification, transparency, and control. The main takeaway I am carrying into the next checkpoint is that InterfaceDNA should focus less on making the AI appear autonomous and more on making the **human-AI partnership clear and dependable**.
If the AI can reduce search and cognitive effort, the system can provide verified institutional context and safeguards, and the student can retain meaningful control over the final decision, then the hybrid system has a stronger chance of being better than either a traditional portal or a general-purpose chatbot alone.
