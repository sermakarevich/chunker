# scala-option-handling-errors

**Parent:** [[content/L1/scala-functional-programming-concepts|scala-functional-programming-concepts]] — Advanced Scala FP concepts cover immutable data structures (`List` trait), total function design using `Option[+A]` for error handling, and detailed descriptions of higher-order functions like `map`, `flatMap`, and `foldRight`.

This section details advanced Scala concepts, including how to handle errors using the `Option[+A]` Algebraic Data Type (ADT) instead of traditional exceptions or sentinel values.

The `Option` data type is beneficial because it forces calling code to explicitly handle the possibility that a function result might not always be defined. A function designed to return an `Option[A]` accurately reflects that the result may be missing, turning the function into a total function.

Key methods provided by the `Option` trait include:

*   **`map[B](f: A => B): Option[B]`**: Applies a function `f` to the contained value of the `Option`, converting the result to a new `Option[B]`. This function executes the transformation only if the `Option` contains a value (`Some`); otherwise, the computation aborts, and the method returns `None`. For instance, if `lookupByName("Joe")` returns `Some(Employee(name="Joe", department="Sales"))`, calling `.map(_.department)` results in `Some("Sales")`. If `lookupByName("Joe")` returns `None`, the `map` function does not call the `_.department` function and returns `None`.
*   **`flatMap[B](f: A => Option[B]): Option[B]`**: Applies a function `f` that itself returns an `Option[B]` to the contained value. This method executes the transformation only if the `Option` contains a value (`Some`) and efficiently handles the resulting `Option` value. For example, if `lookupByName("Joe")` returns `Some(employee)`, and `employee.manager` returns `Some(manager)`, then `flatMap` yields `Some(manager)`. If the initial `Option` is `None`, or if the function `f` returns `None`, `flatMap` returns `None`.
*   **`getOrElse[B >: A](default: => B): B`**: Retrieves the contained value if the `Option` exists (`Some`); otherwise, it returns the provided default value. The default value must be a supertype of the contained type `A` (denoted by `B >: A`). If `lookupByName("Joe")` results in `Some(employee)`, `getOrElse("Default Dept.")` returns the department string; if the `Option` is `None`, it returns `
