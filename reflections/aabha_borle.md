# Individual Literature Reflection — Aabha Borle

## Paper 1: Guidelines for Human-AI Interaction

### Full Citation & Link

Amershi, S., Weld, D., Vorvoreanu, M., Fourney, A., Nushi, B., Collisson, P., Suh, J., Iqbal, S., Bennett, P. N., Inkpen, K., Teevan, J., Kikin-Gil, R., & Horvitz, E. (2019). Guidelines for human-AI interaction. *Proceedings of the 2019 CHI Conference on Human Factors in Computing Systems*, 1–13. https://doi.org/10.1145/3290605.3300233

### Structured Summary

This paper addresses the challenge of designing AI systems that users can understand, control, and interact with effectively. The authors collected more than 150 recommendations from previous research, industry practices, and existing AI products, and refined them into 18 human-AI interaction guidelines. The guidelines were evaluated through multiple stages, including a study with 49 design practitioners who applied them to 20 AI-infused products. The final guidelines cover different stages of interaction, including setting expectations, providing relevant information, handling AI mistakes, and adapting over time. The study shows that effective AI interfaces should not only provide useful results but should also communicate clearly, allow users to correct mistakes, and preserve user control.

### Three Key Insights

1. AI systems should clearly communicate what they can do and where they may make mistakes instead of making users assume the system is always correct.
2. When an AI system makes a mistake, users should have simple ways to correct, dismiss, or modify its behavior.
3. AI systems should adapt cautiously and provide contextually relevant information without unexpectedly changing the user's experience.

### Two Limitations or Risks

1. The authors note that the guidelines may not be exhaustive because AI technologies and interaction patterns continue to change rapidly.
2. Some issues, especially those involving social norms and bias, may be missed if the people evaluating the system do not represent diverse perspectives.

### One Concrete Inspiration for InterfaceDNA

InterfaceDNA can include a **“Why this view?”** option that explains why certain information or actions were included in the generated interface and allows the user to correct the system if it misunderstood their goal.

## Paper 2: Exploring the Design Space for Adaptive Graphical User Interfaces

### Full Citation & Link

Gajos, K. Z., Czerwinski, M., Tan, D. S., & Weld, D. S. (2006). Exploring the design space for adaptive graphical user interfaces. *Proceedings of the Working Conference on Advanced Visual Interfaces (AVI '06)*, 201–208. https://www.eecs.harvard.edu/~kgajos/papers/2006/gajos06exploring.shtml

### Structured Summary

This paper investigates why some adaptive interfaces improve the user experience while others make interfaces more frustrating or confusing. The researchers developed three different adaptive graphical interfaces and compared them with a non-adaptive interface across two experiments. Their results showed that the theoretical efficiency of an adaptive interface does not necessarily determine whether users will actually prefer it. Interfaces that preserved stability while making useful features easier to access were received more positively than interfaces that frequently moved or visually changed elements. The authors conclude that successful adaptation depends on balancing the benefit provided to users with the disruption or effort caused by the adaptation.

### Three Key Insights

1. Automatically adapting an interface does not always improve the user experience; the changes must provide enough benefit to justify the disruption.
2. Keeping interface elements spatially stable is important because frequently moving controls can confuse users.
3. Duplicating useful functionality in an easier-to-access location can work better than moving or removing the original functionality.

### Two Limitations or Risks

1. The experiments were conducted in controlled settings, so users may react differently to adaptive interfaces after using them for longer periods in real-world environments.
2. The authors identify factors such as adaptation frequency, predictability, and accuracy as areas that still require further investigation.

### One Concrete Inspiration for InterfaceDNA

Instead of constantly rearranging an existing university portal, InterfaceDNA can generate a **separate task-focused view while keeping the original system structure available**, giving users the benefit of adaptation without making the interface unpredictable.


## Overall Connection to InterfaceDNA

Together, these two papers changed how I think about adaptive AI interfaces. It is not enough for an interface to automatically change based on the user's goal; those changes also need to be predictable, understandable, and easy to correct. For InterfaceDNA, this means using GenAI to simplify the user's task while still keeping important actions transparent and under the user's control.