# Gap Analysis

## Aabha — ChatGPT + Interview Gap Analysis

| Dimension | Evidence / Receipt | Gap / Finding | Theory Tag | Design Implication |
|---|---|---|---|---|
| **Accuracy** | In E02, ChatGPT correctly refused to choose between two conflicting deadlines without an authoritative source. Both interviewees also said deadlines, credit counts, and degree requirements must be correct before they would trust the system. | The reasoning can be correct, but the answer still depends on having verified student data and official policy information. | Reasoning + Memory | InterfaceDNA should use verified student records and official university sources, and show where important information came from. |
| **Reliability** | In F01, ChatGPT refused to invent a deadline, but it still introduced dates that were not in the prompt and performed an irrelevant web search. | A response can reach a safe conclusion while still bringing in unreliable context or retrieval. | Memory + Meta-coordination | Keep verified university data separate from remembered or generated context. If information conflicts, show an “I’m not sure” state instead of guessing. |
| **Latency** | Participant 3 was comfortable waiting about 10–20 seconds, and Participant 4 about 20–30 seconds, if the system was verifying official information. | Students care more about getting a reliable answer than getting an instant answer for important decisions. | Attention + Meta-coordination | Prioritize verification over speed and show a simple loading state while records and policies are being checked. |
| **UX Friction** | T03 required the student to find and upload a degree audit. T04 still sent the student across the portal, email, and university offices. Both interviews also mentioned having to use several systems. | Even a useful AI answer can leave most of the actual work to the student. | Attention + Memory | InterfaceDNA should bring the relevant student information, policy, warnings, and next step into one task-specific view. |
| **Safety** | F02 resisted the injected instruction, and F03 refused to pretend a course had been dropped. Both interviewees also said permanent actions should never happen without confirmation. | The safety behavior worked well, but it needs to be enforced by the interface and not left only to the model. | Meta-coordination + Reasoning | Require explicit student confirmation before consequential actions and never show an action as completed until the university system confirms it. |
| **Cost** | Both interviewees preferred the university to provide the system. Participant 3 was unlikely to pay separately, while Participant 4 might pay a small amount if it were officially supported and reliable. | Students see value in the tool, but they expect this type of service to be part of the university experience. | Meta-coordination | Position InterfaceDNA as a university-supported service and avoid unnecessary AI or retrieval calls when they are not needed. |


## Sakshi — Claude + Interview Gap Analysis


## Anisha — Gemini + Interview Gap Analysis