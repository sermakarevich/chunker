# api-algebra-deadlock-analysis

**Parent:** [[content/L1/functional-api-algebra-and-parallel-combinator-laws|functional-api-algebra-and-parallel-combinator-laws]] — The design of a functional API must be treated as an algebra governed by laws, such as the mandatory requirement that `map(unit(1))(_ + 1) == unit(2)` and that `map(y)(id) == y`. The parallel combinator `fork` must satisfy the law `fork(x) == x`, but its current implementation risks deadlocking when using a fixed-size thread pool (like `Executors.newFixedThreadPool(1)`) because the outer `Callable` blocks on the inner computation's `get` call within the same single thread.

The conceptual design of an API requires defining its behavior through an algebra—a set of operations combined with specific axioms or properties (laws). While it may seem unusual to state and prove such properties about an API, this practice is crucial in functional programming because side effects and hidden assumptions severely undermine compositionality, making it difficult or impossible to treat API components as black boxes. For instance, if the law positing that `fork(x)` is equivalent to `x` for all expressions `x` and all choices of `ExecutorService` does not hold, general-purpose combinators like `parMap` would lose their soundness, potentially leading to dangerous issues such as deadlocks in the usage of these combinators. 

Specifically, a subtle bug occurs in most implementations of `fork` when using an `ExecutorService` backed by a fixed-size thread pool (such as those created by `Executors.newFixedThreadPool`). If the maximum number of threads in the pool is limited to one, the following code example will likely deadlock:

`val a = lazyUnit(42 + 1)`
`val S = Executors.newFixedThreadPool(1)`
`println(Par.equal(S)(a, fork(a)))`

The deadlock arises from the implementation of `fork`: `def fork[A](a: => Par[A]): Par[A] = es => es.submit(new Callable[A] { def call = a(es).get })`. This structure results in the outer `Callable` being submitted and handled by the sole available thread. However, within that thread, the code then submits and blocks, waiting for the result of a second `Callable` via `a(es).get`. Because the thread pool is limited to one thread, there are no available threads to execute the second `Callable`, causing a deadlock.

To test the robustness of the `fork` implementation, developers should re-examine the law `fork(x) == x` and determine if it holds for the specific implementation or if the law needs refinement (e.g., stipulating a requirement for unbounded thread pools).

Alternative implementations for `fork` were considered: 
1. `def fork[A](a: => Par[A]): Par[A] = es => fa(es)`: This avoids deadlock but fails to genuinely fork a separate logical thread for evaluating `fa`, meaning `fork(hugeComputation)(es)` would run `hugeComputation` in the main thread. This variant is, however, useful because it allows the computation delay until it is actually needed. This combinator is named `delay`.
2. To truly run arbitrary computations over fixed-size thread pools, a different, fully non-blocking representation of `Par` is necessary. The essential problem with the current representation is that a value cannot be retrieved from a `Future` without the current thread blocking on its `get` method. A representation of `Par` that avoids resource leaks and blocking requires that the implementations of `fork` and `map2` never call a method that blocks the current thread, such as `Future.get`.
