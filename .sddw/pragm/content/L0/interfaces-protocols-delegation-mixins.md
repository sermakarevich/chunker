# interfaces-protocols-delegation-mixins

**Parent:** [[content/L1/program-as-transformation-pipeline|program-as-transformation-pipeline]] — Programming is best viewed as a data transformation pipeline (like a Unix pipe: `find . -type f | xargs wc -l | sort -n | tail -5`), which minimizes coupling by passing data continuously through functional steps; to achieve polymorphism and structure robust code, developers should favor interfaces/protocols, delegation, and mixins/traits over inheritance to avoid architectural coupling.

When designing code, developers should consider using interfaces and protocols, which allow specifying one or more sets of behaviors that a class must implement. For example, a `Car` class could be designed to implement both `Drivable` and `Locatable` behaviors. In Java, this structure might look like `public class Car implements Drivable, Locatable { ... }`. Java calls these behavioral specifications interfaces, while other languages may refer to them as protocols or traits. Interfaces are defined abstractly, specifying required methods: for instance, `public interface Drivable { double getSpeed(); void stop(); }` mandates that any implementing class must include both `getSpeed()` and `stop()`. Similarly, `public interface Locatable() { Coordinate getLocation(); boolean locationIsValid(); }` requires implementing classes to define `getLocation()` and `locationIsValid()`. These declarations establish contractual obligations—they do not provide code—meaning any class named `Car` must include all four specified methods to be valid.

These features are powerful because they allow the use of interfaces and protocols as types. Any class that implements an appropriate interface will be compatible with that type. For instance, if both `Car` and `Phone` implement `Locatable`, they can all be stored together in a list of locatable items: `List<Locatable> items = new ArrayList<>(); items.add(new Car(...)); items.add(new Phone(...)); items.add(new Car(...));`. This allows processing the list safely, knowing that every item possesses `getLocation()` and `locationIsValid()` methods.

**Preferring Interfaces for Polymorphism**
Interfaces and protocols enable polymorphism without resorting to inheritance. Inheritance encourages creating classes whose objects have a large number of methods; if a parent class has 20 methods, and the subclass only needs two, the subclass's object still contains the other 18 unused methods, causing the class to lose control of its interface. This is a common issue seen in persistence and UI frameworks that mandate that application components subclass a supplied base class (e.g., `class Account < PersistenceBaseClass`). When this happens, the `Account` class carries all of the persistence class’s API, even if it does not need it.

Instead, developers can use **Delegation** to solve this. For example, an alternative structure uses delegation: 

```ruby
class Account
  def initialize(.)
    @repo = Persister.for(self)
  end
  def save
    @repo.save()
  end
end
```

By delegating, the `Account` class exposes none of the framework's API to clients, which breaks the undesirable coupling. Furthermore, the developer is no longer constrained by the framework’s API, allowing freedom to create the necessary API while avoiding the risk that an underlying persistence API will be bypassed.

**Delegating to Services: Has-A Trumps Is-A**
Developers can take this principle further by having an object, like `Account`, focus solely on its core business rules and not know how to persist itself. A separate class, like `AccountRecord`, can wrap the account and handle fetching and storing the account. This leads to increased decoupling.

However, a cost arises: the developer must write more code, often including boilerplate like a `find` method for all record classes. Fortunately, **Mixins** and **Traits** solve this. Mixins allow extending classes and objects with new functionality without using inheritance. The basic concept is to create a set of functions, name that set, and then extend a class or object with those functions. This creates a new class or object combining the capabilities of the original and all its mixins. In most cases, this extension can happen even if the developer lacks access to the original class's source code.

The implementation and name of this feature vary across languages; developers should view it as a language-agnostic capability crucial for merging functionality between existing and new things. For example, an `AccountRecord` can use mixins: `class AccountRecord extends BasicRecord with CommonFinders` and `class OrderRecord extends BasicRecord with CommonFinders`, where `CommonFinders` provides standard methods like `find(id)` and `findAll()`.

Mixins are also useful for grouping business validations. Instead of bundling all validation logic into a single business object (which is considered less than ideal), developers can use mixins to create specialized classes. For instance, defining `class AccountForCustomer extends Account with AccountValidations, AccountCustomerValidations` and `class AccountForAdmin extends Account with AccountValidations, AccountAdminValidations` ensures that the correct, specialized validation logic is automatically applied when passing instances of `AccountForCustomer` or `AccountForAdmin` between code parts. Ultimately, regardless of whether the technique is interfaces/protocols, delegation, or mixins/traits, the best approach is always to use the technique that most accurately expresses the developer's architectural intent.
