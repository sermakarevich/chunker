# stream-laziness-and-unfold

**Parent:** [[content/L1/scala-stream-laziness-advanced-concepts|scala-stream-laziness-advanced-concepts]] — Stream processing relies on laziness to compute elements only when demanded, facilitating efficient chaining of combinators like `map` and `filter` without intermediate stream instantiation. Utility functions and advanced concepts include using `unfold` for memory-efficient stream generation, and implementing combinators like `hasSubsequence` using the `tails` function.

This section details advanced concepts concerning strictness and laziness when manipulating streams. The core principle is that stream operations are incremental; they do not fully generate results until a consuming computation (such as converting the stream to a `List`) requires the elements. Because of this incremental nature, functions like `map`, `filter`, `append`, and `flatMap` can be chained sequentially without fully instantiating the intermediate results. 

For example, considering the trace `Stream(1,2,3,4).map(_ + 10).filter(_ % 2 == 0).toList` reveals that the computation alternates between generating a single element via `map` and testing that element via `filter` for divisibility by 2. Crucially, the trace shows that intermediate streams are not fully instantiated. 

This lazy, incremental generation provides several benefits: it allows chaining combinators in novel ways, as demonstrated by defining `find(p: A => Boolean): Option[A] = filter(p).headOption`. Furthermore, the lack of intermediate stream instantiation means that a stream transformation requires only enough working memory to store and transform the current element, allowing the garbage collector to reclaim space for values (like 11 and 13 in the example) as soon as they are no longer needed by the consumer. 

This lazy evaluation also enables stream functions to work with infinite streams. An infinite `Stream[Int]` of 1s, defined as `val ones: Stream[Int] = Stream.cons(1, ones)`, can be processed safely because functions only inspect the portion of the stream necessary for the demanded output. For example, `ones.take(5).toList` evaluates to `List(1, 1, 1, 1, 1)`, and `ones.exists(_ % 2 != 0)` evaluates to `true` immediately. However, developers must be cautious, as writing expressions that never terminate or are not stack-safe can cause issues; for instance, `ones.forAll(_ == 1)` will cause the program to loop forever (manifesting as a stack overflow rather than an infinite loop) because it never encounters an element that allows it to terminate with a definite answer. 

Developers can use specialized methods to generate streams, including: 
*   `def constant[A](a: A): Stream[A]` (EXERCISE 5.8) to return an infinite `Stream[A]` of a given value `a`. 
*   `def from(n: Int): Stream[Int]` (EXERCISE 5.9) to generate an infinite stream of integers starting from `n`, then `n + 1`, and so on. 
*   `def fibs` (EXERCISE 5.10) to generate the infinite stream of Fibonacci numbers (0, 1, 1, 2, 3, 5, 8, etc.). 
*   `def unfold[A, S](z: S)(f: S => Option[(A, S)]): Stream[A]` (EXERCISE 5.11), which is a highly general stream-building function that takes an initial state `z` and a function `f` to produce both the next state and the next value. The `Option` type is used by `f` to signal when the stream should terminate, if at all. The `unfold` function represents a corecursive function: whereas a recursive function consumes data, a corecursive function produces data. 

Advanced stream functions can be implemented using `unfold`: 
*   `def fibs` (EXERCISE 5.12) 
*   `def from` (EXERCISE 5.12) 
*   `def constant` (EXERCISE 5.12) 
*   `def ones` (EXERCISE 5.12) 

Using `unfold` to define `constant` and `ones` achieves constant memory usage, unlike the simple recursive definition `val ones: Stream[Int] = Stream.cons(1, ones)`, which consumes memory even when the stream is traversed. 

Finally, developers can implement other stream combinators using `unfold`: 
*   `def map` (EXERCISE 5.13) 
*   `def take` (EXERCISE 5.13) 
*   `def takeWhile` (EXERCISE 5.13) 
*   `def zipWith[B](s2: Stream[B]): Stream[(A, B)]` (EXERCISE 5.13), which should follow the pattern of Chapter 3's `zipWith`. 
*   `def zipAll[B](s2: Stream[B]): Stream[(Option[A], Option[B])]` (EXERCISE 5.13), which continues traversal as long as either stream has more elements, using `Option` to track exhaustion. 

Advanced patterns include: 
*   `def startsWith[A](s: Stream[A]): Boolean` (EXERCISE 5.14), which checks if one stream is a prefix of another (e.g., `Stream(1,2,3)` starts with `Stream(1,2)` is true). 
*   `def tails: Stream[Stream[A]]` (EXERCISE 5.15), which returns a stream of suffixes of the input sequence, starting with the original stream (e.g., `Stream(1,2,3)` returns `Stream(Stream(1,2,3), Stream(2,3), Stream(3), Stream())`). 

Using these simpler functions, developers can implement `def hasSubsequence[A](s: Stream[A]): Boolean = tails exists (_ startsWith s)` (EXERCISE 5.14), checking whether a stream contains a given subsequence.
