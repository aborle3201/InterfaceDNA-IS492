# Individual Literature Reflection - Sakshi Katolkar

## Paper 1: Generative Interfaces for Language Models

### Full Citation & Link

Chen, J., Zhang, Y., Zhang, Y., Shao, Y., & Yang, D. (2026). Generative interfaces for language models. *Findings of the Association for Computational Linguistics: ACL 2026*, 1499–1519.

Paper link: https://aclanthology.org/2026.findings-acl.74/

### Structured Summary

This paper looks at whether large language models can do more than just give conversational answers and instead create interactive interfaces based on what the user is trying to do. The authors introduce a Generative Interface framework that turns a user query into a structured representation of interaction flows, interface states, and component behavior. From there, the system generates a working interface and improves it through several refinement steps using task-specific evaluation criteria. The researchers compare these generated interfaces with normal conversational interfaces across areas such as functionality, interactivity, and overall user experience. Their results show that users often preferred the generative interfaces, especially for structured or information-heavy tasks where better organization and interaction helped make the task easier to understand.

### Three Key Insights

1. A user does not always need another text response; some goals are better supported by a task-specific interactive interface.
2. Converting a natural-language request into a structured representation before generating the UI can make the resulting interface more controllable and consistent.
3. Iterative refinement is important because an interface can be evaluated and improved instead of relying only on a single generation attempt.

### Two Limitations or Risks

1. Generating a useful interface is difficult because the possible design space is very large, and the system has to correctly represent interaction flows, component behavior, and state changes.

2. The system depends on several LLM-driven stages, from understanding the user's requirements to generating and refining the interface. If an earlier stage misunderstands the request or produces incorrect logic, that error could carry into the final interface.

### One Concrete Inspiration for InterfaceDNA

InterfaceDNA can first convert the student's request into a structured task representation containing the goal, required information, warnings, available actions, and interface components before generating the final view. This would help keep generated interfaces predictable instead of allowing the model to freely design the entire experience.

## Paper 2: WorkArena: How Capable Are Web Agents at Solving Common Knowledge Work Tasks?

### Full Citation & Link

Drouin, A., Gasse, M., Caccia, M., Laradji, I. H., Del Verme, M., Marty, T., Vazquez, D., Chapados, N., & Lacoste, A. (2024). WorkArena: How capable are web agents at solving common knowledge work tasks? *Proceedings of the 41st International Conference on Machine Learning, 235*, 11642–11662.

Paper link: https://proceedings.mlr.press/v235/drouin24a.html

### Structured Summary

This paper studies how well LLM-based agents can perform everyday knowledge-work tasks inside complex enterprise software. The authors introduce WorkArena, a benchmark built around ServiceNow with 33 task types, along with BrowserGym, an environment for developing and evaluating web agents using different observations and actions. The experiments show that current agents can complete some tasks, but there is still a large gap before they can reliably automate realistic enterprise work. The paper also highlights how complex interfaces, multiple interaction steps, and varied task structures make these environments difficult for current agents. Overall, the findings show that web agents are promising, but still not dependable enough for full automation in enterprise settings.

### Three Key Insights

1. Tasks that seem simple to humans, such as filling out a form or navigating a menu, can still be difficult for AI when the interface is complex.
2. Enterprise systems contain many different interaction patterns, so successfully understanding the user's goal is only one part of completing the task.
3. Evaluation should check whether the final task was completed correctly rather than only whether the agent performed reasonable-looking actions.

### Two Limitations or Risks

1. WorkArena is mainly built around the ServiceNow platform, so its results may not fully represent every type of institutional or consumer system.
2. Current agents still perform poorly on some interface structures, showing that giving an AI unrestricted control over important actions could lead to errors.

### One Concrete Inspiration for InterfaceDNA

Rather than making an agent navigate every part of a complicated university portal, InterfaceDNA can retrieve the required state and actions first and then expose only the relevant controls in a focused interface. This could reduce the amount of unnecessary navigation and interaction the AI must perform.

## Paper 3: WebArena: A Realistic Web Environment for Building Autonomous Agents

### Full Citation & Link

Zhou, S., Xu, F. F., Zhu, H., Zhou, X., Lo, R., Sridhar, A., Cheng, X., Ou, T., Bisk, Y., Fried, D., Alon, U., & Neubig, G. (2024). WebArena: A realistic web environment for building autonomous agents. *The Twelfth International Conference on Learning Representations (ICLR 2024)*.

Paper link: https://proceedings.iclr.cc/paper_files/paper/2024/hash/4410c0711e9154a7a2d26f9b3816d1ef-Abstract-Conference.html

### Structured Summary

This paper introduces WebArena, a realistic and reproducible environment for testing AI agents on complex web tasks given through natural-language instructions. The benchmark includes fully functional websites from areas such as online shopping, discussion forums, software development, and content management, along with supporting tools and knowledge resources. The researchers created 812 long-horizon tasks and evaluated agents based on whether they actually completed the intended goal, rather than whether they followed one exact sequence of steps. The results showed a large gap between humans and AI agents, with the best GPT-4-based agent reaching only a 14.41% success rate compared with 78.24% for humans. Overall, the paper shows that current web agents still struggle with realistic multi-step tasks, especially when they need strong planning, active exploration, state tracking, and recovery from mistakes.

### Three Key Insights

1. Real-world web tasks often require several connected steps, so an AI system needs to maintain context throughout the entire task.
2. A system should be evaluated based on whether it actually achieves the user's goal, not simply whether it follows one expected sequence of actions.
3. Failure recovery is essential because one incorrect decision early in a multi-step workflow can prevent the entire task from being completed.

### Two Limitations or Risks

1. Even strong language models still perform much worse than humans on complex, multi-step web tasks, which shows that fully autonomous execution is not reliable enough yet.

2. Although WebArena is designed to be realistic, it is still a controlled, self-hosted benchmark with a limited set of websites and tasks, so it may not fully represent the unpredictability of the real web.

### One Concrete Inspiration for InterfaceDNA

InterfaceDNA should evaluate its generated interface based on goal completion, not only whether the generated UI looks correct. For example, if the user asks, “Can I drop CS 411?”, the system should be tested on whether it identifies the correct policy, warnings, dependencies, and valid next action rather than simply producing an attractive interface.