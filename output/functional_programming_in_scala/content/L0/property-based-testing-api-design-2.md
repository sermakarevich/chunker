# property-based-testing-api-design-2

**Parent:** [[content/L1/functional-programming-patterns-and-pbt|functional-programming-patterns-and-pbt]] — Functional programming mandates total type safety via ADTs like `Option` and `Either`, and utilizes non-strictness (laziness) via `Stream` to optimize data transformations and handle infinite sequences. Concurrency is managed by `Par[A]`, which relies on the non-blocking Actor model and specific laws (like `fork(x) == x`) to manage parallelism without resource exhaustion. Property-Based Testing (PBT) uses the `Gen[A]` and `Prop` types, where `Prop` is structured as `case class Prop(run: (TestCases, RNG) => Result)` to track testing state accurately.

The `forAll` function, which accepts a generator of type `Gen[A]` and a predicate of type `A => Boolean`, creates a property. The resulting property, stored in a new type called `Prop` (short for property, following the ScalaCheck naming), is intended to wrap the result of binding a generator to a predicate.

Initially, `Prop` was theorized to be a trait with `def check: Unit` and `def &&(p: Prop): Prop = ???`. Because the `check` method only printed a test report side effect, implementing property composition using the `&&` operator for `Prop` would require running two separate `check` methods, leading to two distinct reports for failures and successes, which is likely incorrect.

To enable composition using combinators like `&&`, the `check` function (or any function that 'runs' properties) must return a meaningful value. The minimum required information is knowing whether the property succeeded or failed, which allows for the implementation of `&&`. 

If `Prop` is represented simply as a non-strict Boolean, then any standard Boolean function (like AND, OR, NOT, XOR, etc.) can be defined for `Prop`. However, a Boolean is probably insufficient. If a property fails, developers might want to know both the count of successful tests and the arguments that caused the failure. Conversely, if a property succeeds, it is useful to know how many tests were run.

Considering the goal is primarily finding bugs by inspecting test cases, and the failure details are typically printed to the screen for human inspection, the returned value does not need to be something that can be computationally processed. Therefore, the `Prop` type can be represented as a trait with the following structure:
```scala
trait Prop { def check: Either[(FailedCase, SuccessCount), SuccessCount] }
```
In this representation, if a property fails, `check` returns a `Left((String, Int))`, where the first `String` represents the value that caused the failure, and the `Int` is the number of cases that succeeded before the failure occurred. If the property succeeds, `check` returns a `Right[Int]` (the total number of cases run).

Developers can further refine the API by looking at the generators themselves. Since `forAll` takes a `Gen[A]` and a predicate `A => Boolean`, the implementation of `check` requires internal access to the mechanism that generates values of type `A`.

To understand the requirements for `Gen[A]`, it is helpful to recall that a `Gen[A]` is something that knows how to generate values of type `A`. The suggested approach is to make `Gen` a type that wraps a state transition over a random number generator (RNG), specifically:
```scala
case class Gen[A](sample: State[RNG, A])
```
Using this representation, developers can implement functions like `choose` (to generate integers in the range `start` to `stopExclusive`), `unit` (to always generate value `a`), and `listOfN` (to generate lists of a specified length `n` using generator `g`).

If developers want to implement a generator that depends on another generated value (for example, generating pairs `(String, String)` where the second string only contains characters from the first), they need `flatMap`. This function allows one generator to use its generated value to determine which subsequent generator to use. The specialized `listOfN` can then be generalized to support variable lengths by implementing `listOfN(size: Gen[Int]): Gen[List[A]]` using `flatMap`.
