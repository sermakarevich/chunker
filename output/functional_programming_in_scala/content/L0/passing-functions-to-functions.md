# passing-functions-to-functions

**Parent:** [[content/L1/scala-functional-programming-basics|scala-functional-programming-basics]] — Scala treats functions as first-class values, allowing them to be passed as arguments to Higher-Order Functions (HOFs), which is a core concept in functional programming.

In Scala, object members can be accessed using the standard object-oriented dot notation, for example, `MyModule.abs(-42)` to call the `abs` member. For demonstration, to use the `toString` member on the object `42`, one would write `42.toString`. Object members can refer to each other without prefixing the object name (unqualified calls), but they retain access to their enclosing object using the special name `this`. Furthermore, even a simple arithmetic expression like `2 + 1` is implicitly calling a member of an object; specifically, the program is calling the `+` member of the object `2` and passing `1` as an argument, which is syntactic sugar for `2.+(1)`. Scala does not have special concepts for operators; rather, the plus symbol (`+`) is simply a valid method name. Any method name can be used infix—by omitting the dot and parentheses—when calling it with a single argument. For instance, instead of writing `MyModule.abs(42)`, the program can write `MyModule abs 42` and achieve the same result, allowing the user to select the format that is most pleasing. 

Programmers can bring an object's member into scope by using the `import` keyword, which allows subsequent calls to the member to be made unqualified. For example, `import MyModule.abs` allows the code to call `abs(-42)` directly. Alternatively, to bring all of an object's nonprivate members into scope, the code can use the underscore syntax: `import MyModule._`.

### Higher-Order Functions: Passing Functions to Functions

After covering basic Scala syntax, the focus shifts to writing functional programs. The first core concept to grasp is that functions are values. Consequently, just as other data types—such as integers, strings, and lists—can be assigned to variables or stored in data structures, functions can also be passed as arguments to other functions. 

When developing purely functional programs, programmers frequently use a function that accepts other functions as arguments; this concept is known as a Higher-Order Function (HOF). The text provides an example demonstrating how to adapt a program to print both the absolute value of a number and the factorial of another number, with a sample run showing:

The absolute value of -42 is 42
The factorial of 7 is 5040

In this book, the term function is used generally to refer to either standalone functions, like `sqrt` or `abs`, or members of a class, including methods. When the context is clear, the terms method and function can be used interchangeably, because the essential consideration is not the syntax of invocation (whether it is `obj.method(12)` or `method(obj, 12)`), but the fact that the programmer is referring to some parameterized block of code.

#### A Short Detour: Writing Loops Functionally

To calculate the factorial of a number, a recursive approach is used: `def factorial(n: Int): Int = { def go(n: Int, acc: Int): Int = if (n <= 0) acc else go(n-1, n*acc) go(n, 1) }`. This structure utilizes an inner function, or local definition, which is common in Scala to write functions that are local to the body of another function. In functional programming, this structure is not viewed as unusual. 

The functionally correct way to write loops is through recursion, without mutating a loop variable. A recursive helper function, often named `go` or `loop` by convention, is defined inside the body of the `factorial` function. Since the `go` function is local, it can only be called from within the body of the `factorial` function, similar to how a local variable would be constrained. The `factorial` function's definition merely involves calling `go` with the initial state conditions: the remaining value `n`, and the current accumulated factorial `acc`. To proceed to the next iteration, the program calls `go` recursively with the updated loop state (`go(n-1, n*acc)`). To terminate the loop, the function returns a value without making a recursive call (when `n <= 0`, the function returns `acc`). Scala automatically detects this type of self-recursion and compiles it to the same bytecode as a `while` loop, provided the recursive call is in tail position. 

A call is in tail position if the caller's only action is to return the value of the recursive call. For example, calling `go(n-1, n*acc)` is in tail position because the method directly returns this value without additional processing. Conversely, if the method were to calculate `1 + go(n-1, n*acc)`, `go` would not be in tail position because the method would still have to perform addition after `go` returned its result. 

If all recursive calls within a function are in tail position, Scala automatically compiles the recursion into iterative loops that do not consume a call stack frame for every iteration. While Scala does not automatically announce successful tail call elimination, programmers can use the `tailrec` annotation to guide the Scala compiler. Using `@annotation.tailrec` ensures that the compiler issues a compile error if it is unable to eliminate the tail calls, confirming the assumption. This provides the syntax: `def factorial(n: Int): Int = { @annotation.tailrec def go(n: Int, acc: Int): Int = if (n <= 0) acc else go(n-1, n*acc) go(n, 1) }`.

**Writing the First Higher-Order Function**

Building upon the `factorial` function, the program can be generalized using a higher-order function named `formatResult`. This function accepts three parameters: a `String` name, an integer `n`, and a function `f` (which must have the type `Int => Int`). The signature is: `def formatResult(name: String, n: Int, f: Int => Int)`. The `formatResult` function serves as the HOF because it accepts another function, `f`, as an argument. The function body then constructs a descriptive message: `val msg = 
