# refining-the-parallel-api

**Parent:** [[content/L1/functional-par-design-patterns|functional-par-design-patterns]] — Functional programming manages non-fatal control flow using types like `Option[+A]` and `Either[+A, +B]`, while efficiency is achieved through non-strictness and the specialized lazy structure `Stream[+A]`. Parallel computations are modeled abstractly by `Par[A]`, requiring combinators like `map2` and `fork` to ensure concurrent execution and maintain API purity, allowing complex operations like `sum` to be recursively defined and generalized through the derivation of `map` from `map2`.

Given existing combinators for parallel computations, such as `map2` and `unit`, developers can express new functionalities. For example, if a user has a parallel computation represented by `Par[List[Int]]`, and the goal is to produce a `Par[List[Int]]` whose contained list is sorted, one can define the function `sortPar`:

`def sortPar(parList: Par[List[Int]]): Par[List[Int]]`

Instead of executing the parallel computation (`Par[List[Int]]`) and sorting the resulting list externally, one can use existing combinators. Since `map2` is the only available combinator allowing manipulation of a `Par`'s internal value, passing `parList` to the first argument of `map2` and passing a no-operation argument (e.g., `unit(())`) to the second argument enables access to the internal list structure. The function `sortPar` is implemented as:

`def sortPar(parList: Par[List[Int]]): Par[List[Int]] = map2(parList, unit(()))((a, _) => a.sorted)`

This demonstrates how the `map2` combinator facilitates transforming the value inside a parallel computation. This process can be generalized by creating a `map` function, which allows mapping any function of type `A => B` over a `Par[A]` value to produce a `Par[B]`. The implementation of this generalized `map` function is:

`def map[A,B](pa: Par[A])(f: A => B): Par[B] = map2(pa, unit(()))((a,_) => f(a))`

With this generalized `map` function, the specific `sortPar` function becomes simpler: `def sortPar(parList: Par[List[Int]]) = map(parList)(_.sorted)`.

It is important to recognize that the ability to implement `map` using `map2` (by passing `pa` to one side and `unit(())` to the other side of `map2`) shows that `map2` is strictly more powerful than `map`. This illustrates a common pattern in library design where a seemingly primitive function may be expressible using a more powerful, foundational primitive.

Furthermore, one may consider implementing a function `parMap` which combines $N$ parallel computations. Unlike `map2`, which only combines two computations, `parMap` needs to combine a list of parallel computations (`List[A]`) using a function `f: A => B` to return `Par[List[B]]`:

`def parMap[A,B](ps: List[A])(f: A => B): Par[List[B]]`

While it is possible to define `parMap` as a new primitive, in certain situations, developers might be able to implement the desired operation more efficiently by taking advantage of specific assumptions about the underlying representation of the data types.
