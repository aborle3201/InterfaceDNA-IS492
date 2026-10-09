# Individual Validation Reflection: Sakshi Katolkar

**Team:** InterfaceDNA (Aabha Borle, Anisha Kango, Sakshi Katolkar)
**Tool I tested:** Claude Sonnet 5.5, all 10 scenarios (T01–T04, E01–E03, F01–F03)
**Evidence:** `/validation/transcripts/claude_outputs.md`, my screenshots, and my two interviews (P1, P2)

---

## What I assumed going in

I honestly thought Claude's memory would be a plus. If it already knows who I am and what I'm taking, I figured it would give better answers without me explaining everything again.

## What actually happened

It went the other way. In T03 (the graduation check), Claude said it "already knew" my courses and brought up my work commitments. None of that was in the prompt. It all came from old chats. In E03 it assumed a specific university and even pulled in a calendar tool, when the prompt never named a school.

The scary part is that it all sounded right. Nothing showed where it came from or if it was still true. If a student used this to decide whether to drop a class, a remembered fact would look exactly like an official record.

## How I connect it to the theory

This is the memory piece of the Gonzalez et al. complementarity idea. A human and AI team only works better than either alone if the AI has the right information, not just more of it. Claude had more information, but nobody could check it, so the team ended up worse off. For our design, that points to the knowledge infrastructure principle: a student's facts should come from the real institutional record, with the source shown, and not from chat memory.

## What the interviews added

Both people I interviewed (P1, P2) said they don't want every screen to look different. They liked familiar pieces and extra detail only when they ask for it. They also wanted an easy way to hand things off to a real office when the AI can't help. I had assumed personalization meant a fresh interface every time, but they saw that as more work to figure out.

## What this means for our design

- Student facts come only from the verified record, with the source labeled.
- The content changes with the task, but the building blocks stay the same.
- If something can't be verified, the system says "I'm not sure" instead of guessing.

## Limits

I ran each prompt once, in separate chats, with memory left on. That's exactly why the memory problem showed up, and I noted it in my transcript header. My first attempt was invalid (wrong wording, one chat, memory and web search on), so I redid it. I didn't time the responses. And with only two interviews, this shows a direction, not proof.

---

## Class storyboard

Panel | What happens
1     | Student asks: "Am I on track to graduate?" No personal details in the question. 
2     | The AI answers with courses and commitments from old chats. It sounds confident, no source. 
3     | The student can't tell what's current or official, so they end up checking the portal anyway. 
4     | With InterfaceDNA, the facts come from the student record and each one is labeled "Verified from student record." 
5     | Anything unclear is flagged "Not sure, check with your advisor," and nothing happens until the student confirms. 