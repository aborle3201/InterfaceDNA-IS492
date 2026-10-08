# Aabha — User Interviews

## Interview 1

**Participant 3:**
**Student type:** International student
**Date:** 2026-10-06

### Current experience

Participant 3 said university tasks like dropping a course or checking graduation requirements can be frustrating because the information is spread across the student portal, academic calendar, department websites, and advising offices.

### Accuracy

He said deadlines, credit count, degree requirements, and graduation impact would all need to be correct before he would trust an AI assistant.

### Reliability

If two policies conflict, he would want the system to show both sources, clearly say there is a conflict, and direct him to the right university office instead of choosing one on its own.

### Latency

He would be comfortable waiting around 10-20 seconds if the system was using that time to verify official university information.

### UX Friction

His biggest frustration is having to open several university websites and repeatedly provide information the university already has, such as his major, credits, and completed courses.

### Safety

He said the AI should never drop a class, change registration, or submit anything permanent without first showing the consequences and getting explicit confirmation.

### Cost

He would use the system if it were provided by the university. He would be less likely to pay for it separately unless it offered much more than existing university tools.

### Suggested improvement

He suggested showing a short summary of the important consequences before an action instead of giving a long explanation.

### Main finding

Participant 3 values **verified sources, concise consequence summaries, and less navigation across university systems**.

### Assumption confirmed or changed

**Confirmed:** Students would benefit from one task-specific interface that combines their student information with verified university policies.

---

## Interview 2

**Participant 4:** 
**Student type:** International student
**Date:** 2026-10-06

### Current experience

Participant 4 said academic decisions can also affect immigration status. For something like dropping a course, he may need to check with an advisor, the registrar, and the international student office before taking action.

### Accuracy

He said the system would need to correctly identify his current credit load, minimum enrollment requirements, deadlines, and any required approvals.

### Reliability

If the system is unsure or finds conflicting policies, he would rather have it stop and say that it is uncertain than guess. It should then direct him to the appropriate university office.

### Latency

He would be willing to wait around 20-30 seconds if the additional time helped verify the correct academic and international-student policies.

### UX Friction

His biggest frustration is having to confirm the same decision with several offices. A course drop may be academically allowed but still affect enrollment or immigration requirements.

### Safety

He said the AI should never change his enrollment without explicit confirmation. It should also clearly warn him when an action could affect full-time enrollment or immigration status.

### Cost

He would prefer the university to provide the system. He might consider paying a small amount if it were officially supported and reliably handled both academic and international-student requirements.

### Suggested improvement

He suggested showing a clear warning whenever an action could affect visa or enrollment status, along with the office the student should contact.

### Main finding

For Participant 4, **personalized consequence checking and escalation to the correct authority** are especially important.

### Assumption confirmed or changed

**Confirmed and refined:** InterfaceDNA needs verified student context rather than generic advice, especially when enrollment or authorization requirements may change the consequences of an action.

---

## Combined Findings

Both interviews supported the main InterfaceDNA idea.

- Students care more about **verified information than instant answers**.
- They want the system to use their actual student context instead of giving generic advice.
- Conflicting information should be shown clearly rather than silently resolved.
- Important actions should always require confirmation.
- Students want fewer portals, fewer repeated checks, and shorter consequence summaries.
- Both participants preferred the system to be officially supported by the university.

## Design Implications

Based on these interviews, InterfaceDNA should:

- use verified student records and official university sources;
- show conflicts and uncertainty clearly;
- give concise consequence summaries;
- warn students about high-impact enrollment changes;
- direct students to the correct office when human review is needed; and
- require explicit confirmation before any permanent action.