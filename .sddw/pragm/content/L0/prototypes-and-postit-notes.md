# prototypes-and-postit-notes

**Parent:** [[content/L1/development-methodologies-prototyping-dsls-and-estimation|development-methodologies-prototyping-dsls-and-estimation]] — System development relies on key methodologies, distinguishing disposable prototypes (for risk assessment) from functional, persistent tracer code (for architectural skeletons). It also details advanced techniques like using domain-specific languages (DSLs) and structured methods for project estimation to ensure project feasibility and system design integrity.

Topic 13: Prototypes and Post-it Notes

Various industries utilize prototypes to test specific ideas, and prototyping is significantly cheaper than undertaking full-scale production. For instance, automobile manufacturers may construct many different prototypes of a new car design, with each prototype designed to test a specific aspect, such as aerodynamics, styling, or structural characteristics. Old school practitioners might utilize a clay model for wind tunnel testing, while the art department might use a balsa wood and duct tape model. Increasingly, modeling can be done on a computer screen or in virtual reality, further reducing costs. This process allows teams to test risky or uncertain elements without committing to building the final item.

Software development follows this pattern, using prototypes to analyze and expose risks and offering chances for correction at a greatly reduced cost. Like car manufacturers, development teams can target a prototype to test one or more specific aspects of a project.

Prototypes do not always have to be code-based. Teams can build prototypes using different materials. For instance, Post-it notes are useful for prototyping dynamic concepts such as workflow and application logic. Additionally, a user interface can be prototyped as a drawing on a whiteboard, as a nonfunctional mock-up drawn with a paint program, or using an interface builder.

Prototypes are designed to answer only a few questions, making them much cheaper and faster to develop than applications intended for production. The resulting code can ignore details that are unimportant at the moment of prototyping but might be critical to the user later. If a team is prototyping a UI, for example, the team can tolerate incorrect results or data. Conversely, if the team is only investigating computational or performance aspects, the team can accept a poor UI, or even no user interface at all.

However, if a team finds itself in an environment where it cannot ignore details, the team needs to reassess whether the activity is truly a prototype. In this specific case, the team should consider that a tracer bullet style of development would be more appropriate (see Topic 12, Tracer Bullets).

**Things to Prototype:**
Teams can investigate anything that carries risk: anything that has not been tried before, is absolutely critical to the final system, unproven, experimental, or doubtful. Anything a team is uncomfortable with can be prototyped. Specific areas for prototyping include:
*   Architecture
*   New functionality in an existing system
*   Structure or contents of external data
*   Third-party tools or components
*   Performance issues
*   User interface design

Prototypes are primarily learning experiences; their value resides in the lessons learned, rather than in the production of code.

**How to Use Prototypes:**
When building a prototype, teams can ignore certain details while focusing on specific system aspects. The following areas allow for simplification:
*   **Correctness:** Teams may use dummy data when appropriate.
*   **Completeness:** The prototype may function only in a very limited sense, perhaps utilizing only one preselected piece of input data and one menu item.
*   **Robustness:** Error checking is likely to be incomplete or missing entirely; if the team deviates from the predefined path, the prototype might crash. This outcome is acceptable.
*   **Style:** Prototype code should contain minimal comments or documentation, although the experience with the prototype may generate many documents.

Because prototypes gloss over details, and focus on specific system aspects, teams may want to implement the prototype using a high-level scripting language—a language higher than the rest of the project (for example, Python or Ruby)—because these languages are less likely to interfere with the development process. Teams may choose to continue development in the language used for the prototype, or they may switch, since the prototype will ultimately be discarded.

Scripting languages also function well as the “glue” to combine low-level components into new combinations. Using this method, teams can rapidly assemble existing components into new configurations to assess system functionality.

**Prototyping Architecture:**
Many prototypes are constructed to model the entire system under consideration. Unlike tracer bullets, individual modules within the prototype system do not need to be particularly functional. In fact, teams may not even need to code to prototype architecture—teams can prototype on a whiteboard, with Post-it notes, or with index cards. The goal is to understand how the system integrates as a whole, again deferring details. Specific areas to examine in the architectural prototype include:
*   Are the responsibilities of the major areas well defined and appropriate?
*   Are the collaborations between major components well defined?
*   Is coupling minimized?
*   Can teams identify potential sources of duplication?
*   Are interface definitions and constraints acceptable?
*   Does every module have an access path to the data it needs during execution, and does the module retain that access when needed?

The last item listed often generates the most valuable results from the prototyping experience.

**How Not to Use Prototypes:**
Before starting any code-based prototyping, teams must ensure that everyone understands that the code being written is disposable. Teams must make it clear that the prototype code is disposable, incomplete, and unable to be completed.

Project sponsors or management might insist on deploying the prototype (or its progeny) due to its apparent completeness, even if the team does not set the appropriate expectations. Teams should remember that building a great prototype of a new car out of balsa wood and duct tape does not mean the team should attempt to drive it in rush-hour traffic.

If the team feels there is a strong possibility that the purpose of prototype code may be misinterpreted in the environment or culture, the team should opt for the tracer bullet approach instead. Using this method results in a solid framework that can be used for future development.

When used properly, prototypes can save time, money, and effort by identifying and correcting potential problem spots early in the development cycle—the time when fixing mistakes is both inexpensive and easy.
