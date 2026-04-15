# managing-resources-and-deallocation

**Parent:** [[content/L1/software-proficiency-systems-architecture-and-resource-management|software-proficiency-systems-architecture-and-resource-management]] — Professional proficiency requires mastery of specialized tools and workflows, utilizing techniques like PERT (requiring optimistic, most likely, and pessimistic estimates) and Incremental Iteration. Code stability demands rigorous resource management through techniques such as scope-based cleanup, `finally` clauses, and adherence to architectural principles like the Law of Demeter (minimizing method chaining) and utilizing the 'chop' technique for debugging large systems.

When developing software, programmers must manage both ephemeral resources used by a running process and other potential messes left behind. For instance, if a programmer creates logging records, the programmer must implement a mechanism to rotate and clean up the logs, which consumes storage space. Similarly, if a program creates unofficial debug files or adds logging records to a database, a cleanup process must be in place to expire these resources, considering how to balance all created finite resources.

**Nested Allocations**
For routines requiring multiple resources, the basic resource allocation pattern can be extended with two primary rules:
1. **Deallocate resources in the reverse order of allocation:** This prevents resources from becoming orphaned if one resource contains references to another. 
2. **Allocate resources in the same order:** When allocating the same set of resources in different parts of the code, always allocate them in the same sequence to minimize the possibility of deadlock (for example, if Process A claims resource1 and is about to claim resource2, while Process B has claimed resource2 and is trying to get resource1, the two processes will wait indefinitely).

Regardless of the resource type—including transactions, network connections, memory, files, threads, or windows—the core rule remains: the party that allocates a resource must be responsible for deallocating it. This concept can be further developed in object-oriented languages.

**Objects and Exceptions**
The management of resource allocation and deallocation is analogous to an object-oriented class's constructor and destructor. In this pattern, the class represents a resource; the constructor provides a specific object of that resource type, and the destructor removes it from the program’s scope. If a developer is using an object-oriented language, developers can encapsulate resources in classes: when an object is no longer needed or is reclaimed by the garbage collector, the object's destructor automatically deallocates the wrapped resource.

This approach is particularly beneficial when working with languages that support exceptions. Languages supporting exceptions make resource deallocation complex because developers must ensure that all resources allocated before an exception is thrown are properly cleaned up. Developers generally have two primary choices for managing this:
1. **Using variable scope:** Languages like C++ or Rust allow the variable's memory to be reclaimed when the variable exits its scope, whether through a return, a block exit, or an exception. Developers can hook into the variable's destructor to cleanup any external resources, as demonstrated by the Rust variable `accounts` which automatically closes the associated file upon exiting its scope.
2. **Using a `finally` clause:** If the language supports it, a `finally` clause guarantees that the specified cleanup code will run, regardless of whether an exception was raised in the `try...catch` block. Developers must ensure that the allocation occurs before the `begin` block, otherwise, the `finally` clause will attempt to deallocate a resource that was never allocated.

**When Resource Balancing is Difficult**
Sometimes, the basic resource allocation pattern is insufficient, a common scenario being programs that use dynamic data structures. If one routine allocates a memory area and links it into a larger structure, the developer must decide who is responsible for the data within the aggregate structure. Developers have three main options for this decision, which must be made explicit and implemented consistently:
1. The top-level structure is responsible for freeing all contained substructures, which then recursively delete the data they contain. 
2. The top-level structure is simply deallocated, allowing any structures it pointed to (that are not referenced elsewhere) to become orphaned. 
3. The top-level structure refuses to deallocate itself if it contains any substructures.

The choice among these options depends on the specific circumstances of the individual data structure. For procedural languages like C, where data structures are not active, the preferred method is to write a module for each major structure that provides standard allocation and deallocation facilities. This module can also provide ancillary services such as debug printing, serialization, deserialization, and traversal hooks.

**Checking the Balance**
Because responsible developers mistrust anyone, including themselves, building code that actively checks that resources are properly freed is essential. For most applications, this involves creating wrappers for each resource type to track all allocations and deallocations. Program logic should use these wrappers to check the resource state at expected points (e.g., at the top of a main processing loop that waits for the next request). At a lower level, developers can also use tools that check running programs for memory leaks.
