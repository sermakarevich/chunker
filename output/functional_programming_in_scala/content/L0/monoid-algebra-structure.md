# monoid-algebra-structure

**Parent:** [[content/L1/Est',|Est',]] — Hic

By the end of Part 2, developers gain comfort considering data types in terms of their algebras—which encompasses the operations they support and the laws governing those operations. Since the algebras of very different data types tend to share common patterns, this chapter begins identifying these patterns and leveraging them. The first purely algebraic structure considered is the monoid, which is defined solely by its algebra. Monoids can be useful because they are simple, ubiquitous, and useful, even if different monoid instances have little relation to one another.

Monoids are commonly encountered in programming, such as when working with lists, concatenating strings, or accumulating loop results. Monoids are useful in two key ways: they facilitate parallel computation by allowing problems to be broken into chunks that can be computed in parallel, and they can be composed to assemble complex calculations from simpler pieces.

### What is a monoid?

Consider the algebra of string concatenation. The operation includes the identity element, which is the empty string (`""`), such that combining any string `s` with the empty string—whether as `(s + "")` or `("" + s)`—results in `s`. Furthermore, the operation is associative, meaning the order of parenthesization does not matter: `((r + s) + t)` yields the same result as `(r + (s + t))`. The same rules apply to integer addition, which is associative and has an identity element of 0; multiplication is also associative and has an identity element of 1. Likewise, the Boolean operators `&&` and `||` are associative and have identity elements of `true` and `false`, respectively.

These examples demonstrate that algebras like this, which are defined by the laws of associativity and identity, are termed monoids. A monoid must satisfy the following structure:

1. A type, designated as `A`.
2. An associative binary operation, `op`, that accepts two values of type `A` and combines them into one: the law requires `op(op(x,y), z)` to equal `op(x, op(y,z))` for any choice of `x: A`, `y: A`, and `z: A`.
3. A value, designated as `zero: A`, that acts as an identity element for the operation: the law requires `op(x, zero)` to equal `x` and `op(zero, x)` to equal `x` for any `x: A`.

Developers can implement this structure using the following Scala trait:
```scala
trait Monoid[A] {
  def op(a1: A, a2: A): A
  val zero: A
  // Laws:
  // op(op(x,y), z) == op(x, op(y,z))
  // op(x, zero) == x
  // op(zero, x) == x
}
```

Concrete examples include:
*   **String Monoid:** `val stringMonoid = new Monoid[String] { def op(a1: String, a2: String) = a1 + a2; val zero = "" }`.
*   **List Monoid:** `def listMonoid[A] = new Monoid[List[A]] { def op(a1: List[A], a2: List[A]) = a1 ++ a2; val zero = Nil }`.

The abstract nature of an algebraic structure is that the monoid is defined by the type `A` and the `Monoid[A]` instance that satisfies the laws. This type becomes the monoid, not the other way around.

### Folding Lists with Monoids

Monoids are intimately connected with lists. The `foldLeft` and `foldRight` functions have signatures that accept an initial value and a combining function, where the combining function uses the monoid's operation (`op`).

When the list elements and the monoid's type are the same, both `foldRight` and `foldLeft` yield identical results because the monoid laws (associativity and identity) hold. For example, when folding a list of Strings: `val words = List("Hic", "Est", "Index")`, both `words.foldRight(stringMonoid.zero)(stringMonoid.op)` and `words.foldLeft(stringMonoid.zero)(stringMonoid.op)` result in the string `"HicEstIndex"`.

Because both `foldLeft` and `foldRight` are tail-recursive, the general function `concatenate` can be written using either fold: `def concatenate[A](as: List[A], m: Monoid[A]): A = as.foldLeft(m.zero)(m.op)`. When the list elements do not have a Monoid instance, developers can map over the list first to convert the elements into a type that does have a Monoid instance, using the function `foldMap`: `def foldMap[A,B](as: List[A], m: Monoid[B])(f: A => B): B`.
