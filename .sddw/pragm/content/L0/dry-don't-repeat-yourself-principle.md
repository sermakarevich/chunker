# dry-don't-repeat-yourself-principle

**Parent:** [[content/L1/principle-of-dry-knowledge-representation|principle-of-dry-knowledge-representation]] — The DRY principle mandates that every piece of knowledge must have a single, authoritative representation, extending beyond code to data structures and external interfaces; failure to follow DRY invites maintenance nightmares, illustrated by the risk of data structure duplication (e.g., storing calculated line length) and the necessity of centralized knowledge sharing to prevent dangerous inter-developer duplication, such as the discovery of over 10,000 distinct SSN validation codes in U.S. governmental systems.

When facing technical situations where a clear path is unavailable, developers can employ two strategies. First, because the specific form of future changes might be unknown, developers should always strive to make the code they write replaceable. Doing this ensures that future changes will not be blocked by the current code structure. Although this approach may seem extreme, maintaining decoupled and cohesive code should be a constant practice. Second, developers can use this process to develop engineering instincts. One should note the situation and the available choices in an engineering daybook and include a tag in the source code. Later, when the code must be changed, looking back at this record allows the developer to provide feedback that might help navigate similar complex decisions in the future. 

The subsequent sections of this chapter propose specific design ideas, but they all stem from one core principle: the DRY principle.

**Topic 9: DRY—The Evils of Duplication**

Giving a computer two contradictory pieces of knowledge, similar to Captain James T. Kirk’s method of disabling a marauding artificial intelligence, can unfortunately cause a program to fail. Programmers continually collect, organize, maintain, and harness knowledge, documenting this knowledge in specifications, incorporating it into running code, and utilizing it to provide necessary checks during testing. However, knowledge is inherently unstable and frequently changes rapidly; for example, a client meeting may change a requirement, a government may update a regulation that renders some business logic outdated, or tests might reveal an algorithm failure. This constant instability means that programmers spend a large amount of time in a maintenance mode, which involves reorganizing and reexpressing knowledge within the systems. Most people mistakenly believe that maintenance only starts after an application is released, equating it solely to fixing bugs and adding features. Programmers, however, are constantly in a state of maintenance because their understanding changes daily, new requirements arrive, and existing requirements evolve throughout the project's life, possibly due to changes in the operating environment. Regardless of the reason, maintenance is not a distinct activity but rather a routine part of the entire development process.

When performing maintenance, developers must locate and change the representations of things—the encapsulated pieces of knowledge embedded in the application. The challenge is that it is easy to duplicate knowledge across the specifications, processes, and programs developed. When duplication occurs, it invites a maintenance nightmare that begins long before the application is released.

To develop software reliably and ensure that developments are easier to understand and maintain, developers should follow the DRY principle: Every piece of knowledge must have a single, unambiguous, authoritative representation within the system.

**Understanding DRY: Don’t Repeat Yourself**

The alternative to following DRY is having the same knowledge expressed in two or more places. If one changes one instance, the developer must remember to change all others; otherwise, similar to the alien computers, the program will collapse due to contradiction. The issue is not whether a developer will remember, but when the developer will forget.

The DRY principle appears repeatedly throughout the book, often in contexts unrelated to coding, and is viewed as one of the most critical tools in a Pragmatic Programmer’s toolbox.

**DRY is More Than Code**

In the first edition of the book, the explanation of Don’t Repeat Yourself was insufficient, leading many people to interpret DRY as referring only to code, specifically thinking it meant 
