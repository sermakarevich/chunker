# functor-monad-algebra

**Parent:** [[content/L1/algebraic-functional-design-patterns|algebraic-functional-design-patterns]] — The Monad pattern unifies disparate types (like Option, Parser, Gen, Par) by providing a minimal abstract interface using only `unit` and `flatMap` to derive `map` and `map2`, enabling generalized operations such as `sequence` and `traverse` that ensure type safety and manage side effects within a structured functional algebra.

Following the introduction of the monoid, which established the first purely algebraic interface by defining an abstract structure using only a collection of laws and operations, the discussion moves to identifying broader abstract structures within the written libraries. The goal is to factor out code duplication across various implemented combinator libraries, leading to the discovery of two new abstract interfaces: Functor and Monad.

### 11.1 Functors: Generalizing the map function

In Parts 1 and 2, multiple combinator libraries were written. Each case involved defining a small set of primitives and then deriving numerous combinators based on those primitives. Similarities were observed in the derived `map` function across different data types. For the types `Gen`, `Parser`, and `Option`, the `map` function signatures were defined as:

*   `def map[A,B](ga: Gen[A])(f: A => B): Gen[B]`
*   `def map[A,B](pa: Parser[A])(f: A => B): Parser[B]`
*   `def map[A,B](oa: Option[A])(f: A => B): Option[A]`

The names Functor and Monad originated in category theory, but specific knowledge of category theory is not required to understand this content. The core idea is captured by the `Functor` trait, which parameterizes the `map` function over a type constructor, `F[_]`, similar to how `Foldable` was parameterized.

```scala
trait Functor[F[_]] {
  def map[A,B](fa: F[A])(f: A => B): F[B]
}
```

When a type constructor, such as `List` (or `Option`, or `F`), implements the `Functor[F]` instance, that type constructor is deemed a functor. For example, the `List` instance is implemented as:

```scala
val listFunctor = new Functor[List] {
  def map[A,B](as: List[A])(f: A => B): List[B] = as map f
}
```

This abstraction allows for defining useful functions algebraically. For instance, if `F` is a functor and we consider the product type `F[(A, B)]`, we can define a generic `distribute` function to extract the components: 

```scala
trait Functor[F[_]] {
  // ...
  def distribute[A,B](fab: F[(A, B)]): (F[A], F[B]) = 
    (map(fab)(_._1), map(fab)(_._2))
}
```

Applying `distribute` to `List[(A, B)]` results in two lists of the same length: one containing all `A` values and the other containing all `B` values; this operation is known as `unzip`. Similarly, if we apply this abstract reasoning to a sum/coproduct (like `Either`), we can define `codistribute[A,B](e: Either[F[A], F[B]]): F[Either[A, B]]`, which handles the pattern of generating either `A` or `B` based on the input's structure.

### 11.1.1 Functor Laws

When creating an abstraction like `Functor`, the required laws are crucial for reasoning about the algebra independently of the instances. For `Functor`, the key law to stipulate is the identity law: mapping over a structure `x` with the identity function must equal `x` itself.

`map(x)(a => a) == x`

This law dictates that the `map` function must 
