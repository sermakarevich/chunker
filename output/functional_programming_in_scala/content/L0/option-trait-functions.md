# option-trait-functions

**Parent:** [[content/L1/scala-functional-programming-concepts|scala-functional-programming-concepts]] — Advanced Scala FP concepts cover immutable data structures (`List` trait), total function design using `Option[+A]` for error handling, and detailed descriptions of higher-order functions like `map`, `flatMap`, and `foldRight`.

The `Option` data type can be conceptually understood as a specialized list capable of holding at most one element. Consequently, many functions previously discussed for `List` also have analogous implementations for `Option`. The authors choose to place these functions within the body of the `Option` trait for stylistic consistency, allowing invocation using the syntax `obj.fn(arg1)` or `obj fn arg1`, rather than the traditional standalone function syntax `fn(obj, arg1)`. This design choice, while stylistic, introduces an additional complication regarding variance that must be addressed.

Key methods provided by the `Option` trait include:

*   **`def map[B](f: A => B): Option[B]`**: Applies a function `f` to the contained value of the `Option`, converting the result to a new `Option[B]`. This function executes the transformation only if the `Option` is not `None`.
*   **`def flatMap[B](f: A => Option[B]): Option[B]`**: Applies a function `f` that itself returns an `Option[B]` to the contained value. This executes the transformation only if the `Option` is not `None` and efficiently handles the resulting `Option` value.
*   **`def getOrElse[B >: A](default: => B): B`**: Provides a default value of type `B`, which must be a supertype of the contained type `A` (`B >: A`). This method retrieves the contained value if it exists, or returns the provided default value otherwise.
*   **`def orElse[B >: A](ob: => Option[B]): Option[B]`**: Returns the contained value of the `Option` if it exists; otherwise, it returns the value of another `Option[B]` (which must also be a supertype of `A`).
*   **`def filter(f: A => Boolean): Option[A]`**: Filters the `Option`'s contained value: if the value satisfies the predicate `f`, the original value is returned wrapped in `Some`; otherwise, it returns `None`.
