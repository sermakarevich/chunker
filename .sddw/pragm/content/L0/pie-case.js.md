# pie-case.js

**Parent:** [[content/L1/concurrency-architectural-patterns-and-coding-practices|concurrency-architectural-patterns-and-coding-practices]] — Software development requires continuous, non-mechanical critical decision-making, underpinned by architectural principles like DRY, orthogonality, and decoupling; for concurrency, the Actor Model (featuring independent state, mailboxes, and message-only communication) and Blackboard Systems (allowing asynchronous coordination by independent agents) are preferred alternatives to traditional shared resources, even if they increase system complexity.

The difficulty of managing concurrency in a shared resource environment necessitates adopting alternative architectural patterns. While many languages offer library support for mutual exclusion through constructs like mutexes, monitors, or semaphores, some languages, such as Rust, enforce concurrency support at the language level, for example, by enforcing data ownership so that only one variable or parameter can reference a specific piece of mutable data at any given time. Furthermore, functional languages, by making data immutable, simplify concurrency, but they still encounter challenges when they must interact with the real, mutable world.

Because concurrency in a shared resource environment is difficult and managing it manually is fraught with challenges, the Actor Model provides a recommended alternative.

**Actors and Processes:**
An actor is defined as an independent virtual processor possessing its own local, private state. Every actor includes a mailbox; when a message arrives in the mailbox and the actor is idle, the actor becomes active, processes the message, and continues processing subsequent messages in the mailbox until the mailbox is empty. When processing a message, an actor has the capability to create other actors, send messages to known actors, and establish a new state for use when the next message is processed. A process is a more general-purpose virtual processor, typically implemented by the operating system to facilitate concurrency. The specialized type of process meant here is one that can be constrained by convention to behave like an actor.

**Core Principles of Actors:**
Actors are designed such that:
1. No single entity controls the system; nothing schedules the sequence of events or orchestrates the transfer of information from raw data to the final output.
2. All system state is held either in messages or in the local state of each individual actor. Messages cannot be examined except by being read by the recipient, and local state remains inaccessible outside the actor.
3. All message transfers are unidirectional; actors cannot reply directly. If an actor must return a response, the sending actor must include its own mailbox address within the message. Crucially, an actor processes each message entirely to completion, and it can only process one message at a time.

As a result, actors execute concurrently, asynchronously, and crucially, share no state. If sufficient physical processors are available, an actor can run on each. If only a single processor is available, a runtime system handles the context switching between actors. In either scenario, the code executed within the actors remains identical.

**Implementation Example: The Diner Scenario:**
To illustrate, the system models a diner using three actors: the customer, the waiter, and the pie case. The message flow proceeds as follows: The external system sends a 'hungry for pie' message to the customer. The customer responds by sending an 'order' message to the waiter, requesting pie. The waiter then instructs the pie case to 'get slice' for the customer. If the pie case has a slice available, it sends the slice to the customer and notifies the waiter to add the slice to the bill. If the pie case has no slices, the case sends an 'error' message to the waiter, and the waiter apologizes to the customer.

The code examples utilize the Nact library in JavaScript and employ a simple wrapper structure where keys represent incoming message types and values are functions executed upon receiving that message.

**Initial Setup and Execution:**
1. **Customer Actor:** The customer receives three types of messages: 'hungry for pie' (from the external context), 'put on table' (from the pie case), and 'no pie left' (from the waiter). When receiving 'hungry for pie', the customer dispatches an 'order' message to the waiter.
2. **Waiter Actor:** The waiter handles an 'order' message (checking if the request is for pie); if so, the waiter dispatches a 'get slice' message to the pie case, passing references to both the customer and the waiter. The waiter also handles 'add to order' and 'error' messages. The 'error' message handler dispatches a 'no pie left' message back to the customer, which triggers the waiter to display an apology.
3. **Pie Case Actor:** The pie case maintains a state that is an array of all available pie slices. Upon receiving a 'get slice' message from the waiter, the pie case checks if the `state.slices.length` is zero. If slices are available, the pie case uses `state.slices.shift()` to get a slice, dispatches 'put on table' to the customer, dispatches 'add to order' to the waiter, and returns the updated state with one less slice. If the array length is zero, the pie case dispatches an 'error' message to the waiter, returning the unmodified state.

**Execution Sequence:**
By manually starting the three actors and passing them initial states (the pie case starts with `[
