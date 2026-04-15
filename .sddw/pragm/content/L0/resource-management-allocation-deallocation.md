# resource-management-allocation-deallocation

**Parent:** [[content/L1/software-development-best-practices|software-development-best-practices]] — Developers must adopt principles like DRY, PERT, and the Tracer Bullet method, and use assertions to proactively detect impossible software outcomes, while managing limited resources through structured allocation/deallocation patterns.

To manage resources in code—such as memory, transactions, threads, network connections, or files—developers must recognize that all these resources have limited availability. Most of the time, resource usage follows a predictable pattern: a developer allocates the resource, uses it, and then deallocates it.

To address the lack of a consistent plan for resource allocation and deallocation, developers should follow the tip: Finish What You Start. This tip means that the function or object responsible for allocating a resource should also be responsible for deallocating it. 

Consider the following Ruby program example, which reads customer information from a file, updates a field, and writes the result back. The original code, which uses instance variables (`@customer_file`) to share the file reference across routines, is tightly coupled: the `read_customer` routine opens the file and stores the file reference in `customer_file`, and then the `write_customer` routine uses that stored reference to close the file when it completes. This shared variable is not even explicitly mentioned in the `update_customer` routine.

If a programmer subsequently receives a specification change—for example, if the balance should only be updated when the new value is not negative—the programmer might modify the `update_customer` routine: 

```ruby
def update_customer(transaction_amount)
  read_customer
  if (transaction_amount >= 0.00)
    @balance = @balance.add(transaction_amount,2)
    write_customer
  end
end
```

Though this modified code appears fine during testing, when the code runs in a production environment, it may fail after several hours due to too many open files. This failure occurs because, in some specific circumstances, `write_customer` is not called, and consequently, the file is not closed.

A poor solution would involve dealing with this special case within `update_customer`, like this:

```ruby
def update_customer(transaction_amount)
  read_customer
  if (transaction_amount >= 0.00)
    @balance += BigDecimal(transaction_amount, 2)
    write_customer
  else
    @customer_file.close # Bad idea!
  end
end
```

Although this modified structure fixes the problem by ensuring the file closes regardless of the new balance, this approach results in three routines that are coupled through the shared variable `customer_file`. Furthermore, tracking when the file should be opened or closed becomes complex. This situation represents a trap that will quickly become difficult to manage.

Applying the 
