# data-sharing-in-functional-data-structures

**Parent:** [[content/L1/functional-data-structures-scala|functional-data-structures-scala]] — In Scala, functional data structures are immutable, utilizing the `sealed trait List[+A]` defined with `Nil` and `Cons(head: A, tail: List[A])`. Functions like `sum` (summing `List[Int]` by matching `Nil => 0` and `Cons(x,xs) => x + sum(xs)`) and `product` (handling `Nil => 1.0` and `Cons(0.0, _) => 0.0`) illustrate recursive pattern matching, while the `foldRight` higher-order function provides a generalized method for list operations, such as calculating $1+2+3=6$ via `foldRight(Cons(1, Cons(2, Cons(3, Nil))), 0)((x, y) => x + y)`.

Data sharing in functional data structures arises because, when data is immutable, functions that modify a data structure, such as adding or removing elements from a list, do not require physical copying of the data. For example, adding an element 1 to the front of an existing list, say `xs`, simply creates a new list, `Cons(1, xs)`. Since lists are immutable, the operation reuses the original list `xs`, which is called data sharing. This sharing allows programmers to efficiently implement functions without worrying that subsequent code will modify the data. Similarly, removing the element from the front of a list defined as `mylist = Cons(x, xs)` merely involves returning its tail, `xs`; the original list `mylist` remains available and unharmed. Functional data structures are therefore **persistent**, meaning that existing references are never changed by operations on the data structure.

**The Principle of Data Sharing**

Data sharing is highly efficient. For instance, when executing `.tail` on `List("a", "b", "c", "d")`, the operation does not modify the original list; instead, it simply references the tail of the original list. Because the list is immutable, defensive copying is unnecessary.

This principle contrasts sharply with mutable data, where passing the data through a chain of components might necessitate each component making its own copy to prevent unintended modifications. Because immutable data is always safe to share, Functional Programming (FP) often achieves greater efficiency than approaches relying on side effects, due to much greater sharing of data and computation.

**Implementing List Operations**

Developers can implement list modification functions within the `List` companion object. Two specialized functions illustrate this: `tail` (which removes the first element, taking constant time) and `setHead` (which replaces the first element). More generally, the `drop` function removes the first $n$ elements of a list, taking time proportional only to the number of elements being dropped, without copying the entire list. Similarly, `dropWhile` removes elements from the list prefix as long as they match a given predicate `f: A => Boolean`. 

A particularly efficient demonstration of data sharing is the `append` function, which adds all elements of one list (`a2`) to the end of another (`a1`). This definition only copies values until the first list (`a1`) is exhausted; thus, its runtime and memory usage are determined only by the length of `a1`, and the remaining list simply points to `a2`. This makes the immutable linked list much more efficient for concatenation compared to performing the same operation on two arrays.

**Challenges in Data Sharing: The `init` Function**

Not all operations are efficient due to data sharing. The `init` function, which is supposed to return a list consisting of all but the last element of a given list (e.g., `List(1, 2, 3, 4)` returns `List(1, 2, 3)`), cannot be implemented in constant time like `tail`. This is because, given the structure of a singly linked list, any time a programmer needs to replace the tail of a `Cons`, even if it is the final `Cons` in the list, the programmer must copy all preceding `Cons` objects.

**Generalizing to Higher-Order Functions (HOFs) and Folds**

When generalizing operations like `sum` and `product` over lists, developers can use the `foldRight` function, which serves as a powerful higher-order function (HOF). The signature for `foldRight` is `def foldRight[A, B](as: List[A], z: B)(f: (A, B) => B): B`. This function processes the list by pattern matching: it uses `z` as the initial value and `f` (a function) to combine the list element (`A`) with the accumulated result (`B`). For example, implementing `sum2` is done by calling `foldRight(ns, 0)((x, y) => x + y)`, where 0 is the initial value, and the lambda function `(x, y) => x + y` dictates the addition operation. The structure shows how `foldRight` replaces the list constructors `Nil` and `Cons` with the initial value `z` and the combining function `f`.

**Optimizing Type Inference**

Higher-order functions like `dropWhile` often accept anonymous functions. To improve type inference for such cases, Scala allows grouping arguments into multiple argument lists. If the function definition is restructured as `def dropWhile[A](as: List[A])(f: A => Boolean): List[A] = ...`, the first argument group (`as: List[A]`) fixes the type parameter `A` (e.g., to `Int` if `as` is `List[Int]`). This allows the programmer to write the calling anonymous function, such as `x => x < 4`, without explicitly annotating the argument `x`.

**Function Composition via `foldRight`**
The `foldRight` structure is highly generalizable: it is not specific to any element type `A`, nor is the final return type `B` required to be the same type as the list elements `A`.

**Summary of Execution Trace:**

To illustrate the function's behavior, an evaluation trace for `foldRight(Cons(1, Cons(2, Cons(3, Nil))), 0)((x, y) => x + y)` proceeds by repeatedly substituting the definition of `foldRight`. The process evaluates as:
`1 + foldRight(Cons(2, Cons(3, Nil)), 0)((x, y) => x + y)`
$ightarrow$ `1 + (2 + foldRight(Cons(3, Nil), 0)((x, y) => x + y)))`
$ightarrow$ `1 + (2 + (3 + (foldRight(Nil, 0)((x, y) => x + y))))`
Substituting the definition for the final `foldRight(Nil, 0)((x, y) => x + y)` returns the initial value $z$, which is 0. Thus, the final result is $1 + (2 + (3 + 0))$, yielding 6.
