# decoupled-code-and-methods

**Parent:** [[content/L1/software-proficiency-systems-architecture-and-resource-management|software-proficiency-systems-architecture-and-resource-management]] — Professional proficiency requires mastery of specialized tools and workflows, utilizing techniques like PERT (requiring optimistic, most likely, and pessimistic estimates) and Incremental Iteration. Code stability demands rigorous resource management through techniques such as scope-based cleanup, `finally` clauses, and adherence to architectural principles like the Law of Demeter (minimizing method chaining) and utilizing the 'chop' technique for debugging large systems.

When designing systems, aiming for structural rigidity, as seen in linked structures, can be beneficial when building things like bridges, but when developing software intended for change, flexibility is the goal. To achieve flexibility, individual components must couple to as few other components as possible. The challenge is that coupling is transitive: if Component A couples to Component B and Component C, and Component B couples to Component M and Component N, and Component C couples to Component X and Component Y, then Component A is actually coupled to B, C, M, N, X, and Y. To follow this principle, developers should adopt the guideline: Decoupled Code Is Easier to Change.

To understand how to decouple code, this section discusses common sources of tight coupling: Train Wrecks (chains of method calls), Globalization (the dangers of static dependencies), and Inheritance (why subclassing is dangerous). Note that coupling can occur whenever two pieces of code share something; developers should keep an eye out for these underlying patterns.

Signs of coupling include: 
*   Wacky dependencies between unrelated modules or libraries.
*   Making "simple" changes to one module that propagate through unrelated modules or break functionality elsewhere.
*   Developers becoming afraid to change code because they are unsure of the potential impact of those changes.
*   Mandatory meetings where all developers must attend because no one is sure who will be affected by a proposed change.

**Train Wrecks**

Train wreck code often involves traversing multiple levels of abstraction. For example, consider this pseudocode: `public void applyDiscount(customer, order_id, discount) { totals = customer.orders.find(order_id).getTotals(); totals.grandTotal = totals.grandTotal - discount; totals.discount = discount; }`

This example shows that the top-level code needs implicit knowledge across five levels of abstraction: the `customer` object exposes `orders`; the `orders` collection has a `find` method accepting an `order_id` and returning an `order` object; and the `order` object has a `totals` object, which includes getters and setters for `grandTotal` and `discount`. This extensive implicit knowledge creates a tight coupling that makes the code difficult to maintain, as changes to any part of the system could break it. The core problem is that the `totals` object is merely a container for fields that anyone can query and update, rather than an object responsible for managing the totals.

**Solution: Tell, Don’t Ask**
The fix for the train wreck is to delegate the responsibility for discounting to the `totals` object itself, applying the principle known as Tell, Don’t Ask (TDA). TDA advises against making decisions based on an object's internal state and then updating that object, as doing so undermines encapsulation and spreads implementation knowledge throughout the code. The corrected code delegates the discounting logic:

```
public void applyDiscount(customer, order_id, discount) {
customer.orders.find(order_id).getTotals().applyDiscount(discount);
}
```

Similar TDA issues occur with the `customer` object and its `orders` collection, and with the `order` object and its `totals` object. The goal is to simplify the interface so that the outside world does not need to know that an `order` uses a separate object for its `totals`.

**The Law of Demeter (LoD)**

The Law of Demeter (LoD), originally set of guidelines written in the late '80s by Ian Holland for the Demeter Project, recommends that a method defined in a class C should only call: 
1. Other instance methods within class C.
2. Methods belonging to C's parameters.
3. Methods in objects that C creates (on the stack or the heap).
4. Global variables (though this is generally discouraged).

While the original advice included global variables, the principle remains sound, favoring a simpler expression: **Don’t Chain Method Calls**. Developers should try to limit method access to having no more than one dot (`.`) when accessing object functionality. Intermediate variables are also restricted; for example, both the following styles are poor practices:

```
amount = customer.orders.last().totals().amount;
orders = customer.orders;
last = orders.last();
totals = last.totals();
amount = totals.amount;
```

The rule does not apply if the chained components are genuinely unlikely to change. In practice, almost all elements in an application should be treated as likely to change, especially third-party library components whose maintainers might change APIs between releases.

**Chains and Pipelines**

Unlike train wrecks of method calls, composing functions into pipelines (as discussed in Transforming Programming) transforms data by passing it from one function to the next, and this form of coupling is far less problematic than coupling introduced by train wrecks.
