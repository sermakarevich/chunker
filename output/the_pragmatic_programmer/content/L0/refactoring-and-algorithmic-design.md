# refactoring-and-algorithmic-design

**Parent:** [[content/L1/software-architecture-and-refactoring-lifecycle|software-architecture-and-refactoring-lifecycle]] — Software development is an iterative, continuous process (like gardening) that prioritizes refactoring—the disciplined restructuring of code without altering external behavior—triggered by issues like duplication or drifting requirements. Advanced system design requires adopting patterns like Publish/Subscribe and Reactive Programming for decoupling, utilizing the Actor Model or Blackboard system for concurrency, and always preserving accurate records when performing multiple estimations or monitoring program state.

A programmer should view software development not as a static construction process, but as an organic activity, more like gardening. While developers might draw blueprints (analogous to the initial planning stages), the actual process involves continuous adaptation, adjustment, and monitoring. Instead of focusing on construction, developers must adopt a 'gardening' metaphor, recognizing that planting requires careful nurturing, and that some planned elements may fail and become 'compost.'

Whenever a developer learns something new, or gains a deeper understanding of a system, the developer should initiate a process of restructuring the existing code. This process, which is generally called restructuring, has a specific subset known as refactoring. Martin Fowler defines refactoring as a disciplined technique for restructuring an existing body of code by altering its internal structure without changing its external behavior.

The critical requirements for refactoring are that the activity must be disciplined, and the external behavior must remain unchanged; therefore, refactoring should never be used as a time to add new features. Refactoring should not be an infrequent, high-ceremony event (like a wholesale rewrite). Instead, developers should treat refactoring as a daily activity, similar to the low-risk steps of weeding and raking, and focus on making targeted, precise improvements to keep the code easily maintainable.

To guarantee that the external behavior has not changed during refactoring, developers must employ good, automated unit testing that validates the code's behavior. 

Developers should refactor when they learn something new: when the current code no longer fits the problem, when two distinct things should be merged, or whenever anything seems structurally incorrect. Specific triggers for refactoring include:
*   **Duplication:** Discovering a violation of the DRY (Don't Repeat Yourself) principle.
*   **Nonorthogonal design:** Identifying an area of the system that could be designed in a more orthogonal manner.
*   **Outdated knowledge:** Recognizing that requirements drift or the developer's own understanding of the problem has increased.
*   **Usage:** Real-world use of the system reveals that certain features are more critical than originally thought.
*   **Performance:** Needing to move functionality from one part of the system to another to improve performance.

Automated unit testing provides the validation that the refactoring has been successful. Refactoring is most effective when it is performed early and often, ideally as an ongoing activity while coding. A major rule of thumb is that the process of refactoring is always easier when the underlying issues are small. If a significant, high-disruption rewrite is necessary, developers must schedule this work and inform all users of the affected code that rewriting is planned and explain how it might affect the users.

Regarding algorithmic analysis, programmers should remember that the fastest algorithm is not always the best choice for a given problem. For instance, for a small input set, a simple insertion sort can perform equally well as a quicksort, and requires less time for writing and debugging. Developers must also be cautious about premature optimization; the developer should only invest time attempting to improve an algorithm if the algorithm is genuinely identified as a bottleneck.

If accurately timing an algorithm's performance is difficult, programmers should utilize code profilers to count the number of times different steps in the algorithm execute and then plot these figures against the size of the input.
