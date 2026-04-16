# functional-data-structures-and-list-type-definition

**Parent:** [[content/L1/functional-data-structures-scala|functional-data-structures-scala]] — In Scala, functional data structures are immutable, utilizing the `sealed trait List[+A]` defined with `Nil` and `Cons(head: A, tail: List[A])`. Functions like `sum` (summing `List[Int]` by matching `Nil => 0` and `Cons(x,xs) => x + sum(xs)`) and `product` (handling `Nil => 1.0` and `Cons(0.0, _) => 0.0`) illustrate recursive pattern matching, while the `foldRight` higher-order function provides a generalized method for list operations, such as calculating $1+2+3=6$ via `foldRight(Cons(1, Cons(2, Cons(3, Nil))), 0)((x, y) => x + y)`.

The Scala standard library provides `compose` as a method on the `Function1` interface, which represents functions taking one argument. To compose two functions, $f$ and $g$, developers simply write `f compose g`. The standard library also provides an `andThen` method. Using `f andThen g` is equivalent to `g compose f`. For example, if a function $f$ is defined as `(x: Double) => math.Pi / 2 - x`, then the expression `f andThen math.sin` results in a function whose type is `Double => Double` and is equivalent to composing $f$ and `math.sin`. While composing simple one-liners is straightforward, higher-order functions, such as `compose`, work identically whether the underlying functions operate on small one-liners or massive, real-world codebases. This is because polymorphic, higher-order functions do not reference a specific domain; rather, they abstract over a common pattern encountered in many contexts, making programming in large-scale systems share the same flavor as programming in small-scale ones. 

***

**Summary and Outlook**

In this chapter, the reader learned how to define simple functions and programs, including using recursion to express loops, and how to introduce the concept of higher-order functions. The text also covered writing polymorphic functions in Scala, demonstrating that the implementations of polymorphic functions are often significantly constrained, allowing programmers to 'follow the types' to determine the correct implementation. Although the principles discussed are applicable to programming in the large, the next topic will be using pure functions to manipulate data, which will introduce the concept of functional data structures.

***

**Defining Functional Data Structures**

Functional data structures are operated on using only pure functions, meaning they must not change data in place or perform any side effects; thus, these structures are, by definition, immutable. For instance, the empty list (`List()` or `Nil` in Scala) is immutable, similar to integer values 3 or 4. Similarly, concatenating two lists using the syntax `a ++ b` yields a new list without modifying the original two input lists, $a$ and $b$. While this might initially suggest excessive data copying, the actual process is surprisingly efficient.

To begin, the focus is on the singly linked list, which is the `List` data type in Scala's standard library. The definition involves several new concepts: a trait, `sealed trait List[+A]`, is used to declare the type, and `sealed` ensures that all implementations of the trait must be declared in the file. Two data constructors define the two possible list forms: the empty list, denoted by the case object `Nil` (which extends `List[Nothing]`), or a non-empty list, denoted by the case class `Cons[+A](head: A, tail: List[A])` (which extends `List[A]`). The type parameter `+A` indicates that `A` is a covariant parameter. A data constructor provides a function to construct that form of the data type. 

Developers can create various lists, such as `val ex1: List[Double] = Nil` (an empty list of doubles), `val ex2: List[Int] = Cons(1, Nil)` (a list starting with 1), and `val ex3: List[String] = Cons(
