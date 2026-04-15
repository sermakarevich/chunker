# managing-shared-state-in-concurrency

**Parent:** [[content/L1/software-architecture-decoupling-concurrency|software-architecture-decoupling-concurrency]] — Software architecture demands decoupling through protocols/interfaces, delegation, and mixins to avoid coupling and manage ephemeral state, while reliable development requires adhering to DRY, utilizing external configuration services for dynamic parameters, and managing complex workflows using concurrency analysis via activity diagrams and semaphores.

When developing concurrent applications, developers must understand that using shared mutable resources—including files, databases, and external services—by multiple code instances simultaneously creates potential race conditions and concurrency problems. The core issue is shared state, where multiple processes look at or modify a resource independently, without regard for the actions of other processes. For instance, if multiple servers concurrently attempt to sell a limited resource, such as a single piece of apple pie from a display case, each server's independent view of the available pie count is inconsistent, leading to a situation where the resource is over-promised.

Consider the pseudocode for two waiters operating concurrently: 1) check if `display_case.pie_count > 0`; 2) promise the pie to a customer; 3) take the pie using `display_case.take_pie()`; and 4) give the pie to the customer. The problem is not simply that two processes write to the same memory, but that neither process can guarantee that its view of the memory remains consistent when the underlying value changes during execution. Specifically, fetching the pie count and then updating the count is not an atomic operation, meaning the underlying value can change in the middle of the sequence.

To solve this, developers must ensure that resource access is atomic. One technique is employing semaphores or other forms of mutual exclusion. Developers can use a semaphore to control access to the pie case, requiring any waiter wishing to update the pie case contents to first acquire the semaphore. The process involves attempting to acquire the semaphore (analogous to the pseudocode operation `case_semaphore.lock()`), performing the actions (checking count, promising, taking, and giving the pie), and then releasing the semaphore (analogous to `case_semaphore.unlock()`). The semaphore suspends any waiter who fails to acquire it until the first waiter completes the order and releases the semaphore, ensuring that the operations happen sequentially.

However, this approach is fallible because it relies on the convention that *every* developer accessing the pie case must follow the semaphore convention. A more robust solution is to centralize the control by changing the API so that the resource access is managed within the resource object itself. The developer should create a method, such as `get_pie_if_available()`, within the `display_case` class. This method must be protected by a semaphore lock and must use a `try...ensure` block to guarantee that the semaphore is always unlocked, even if an exception occurs during processing. For example:

```pseudocode
def get_pie_if_available():
  @case_semaphore.lock()
  try {
    if @slices.size > 0:
      update_sales_data(:pie)
      return @slices.shift
    else:
      false
  ensure {
    @case_semaphore.unlock()
  }
end
```

When dealing with multiple resources, such as needing both pie and ice cream for an apple pie à la mode, simply calling two separate methods is inadequate, because if the first resource is acquired and the second is unavailable, the first resource remains held, which is undesirable. The optimal fix is to recognize the composite item—the 'apple pie à la mode'—as a single, new resource. The developer should thus move the resource handling code into a dedicated module that manages the acquisition and release of all component resources atomically. This approach encapsulates the complexity, allowing the client code to simply call a single method like “get me apple pie with ice cream,” which either succeeds or fails entirely.

Finally, shared state issues extend beyond memory. Any time an application code shares mutable resources—be it files, databases, or external services—multiple instances of the code can access it concurrently. For example, in a parallel build process using threads, a thread changing the current directory temporarily might cause another thread to fail later with a file-not-found error because the current directory, which is shared, is in an unexpected state, illustrating that even transient changes to shared environment variables can lead to failures in concurrent environments.
