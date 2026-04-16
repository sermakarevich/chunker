# monad-laws-and-definitions

**Parent:** [[content/L1/advanced-functional-abstractions-monads-applicatives|advanced-functional-abstractions-monads-applicatives]] — The Monad structure is defined by the minimal primitives `unit` and `flatMap`, which derivedly yield `map` and `map2`. The Monad is guaranteed to satisfy algebraic laws, including associativity and the two identity laws, while the `Applicative` abstraction uses `unit` and `map2` as its core building blocks; crucially, the Monad is a subtype of the Applicative because its $map2$ can be defined using `flatMap`.

To fully understand the Monad interface, developers must understand the laws that govern it. While all Monads must conform to the Functor laws (since a Monad[F] is a Functor[F]), the critical focus is on the laws constraining `flatMap` and `unit`.

### The Associative Law
To determine if combining three monadic values is associative, one must verify if the order of combination matters. This leads to the associative law for Monads. This law states that for any monadic value $x$, the following must hold: $$x.flatMap(f).flatMap(g) == x.flatMap(a => f(a).flatMap(g))$$ 
This law should apply not just to the `Gen` monad, but generally to `Parser`, `Option`, and any other type implementing the Monad interface.

**Proof for Option:**
*   **Case 1: $x$ is `None`**
    $$	ext{None.flatMap}(f).	ext{flatMap}(g) == 	ext{None.flatMap}(a ightarrow f(a).	ext{flatMap}(g))$$ 
    Since $	ext{None.flatMap}(f)$ is $	ext{None}$ for all functions $f$, both sides simplify to $	ext{None} == 	ext{None}$, confirming the law.
*   **Case 2: $x$ is `Some(v)`**
    $$	ext{Some}(v).	ext{flatMap}(f).	ext{flatMap}(g) == 	ext{Some}(v).	ext{flatMap}(a ightarrow f(a).	ext{flatMap}(g))$$ 
    Substituting $	ext{Some}(v)$ for $x$ on both sides yields:
    $$	ext{Some}(v).	ext{flatMap}(f).	ext{flatMap}(g) == 	ext{Some}(v).	ext{flatMap}(a ightarrow f(a).	ext{flatMap}(g))$$ 
    The process simplifies to: $$	ext{f(v)}.	ext{flatMap}(g) == (a ightarrow f(a).	ext{flatMap}(g))(v)$$ 
    By applying function application $(a ightarrow f(a).	ext{flatMap}(g))(v)$, the right side evaluates to $f(v).	ext{flatMap}(g)$, confirming the law holds for all $v$.

**Kleisli Composition (compose):**
While the Monad associative law does not appear similar to the monoid associative law ($	ext{op}(	ext{op}(x,y), z) == 	ext{op}(x, 	ext{op}(y,z))$), the law can be clarified by considering monadic functions. These functions, which map types like $A$ to monadic types like $F[B]$, are called Kleisli arrows. Kleisli arrows can be composed using a function called `compose[A,B,C](f: A ightarrow F[B], g: B ightarrow F[C]): A ightarrow F[C]`. The associative law for Monads can be stated symmetrically using composition: $$	ext{compose}(	ext{compose}(f, g), h) == 	ext{compose}(f, 	ext{compose}(g, h))$$ 

### The Identity Laws
Similar to how `zero` is the identity element for append in a monoid, `unit` acts as the identity element for composition in a monad. This is formalized by two laws: 

1.  **Left Identity:** $	ext{compose}(f, 	ext{unit}) == f$
2.  **Right Identity:** $	ext{compose}(	ext{unit}, f) == f$

These laws can also be expressed using `flatMap`: 
*   $	ext{flatMap}(x)(	ext{unit}) == x$
*   $	ext{flatMap}(	ext{unit}(y))(f) == f(y)$ 

(Note: The function $	ext{unit}$ takes a non-strict value ($	ext{=>} A$) and returns a monadic value ($F[A]$).)

Finally, a third minimal set of Monad combinators is $	ext{join}$, $	ext{map}$, and $	ext{unit}$. Developers should be able to implement $	ext{join}$ in terms of $	ext{flatMap}$, and conversely, implement $	ext{flatMap}$ or $	ext{compose}$ in terms of $	ext{join}$ and $	ext{map}$.

**Conclusion:**
Therefore, a monad is precisely defined by its operations and laws: it must implement one of the minimal sets of monadic combinators ($	ext{unit}$ and $	ext{flatMap}$, or $	ext{unit}$ and $	ext{compose}$, or $	ext{unit}$, $	ext{map}$, and $	ext{join}$) and satisfy the laws of associativity and identity. This is the only correct and precise definition of a monad.
