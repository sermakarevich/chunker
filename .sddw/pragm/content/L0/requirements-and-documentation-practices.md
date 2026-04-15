# requirements-and-documentation-practices

**Parent:** [[content/L1/adaptive-software-development-principles-2|adaptive-software-development-principles-2]] — Software development demands treating naming elements (functions, variables, etc.) with extreme precision, prioritizing specificity and congruence with user domain terminology; architecturally, systems must adhere to DRY, orthogonality, and reversibility, managing global data through controlled APIs and interfaces; regarding requirements, developers must adopt a role of discovery, viewing initial statements as invitations for exploration rather than final specifications, favoring abstract user stories and iterative feedback (prototypes) over detailed, monolithic documents.

When designing software, developers should recognize that stating a policy, such as 'Only authorized users may access an employee record,' naturally leads to designing and implementing an access control system. When policy changes occur, only the metadata for that system needs to be updated, allowing the system to be well factored to support metadata. Therefore, developers should implement the general case, using policy information as an example of the type of system requirement the system needs to support.

**Requirements vs. Reality:**

In a January 1999 Wired magazine article, producer and musician Brian Eno described the ultimate mixing board, which could achieve any sound. However, instead of helping musicians make better music or speeding up recording, the board was disruptive because its interface did not leverage the intuitive, innate feedback loop developed by recording engineers using sliding faders and rotating knobs. Instead, the new mixer forced users to type on a keyboard or click a mouse, providing comprehensive functions but packaging them in unfamiliar and exotic ways. The functions the engineers actually needed were often hidden behind obscure names or achieved through nonintuitive combinations of basic facilities. This example illustrates the principle that successful tools must adapt to the hands that use them. Consequently, successful requirements gathering must account for this, which is why early feedback, using prototypes or tracer bullets, allows clients to respond with, “yes, it does what I want, but not how I want.”

**Documenting Requirements:**

Developers should treat working code as the best—perhaps the only—form of requirements documentation. However, this does not mean developers can ignore the need to document their understanding of client needs; such documents should not be considered final deliverables for client sign-off. Instead, they function merely as mileposts to guide the implementation process. 

**Requirements Documents are Not for Clients:**

Historically, some projects generated exceptionally detailed requirements documents, expanding upon a client's initial two-minute explanation into inch-thick masterpieces filled with diagrams and tables. These specifications were detailed enough to leave almost no room for ambiguity in implementation, and sufficiently powerful tools could turn the document into the final program itself. This approach was flawed for two reasons. First, the client does not truly know what they want initially. Expanding what the client says into what is almost a legal document builds an incredibly complex system on quicksand. Second, even when the document is presented for sign-off, the client rarely reads the detailed technical document because the client is motivated by solving a high-level, somewhat nebulous problem, while programmers are interested in all the details and nuances. A twenty-page requirements document will likely cause the client to only read the first couple of paragraphs (which is why the first two paragraphs are always titled Management Summary) and may only flick through the rest, possibly stopping at a neat diagram. Giving the average developer a large technical document is comparable to giving them a copy of the Iliad in Homeric Greek and asking them to code the video game from it.

**Requirements Documents are for Planning:**

Developers should not rely on monolithic, heavy requirements documents. Nevertheless, requirements must be written down so that developers on a team know what they will be doing. The preferred form is a short description, often called a user story, that can fit on a real (or virtual) index card. These user stories describe what a small portion of the application should do from the perspective of a user of that functionality. Placing these requirements on a board and moving them allows developers to track both status and priority. Although a single index card cannot hold all the necessary information to implement a component of the application, this limitation is intentional. Keeping the statement of requirements short encourages developers to ask clarifying questions, thereby enhancing the feedback process between clients and developers before and during the creation of every piece of code.

**Over-specification:**

Another danger in creating requirements documents is being too specific. Good requirements must be abstract; the simplest statement that accurately reflects the business need is best. While developers must capture underlying semantic invariants as requirements, the specific or current work practices should instead be documented as policy. Requirements are needs, not architecture, design, or the user interface.

**Scope Creep Management:**

Many project failures are wrongly blamed on scope increase (feature bloat, requirements creep). This is related to the boiled-frog syndrome. The prevention of requirement creep relies on feedback: when developers work with the client in iterations with constant feedback, the client will experience first-hand the impact of “just one more feature.”

**Maintaining a Glossary:**

As developers discuss requirements, users and domain experts frequently use terms that have specific meanings to them. These terms may differentiate between 
