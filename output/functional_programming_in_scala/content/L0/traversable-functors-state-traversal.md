# traversable-functors-state-traversal

**Parent:** [[content/L1/functional-fp-architecture-context|functional-fp-architecture-context]] — The design of functional programming necessitates managing computations as first-class values, utilizing special types ('effects') like Option, Either, Par, and Stream to handle potential failures and side effects without violating referential transparency. Applicative funtors combine independent results using fixed structure (e.g., `map2`), while Monads are required when the result of one calculation influences subsequent steps (e.g., `flatMap`). State management across all traversable functors (like List, Tree) is generalized using the `mapAccum` function, which allows for writing reusable core combinators such as `toList` and `zipWithIndex` for any structure.

The `State` applicative functor is a particularly powerful structure. When using a `State` action to traverse a collection, developers can implement complex traversals that maintain an internal state. Although partially applying `State` requires significant type annotation, the commonality of state-based traversals allows for the creation of a specialized method to standardize these annotations:

```scala
def traverseS[S,A,B](fa: F[A])(f: A => State[S, B]): State[S, F[B]] =
traverse[({type f[x] = State[S,x]})#f,A,B](fa)(f)(Monad.stateMonad)
```

To demonstrate this concept, the following example shows a `State` traversal that assigns a position label to every element. This process utilizes an integer state, initialized to 0, and increments the state by 1 at each step:

**Listing 12.9 Numbering the elements in a traversable:**

```scala
def zipWithIndex[A](ta: F[A]): F[(A,Int)] =
traverseS(ta)((a: A) => (for {
  i <- get[Int]
  _ <- set(i + 1)
} yield (a, i))).run(0)._1
```

This `zipWithIndex` definition works for `List`, `Tree`, or any other traversable functor. Following this pattern, developers can manage a state of type `List[A]` to convert any traversable functor into a `List`:

**Listing 12.10 Turning traversable functors into lists:**

```scala
def toList[A](fa: F[A]): List[A] =
traverseS(fa)((a: A) => (for {
  as <- get[List[A]]
  _ <- set(a :: as)
} yield ())).run(Nil)._2.reverse
```

In `toList`, developers start with an initial state of the empty list `Nil`. At every element in the traversal, the current element is added to the front of the accumulated list, which is then set as the new state. Because this process constructs the list in reverse order, the final step involves reversing the resultant list from running the completed state action. Because the goal is to track the list state and not return a specific value, the action yields `()`. 

Similarly, the code for `toList` and `zipWithIndex` are nearly identical. This leads to factoring out the common logic into the `mapAccum` function:

**Listing 12.11 Factoring out our mapAccum function:**

```scala
def mapAccum[S,A,B](fa: F[A], s: S)(f: (A, S) => (B, S)): (F[B], S) =
traverseS(fa)((a: A) => (for {
  s1 <- get[S]
  (b, s2) = f(a, s1)
  _ <- set(s2)
} yield b)).run(s)

override def toList[A](fa: F[A]): List[A] = 
mapAccum(fa, List[A]())((a, s) => ((), a :: s))._2.reverse

def zipWithIndex[A](fa: F[A]): F[(A, Int)] = 
mapAccum(fa, 0)((a, s) => ((a, s), s + 1))._1
```

These general functions are used when working with traversable functors.

### Uses of Traverse

**EXERCISE 12.16 (Reverse):** Developers are tasked with writing a function `reverse[A](fa: F[A]): F[A]` that reverses any traversable functor, which must obey the law: `toList(reverse(x)) ++ toList(reverse(y)) == reverse(toList(y) ++ toList(x))` for appropriate types $x$ and $y$.

**EXERCISE 12.17 (FoldLeft):** Developers must use `mapAccum` to provide a default implementation of `foldLeft` for the `Traverse` trait.

**12.7.3 Combining traversable structures:**
The inherent nature of a traversal is that it must preserve the shape of its argument, which is both a strength and a weakness. This difficulty is evident when combining two structures. Given a `Traverse[F]`, developers seek a way to combine `F[A]` and `F[B]` into `F[C]`. The generic `zip` function attempts to use `mapAccum` for this purpose:

**Listing 12.12 Combining two different structure types:**

```scala
def zip[A,B](fa: F[A], fb: F[B]): F[(A, B)] = 
(mapAccum(fa, toList(fb)) { 
case (a, Nil) => sys.error("zip: Incompatible shapes.")
case (a, b :: bs) => ((a, b), bs)
})._1
```

This version of `zip` cannot handle arguments with differing 
