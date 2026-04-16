# monad-trait-and-combinators

**Parent:** [[content/L1/algebraic-functional-design-patterns|algebraic-functional-design-patterns]] — The Monad pattern unifies disparate types (like Option, Parser, Gen, Par) by providing a minimal abstract interface using only `unit` and `flatMap` to derive `map` and `map2`, enabling generalized operations such as `sequence` and `traverse` that ensure type safety and manage side effects within a structured functional algebra.

The concept of Monad aims to unify Parser, Gen, Par, Option, and other data types by defining a single abstract interface, allowing for the definition of functions like `map2` once, instead of repeating the definitions for every concrete data type. Following the previous focus on individual data types and finding minimal primitives, this section refines an abstract interface to a small set of primitives. 

Initially, a trait called `Mon` was introduced to house the desired functions. Since the goal was to define `map2`, the definition was added. This initial structure was found not to compile because the functions `map` and `flatMap` were undefined in that context. 

Consequently, the implementation of `map2` was used to add `map` and `flatMap` abstractly to the `Mon` interface. While the syntax for calling these functions changed (infix syntax was lost), the structure remained the same. The resulting `Mon` trait was:<br><pre>trait Mon[F[_]] {<br>def map[A,B](fa: F[A])(f: A => B): F[B]<br>def flatMap[A,B](fa: F[A])(f: A => F[B]): F[B]<br>def map2[A,B,C](fa: F[A], fb: F[B])(f: (A,B) => C): F[C] =<br>flatMap(fa)(a => map(fb)(b => f(a,b)))<br>}</pre>

This translation was mechanical: developers inspected the implementation of `map2` and added all the functions it utilized, namely `map` and `flatMap`, as suitably abstract methods to the `Mon` interface. The choice of the type constructor argument `F` was arbitrary; convention typically dictates using one-letter uppercase names like F, G, H, or M, N, P, or Q for such arguments.

Next, the goal was to determine if `flatMap` and `map` were a minimal set of primitives required for `map2`. Given that all data types that implemented `map2` also had a `unit` function, and knowing that `map` can be implemented using `flatMap` and `unit`, the authors selected `unit` and `flatMap` as the minimal set of primitives. A single concept, `Monad`, was established to unify all data types possessing these two functions. This Monad trait is defined as:<br><pre>trait Monad[F[_]] extends Functor[F] {<br>def unit[A](a: => A): F[A]<br>def flatMap[A,B](ma: F[A])(f: A => F[B]): F[B]<br><br>// Because Monad provides a default implementation of map, it extends Functor.<br>def map[A,B](ma: F[A])(f: A => B): F[B] =<br>flatMap(ma)(a => unit(f(a)))<br>def map2[A,B,C](ma: F[A], mb: F[B])(f: (A, B) => C): F[C] =<br>flatMap(ma)(a => map(mb)(b => f(a, b)))<br>}</pre>

All monads are functors, but not all functors are monads. By implementing the `Monad` instance for `Gen` (the `genMonad` object), developers only need to implement `unit` and `flatMap` to automatically gain `map` and `map2` for the `Gen` data type. This establishes that the Monad pattern allows developers to implement functionality once and apply it universally to any data type that supplies a Monad instance.

Other advanced functional operations can also be generalized and implemented using the `Monad` structure. For example:

1. **`sequence`**: `def sequence[A](lma: List[F[A]]): F[List[A]]`
2. **`traverse`**: `def traverse[A,B](la: List[A])(f: A => F[B]): F[List[B]]`
3. **`replicateM`**: This function implements the concept of replicating a computation within a monad: `def replicateM[A](n: Int, ma: F[A]): F[List[A]]`
4. **`product`**: This combines two monadic computations into a single pair: `def product[A,B](ma: F[A], mb: F[B]): F[(A, B)] = map2(ma, mb)((_, _))`
5. **`filterM`**: This function generalizes filtering when the condition itself is a monadic computation: `def filterM[A](ms: List[A])(f: A => F[Boolean]): F[List[A]]`
