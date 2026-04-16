# applicative-vs-monad-effects

**Parent:** [[content/L1/functional-fp-architecture-context|functional-fp-architecture-context]] — The design of functional programming necessitates managing computations as first-class values, utilizing special types ('effects') like Option, Either, Par, and Stream to handle potential failures and side effects without violating referential transparency. Applicative funtors combine independent results using fixed structure (e.g., `map2`), while Monads are required when the result of one calculation influences subsequent steps (e.g., `flatMap`). State management across all traversable functors (like List, Tree) is generalized using the `mapAccum` function, which allows for writing reusable core combinators such as `toList` and `zipWithIndex` for any structure.

In functional programming, type constructors like `Par`, `Option`, `List`, `Parser`, and `Gen` are often called 'effects.' This term is distinct from 'side effect,' which implies a violation of referential transparency. Calling these types 'effects' means they augment ordinary values with specialized capabilities: for example, `Par` adds the ability to define parallel computation, and `Option` adds the possibility of failure.

When a type has an associated `Monad` or `Applicative` instance, it is referred to as having a 'monadic effect' or 'applicative effect.'

**Comparison of Applicative vs. Monad:**

**1. The Option Applicative versus the Option Monad**

If developers need to combine results from two independent lookups, such as retrieving salaries and department names for a given employee name, the `Applicative` interface is sufficient. The `Applicative` interface allows combining results when the lookups are independent, meaning the result of one lookup does not influence which lookups are performed next. For example, using `Option` to retrieve department and salary for "Alice" from two independent maps (`depts: Map[String,String]` and `salaries: Map[String,Double]`), the computation can be structured using `F.map2(depts.get("Alice"), salaries.get("Alice"))((dept, salary) => s"Alice in $dept makes $salary per year")`, where `F` is an `Applicative[Option]` instance. Here, the lookups are independent, and `Applicative` ensures that the structure of the computation remains fixed.

However, if the result of one lookup must influence what subsequent lookups are performed, the `Monad` interface, specifically utilizing `flatMap` or `join`, is required. Consider looking up an employee's ID first, then using that ID to query two other maps (`depts: Map[Int,String]` and `salaries: Map[Int,Double]`). This scenario requires the `Monad` functionality because the results of previous computations influence the subsequent lookups. The computation proceeds like this: `idsByName.get("Bob").flatMap { id => F.map2(depts.get(id), salaries.get(id))((dept, salary) => s"Bob in $dept makes $salary per year")}`. This structure demonstrates that while the `Applicative` approach assumes a fixed computation structure, the `Monad` approach allows the results of computations to influence subsequent computation steps.

**2. The Parser Applicative versus the Parser Monad**

This distinction is illustrated when parsing structured data, such as a file of comma-separated values containing a date and a temperature.

*   **Fixed Order (Applicative):** If the file guarantees a fixed column order (e.g., date first, then temperature), the `Applicative` pattern is adequate. In this case, the row parser, `row: Parser[Row]`, can be constructed using `F.map2(d, temp)(Row(_, _))`, where `d: Parser[Date]` and `temp: Parser[Double]` are defined independently. The `Applicative` approach encodes the fixed order of the columns in the parser construction.

*   **Variable Order (Monadic):** If the column order is unknown and must be dynamically determined from a header line, the `Monad` interface is necessary. The `Monad` allows the parsing process to select which parser to run next based on the result of the preceding parser. For example, parsing a header that results in a `Parser[Row]` object requires `F.flatMap(header) { row => row.sep("\n") }`. Here, the initial header parsing results in a `Parser[Row]`, and this resulting parser is then used to execute subsequent row parsing, demonstrating that the results of previous parsings influence the structure of the remaining computation.
