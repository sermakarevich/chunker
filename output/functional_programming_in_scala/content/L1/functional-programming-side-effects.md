# functional-programming-side-effects

**Parent:** [[content/L2/functional-programming-principles-in-scala|functional-programming-principles-in-scala]] — The book *Functional Programming in Scala* systematically teaches FP principles using Scala as a vehicle, demonstrating how to refactor impure code (like a coffee shop charge system) into pure functional forms that achieve superior testability and reusability by separating core business logic from external effects.

The field of Functional Programming (FP) offers substantial benefits, primarily through achieving increased modularity by utilizing pure functions. This increased modularity inherently makes pure functions easier to test, reuse, parallelize, generalize, and reason about, while also making them significantly less prone to bugs. To illustrate these advantages, the concept is often demonstrated by comparing an initial program segment that contains side effects (an impure program) with a revised version that successfully removes those side effects.

### Demonstrating the Shift from Impure to Pure Code

To ground these abstract ideas, an example was constructed involving a simulated system for handling purchases at a coffee shop. This scenario serves as the reader's initial exposure to Scala's syntax; the subsequent parts of the book will provide more detailed discussions of the language's syntax, so readers should focus on grasping the general code logic presented.

**The Initial Impure Approach (The `Cafe` Class):**
The first attempt at implementation, using a Scala program (Listing 1.1), established the `buyCoffee` method within a `Cafe` class. This initial design utilized side effects. Specifically, the line `cc.charge(cup.price)` represents a significant side effect. Charging a credit card involves external interactions—such as communicating with a credit card company via a web service, authorizing the transaction, and persisting a detailed record of the transaction. Although the `buyCoffee` method merely returns a `Coffee` object, the credit card charging and record persistence occur externally, which gives rise to the term 'side effect.'

*Details of the Initial Scala Program (Listing 1.1):*
* The program structure uses the `class` keyword (similar to Java) and contains the class body within curly braces, `{` and `}`.
* A method is introduced using the `def` keyword. The syntax `cc: CreditCard` defines a parameter named `cc` of type `CreditCard`. The method's return type follows the parameter list, and the method body uses a block delimited by curly braces after an `=` sign.
* The language is syntactically minimal, requiring no semicolons, and statements are delimited by newlines within a block.
* Because `cup` is the last statement executed in the block, the method automatically returns the `cup` object.

*Critique of Initial Testability:* Due to the side effect, the original code is difficult to test because testing procedures cannot involve making actual charges to the credit card company. The initial problem highlights that the `CreditCard` class should ideally be ignorant of external concerns, such as how to contact the credit card company or how to persist charge records in internal systems. To address this modularity concern, the initial suggestion was to pass a `Payments` object into `buyCoffee`.

**Attempts at Modular Improvement and Limitations:**
*A Revised Scala Program (Listing 1.2):*
```scala
class Cafe {
  def buyCoffee(cc: CreditCard, p: Payments): Coffee = {
    val cup = new Coffee()
    p.charge(cc, cup.price)
    cup
  }
}
```
While the revised code—where the `buyCoffee` method accepts a `Payments` object `p`—regained some testability because `Payments` could potentially be implemented as an interface, this approach was critiqued as not being ideal. The initial issue was that forcing `Payments` to be an interface required making a concrete class an interface. Furthermore, any mock implementation of `Payments` might contain internal state that needs inspecting after the call to `buyCoffee`, necessitating explicit checks to confirm that the state was appropriately modified (mutated) by the call to `charge`. The authors noted that this complexity feels like an unnecessary overhead if the only goal is simply to test that `buyCoffee` correctly generates a charge equal to the price of a cup of coffee.

Separately, the initial structure faced difficulties with reusability. For instance, if a customer, Alice, wanted to order 12 cups of coffee, calling the original `buyCoffee` implementation 12 times would initiate 12 separate contacts with the payment system, authorizing 12 distinct charges to Alice’s credit card. This outcome not only incurs extra processing fees but is detrimental to both Alice and the coffee shop. Solving this required implementing specialized logic, such as a new function, `buyCoffees`, designed for batching charges. Alternatives included writing a specialized `BatchingPayments` implementation of the `Payments` interface that would attempt to consolidate successive charges to the same credit card. However, this introduced further complexity, demanding that the implementation address specifics like the optimal number of charges to batch, the required waiting duration, and whether the `buyCoffee` function itself needed to explicitly signal the completion of a batch, potentially by calling a method such as `closeBatch`.

**The Pure Functional Solution (Separation of Concerns):**

The truly functional improvement demonstrated the principle of separation of concerns by eliminating side effects. In the revised functional approach, the `buyCoffee` method is redesigned to return a tuple of type `(Coffee, Charge)`, where `Charge` is a newly introduced data type. Instead of directly executing the charge via a side effect (`cc.charge(cup.price)`), the function now constructs the `Charge` object: `(cup, Charge(cc, cup.price))`. This pivotal change means the `buyCoffee` function merely *creates* the charge value; no external payment system interaction is involved. This design dramatically enhances both testability and reusability.

Since `Charge` is treated as a first-class data value, it can be passed around and combined using a specialized `combine` function. This function is designed to handle the merging of multiple charges that pertain to the same `CreditCard` (if `cc == other.cc`) or, alternatively, to throw an exception if the cards differ. To purchase $n$ cups of coffee, the sophisticated new function `buyCoffees(cc: CreditCard, n: Int): (List[Coffee], Charge)` utilizes higher-order functions from the Scala standard library, specifically `List.fill(n)(buyCoffee(cc))`, `unzip`, and the `charges.reduce((c1,c2) => c1.combine(c2))` method, to efficiently compute the total charge by combining all individual charges. The function body is defined as: `def buyCoffees(cc: CreditCard, n: Int): (List[Coffee], Charge) = { val purchases: List[(Coffee, Charge)] = List.fill(n)(buyCoffee(cc)) val (coffees, charges) = purchases.unzip (coffees, charges.reduce((c1,c2) => c1.combine(c2))) }`.

This pure approach is trivial to test because the `Cafe` class is rendered entirely ignorant of how the resulting `Charge` values will ultimately be processed. Furthermore, making `Charge` a first-class value enables the assembly of complex business logic. For example, the `coalesce` function can be written to group an arbitrary list of individual charges by their associated credit card and combine them into a single total charge: `def coalesce(charges: List[Charge]): List[Charge] = charges.groupBy(_.cc).values.map(_.reduce(_ combine _)).toList`. The use of anonymous functions, such as `_.cc` and `_ combine _`, within this function powerfully illustrates the composability inherent to FP. 

In essence, the overall benefit demonstrated is that a function initially equipped with side effects can be elegantly refactored into a pure core function. This pure core then returns a value (like `Charge`) that is managed by an outer layer of the program to process the actual effects. This process preserves the core business logic while fundamentally separating the concern of value creation from the concern of value interpretation or actual processing, thereby achieving maximum testability and reusability without needing mock objects or interfaces.

## Children
- [[content/L0/functional-programming-benefits|functional-programming-benefits]] — Functional programming (FP) improves code quality by increasing modularity through pure functions, making code easier to test, reuse, parallelize, generalize, and reason about. The chapter uses a coffee shop example to demonstrate this, showing that initially, a side-effect prone `buyCoffee` method is difficult to test and reuse for bulk orders (like 12 cups), leading to the suggestion of refactoring to use a modular `Payments` object to achieve better testability and better batching capability.
- [[content/L0/functional-programming-side-effects-buycoffee|functional-programming-side-effects-buycoffee]] — The text illustrates that functional programming improves code testability and reusability by eliminating side effects. Instead of having the `buyCoffee` function directly charge a credit card, the revised function returns a `(Coffee, Charge)` pair, where `Charge` is a specialized, immutable data type. This design allows the function to be reused to process multiple purchases via the `buyCoffees` function and enables the implementation of complex logic like `coalesce` to combine multiple individual charges into a single transaction.
