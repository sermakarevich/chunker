# st-monad-scoping-of-side-effects

**Parent:** [[content/L1/functional-algebraic-type-theory|functional-algebraic-type-theory]] — Advanced functional programming uses algebraic structures (Functors, Applicatives, Monads, Free[F,A]) to model computation as first-class, manipulable values, ensuring type safety and referential transparency by explicitly tracking all potential effects, including those related to I/O, concurrency (using Par and the Actor model), and local state mutation (using the ST monad).

In functional programming, certain algorithms, such as quicksort, require the ability to mutate data in place for correct or efficient execution. Fortunately, when data is created locally within a function's scope, side effects are safe, meaning any function can use side-effecting components internally while presenting a pure external interface to its callers. While pure functional components are often preferred because they are easier to assemble and prove correct, utilizing local side effects in an implementation is permissible.

To improve on the loose reasoning regarding the scope of side effects, it is sometimes desirable to formally enforce effect scoping using Scala's type system. Previously, the type system did not offer help in controlling the scope of side effects from constituent parts of algorithms like quicksort, nor did it alert developers if side effects or mutable state were leaked beyond the intended scope.

This section develops a specialized data type to enforce the scoping of mutations. The standard `IO` monad is unsuitable for modeling local mutable state because an `IO` action that returns `IO[List[Int]]` would be an action that is perfectly safe to run and would have no side effects, which is not true in general for arbitrary `IO` actions. Therefore, a new type is required to distinguish between effects that are safe to run (like locally mutable state) and external effects like Input/Output (I/O).

### A Little Language for Scoped Mutation

The most natural approach to modeling mutable state is using the `State[S, A]` monad, which, as previously learned, is simply a function of type `S => (A, S)` that accepts an initial state `S` and produces a result `A` along with the final state `S`. However, when the goal is to simulate in-place mutation of a state, the system should not treat the state as being passed from one action to the next. Instead, a specialized token, marked with the type `S`, should be passed, which grants the function authority to mutate data tagged with that same type `S`.

This new data type, which we call the `ST` monad (standing for state thread, state transition, or state tag), utilizes Scala’s type system to ensure two static invariants: 1) if a reference to a mutable object is held, no external code can observe the mutation; and 2) a mutable object can never be observed outside the scope where it was created. 

We can observe the first invariant with the quicksort example, where mutating an array is private since no outside code holds a reference to that array. The second invariant is subtler: it ensures that mutable state references are not leaked outside their scope. For instance, in a file I/O library, if the underlying OS file read operation fills a mutable buffer (like `Array[Byte]`), returning a 
