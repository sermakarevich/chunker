# algebraic-functional-design-patterns

**Parent:** [[content/L2/functional-algebra-design-patterns-2|functional-algebra-design-patterns-2]] — The advanced functional API is built on a functional algebra, requiring the explicit use of ADTs like `Option` and `Either` for controlled error/control flow, and relies on `Stream[+A]` for lazy, memory-efficient data transformation by avoiding intermediate lists. Concurrency uses `Par[A]` governed by the non-blocking Actor model, while complex state and structure composition is unified by the Monad type class (requiring `unit` and `flatMap`) and specialized algebraic structures like the Monoid (e.g., `mapMergeMonoid`).

The synthesis of advanced functional API design requires establishing deep algebraic structures to model computation, control flow, and data transformation. This development process mandates treating computation itself as a first-class value, necessitating that the API be modeled as a rigorous functional algebra consisting of data types, functions, and formally defined laws (axioms).

### Core Abstractions: Functor, Monad, and Functor Laws

The foundational structure is the **Functor** trait, which parameterizes the general concept of the `map` function over an arbitrary type constructor, `F[_]`. This trait defines: `def map[A,B](fa: F[A])(f: A => B): F[B]`. Any type constructor, such as `List`, `Option`, or `F`, that implements the `Functor[F]` instance is considered a functor. The implementation of `map` allows for defining useful functions algebraically; for instance, if `F` is a functor, the product type `F[(A, B)]` can be processed by a generic `distribute` function, which extracts components via `map(fab)(_._1)` and `map(fab)(_._2)`, an operation commonly known as `unzip`. Furthermore, applying this reasoning to a sum/coproduct (like `Either`) allows for defining `codistribute[A,B](e: Either[F[A], F[B]]]): F[Either[A, B]]`, handling the pattern of generating either `A` or `B` based on the input's structure.

For a structure to be recognized as a Functor, it must satisfy key laws. The fundamental law for `Functor` is the identity law: `map(x)(a => a) == x`. This law mandates that mapping over a structure $x$ using the identity function must result in $x$ itself.


### Algebraic Data Types and Control Flow Management

Type safety and comprehensive error handling are paramount in modern functional programming. Best practices require explicitly encapsulating all potential effects, avoiding traditional mechanisms like runtime exceptions or sentinel values. For managing non-fatal control flow, two specialized Algebraic Data Types (ADTs) are critical: `Option[+A]` and `Either[+A, +B]`.

1.  **`Option[+A]`**: This type models potential presence or absence, defined by two cases: `Some[+A](get: A)` for a defined value, and `None` for an undefined state. Using `Option[Double]`, for example, ensures that failure (like calculating the mean of an empty sequence) is elevated to a static, compile-time contract, improving upon boilerplate `try-catch` blocks. $	ext{Option}$ is designed to define *total functions*.
2.  **`Either[+A, +B]`**: This provides a structured, two-sided mechanism: success is carried by `Right[+A]`, and failure/error is represented by `Left[+B]`. These constructs are Higher-Order Functions (HOFs) that abstract complex error propagation patterns, guaranteeing reliable, compile-time checked error handling.


### Advanced Data Structures and Composition

#### Streams and Non-Strictness

Efficiency in data transformation is handled by leveraging *non-strictness*, or laziness, to avoid the computational and memory overhead of creating numerous temporary intermediate data structures. Traditional list processing (e.g., `List(1, 2, 3, 4)` through `map(_ + 10).filter(_ % 2 == 0).map(_ * 3)`) requires multiple passes, leading to significant memory allocation. Non-strictness, where a function is permitted not to evaluate all its arguments, mitigates this issue.

This concept is robustly implemented in `Stream[+A]`, a specialized trait for lazy lists. Structurally, `Stream` is defined by `Empty` (for empty streams) and `Cons[+A](h: () => A, t: () => Stream[A])` (for non-empty streams). The use of empty function literals (`() => A` and `() => Stream[A]`) forces both the head (`h`) and tail (`t`) components to be non-strict (thunks). This is structurally critical because it guarantees that both the head value and the tail computation are evaluated only once upon first demand, a process known as memoization. The smart constructor `cons[A](hd: => A, tl: => Stream[A]): Stream[A]` manages this memoization, while `Stream.apply[A](as: A*)` builds streams recursively using `cons`, automatically wrapping all components in thunks.

Accessing stream components requires explicit thunk handling; for example, `headOption: Option[A]` returns `None` if the stream is `Empty`, or `Some(h())` if it is `Cons(h, t)`, explicitly calling `h()` without forcing the tail. Utility methods include `take(n)` (getting the first $n$ elements), `drop(n)` (skipping the first $n$), and `takeWhile(p: A => Boolean)` (filtering based on predicate $p$).

Core combinators like `map`, `filter`, `append`, and `flatMap` benefit immensely from laziness. They chain transformations without intermediate results; `Stream(1,2,3,4).map(_ + 10).filter(_ % 2 == 0).toList` demonstrates sequential element generation, saving memory and allowing the garbage collector to reclaim space, which is vital for infinite streams. Infinite streams can be safely processed, such as `val ones: Stream[Int] = Stream.cons(1, ones)` being analyzed via `ones.take(5).toList` or `ones.exists(_ % 2 != 0)`. However, developers must avoid infinite loops, like `ones.forAll(_ == 1)`, which causes a stack overflow.

Generators are powerful, including `constant[A](a: A)` and `from(n: Int)` (infinite sequence). The most generalized builder is the corecursive function `unfold[A, S](z: S)(f: S => Option[(A, S)]): Stream[A]`, which takes an initial state $z$ and function $f$, terminating when $f$ returns `None`. `unfold` defines builders like `constant` and `from`, and implements combinators like `map`, `take`, `takeWhile`, and `zipWith[B](s2: Stream[B]): Stream[(A, B)]`. A paired function, `zipAll[B](s2: Stream[B]): Stream[(Option[A], Option[B])]`, handles termination when either input stream is exhausted using `Option` tracking.

Structural methods include `def startsWith[A](s: Stream[A]): Boolean` (checking prefix relationship) and the critical `def tails: Stream[Stream[A]]` (returning a stream of all suffixes; e.g., for `Stream(1,2,3)`, this yields `Stream(Stream(1,2,3), Stream(2,3), Stream(3), Stream())`).

#### Concurrency and Parallelism (Par)

Concurrency and parallelism are managed using the `Par[A]` data type, designed to represent a non-blocking computation. Unlike standard Java blocking mechanisms (which require calling `.get()`), `Par[A]` utilizes a continuation function `k: A => Unit`, which handles the result $A$ and performs subsequent effects, confining any internal side effects (`A => Unit`) and making them unobservable to the user.

The formalization of parallel concepts is governed by mathematical laws. For instance, `map(unit(1))(_ + 1) == unit(2)` and `map(y)(id) == y`. Advanced combinators, such as `map2[A,B,C](p: Par[A], p2: Par[B])(f: (A,B) => C): Par[C]`, require sophisticated state management.

To ensure reliable compositionality, especially in fixed-size thread pools (like `Executors.newFixedThreadPool(1)`), the **Actor** model is employed. An Actor processes messages sequentially, maintaining state (e.g., two variables, `ar: Option[A]` and `br: Option[B]` for `map2`). When the first result arrives, the Actor stores it and waits for the second result; upon receipt, it executes the combining function $f$ and propagates the final $C$ result. This non-blocking design successfully allows combinators like `parMap(List.range(1, 100000))(math.sqrt(_))` to run efficiently using a limited thread pool (e.g., two threads) without exhausting resources, validating the law of forking even under resource constraints. 

*Note on Deadlock:* A specific deadlock case arises when using an `ExecutorService` backed by a fixed-size thread pool of size one, attempting to evaluate `println(Par.equal(S)(a, fork(a)))` for `val a = lazyUnit(42 + 1)`, because the internal `fork` implementation blocks waiting for the result of a second `Callable` on the sole available thread.


### Monoids and Algebraic Composition

The **Monoid** abstraction is a fundamental algebraic structure defined by an associative binary operation (`op`) and an identity element (`zero`). Monoids facilitate parallel computation and the composition of complex calculations from simpler, contained parts.

1.  **Product Monoid**: If $A$ and $B$ are monoids, their product type $(A, B)$ is also a monoid. The required function is `def productMonoid[A,B](A: Monoid[A], B: Monoid[B]): Monoid[(A,B)]`, which relies on the fact that $A.	ext{op}$ and $B.	ext{op}$ are both associative.
2.  **Map Merge Monoid**: A monoid exists for merging key-value Maps, provided the value type is itself a monoid. This is implemented by `mapMergeMonoid[K,V]`. This structure utilizes `V: Monoid[V]` and defines: 
    $$	ext{def mapMergeMonoid}[K,V](	ext{V}: 	ext{Monoid}[	ext{V}]):	ext{Monoid}[	ext{Map}[K, 	ext{V}]] = 	ext{new Monoid}[	ext{Map}[K, 	ext{V}]] 	ext{ { def zero = Map}[K,V]() \ 	ext{def op}(a: 	ext{Map}[K, 	ext{V}], b: 	ext{Map}[K, 	ext{V}]) = (a.	ext{keySet} ++ b.	ext{keySet}).	ext{foldLeft}(	ext{zero}) 	ext{ { (acc,k) => acc.updated}(k, 	ext{V}.	ext{op}(a.	ext{getOrElse}(k, 	ext{V}.	ext{zero}), b.	ext{getOrElse}(k, 	ext{V}.	ext{zero})))} 	ext{ }$$ 

This allows defining complex nested monoids. For example, `M: Monoid[Map[String, Map[String, Int]]]` can be constructed by combining `mapMergeMonoid` iteratively with the `intAddition` monoid: `val M: Monoid[Map[String, Map[String, Int]]] = mapMergeMonoid(mapMergeMonoid(intAddition))`. Using `M.op` demonstrates sophisticated composition of data maps.


### The Monad: Unification of Computational Contexts

Following the structure of Functor, the **Monad** aims to unify disparate data types—including `Parser`, `Gen`, `Par`, and `Option`—by defining a single, abstract interface. The goal is to enable functions like `map2` to be defined once, eliminating code duplication across different concrete types.

Initially, a trait `Mon` was introduced, leading to the definition of `map2`. This definition subsequently required the abstract inclusion of `map` and `flatMap` to the `Mon` interface, resulting in the structure:
$$	ext{trait Mon}[	ext{F}[	ext{_}]]$$: 
$$	ext{def map}[	ext{A}, 	ext{B}](	ext{fa}: 	ext{F}[	ext{A}])(	ext{f}: 	ext{A} 	o 	ext{B}): 	ext{F}[	ext{B}]$$
$$	ext{def flatMap}[	ext{A}, 	ext{B}](	ext{fa}: 	ext{F}[	ext{A}])(	ext{f}: 	ext{A} 	o 	ext{F}[	ext{B}]): 	ext{F}[	ext{B}]$$
$$	ext{def map2}[	ext{A}, 	ext{B}, 	ext{C}](	ext{fa}: 	ext{F}[	ext{A}], 	ext{fb}: 	ext{F}[	ext{B}])(	ext{f}: (	ext{A}, 	ext{B}) 	o 	ext{C}): 	ext{F}[	ext{C}] = 	ext{flatMap}(	ext{fa})(	ext{a} 	o 	ext{map}(	ext{fb})(	ext{b} 	o 	ext{f}(	ext{a}, 	ext{b})))$$ 

The minimal set of primitives required for this abstraction is `unit` and `flatMap`. Thus, the final `Monad` trait is defined as:
$$	ext{trait Monad}[	ext{F}[	ext{_}]] 	ext{ extends Functor}[	ext{F}]:$$ 
$$	ext{def unit}[	ext{A}](	ext{a}: 	ext{=>} 	ext{A} ): 	ext{F}[	ext{A}]$$
$$	ext{def flatMap}[	ext{A}, 	ext{B}](	ext{ma}: 	ext{F}[	ext{A}])(	ext{f}: 	ext{A} 	o 	ext{F}[	ext{B}]): 	ext{F}[	ext{B}]$$
$$	ext{def map}[	ext{A}, 	ext{B}](	ext{ma}: 	ext{F}[	ext{A}])(	ext{f}: 	ext{A} 	o 	ext{B}): 	ext{F}[	ext{B}] = 	ext{flatMap}(	ext{ma})(	ext{a} 	o 	ext{unit}(	ext{f}(	ext{a})))$$ 
$$	ext{def map2}[	ext{A}, 	ext{B}, 	ext{C}](	ext{ma}: 	ext{F}[	ext{A}], 	ext{mb}: 	ext{F}[	ext{B}])(	ext{f}: (	ext{A}, 	ext{B}) 	o 	ext{C}): 	ext{F}[	ext{C}] = 	ext{flatMap}(	ext{ma})(	ext{a} 	o 	ext{map}(	ext{mb})(	ext{b} 	o 	ext{f}(	ext{a}, 	ext{b})))$$ 

Implementing the `Monad` instance for `Gen` (the `genMonad` object) allows developers to automatically gain `map` and `map2` for the `Gen` data type by only implementing `unit` and `flatMap`. The Monad pattern permits generalizing advanced operations such as:

1.  **`sequence`**: Converts a list of monadic computations to a computation over a list of values: $	ext{def sequence}[	ext{A}](	ext{lma}: 	ext{List}[	ext{F}[	ext{A}]]): 	ext{F}[	ext{List}[	ext{A}]]$ 
2.  **`traverse`**: Transforms a list of values using a monadic function: $	ext{def traverse}[	ext{A}, 	ext{B}](	ext{la}: 	ext{List}[	ext{A}])(	ext{f}: 	ext{A} 	o 	ext{F}[	ext{B}]): 	ext{F}[	ext{List}[	ext{B}]]$ 
3.  **`replicateM`**: Replicates a monadic computation $n$ times: $	ext{def replicateM}[	ext{A}](	ext{n}: 	ext{Int}, 	ext{ma}: 	ext{F}[	ext{A}]): 	ext{F}[	ext{List}[	ext{A}]]$ 
4.  **`product`**: Combines two monadic computations into a pair: $	ext{def product}[	ext{A}, 	ext{B}](	ext{ma}: 	ext{F}[	ext{A}], 	ext{mb}: 	ext{F}[	ext{B}]): 	ext{F}[(	ext{A}, 	ext{B})] = 	ext{map2}(	ext{ma}, 	ext{mb})((_, _))$ 
5.  **`filterM`**: Filters a list where the condition itself is a monadic computation: $	ext{def filterM}[	ext{A}](	ext{ms}: 	ext{List}[	ext{A}])(	ext{f}: 	ext{A} 	o 	ext{F}[	ext{Boolean}]): 	ext{F}[	ext{List}[	ext{A}]]$

## Children
- [[content/L0/i1,i2|i1,i2]] — o1
- [[content/L0/functor-monad-algebra|functor-monad-algebra]] — The Functor trait generalizes the `map` function across type constructors like `Gen`, `Parser`, and `Option`, establishing a core algebraic pattern. It defines laws, such as `map(x)(a => a) == x`, that allow for algebraic reasoning and the definition of universal functions like `unzip` and `codistribute`.
- [[content/L0/monad-trait-and-combinators|monad-trait-and-combinators]] — The Monad trait unifies various data types (like Parser, Gen, Par, Option) by defining map, flatMap, and map2 abstractly. It establishes that `unit` and `flatMap` are the minimal required primitives, providing default implementations for all other functions, such as `map` and `map2`, which can then be applied to any data type providing a Monad instance.
