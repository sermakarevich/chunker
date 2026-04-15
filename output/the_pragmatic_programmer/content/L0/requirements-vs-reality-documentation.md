# requirements-vs-reality-documentation

**Parent:** [[content/L1/professional-mastery-workflow-architecture|professional-mastery-workflow-architecture]] — Professional mastery requires integrating foundational skills (like woodworker tool maintenance) with advanced workflows, including structured estimation methods (PERT, iterative cycles) and digital proficiencies (command shell mastery, editor fluency, using VCS for branching and CI/CD). Crucially, the development process mandates treating initial client statements as explorations, generating feedback via prototypes to distinguish underlying business policy from simple requirements, and adopting advanced architectural patterns like FSMs and PubSub for low coupling.

When an application requires role-based access, such as when determining if only authorized users may access an employee record, the developer should design and implement an access control system. When security policies change, only the metadata for this system needs updating. This systematic approach naturally leads to a well-factored system that supports metadata.

**General Rule: Policy Is Metadata**
Developers should implement the general case, using the specific policy information as an example of the type of support the system must provide.

**Requirements vs. Reality**
In a January 1999 Wired magazine article, producer and musician Brian Eno described the ultimate mixing board, a technology capable of generating any sound. However, instead of helping musicians create better music or speed up recording, the device interfered with the creative process. Recording engineers intuitively balance sounds, developing a feedback loop using their ears and fingertips by sliding faders and rotating knobs. The new mixer, though comprehensive, failed to leverage these abilities, instead forcing users to type on a keyboard or click a mouse. The functions the engineers needed were often hidden behind obscure names or achieved through nonintuitive combinations of basic facilities.

This example suggests that successful tools must adapt to the capabilities of the users. Therefore, effective requirements gathering must take this into account. Early feedback, utilizing prototypes or tracer bullets, allows clients to confirm that the solution "does what I want, but not how I want."

**Documenting Requirements**
Although the best form of requirements documentation—and perhaps the only one—is working code, developers cannot forgo documenting their understanding of the client's needs. However, such documents should not be presented to the client as a deliverable or a document requiring sign-off. Instead, these documents should serve only as mileposts to guide the implementation process.

**Requirements Documents Should Not Be for Clients**
In the past, individuals have worked on projects that generated highly detailed requirements documents. These substantial documents often expanded on the client’s initial two-minute explanation, resulting in inch-thick masterpieces filled with diagrams and tables, specifying functionality to the point where the resulting document could effectively be the final program itself. Creating these documents is flawed for two primary reasons. First, because the client does not truly know all requirements up front, expanding what the client says into a document that resembles a legal agreement builds a complex structure on an unstable foundation. Second, even if the document is presented to the client for sign-off, clients rarely read the detailed specifications. The client seeks to solve a high-level, often nebulous problem, but programmers are interested in the details and nuances. Since the requirements document is written for developers, it often contains information and subtleties that are frequently confusing or boring to the client.

For example, submitting a 200-page requirements document would likely result in the client only reading the first few paragraphs (which is why the first two paragraphs should always be titled Management Summary) or glancing at diagrams.

**Requirements Documents Should Be for Planning**
Despite the pitfalls, requirements must still be documented because development teams need a shared understanding of the work. The preferred form is a concise description, ideally fitting on a real or virtual index card. These short descriptions, known as user stories, describe what a small portion of the application should do from the perspective of the user. When written this way, requirements can be placed on a board and moved around to track status and priority. Keeping the statement of requirements short is crucial because it encourages developers to ask clarifying questions, thereby improving the feedback process between clients and coders both before and during the creation of each piece of code.

**Over-Specification and Specificity**
Another significant danger is over-specification. Good requirements should be abstract. When documenting requirements, the simplest statement that accurately reflects the business need is best. While this does not imply vagueness, developers must capture the underlying semantic invariants as requirements, and document the current, specific work practices as policy. Remember: Requirements are a need, not architecture, design, or the user interface.

**Preventing Scope Creep**
Many project failures are attributed to scope increases, also known as feature bloat, requirements creep, or creeping featurism (an aspect of the boiled-frog syndrome). The most effective preventative measure against requirements creep is continuous feedback. Working with the client in iterations and receiving constant feedback allows the client to experience first-hand the impact of adding "just one more feature."

**Maintaining a Glossary**
As requirements discussions begin, users and domain experts will use specialized terms with specific meanings. The developer must create and maintain a project glossary—a single location defining all specific terms and vocabulary used in a project. Every participant, including end users and support staff, must use the glossary to ensure consistent vocabulary. This glossary should be widely accessible, such as through online documentation. If users and developers refer to the same thing by different names, or worse, refer to different things by the same name, success on the project is difficult.
