# purely-functional-parallelism-design

**Parent:** [[content/L1/functional-abstraction-patterns|functional-abstraction-patterns]] — Functional programming mandates explicit state management via generalizations like `State[S,A]` (e.g., `Rand[A] = State[RNG, A]`) and utilizes combinators such as `map`, `map2`, and `sequence` to model state transitions abstractly. Furthermore, functional APIs for parallel computations (`Par[A]`) and lazy streams (`Stream[A]`) solve issues of side effects, excessive intermediate data structure allocation, and forced sequential execution, respectively, by ensuring non-strict evaluation and controlled side-effect timing.

Purely functional programming requires explicit state management. While traditional imperative programming uses shared mutable memory for communication among execution threads, which can lead to difficult-to-reason-about issues like race conditions and deadlocks, functional programming aims to build purely functional libraries for parallel and asynchronous computations. By describing parallel programs using only pure functions, the system can leverage the substitution model, simplifying reasoning about concurrent computations. The overall goal of functional library design is to promote highly composable and modular structures, maintaining the principle of separating the description of a computation from its actual execution. Throughout the design process, it is necessary to identify common patterns and fundamental abstractions to remove code duplication. A core goal is to design a parallel library that is insulated from the internal details of execution, allowing users to write programs at a high level. For instance, a combinator named `parMap` could apply a function `f` to every element in a collection simultaneously, as shown by `val outputList = parMap(inputList)(f)`. 

To begin the design process, one examines a simple, parallelizable computation: summing a list of integers. The standard sequential approach uses a fold, such as `def sum(ints: Seq[Int]): Int = ints.foldLeft(0)((a,b) => a + b)`. However, by using a divide-and-conquer algorithm, the sum can be calculated in parallel. This requires the `IndexedSeq` superclass, which provides an efficient `splitAt` method. The parallel implementation uses the following recursive structure:
```scala
def sum(ints: IndexedSeq[Int]): Int =
if (ints.size <= 1)
    ints.headOption getOrElse 0
else {
    val (l,r) = ints.splitAt(ints.length/2)
    sum(l) + sum(r)
}
```
When designing a library, the focus should be on abstracting common concerns from such examples. Instead of forcing the design to rely directly on concurrency primitives (like `java.lang.Thread` or `java.util.concurrent` library elements), the design process should work backward from the ideal API. Observing the recursive call structure, any data type representing parallel computations must be able to contain a result. Therefore, the text proposes creating a container type, `Par[A]` (for parallel), and defining two essential functions: `def unit[A](a: => A): Par[A]` to wrap a single value, and `def get[A](a: Par[A]): A` to extract the resulting value. Applying these conceptual abstractions to the summation example leads to the revised definition:
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
