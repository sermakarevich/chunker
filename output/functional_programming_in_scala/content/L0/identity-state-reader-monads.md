# identity-state-reader-monads

**Parent:** [[content/L1/advanced-functional-abstractions-monads-applicatives|advanced-functional-abstractions-monads-applicatives]] — The Monad structure is defined by the minimal primitives `unit` and `flatMap`, which derivedly yield `map` and `map2`. The Monad is guaranteed to satisfy algebraic laws, including associativity and the two identity laws, while the `Applicative` abstraction uses `unit` and `map2` as its core building blocks; crucially, the Monad is a subtype of the Applicative because its $map2$ can be defined using `flatMap`.

### The Identity Monad
To understand the identity monad, consider the simple wrapper type `Id[A]` defined as `case class Id[A](value: A)`. Developers should implement `map` and `flatMap` as methods on this class and define an instance for the `Monad[Id]` trait.

Although `Id` is merely a simple wrapper, it behaves as an identity because the wrapped type and the unwrapped type are totally isomorphic, meaning information can be lostlessly converted between them. When applying `Id`, the action is equivalent to variable substitution. For example, running `Id("Hello, ") flatMap (a => Id("monad!") flatMap (b => Id(a + b)))` results in `Id("Hello, monad!")`. Using a for-comprehension yields the same result: `for { a <- Id("Hello, "); b <- Id("monad!") } yield a + b` also results in `Id("Hello, monad!")`. Because `flatMap` simply substitutes variables, the behavior of `Id` is identical to using standard Scala variables (e.g., `val a = "Hello, "` and `val b = "monad!"`, giving `a + b` with the result `"Hello, monad!"`). Consequently, the `Id` wrapper provides no functional difference.

### The State Monad and Partial Type Application
Developers can examine the `State` data type, which stores a function `run: S => (A, S)`, where `S` is the state type and `A` is the result type. The `State` type supports `map` and `flatMap` combinators. Since the `Monad` trait requires a single-argument type constructor, developers cannot simply use `Monad[State]`. However, by fixing the first type argument `S`, they can define a type constructor that fits the `Monad` pattern. For instance, they can create an `IntState` type alias: `type IntState[A] = State[Int, A]`. Since `IntState` is the required structure, developers define an `IntStateMonad` object which implements `Monad[IntState]`:

```scala
object IntStateMonad extends Monad[IntState] {
  def unit[A](a: => A): IntState[A] = State(s => (a, s))
  def flatMap[A,B](st: IntState[A])(f: A => IntState[B]): IntState[B] = st flatMap f
}
```

Due to the repetitive nature of writing a `Monad` instance for every specific state type, developers utilize a mechanism similar to lambda syntax at the type level. They define a `StateMonad` trait that provides a generalized `Monad` instance for any given state type `S` using an anonymous type constructor (a type lambda). The resulting `StateMonad[S]` instance defines: `def unit[A](a: => A): State[S,A] = State(s => (a, s))` and `def flatMap[A,B](st: State[S,A])(f: A => State[S,B]): State[S,B] = st flatMap f`.

Developers can observe that the state action execution, visible through a for-comprehension, simulates imperative variable binding. For instance, the function `zipWithIndex[A]` numbers all elements in a list by using a `State` action that maintains and increments an `Int` state. The for-comprehension utilizes `getState` (to read the current state) and `setState` (to propagate the new state). The combination of `unit` and `flatMap` ensures that the current state is available to `getState`, and that the new state value from `setState` is passed to all subsequent actions. The core distinction is that the `Id` monad performs only unwrapping and rewrapping, while the `State` monad explicitly tracks and propagates the current state (the `Int` value) between statements. This reveals that a monad specifies what happens at statement boundaries: for `Id`, nothing happens; for `State`, the most current state is passed to the next statement; and for `Option`, a statement may return `None` to terminate the program; and for `List`, a statement may return multiple results, allowing subsequent statements to run for each result.

### Advanced Monadic Pattern: Reader
For a type like `Reader[R, A]`, which wraps a function `run: R => A`, developers define a `readerMonad[R]` instance. This instance implements `unit[A](a: => A): Reader[R,A]` and `flatMap[A,B](st: Reader[R,A])(f: A => Reader[R,B]): Reader[R,B]`. This pattern allows `Reader` to behave as a monad, enabling the use of standard monadic combinators.

**Summary:** The Identity monad (`Id[A]`) simply wraps a value, serving as an algebraic identity because the wrapped type is isomorphic to the unwrapped type. The State monad (`State[S, A]`) and the `Reader[R, A]` monad demonstrate that monads provide a structure for sequencing computations. While `Id` performs only unwrapping/rewrapping, `State` actively tracks and propagates a state value (`S`) between statements using `getState` and `setState`. The `Reader` monad allows composition by treating a function `R => A` as an effect that depends on an external environment `R`.
