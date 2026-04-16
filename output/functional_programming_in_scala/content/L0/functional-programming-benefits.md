# functional-programming-benefits

**Parent:** [[content/L1/functional-programming-side-effects|functional-programming-side-effects]] — Functional Programming improves modularity and testability by refactoring functions from impure methods with side effects (like directly charging a credit card) into pure functions that return values (like a `Charge` data type), enabling complex business logic such as batching charges using functions like `coalesce` and `buyCoffees`.

Functional programming (FP) is beneficial due to the increased modularity gained from programming with pure functions. Because of this modularity, pure functions are easier to test, reuse, parallelize, generalize, and reason about, and pure functions are also much less prone to bugs. To illustrate the benefits of FP, the chapter first demonstrates a simple program containing side effects and then shows the benefits of FP by removing those side effects. The text also discusses the general benefits of FP and defines two important concepts: referential transparency and the substitution model.

### 1.1 The benefits of FP: a simple example

To illustrate some basic ideas—concepts the reader will encounter throughout the book—consider an example demonstrating the benefits of programming with pure functions. This segment serves as the reader's first exposure to Scala's syntax; more detailed discussions of Scala's syntax will occur in the next chapter, so readers should focus primarily on understanding the general code logic.

#### 1.1.1 A program with side effects

Suppose the task is implementing a program to handle purchases at a coffee shop. The initial approach begins with a Scala program that uses side effects, which is also known as an impure program.

**Initial Scala Program (Listing 1.1):**
```scala
class Cafe {
  def buyCoffee(cc: CreditCard): Coffee = {
    // Side effect.
    // Actually charges the credit card.
    val cup = new Coffee()
    cc.charge(cup.price)
    cup
  }
}
```

*Details on Listing 1.1:* 
* The `class` keyword introduces a class, similar to Java. The class body is contained within curly braces, `{` and `}`.
* A method of a class is introduced using the `def` keyword. 
* The syntax `cc: CreditCard` defines a parameter named `cc` of type `CreditCard`. The `buyCoffee` method's return type is specified after the parameter list, and the method body uses a block within curly braces after an `=` sign.
* No semicolons are required, and newlines delimit statements within a block.
* Since `cup` is the last statement in the block, the method automatically returns the `cup` object.

The line `cc.charge(cup.price)` represents a side effect. Charging a credit card requires external interaction—such as contacting the credit card company via a web service, authorizing the transaction, and (if successful) persisting a record of the transaction. Although the `buyCoffee` function merely returns a `Coffee` object, the credit card charging and record persistence happen on the side, giving rise to the term “side effect.” (The chapter will define side effects more formally later.)

As a result of this side effect, the code is difficult to test. Testing cannot involve actually contacting the credit card company and charging the card. This lack of testability suggests a design change: the `CreditCard` class should not contain knowledge about how to contact the credit card company or how to persist a charge record in internal systems. To make the code more modular and testable, the `CreditCard` class should be made ignorant of these concerns, and a `Payments` object should be passed into `buyCoffee` instead.

**Revised Scala Program (Listing 1.2):**
```scala
class Cafe {
  def buyCoffee(cc: CreditCard, p: Payments): Coffee = {
    val cup = new Coffee()
    p.charge(cc, cup.price)
    cup
  }
}
```

*Critique of Listing 1.2:* 
While calling `p.charge(cc, cup.price)` still involves side effects, the revised code has regained some testability because `Payments` can be implemented as an interface, allowing for a mock implementation suitable for testing. However, this approach is not ideal. The initial problem was that forcing `Payments` to be an interface requires making a concrete class an interface, and any mock implementation might contain internal state that needs inspecting after the call to `buyCoffee`, necessitating checks to ensure that the state was appropriately modified (mutated) by the call to `charge`. The authors suggest that this complexity feels like overkill if the goal is merely to test that `buyCoffee` correctly creates a charge equal to the price of a cup of coffee.

Separate from testing concerns, a second problem exists: the `buyCoffee` function is difficult to reuse. For instance, if a customer, Alice, wishes to order 12 cups of coffee, calling the current `buyCoffee` implementation 12 times would contact the payment system 12 times, authorizing 12 separate charges to Alice’s credit card. This incurs extra processing fees and is detrimental to Alice and the coffee shop. Addressing this requires implementing a new function, `buyCoffees`, with specialized logic for batching charges. Alternatively, one could write a specialized `BatchingPayments` implementation of the `Payments` interface that attempts to batch successive charges to the same credit card. However, this introduces complexity: the implementation must address questions like how many charges to batch, how long to wait, and whether the `buyCoffee` function must explicitly signal when the batch is finished, perhaps by calling a method like `closeBatch`.


