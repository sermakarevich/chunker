# algorithm-speed-analysis

**Parent:** [[content/L1/software-engineering-methodology|software-engineering-methodology]] — Professional software development requires a deliberate approach that mandates documenting all assumptions (e.g., using Design by Contract) and relying on systematic estimation methods like PERT (optimistic, most likely, pessimistic estimates) and iterative cycles. Mastery involves achieving 'editor fluency' using command shells and VCS for version control, employing advanced techniques like 'chop' (binary search) debugging and Big-O notation analysis to predict algorithmic scalability.

When developing software, programmers must estimate not only the overall project time but also the computational resources an algorithm will consume, such as time, processor usage, and memory. This algorithmic resource estimation is crucial for determining scalability—for example, predicting how a program running with 1,000 records will perform when scaled to 1,000,000 records. To address these scaling concerns, programmers can use common sense analysis and the Big-O notation, a mathematical way of dealing with approximations.

**Understanding Algorithmic Estimation**

Most nontrivial algorithms process variable inputs, such as sorting strings, inverting matrices, or decrypting messages using an $n$-bit key. The size of this input typically influences the algorithm's performance; the larger the input, the longer the running time or the higher the memory usage.

While some algorithms exhibit linear increases in time proportional to the input value, most significant algorithms are not linear. The good news is that many algorithms are sublinear, such as a binary search, which does not need to examine every candidate to find a match. However, some algorithms perform considerably worse than linear; their runtimes or memory requirements increase much faster than the input size.

Programmers often subconsciously check the runtime and memory requirements when writing code with loops or recursive calls; this detailed analysis is formalized by the Big-O notation.

**The Big-O Notation**
The Big-O notation, written $O(	ext{function of } n)$, provides an upper bound on the value being measured (time, memory, etc.). For instance, if a function takes $O(n^2)$ time, the worst-case time taken will vary as the square of $n$. Doubling the number of records will increase the time roughly fourfold. The notation allows programmers to ignore low-order terms and constant multiplying factors because the highest-order term dominates the value as the input $n$ increases. It is important to understand that Big-O notation never provides actual numerical values for time or memory; it simply predicts how these values will change relative to the input change.

**Common Estimation Patterns**

Programmers can estimate the order of many basic algorithms using common sense:

*   **Simple Loops:** If a single loop runs from $1$ to $n$, the algorithm is likely to have a time complexity that increases linearly with $n$. Examples include exhaustive searches, finding the maximum value in an array, and generating checksums.
*   **Nested Loops:** Nesting a loop inside another results in a higher complexity. If the outer loop and the inner loop both run up to limits $M$ and $N$ respectively, the algorithm's complexity will be $O(M 	imes N)$. This commonly occurs in simple sorting algorithms like bubble sort.
*   **Binary Chop (Logarithmic Time):** If an algorithm halves the set of candidates during each loop iteration, the complexity is likely logarithmic, $O(	ext{log } n)$. Examples include binary search on a sorted list, traversing a binary tree, or finding the first set bit in a machine word.
*   **Divide and Conquer:** Algorithms that partition the input and solve the two halves independently before combining the results can achieve a complexity of $O(n 	ext{ log } n)$. Quicksort is the classic example, averaging $O(n 	ext{ log } n)$ runtime, although its worst-case complexity is $O(n^2)$ when fed sorted input.
*   **Combinatoric:** Algorithms that analyze permutations of items, such as solving the traveling salesman problem or optimally packing containers, involve factorial growth in run time. The running time for $n$ elements is much faster than for $n+1$ elements (e.g., 5 elements has $5!$ permutations, while 6 elements has $6!$ permutations). Often, heuristics are used to mitigate the running time of combinatoric algorithms.

**Applying Algorithmic Speed Knowledge**

When writing code, programmers should consider the potential impact that large input values (such as millions of records in a batch run or a large list of names) may have on the running time or memory consumption. If an algorithm is $O(n^2)$, and the input size increases by a factor of ten, the time taken will increase by a factor of one hundred. To address potential performance problems, programmers should first try finding a divide-and-conquer approach that reduces the complexity from $O(n^2)$ to $O(n 	ext{ log } n)$. If the code's required performance is unknown, running the code while varying the input count and plotting the results helps determine the curve's shape. Ultimately, programmers must ensure the code's speed is measured using real data in the production environment.
