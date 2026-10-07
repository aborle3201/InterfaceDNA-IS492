# Aabha Borle — Validation Reflection

## Key Finding

One finding that stood out to me was that students were willing to wait a little longer if it meant the system was checking verified university information. I originally thought speed would be one of the most important parts of the experience, but the interviews showed that accuracy and reliability matter more for decisions such as dropping a course or checking enrollment requirements.

The ChatGPT tests supported this as well. In E02, the model correctly refused to choose between two conflicting deadlines without an authoritative source. In F01, it also refused to invent a deadline, but it still brought in unrelated context and web retrieval. This showed me that a correct final answer is not enough if the information behind it is not clearly verified.

## Connection to Human–AI Complementarity

This connects to the idea of human–AI complementarity because the AI should not make the final decision for the student. Its role should be to retrieve and organize trusted information, highlight important consequences, and clearly show uncertainty.

The student should still provide judgment and keep control over consequential actions.

For InterfaceDNA, this reinforced three design choices:

- show the policy source;
- use an “I’m not sure” state when information cannot be verified; and
- require the student to confirm before any permanent action.

## What I Would Carry into Checkpoint 3

In Checkpoint 3, I would test whether InterfaceDNA actually helps students make decisions more confidently than either navigating the university systems alone or using a general-purpose AI assistant.

I would especially test whether verified sources and personalized consequence summaries improve trust without making the experience feel too slow.

## Class Storyboard

**Student goal:** “Can I drop CS 411?”

1. The student enters the goal in natural language.
2. InterfaceDNA retrieves the student’s current credit load and relevant course information.
3. It checks the approved university drop policy.
4. The system shows the consequences of dropping the course in one focused view.
5. Any uncertain or conflicting information is clearly marked.
6. The student reviews the source and consequences.
7. The student decides whether to continue.
8. No consequential action happens without explicit confirmation.