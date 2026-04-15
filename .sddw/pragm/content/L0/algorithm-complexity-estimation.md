# algorithm-complexity-estimation

**Parent:** [[content/L1/software-architecture-scaling-design|software-architecture-scaling-design]] — Modern software development requires adherence to foundational principles like DRY and orthogonality, using techniques like Abstraction and Componentization to ensure reversibility and decoupling. Algorithmic performance is estimated using Big-O notation to predict scaling issues (e.g., $O(N^2)$ vs. $O(N 	ext{ log } N)$), and the development process relies on Test-Driven Development (TDD) and iterative Refactoring to maintain quality.

## Common Sense Estimation of Algorithm Running Time

Developers can estimate the order of many basic algorithms using common sense principles:

*   **Simple Loops:** If a simple loop iterates from $1$ to $N$, the algorithm's runtime is likely to be $O(N)$. Examples of simple loops include exhaustive searches, finding the maximum value in an array, and generating checksums.
*   **Nested Loops:** If a developer nests one loop inside another, the algorithm's runtime becomes $O(N^2)$, where $N$ is the maximum limit used by the outer loop, and $M$ is the maximum limit used by the inner loop. This commonly occurs in simple sorting algorithms like bubble sort, where the outer loop scans each element in the array sequentially, and the inner loop determines the correct position for that element in the sorted result. Such sorting algorithms tend to be $O(N^2)$.
*   **Binary Chop (Logarithmic Time):** If an algorithm halves the set of items it considers during each iteration, the runtime is likely to be logarithmic, $O(	ext{log} N)$. Examples of algorithms running in $O(	ext{log} N)$ time include performing a binary search on a sorted list, traversing a binary tree, or finding the first set bit in a machine word.
*   **Divide and Conquer:** Algorithms that partition their input data into two halves and then independently combine the results can achieve $O(N 	ext{ log } N)$ runtime. Quicksort is a classic example; it works by partitioning the data into two halves and recursively sorting each half. Although qusorting is technically $O(N^2)$ because its behavior degrades when fed sorted input, its average runtime is $O(N 	ext{ log } N)$.
*   **Combinatoric Complexity:** Whenever algorithms examine the permutations of items, their running times may escalate quickly. This is because permutations involve factorials. For example, a combinatoric algorithm for five elements involves $5!$ permutations, while running it for six elements involves $6!$ (six times longer), and for seven elements involves $7!$ (42 times longer). Combinatoric complexity examples include algorithms for the traveling salesman problem, optimally packing containers, and partitioning a set of numbers so that each resulting set shares the same total. Developers often use heuristics to reduce the running times of these types of algorithms in specific problem domains.

## Algorithm Speed in Practice

Developers are unlikely to spend much time writing sort routines because existing libraries generally outperform custom implementations. Nevertheless, the fundamental types of algorithms described previously appear repeatedly. If a developer finds themselves writing a simple loop, the runtime is $O(N)$. If that loop contains an inner loop, the runtime is $O(N^2)$. Developers should consider how large the input values might become. If the inputs are bounded, the developer can predict the runtime. If the inputs depend on external factors (such as the number of records in an overnight batch run, or the number of names in a list of people), the developer must stop and consider the effect that large external values may have on the algorithm's running time or memory consumption.

**Tip 63: Estimating the Order of Algorithms**

If a developer has an algorithm that is $O(N)$, the developer should try finding a divide-and-conquer approach that will reduce the complexity to $O(N 	ext{ log } N)$. If the developer is unsure about the algorithm's time or memory usage, the developer should test the algorithm while varying the input record count or other factors likely to impact the runtime and plot the results. Plotting three or four points will provide an idea of the curve's shape: whether the input size increase causes the runtime to curve upward, increase linearly, or flatten off. Additionally, developers should consider the code structure itself: a simple loop might perform better than a complex, $O(N^2)$ routine for smaller input values of $N$, especially if the $O(N^2)$ algorithm contains a significantly expensive inner loop.

In addition to theory, developers must consider practical considerations. A runtime might increase linearly for small input sets but suddenly degrade when processing millions of records because the system begins to thrash. If developers test a sort routine using random input keys, the routine might perform differently the first time it encounters ordered input. Developers must cover both the theoretical and practical considerations. Ultimately, the only timing that counts is the speed of the code running in the production environment using real data.

**Tip 64: Testing Algorithm Estimates**

If accurate timing measurements are difficult, developers should use code profilers to count the number of times different steps in the algorithm are executed and plot these figures against the size of the input.

**Best is Not Always Best**

Developers must remain pragmatic when selecting algorithms; the fastest algorithm is not always the best solution. For a small input set, a straightforward insertion sort will perform similarly to a quicksort, and requires less time to write and debug. Developers must also consider if the chosen algorithm has a high setup cost. For small input sets, this setup cost may exceed the running time and render the algorithm inappropriate. Furthermore, developers should be wary of premature optimization and should ensure an algorithm is genuinely a bottleneck before spending time trying to improve it.
