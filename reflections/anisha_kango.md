# Individual Literature Reflection — Anisha Kango

## Paper 1: WebVoyager: Building an end-to-end web agent with large multimodal models. 

### Full Citation & Link

He, H., Yao, W., Ma, K., Yu, W., Dai, Y., Zhang, H., Lan, Z., & Yu, D. (2024). WebVoyager: Building an end-to-end web agent with large multimodal models. Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics, 6864–6890.

Paper link: https://aclanthology.org/2024.acl-long.371/

### Structured Summary

This paper addresses the challenge of building AI agents that can complete tasks on real-world websites rather than only working in simplified or simulated web environments. The authors introduce WebVoyager, a multimodal web agent that uses both webpage screenshots and textual information about interactive elements to understand a website and decide what action to take. The system was evaluated using 643 tasks across 15 real websites, including Amazon, GitHub, Google Flights, Booking, and Coursera. WebVoyager achieved a 59.1% task success rate, outperforming both a text-only version of the system and the GPT-4 All Tools baseline. The authors also found that failures commonly came from getting stuck during navigation, difficulty identifying visual elements correctly, hallucination, and problems following complex instructions, showing that real-world web interaction still requires stronger grounding and reliability.

### Three Key Insights

1. Combining visual information with textual webpage information is more effective than relying only on webpage text, especially for interfaces containing calendars, buttons, menus, and other visual elements.
2. Completing tasks on real websites requires more than understanding the user's request; the agent must continuously observe changes in the interface and decide the correct next action.
3. Even capable multimodal agents can make errors such as selecting the wrong element, repeating unsuccessful actions, or producing a partially correct answer, so important actions should not be executed without validation.

### Two Limitations or Risks

1. WebVoyager does not support every interaction that a human user can perform, such as drag-and-drop, and its file understanding is limited mainly to basic formats such as text and PDFs.
2. Autonomous web interaction introduces privacy and security risks because an agent could accidentally enter confidential information on a public website, access unsafe content, or perform unintended actions.
   
### One Concrete Inspiration for InterfaceDNA

InterfaceDNA can use a multimodal grounding layer that considers both the visible interface and the available webpage actions before generating a task-specific view. Instead of letting the AI invent buttons or actions, the generated interface would only expose actions that have been verified to exist in the underlying system.

## Paper 2: Mind2Web: Towards a Generalist Agent for the Web

### Full Citation & Link

Deng, X., Gu, Y., Zheng, B., Chen, S., Stevens, S., Wang, B., Sun, H., & Su, Y. (2023). Mind2Web: Towards a generalist agent for the web. Advances in Neural Information Processing Systems (NeurIPS 2023).

Paper link: https://proceedings.neurips.cc/paper_files/paper/2023/hash/5950bf290a1570ea401bf98882128160-Abstract-Datasets_and_Benchmarks.html

### Structured Summary

This paper focuses on developing web agents that can understand a high-level user goal and complete tasks across many different real-world websites. The authors introduce Mind2Web, a dataset containing 2,350 tasks across 137 websites and 31 domains, with human-demonstrated sequences showing the actions required to complete each task. They also develop MindAct, which first filters the large number of webpage elements using a smaller language model and then uses an LLM to select the relevant element and action. The experiments show that language models can generalize to websites and even domains that were not seen during training, although performance is still far from that required for a truly general-purpose web agent. The study demonstrates that translating natural-language goals into structured web actions is possible, while also showing that real websites remain noisy, dynamic, and difficult to navigate reliably.

### Three Key Insights

1. Users can describe a high-level goal rather than providing detailed step-by-step instructions, and an AI system can attempt to translate that goal into a sequence of website actions.
2. Real webpages contain a very large amount of irrelevant information, so identifying and filtering the information related to the current task is an important part of effective AI interaction.
3. Human involvement remains important because users may need to change their requirements during a task or confirm an action when the system is uncertain about their intent.

### Two Limitations or Risks

1. The Mind2Web dataset mainly contains English-language websites commonly used in the United States, and its annotators were recruited through Amazon Mechanical Turk, which may not represent users with different languages, accessibility needs, or levels of web experience.
2. The MindAct approach primarily uses textual webpage information and evaluates actions using cached website environments. This means it does not fully capture visual information or all of the dynamic changes that occur when interacting with live websites.

### One Concrete Inspiration for InterfaceDNA

InterfaceDNA can first create a goal-to-action plan before generating an interface. For example, if a student says, “I want to drop this course,” the system can identify the relevant information and valid actions first, then build the temporary interface around those verified steps instead of simply generating a page from the prompt.

## Paper 3: SUPPLE: Automatically Generating User Interfaces

### Full Citation & Link
Gajos, K., & Weld, D. S. (2004). SUPPLE: Automatically generating user interfaces. Proceedings of the 9th International Conference on Intelligent User Interfaces (IUI '04), 93–100.

Paper link: https://www.eecs.harvard.edu/~kgajos/papers/2004/gajos04supple.shtml

### Structured Summary
This paper explores how user interfaces can be automatically generated instead of manually designing a fixed interface for every device and user. The authors introduce SUPPLE, a system that treats interface generation as an optimization problem and selects interface components and layouts that satisfy device constraints while minimizing the estimated effort required from the user. The system can also use previous user interaction traces to generate different interfaces based on how an individual typically uses an application. SUPPLE was demonstrated using applications such as a classroom control system and an FTP client and was evaluated for rendering speed, adaptation across devices, and comparison with interfaces designed by human participants. The results show that the same application functionality can be presented differently depending on device characteristics and expected usage, providing an early foundation for adaptive and automatically generated interfaces.

### Three Key Insights
1. An interface does not have to be permanently tied to one layout; the same underlying functionality can be presented differently depending on the user's context and expected actions.
2. Interface generation works more reliably when the system chooses from known interface elements and constraints rather than creating completely unrestricted designs.
3. Personalization can be based on actual user behavior, but frequent changes to an interface can also become distracting, meaning adaptation should remain predictable and purposeful.

### Two Limitations or Risks
1. The initial evaluation was relatively small and used only two comparatively simple applications; the authors note that supporting complex applications such as Microsoft Word or Outlook would require more sophisticated models.
2. The system optimizes the interface using an estimated user-effort function, but interface quality involves several competing factors such as learnability, efficiency, error recovery, and user preference that cannot easily be represented by one optimization measure.

### One Concrete Inspiration for InterfaceDNA
InterfaceDNA can follow SUPPLE's idea of constrained interface generation by giving the GenAI model a predefined library of trusted components—such as status cards, warnings, forms, progress indicators, and action buttons—and allowing the model to decide which components are most useful for the user's current goal. This would allow the interface to adapt significantly without allowing the model to generate an uncontrolled or inconsistent webpage.


