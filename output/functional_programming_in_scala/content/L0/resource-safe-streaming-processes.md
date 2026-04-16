# resource-safe-streaming-processes

**Parent:** [[content/L1/functional-algebra-stream-processing-mechanisms|functional-algebra-stream-processing-mechanisms]] — The system integrates functional programming concepts, utilizing ADTs like Option and Either for total functions and structured error handling, and employs `Stream` for memory-efficient non-strict data processing. Resource safety is maintained through the `resource` combinator and refined by the `Process1` type for single inputs. Complex multi-input stream processing is managed using the `Tee` structure and its associated combinators ($	ext{awaitL}$, $	ext{awaitR}$, $	ext{zipWith}$), which allow multiple source processes to synchronize and communicate while guaranteeing proper cleanup actions.

When developing a resource-safe streaming mechanism, several guidelines must be followed to ensure underlying resources (like file handles) are properly managed. First, a producer must free resources as soon as it knows it has no more values to emit, whether that exhaustion is due to normal completion or an exception. Second, any process that consumes values from another process must ensure that cleanup actions of the source process run before the consuming process halts, regardless of whether the halting was caused by producer exhaustion, explicit forceful termination, or an error.

To implement this, the `onComplete` combinator allows developers to append cleanup logic to any `Process`. The definition of `onComplete` works similarly to the `++` operator, but ensures that the cleanup process (`p`) always executes before the outer process halts. The `onComplete` combinator utilizes the `asFinalizer` method, which converts a normal `Process` into one that automatically invokes itself when given a `Kill` exception. This design guarantees that even if a consumer wishes to terminate early, the cleanup action is run. This mechanism is formalized in the general `resource` combinator:

`def resource[R,O](acquire: IO[R])(use: R => Process[IO,O])(release: R => Process[IO,O]): Process[IO,O] = await[IO,R,O](acquire)(r => use(r).onComplete(release(r)))`

This combination ensures that the underlying resource is freed, regardless of how the process terminates.

To enable transformations on resource-safe sources, the concept of single-input processes (`Process1[I,O]`) was introduced. `Process1[I,O]` is defined as a type alias for `Process[Is[I]#f, O]`, where `Is[I]#f` is a specialized type that restricts the `Process` to only request values of type `I`. This structure allows defining helper functions like `await1[I,O]`, `emit1[I,O]`, and `halt1[I,O]` for type safety.

Using these single-input helpers, standard combinators like `lift` and `filter` can be redefined for `Process1`:

*   **Mapping (`lift`):** `def lift[I,O](f: I => O): Process1[I,O] = await1[I,O](i => emit(f(i))) repeat`
*   **Filtering (`filter`):** `def filter[I](f: I => Boolean): Process1[I,I] = await1[I,I](i => if (f(i)) emit(i) else halt1) repeat`

Process composition is refined by ensuring that cleanup actions are run correctly when connecting processes. The `|>` combinator, which transforms a process, now incorporates logic to run cleanup actions from the left process before the right process halts. The `|>` combinator implementation handles termination through `Halt(e)` or `Kill` by using `onHalt` and the `onComplete` logic to preserve cleanup.

These resource-safe and single-input process mechanisms allow for the definition of complex stream processing logic, such as the `lines` function, which creates a `Process[IO,String]` reading from a file: `def lines(filename: String): Process[IO,String] = resource{ IO(io.Source.fromFile(filename)) }{ src => lazy val iter = src.getLines // a stateful iterator; def step = if (iter.hasNext) Some(iter.next) else None; lazy val lines: Process[IO,String] = eval(IO(step)).flatMap { case None => Halt(End); case Some(line) => Emit(line, lines) }; lines }{ src => eval_ { IO(src.close) } }`
