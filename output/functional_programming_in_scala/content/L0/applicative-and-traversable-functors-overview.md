# applicative-and-traversable-functors-overview

**Parent:** [[content/L1/advanced-functional-abstractions-monads-applicatives|advanced-functional-abstractions-monads-applicatives]] — The Monad structure is defined by the minimal primitives `unit` and `flatMap`, which derivedly yield `map` and `map2`. The Monad is guaranteed to satisfy algebraic laws, including associativity and the two identity laws, while the `Applicative` abstraction uses `unit` and `map2` as its core building blocks; crucially, the Monad is a subtype of the Applicative because its $map2$ can be defined using `flatMap`.

To understand the full structure of a monadic interface, developers must realize that many combinators can be expressed using a single core interface: the `Monad`. This concept allows writing many combinators once for different data types, even if those types initially appear unrelated. The `Monad` abstract interface is powerful because it enables developers to write programs that behave in a purely functional manner, functionally resembling imperative code through the use of `flatMap`.

In addition to `Monad`, developers should learn about two related abstractions: `Applicative` and `Traversable` functors. `Applicative` functors are less powerful than `Monad` but are generally more common, and their study provides insight into how to discover such general abstractions. Although grasping the full significance of these abstractions may take time, recognizing them repeatedly in daily functional programming work aids understanding.

### Generalizing Monads (Sequence and Traverse)

Since developers have seen various operations, such as `sequence` and `traverse`, implemented many times across different monads, they generalized these implementations to work for any monad `F`: 

1. **`sequence`**: `def sequence[A](lfa: List[F[A]]): F[List[A]]`
2. **`traverse`**: `def traverse[A,B](as: List[A])(f: A => F[B]): F[List[B]]`

The implementation of `traverse` uses `map2` and `unit` in the following way: `as.foldRight(unit(List[B]()))((a, mbs) => map2(f(a), mbs)(_ :: _))`. Furthermore, it is noted that `map2` can be implemented using `flatMap`: `def map2[A,B,C](ma: F[A], mb: F[B])(f: (A,B) => C): F[C] = flatMap(ma)(a => map(mb)(b => f(a,b)))`. The core takeaway is that a large number of useful combinators on `Monad` can be defined using only `unit` and `map2`. The `traverse` combinator is an example of this, as it does not call `flatMap` directly, meaning it remains agnostic regarding whether `map2` is a primitive or a derived combinator.

This suggests an alternative abstraction built upon `unit` and `map2` as the primitives: the `Applicative` functor. While `Applicative` is less powerful than `Monad`, this limitation brings benefits. 

### The Applicative Trait

An `Applicative` functor is captured by a new interface, `Applicative`, which defines `map2` and `unit` as primitives. This interface must also implement the `Functor` trait. The `Applicative` trait defines the following structure:

```scala
trait Applicative[F[_]] extends Functor[F] {
  // primitive combinators
  def map2[A,B,C](fa: F[A], fb: F[B])(f: (A, B) => C): F[C]
  def unit[A](a: => A): F[A]
  // derived combinators
  def map[B](fa: F[A])(f: A => B): F[B] = map2(fa, unit(()))((a, _) => f(a))
  
  // Definition of traverse
  def traverse[A,B](as: List[A])(f: A => F[B]): F[List[B]] =
as.foldRight(unit(List[B]()))((a, fbs) => map2(f(a), fbs)(_ :: _))
}
```

This structure mandates that all `Applicative` instances are also `Functor` instances. The `Applicative` trait implements the `map` function using `map2` and `unit`: `def map[B](fa: F[A])(f: A => B): F[B] = map2(fa, unit(()))((a, _) => f(a))`. The implementation of `traverse` remains unchanged from its definition in the `Applicative` trait.

**EXERCISE 12.1:** Developers are prompted to transfer as many combinators as possible from the `Monad` interface to the `Applicative` interface, using only `map2` and `unit`, or methods derived from them.

**The Applicative Trait Continues:**

The `Applicative` trait is further extended to define:

*   **`sequence`**: `def sequence[A](fas: List[F[A]]): F[List[A]]`
*   **`replicateM`**: `def replicateM[A](n: Int, fa: F[A]): F[List[A]]`
*   **`product`**: `def product[A,B](fa: F[A], fb: F[B]): F[(A,B)]`

**EXERCISE 12.2:** Developers are challenged to prove that the name `Applicative` arises because the interface can be formulated using `unit` and the function `apply`, rather than `unit` and `map2`. This requires showing the equivalence of formulations by defining `map2` and `map` using `unit` and `apply`, and then establishing that `apply` can be implemented using `map2` and `unit`.

**EXERCISE 12.3:** The function `apply` proves useful for implementing `map3`, `map4`, and other higher-arity mapping functions. Developers must implement `map3` and `map4` using only `unit`, `apply`, and Scala's curried function methods.

**Making Monad a Subtype of Applicative:**

The `Monad` trait can be made a subtype of the `Applicative` trait by providing default implementations for the `Applicative` methods. This involves defining `def map2[A,B,C](fa: F[A], fb: F[B])(f: (A, B) => C): F[C] = flatMap(fa)(a => map(fb)(b => f(a,b)))` within the `Monad` trait. This declaration confirms that all monads are also applicative functors, and prevents the need for separate `Applicative` instances for data types that already satisfy the `Monad` interface.

In summary, the `Monad` trait provides the minimal set of primitives (`unit` and `flatMap`) for full functionality, but the `Applicative` trait provides a simpler and highly effective alternative structure using `unit` and `map2`.
