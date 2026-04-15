# actors-and-processes-concurrency

**Parent:** [[content/L1/professional-toolkit-and-distributed-concurrency|professional-toolkit-and-distributed-concurrency]] — Professional mastery requires mastering a comprehensive toolkit, covering physical instruments, systematic workflow management (using techniques like PERT/Scenario-Based and Iterative Estimation), and advanced programming skills (including shell command mastery, editor fluency, and VCS management). For concurrency, developers use the Actor Model (independent virtual processors with private state and unidirectional message passing) or Blackboard systems (central, stateful coordination mechanisms suitable for complex, asynchronous data gathering), while debugging relies on structured techniques like the 'chop' method and the use of tracing statements.

Actors and processes are mechanisms for implementing concurrency without the burden of synchronizing access to shared memory. To understand this approach, one must first define the terms. 

An actor is defined as an independent virtual processor that maintains its own local, private state. Every actor possesses a mailbox; when a message arrives in the mailbox and the actor is idle, the actor activates to process the message. After completing message processing, the actor proceeds to the next message in the mailbox, or returns to sleep if the mailbox is empty. While processing a message, an actor has the ability to create other actors, send messages to known actors, and generate a new state that will become the active state when the subsequent message is processed.

A process is generally a more versatile virtual processor, which operating systems often utilize to facilitate concurrency. For the purposes of this discussion, developers should consider only those processes that are constrained (by convention) to behave like actors.

***

**Key Characteristics of Actors:**
*   Actors do not rely on a single central component for control; no single thing schedules the flow of events or orchestrates the transfer of information from raw data to the final output.
*   The entire system's state is held solely within the messages and within the local state of each individual actor. Messages can only be examined by the recipient reading them, and the local state is inaccessible from outside the actor.
*   All messages are unidirectional; the actor model does not include a concept of replying. If an actor needs to send a response, the user must include the actor's mailbox address within the initial message sent, and the actor will eventually return the response as just another message to that mailbox.
*   An actor processes each message entirely to completion and processes only one message at a time.

Consequently, actors operate concurrently, asynchronously, and without sharing data. If adequate physical processors are available, an actor can run on each. If only a single processor is available, a runtime environment must handle the context switching between the actors. Crucially, the code running within the actors remains consistent regardless of the underlying hardware capability.

***

**Implementing Actors for Concurrency:**

To illustrate, the chunk outlines an implementation of a diner using three actors: the customer, the waiter, and the pie case. The entire message flow begins when an external entity (referred to as a 'God-like being') sends the initial message that the customer is hungry. The customer then messages the waiter, who subsequently messages the pie case to request pie for the customer. If the pie case has a slice available, it sends the slice to the customer and also notifies the waiter to update the bill. If no pie is available, the pie case notifies the waiter, who then apologizes to the customer.

The provided code implements this logic using the Nact library in JavaScript, utilizing a simple object structure where keys represent message types and values contain functions executed upon receiving that message. The customer actor can receive messages like `'hungry for pie'`, `'put on table'`, and `'no pie left'`. The waiter actor processes an `'order'` message and, if the request is for pie, dispatches a request to the pie case, passing references to both the waiter and the customer. The pie case actor handles the `'get slice'` message. If the pie case's state, which is an array of slices of pie, has available slices, the actor shifts a slice, dispatches messages to the customer (to update the display), and dispatches a message to the waiter (to update the order), and finally returns an updated state containing one fewer slice. If the pie case finds no slices, it dispatches an `'error'` message to the waiter.

Finally, the actors are initialized manually using `start_actor` and passed initial state: the pie case receives the initial list of three slices (`['apple', 'peach', 'cherry']`), the waiter receives a reference to the pie case, and both customers (`customer1` and `customer2`) receive a reference to the waiter. The simulation runs by dispatching messages, leading to the observed state changes in the console, such as `customer1 sees 
