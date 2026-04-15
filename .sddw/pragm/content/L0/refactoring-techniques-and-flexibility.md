# refactoring-techniques-and-flexibility

**Parent:** [[content/L1/software-architecture-scaling-design|software-architecture-scaling-design]] — Modern software development requires adherence to foundational principles like DRY and orthogonality, using techniques like Abstraction and Componentization to ensure reversibility and decoupling. Algorithmic performance is estimated using Big-O notation to predict scaling issues (e.g., $O(N^2)$ vs. $O(N 	ext{ log } N)$), and the development process relies on Test-Driven Development (TDD) and iterative Refactoring to maintain quality.

To analyze technical problems, developers should consider the difference between tools with a graphical user interface (GUI) and small, combinable command-line utilities used at shell prompts. When considering which set of tools is superior, developers must evaluate criteria such as orthogonality, ease of use for the intended purpose, combination ability with other tools to meet new challenges, and learning curve. Furthermore, developers must determine if the impact on orthogonality differs between using multiple inheritance and using multiple interfaces, and whether the impact of delegation differs from that of inheritance. 

**Reversibility and Flexible Architecture:**
A critical decision, such as committing to one vendor's database or a specific architectural pattern, can be extremely expensive or impossible to undo. The concept of reversibility highlights the danger of making such critical decisions. For example, if a project team commits to using one vendor's database or a specific architectural pattern, the change might be extremely expensive or impossible to undo. The author advises that even if developers must commit to a technology, abstracting the idea of a database to simply provide persistence as a service provides the flexibility to switch vendors or technologies. Similarly, when adapting a browser-based application to a mobile app, the change should ideally only require stripping out HTML rendering and replacing it with an API, minimizing the impact on the server side. Therefore, developers should avoid making decisions that are cast in stone, instead thinking of decisions as being written in the sand, which can be wiped out by a big wave.

**Recommendations for Flexible Architecture:**
To maintain flexibility, developers must follow three techniques: 1) **Abstraction:** Developers must hide third-party APIs behind their own abstraction layers. 2) **Componentization:** Developers should break the code into components; even if the deployment happens on a single massive server, this approach is much easier than refactoring a monolithic application. 3) **Guidance:** Developers must always enable their code to adapt to change, remembering that there are no final decisions.

In software development, the concept of **Decoupling**, which shows how keeping separate concepts separate through good design principles, makes the code easier to change. The enemy of change is coupling, because it links together things that must change in parallel. This requires developers to either spend time tracking down all parts that need changing or spend time figuring out why things broke when only coupling exists.

**Refactoring: Improving the Design of Existing Code:**
Software code is not static; as a program evolves, developers must be prepared to rethink earlier decisions and rework portions of the code. This process is natural. Instead of viewing software development through the metaphor of building construction (where an architect draws blueprints, contractors build the superstructure, and tenants move in), developers should use the metaphor of gardening. Gardening is more organic than concrete: developers plant things according to an initial plan, and they may move plantings relative to each other to optimize the interplay of light and shadow, prune overgrown parts, or improve aesthetics. This process involves constantly monitoring the system's health and making adjustments (to the soil, the plants, or the layout) as needed. The subset of restructuring code known as refactoring is a disciplined technique for restructuring an existing body of code, altering its internal structure without changing its external behavior.

Refactoring is not a high-ceremony, once-in-a-while activity, but a low-risk, small-scale, day-to-day activity, similar to weeding and raking. Developers must treat refactoring as a precise, targeted approach rather than a wholesale rewrite of the codebase. To guarantee that the external behavior hasn’t changed during refactoring, developers need good, automated unit testing that validates the code's behavior.

**When Developers Should Refactor:**
Developers should refactor when they have learned something new or when they understand something better than they did previously. Potential triggers for refactoring include: 

*   **Duplication:** Discovering a violation of the DRY principle.
*   **Nonorthogonal Design:** Discovering something that could be made more orthogonal.
*   **Outdated Knowledge:** Recognizing that requirements have drifted and the code needs to keep up with the increased knowledge of the problem.
*   **Usage:** Real-world usage reveals features that are more important or less important than initially assumed.
*   **Performance:** Needing to move functionality from one area of the system to another to improve performance.
*   **Successful Testing:** A successful small code addition, confirmed by a test, provides an opportunity to tidy up the newly written code.

Refactoring involves moving functionality and updating earlier decisions; it is best conceptualized as a form of pain management. When a developer commits to refactoring, they should treat the process as a small, deliberate activity, not a massive overhaul. If a full rewrite is unavoidable, developers must schedule the work, and they must ensure that users of the affected code are notified of the change and its potential impact.

**How Developers Should Refactor:**
Refactoring is fundamentally redesign. Instead of ripping up large quantities of code, developers should proceed slowly, deliberately, and carefully. Martin Fowler recommends the following steps: 

1.  Never attempt to refactor and add functionality simultaneously.
2.  Always ensure good tests are in place before starting refactoring; developers must run these tests as often as possible to quickly identify if the changes have introduced errors.
3.  Take short, deliberate steps: move a field from one class to another, split a method, or rename a variable. Developers should focus on making many localized changes that collectively achieve a larger-scale change. Keeping steps small, and testing after each step, helps prevent prolonged debugging.

Although automatic refactoring is available in modern IDEs—allowing automated renaming, splitting routines, and assisting with movement—developers must remember that maintaining good regression tests remains the key to refactoring safely. If developers must change external behavior or interfaces, they should deliberately break the build; this ensures that old clients of the code fail to compile, indicating what needs updating.
