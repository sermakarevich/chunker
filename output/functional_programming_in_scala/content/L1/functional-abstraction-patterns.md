# functional-abstraction-patterns

**Parent:** [[content/L2/functional-programming-design-patterns|functional-programming-design-patterns]] — Functional programming achieves robust design by managing side effects explicitly through structures like `Option[A]` and `Either[A, B]` for type-safe control flow, and by using `Stream[A]` and the `unfold` function for memory-efficient lazy computation. State changes are controlled via the `Rand[A]` type alias and combinators like `map` and `flatMap`, which guarantee referential transparency by explicitly passing the updated state through all computations.

The concept of state management in functional programming mandates explicit handling of state transitions, generalizing patterns previously seen in specific domains like Random Number Generation (RNG) to form a foundational abstraction.

Initially, state handling is exemplified by RNG. Because functions that reuse an RNG state yield identical results, generating distinct random integers necessitates passing the updated state. The signature for generating a pair of random integers, `randomPair`, must use the RNG state returned by the first `rng.nextInt` call when generating the second, thus returning the final state (`rng3`).

To simplify this manual state passing, functional programmers introduced specialized utilities. A type alias, `Rand[A]`, is defined as `RNG => (A, RNG)`, representing a state action. This means a value of type `Rand[A]` is interpreted as a program depending on an initial `RNG` state, using it to generate a value of type `A`, and simultaneously transitioning the `RNG` to a new state. Core methods, such as `RNG`'s `nextInt`, can be adapted into this `Rand[Int]` type via `val int: Rand[Int] = _.nextInt`.

Combinators abstract the state passing mechanism. The unit action, `def unit[A](a: A): Rand[A] = rng => (a, rng)`, accepts the initial `RNG` state and passes it through unchanged. The `map` combinator allows transforming the output of a state action without modifying the state. Since `Rand[A]` is equivalent to `RNG => (A, RNG)`, `map` is implemented as function composition: `def map[A,B](s: Rand[A])(f: A => B): Rand[B] = rng => { val (a, rng2) = s(rng); (f(a), rng2) }`. For example, `def nonNegativeEven: Rand[Int] = map(nonNegativeInt)(i => i - i % 2)` generates an even, non-negative integer.

When two independent actions are combined, `map2` is necessary. This function takes two state actions, `ra` and `rb`, and a combining function `f`, resulting in a new action: `def map2[A,B,C](ra: Rand[A], rb: Rand[B])(f: (A, B) => C): Rand[C]`. To generate pairs, `both[A,B]` uses `map2`: `def both[A,B](ra: Rand[A], rb: Rand[B]): Rand[(A,B)] = map2(ra, rb)((_, _))`. Consequently, generating an (Int, Double) pair uses `val randIntDouble: Rand[(Int, Double)] = both(int, double)`.

Advanced combining structures include `sequence`, which combines a list of state actions `fs: List[Rand[A]]` into a single state transition: `def sequence[A](fs: List[Rand[A]]): Rand[List[A]]`. This generalizes the ability to generate a list of random integers. The improved `rollDie` function, for instance, is defined as `def rollDie: Rand[Int] = map(nonNegativeLessThan(6))(_ + 1)`, ensuring the result is between 1 and 6.

This pattern of state management is generalized further by introducing `State[S,+A]`, representing a state action for any state type $S$. Defining `type Rand[A] = State[RNG, A]` merely specializes this general pattern. By utilizing `State` and `case class State[S,+A](run: S => (A,S))`, functional programming establishes a single, general-purpose mechanism for modeling stateful computations, enabling the creation of highly composable, modular, and type-safe libraries.

--- 

In parallel computing, functional approaches promote designing highly modular and composable structures, allowing parallel libraries to be insulated from the internal details of execution. A critical step in this design process is identifying common abstraction patterns, moving away from direct reliance on concurrency primitives like `java.lang.Thread` or `java.util.concurrent` library elements. Instead, the focus is on designing an ideal, high-level API.

Consider the problem of summing a list of integers. The standard sequential approach uses `ints.foldLeft(0)((a,b) => a + b)`. For a parallel implementation using divide-and-conquer, the method requires an efficient `splitAt` method provided by the `IndexedSeq` superclass. The recursive structure involves splitting the input sequence and summing the halves: 
```scala
def sum(ints: IndexedSeq[Int]): Int = 
if (ints.size <= 1)
    ints.headOption getOrElse 0
else {
    val (l,r) = ints.splitAt(ints.length/2)
    sum(l) + sum(r)
}
```
To abstract this into a parallel context, a container type `Par[A]` is proposed, alongside two foundational functions: `def unit[A](a: => A): Par[A]` to wrap a single value, and `def get[A](a: Par[A]): A` to extract the result.

Applying these conceptual abstractions to the sum problem yields a revised, parallel implementation:
```scala
def sum(ints: IndexedSeq[Int]): Int = 
if (ints.size <= 1)
    ints.headOption getOrElse 0
else {
    val (l,r) = ints.splitAt(ints.length/2)
    val sumL: Par[Int] = Par.unit(sum(l))
    val sumR: Par[Int] = Par.unit(sum(r))
    Par.get(sumL) + Par.get(sumR)
}
```

Further abstractions address the limitations of Java's threading model. The `Runnable` trait has a `run: Unit` method, and the `Thread` class has `start: Unit` and `join: Unit`. Both types are problematic because they lack return values, forcing developers to rely on side effects (like state mutation) to retrieve results, thereby compromising compositionality. Furthermore, `Thread` maps to OS threads, a scarce resource. A better approach is to define 'logical threads' to represent computational units, abstracting beyond physical resources.

Utilities like `java.util.concurrent.Future` and `ExecutorService` provide partial solutions. `ExecutorService`'s `def submit[A](a: Callable[A]): Future[A]` returns a `Future[A]` which has a `def get: A` method. However, these primitives are insufficient because: (1) `Future.get` blocks the calling thread, and (2) the API lacks an inherent mechanism for composing futures. The goal is to build a modular, compositional API suitable for direct use in functional programs.

To achieve true non-blocking parallelism, the design must solve the side-effect problem inherent in `get`. If `unit` evaluates its argument immediately, the subsequent call to `get` waits for that completion, which is sequential. The challenge is designing `unit` so that it represents an asynchronous computation but allows combination without calling `get` individually. The core principle is delaying the side-effect until the final step, ensuring that `Par.unit(sum(l))` and `Par.unit(sum(r))` do not run sequentially upon definition, thus enabling the two sides of the addition to truly execute in parallel.

--- 

In stream processing and lazy evaluation, non-strictness is a core functional property. A function is non-strict if it is allowed to not evaluate all its arguments, contrasting with a strict function that must evaluate every argument. This principle is visible in short-circuiting operators like `&&` and `||`, and in the `if` control construct.

To enforce controlled non-strictness in Scala, `if2[A]` was introduced: `def if2[A](cond: Boolean, onTrue: () => A, onFalse: () => A): A = if (cond) onTrue() else onFalse()`. Using the empty function literal `() => A` ensures the block runs only if the condition is met. A syntactic alias uses the arrow `=>` (e.g., `def if2[A](cond: Boolean, onTrue: => A, onFalse: => A): A = if (cond) onTrue else onFalse`), automatically wrapping the expression in a 'thunk' (unevaluated form) that must be explicitly forced for evaluation.

This concept is robustly implemented in `Stream[+A]`, a specialized trait modeling lazy lists. A stream has two constructors: `Empty` and `Cons[+A](h: () => A, t: () => Stream[A])`. The use of `() => A` and `() => Stream[A]` is structurally critical, forcing both the head (`h`) and tail (`t`) to be non-strict (thunks). This guarantees that the head and the computation of the tail are evaluated only once upon first demand, which is memoization.

The `Stream` object provides `cons[A](hd: => A, tl: => Stream[A]): Stream[A]`, managing this memoization. `Stream.apply[A](as: A*)` builds streams from elements `as`. If `as` is empty, it returns `Empty`; otherwise, it recursively uses `cons`, automatically wrapping initial head and subsequent tail components in thunks, thereby preserving laziness.

Accessing components requires handling thunks; `headOption: Option[A]` returns `None` for `Empty`, or `Some(h())` for `Cons(h, t)`, explicitly calling `h()` to force the head thunk while crucially *not* forcing the tail.

Core combinators (`map`, `filter`, `append`, `flatMap`) benefit from laziness. When applying these to `Stream(1,2,3,4).map(_ + 10).filter(_ % 2 == 0).toList`, the computation generates elements sequentially, saving memory as the garbage collector reclaims space for discarded values (e.g., 11 and 13).

This efficiency is vital for infinite streams. An infinite stream of ones, `val ones: Stream[Int] = Stream.cons(1, ones)`, can be processed with `ones.take(5).toList` (yielding `List(1, 1, 1, 1, 1)`) or `ones.exists(_ % 2 != 0)` (returning `true` immediately). However, terminating an infinite stream is critical: `ones.forAll(_ == 1)` causes an infinite loop (stack overflow) because the predicate never finds a non-matching element that allows termination.

Developers can generate streams using `constant[A](a: A)` (infinite stream of $a$), `from(n: Int)` (infinite sequence starting at $n$), or `fibs` (the infinite Fibonacci sequence). The most powerful mechanism is `unfold[A, S](z: S)(f: S => Option[(A, S)]): Stream[A]`. `unfold` takes an initial state $z$ and a function $f$ that returns `None` upon termination. `unfold` can redefine core builders: `def fibs`, `def from`, `def constant`, and `def ones`, maintaining constant memory usage.

Advanced combinators deepen structural capability. `startsWith[A](s: Stream[A])` checks if $s$ is a prefix of another stream. From this, `hasSubsequence[A](s: Stream[A])` can be implemented using `tails exists (_ startsWith s)`. The most powerful structural method is `def tails: Stream[Stream[A]]`, which returns a stream of all suffixes of the input sequence. For `Stream(1,2,3)`, `tails` generates `Stream(Stream(1,2,3), Stream(2,3), Stream(3), Stream())`.

## Children
- [[content/L0/purely-functional-state-modeling|purely-functional-state-modeling]] — Functional programming can model imperative programs using `State` actions, which are generalized functions that explicitly pass and return the program state, making the process referentially transparent.
- [[content/L0/purely-functional-parallelism-design|purely-functional-parallelism-design]] — The text introduces designing purely functional libraries for parallel and asynchronous computations, aiming to use pure functions and the substitution model to simplify reasoning. The process is illustrated by adapting the sequential summation of an `IndexedSeq[Int]` to a parallel approach, which necessitates defining a custom container type, `Par[A]`, and associated functions like `unit[A]` and `get[A]` to abstract away direct use of concurrency primitives.
- [[content/L0/functional-concurrency-modeling|functional-concurrency-modeling]] — While standard Java utilities like `java.lang.Thread` and `java.util.concurrent.Future` allow handling concurrency, these primitives are too low-level and non-compositional for pure functional programming. The text argues that a functional API must separate the description of computation from execution to achieve genuine concurrency without violating referential transparency.
