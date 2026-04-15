# requirements-discovery-process

**Parent:** [[content/L1/professional-mastery-workflow-architecture|professional-mastery-workflow-architecture]] — Professional mastery requires integrating foundational skills (like woodworker tool maintenance) with advanced workflows, including structured estimation methods (PERT, iterative cycles) and digital proficiencies (command shell mastery, editor fluency, using VCS for branching and CI/CD). Crucially, the development process mandates treating initial client statements as explorations, generating feedback via prototypes to distinguish underlying business policy from simple requirements, and adopting advanced architectural patterns like FSMs and PubSub for low coupling.

At the start of any project, the team must learn the requirements. Simply receiving instructions or listening to users is insufficient; practitioners should read the guidelines in Topic 45, The Requirements Pit, to learn how to avoid common traps and pitfalls. Although conventional wisdom and constraint management are covered in Topic 46, Solving Impossible Puzzles, developers must recognize that difficult problems, whether performing requirements gathering, analysis, coding, or testing, will arise. Typically, these problems will not be as difficult as initially perceived.

When faced with an impossible project, developers should turn to Topic 47, Working Together, which means solving problems collaboratively while coding, rather than merely sharing a large requirements document, sending heavily cc'd emails, or enduring endless meetings. Though the Agile Manifesto begins with "Individuals and interactions over processes and tools," almost all "agile" projects start with an ironic discussion about selecting processes and tools. However, no method can replace careful thought. Instead of relying on a particular process or tool, developers need to focus on the concepts presented in Topic 48, The Essence of Agility. Addressing these critical issues before the project commences better positions the team to avoid "analysis paralysis" and successfully start and complete the project.

### Topic 45: The Requirements Pit

*A quotation by Antoine de St. Exupery from Wind, Sand, and Stars (1939) states: "Perfection is achieved, not when there is nothing left to add but when there is nothing left to take away."*

Many books and tutorials describe requirements gathering as an early project phase. The word "gathering" implies that the requirements are already available—that the developers merely need to find them and place them in a basket.

In reality, requirements rarely lie on the surface. Instead, developers must understand that requirements are normally buried deep beneath layers of assumptions, misconceptions, and politics. Furthermore, requirements often do not truly exist at all.

**Tip 75: No One Knows Exactly What They Want**

In the early days of software development, computers were more valuable (in terms of amortized cost per hour) than the people who worked with them. Consequently, developers saved money by attempting to get things correct the first time. Part of that process involved attempting to specify exactly what the machine was going to do. Early practices involved starting with a specification of requirements, parlaying that into a design document, then into flowcharts and pseudocode, and finally into code. Before feeding the code into a computer, developers would spend time desk checking it.

This process was expensive, and the cost meant that people only tried to automate something when they knew exactly what they wanted. Because early machines were fairly limited, the scope of problems they solved was constrained: it was actually possible to understand the whole problem before starting. 

However, the current real world is messy, conflicted, and unknown. In that world, exact specifications of anything are rare, if not downright impossible.

Programmers, therefore, must help people understand what they want. Practitioners should recognize that helping people understand what they want is probably the most valuable attribute of the programmer. 

**Tip 76: Programmers Help People Understand What They Want**

Consider the people who ask developers to write software; these individuals are the client. The typical client approaches developers with a need, which may be strategic, but is just as likely to be a tactical issue—a response to a current problem. The need may require a change to an existing system or might request something new. The need might be expressed in business terms and sometimes in technical ones.

The common mistake new developers make is to take this initial statement of need and implement a solution for it. Based on experience, this initial statement of need is not an absolute requirement; rather, it functions as an invitation to explore. 

For instance, if a publisher receives the requirement: "Shipping should be free on all orders costing $50 or more," the developer should anticipate questions, such as: Does the $50 include tax? Does the $50 include current shipping charges? Must the $50 apply only to paper books, or can the order also include ebooks? What specific type of shipping is offered (e.g., Priority or Ground)? How often might the $50 limit change in the future?

When presented with something that appears simple, the developer must guide the client by looking for edge cases and asking about them. The client may have already considered some of these points and simply assumed the implementation would work that way; asking the questions helps flush that information out. The developer must identify other questions the client had not previously considered. This situation is where a good developer learns to be diplomatic: the developer interprets what the client says and feeds back the implications. This process is both intellectual and creative, allowing the developer to contribute to a solution that is likely better than what either the developer or the client would have produced alone.

**Requirements are a Process**

The previous example demonstrated that the developer prompted the client by feeding back a consequence, which initiated an exploration. This process illustrates the reality of all requirements gathering: the developer's job is to help the client understand the consequences of their stated requirements. This is done by generating feedback, allowing the client to use that feedback to refine their thinking.

In cases where expressing feedback in words is difficult, developers can rely on the "is this what you meant?" school of feedback. Developers produce mockups and prototypes, allowing the client to interact with them. Ideally, the resulting mockups are flexible enough that the developers can change them during discussions, responding to "that isn’t what I meant" with "so more like this?". Although these mockups might be hastily created within an hour, they serve as a reality check, as all work done, even at the end of a project, involves interpreting what the client wants.

Consequently, the Pragmatic Programmer views the entire project as a requirements gathering exercise, which explains the preference for short iterations that end with direct client feedback. This keeps the process on track and minimizes the time lost if the project must change direction.

**Working with a User to Think Like a User**

Another simple technique for understanding the client's perspective is becoming a client. For instance, a developer writing a system for the help desk should spend time monitoring the phones with an experienced support person. If the developer is automating a manual stock control system, the developer should work in the warehouse for a week. This action not only provides insight into how the system will actually be used but also helps build trust and establishes a basis for communication with the clients. The developer must remember not to get in the way.

**Requirements versus Policy**

If, while discussing a Human Resources system, a client states, "Only an employee’s supervisors and the personnel department may view that employee’s records," the developer must distinguish between a mere requirement and an embedded business policy. Although the statement appears absolute, it represents a subtle distinction with profound implications for the developers. If the requirement is stated as "Only supervisors and personnel can view an employee record," the developer might end up coding an explicit test every time the application accesses this data.
