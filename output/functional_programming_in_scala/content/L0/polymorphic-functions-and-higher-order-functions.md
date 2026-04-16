# polymorphic-functions-and-higher-order-functions

**Parent:** [[content/L1/scala-functional-programming-basics|scala-functional-programming-basics]] — Scala treats functions as first-class values, allowing them to be passed as arguments to Higher-Order Functions (HOFs), which is a core concept in functional programming.

Previously, the function `abs` and the function `factorial` were shown to accept an `Int` and return an `Int`, matching the `Int => Int` type. Because of this type consistency, the `formatResult` function can accept either `abs` or `factorial` as the function argument `f`. For example, running `formatResult("absolute value", -42, abs)` returns the string "The absolute value of -42 is 42.", and running `formatResult("factorial", 7, factorial)` returns the string "The factorial of 7 is 5040." 

### Variable-naming conventions
It is common convention to use names like `f`, `g`, and `h` for parameters to a higher-order function (HOF). In functional programming, developers tend to use very short variable names, often single letters, because HOFs are generally applicable and do not impose constraints on the specific action of the argument; all that the HOF knows about the argument is its type. Many functional programmers find that using short names improves code readability because it makes the underlying code structure easier to observe at a glance.

### Polymorphic functions: abstracting over types
So far, the examples have only defined monomorphic functions, meaning functions that operate on only a single data type. For instance, `abs` and `factorial` are specialized for arguments of type `Int`, and the `formatResult` higher-order function is fixed to operate only on functions that take `Int` arguments. However, when writing HOFs, developers often need to write code that operates for any given type. These functions are called polymorphic functions. The kind of polymorphism used here is specifically known as parametric polymorphism, which differs from the concept of subtyping or inheritance common in object-oriented programming.

### An example of a polymorphic function
Developers can often identify polymorphic functions by observing that several monomorphic functions share a similar underlying structure. For example, the original `findFirst` function was defined to search for a `String` in an `Array[String]` and returned the first index where the specified `key` occurred, or -1 if the key was not present.

**Monomorphic function to find a String in an array:**
`def findFirst(ss: Array[String], key: String): Int = { @annotation.tailrec def loop(n: Int): Int = if (n >= ss.length) -1 else if (ss(n) == key) n else loop(n + 1) loop(0) }`

The function logic dictates that `ss(n)` extracts the `n`th element of the array `ss`, and if this element equals the `key`, the function returns `n`; otherwise, it recursively calls `loop(n + 1)`. If the loop counter `n` exceeds the array length, the function returns -1.

The important realization is that the code structure for `findFirst` remains nearly identical if one changes the search operation to find an `Int` in an `Array[Int]`, or an `A` in an `Array[A]` for any generic type `A`. Therefore, a more general implementation is possible by accepting a function to test each element of the array.

**Polymorphic function to find an element in an array:**
`def findFirst[A](as: Array[A], p: A => Boolean): Int = { @annotation.tailrec def loop(n: Int): Int = if (n >= as.length) -1 else if (p(as(n))) n else loop(n + 1) loop(0) }`

This generalized function `findFirst` is polymorphic because it accepts type `A` as a type parameter. Instead of hardcoding the search for a `String` key, the function takes a predicate function `p` (with the signature `A => Boolean`) that determines if the element at index `n` is a match. The function is abstracting over two components: the type of the elements in the array (`A`) and the criteria used for searching (`p`).

To create a polymorphic function as a method, the developer introduces a comma-separated list of type parameters enclosed in square brackets (e.g., `[A]`) immediately following the function name, like `findFirst[A]`. The type parameters can be any identifier (e.g., `[Foo, Bar, Baz]`), but conventionally, programmers use short, single-letter, uppercase type parameter names such as `[A]`, `[B]`, or `[C]`.
