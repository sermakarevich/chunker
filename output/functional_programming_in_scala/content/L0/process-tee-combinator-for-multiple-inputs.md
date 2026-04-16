# process-tee-combinator-for-multiple-inputs

**Parent:** [[content/L1/functional-algebra-stream-processing-mechanisms|functional-algebra-stream-processing-mechanisms]] — The system integrates functional programming concepts, utilizing ADTs like Option and Either for total functions and structured error handling, and employs `Stream` for memory-efficient non-strict data processing. Resource safety is maintained through the `resource` combinator and refined by the `Process1` type for single inputs. Complex multi-input stream processing is managed using the `Tee` structure and its associated combinators ($	ext{awaitL}$, $	ext{awaitR}$, $	ext{zipWith}$), which allow multiple source processes to synchronize and communicate while guaranteeing proper cleanup actions.

To expand the capabilities of the `Process` type, convenience functions can be added for operations like `take`, `takeWhile`, and similar pattern matches. The `Process` type can handle complex scenarios involving multiple input streams, such as zipping together two files: `f1.txt` and `f2.txt`. This scenario requires adding corresponding functionality to the general `Process` type. Just as `Process1` was a specialized instance of `Process`, a combining mechanism for multiple inputs, called `Tee`, can be defined as a `Process` type. The `Tee` function combines multiple input streams into a single output. The `Tee` structure is formally implemented using a specialized type constructor `f` and resulting classes `L` and `R`, which mimic the structure of `Process` but handle two possible values, $L$ and $R$, using an `Either[I => X, I2 => X]` to distinguish input types during pattern matching.

Developers can define a type alias, `Tee[I,I2,O]`, for processes that accept two distinct types of inputs: `Process[T[I,I2]#f, O]`. To assist in building processes with two inputs, several convenience functions were defined:

*   `haltT[I,I2,O]`: Defines a `Tee[I,I2,O]` that halts using `Halt[T[I,I2]#f,O](End)`. 
*   `awaitL[I,I2,O]`: Waits for input from the left stream (`I`). If the result is `Left(End)` or `Left(err)`, it uses a specified `fallback` process. If successful (`Right(a)`), it attempts to execute the provided continuation function `recv(a)`. This function uses `await[T[I,I2]#f,I,O](L) { case Left(End) => fallback; case Left(err) => Halt(err); case Right(a) => Try(recv(a)) }`.
*   `awaitR[I,I2,O]`: Waits for input from the right stream (`I2`). Similarly, it utilizes `await[T[I,I2]#f,I2,O](R) { case Left(End) => fallback; case Left(err) => Halt(err); case Right(a) => Try(recv(a)) }`.
*   `emitT[I,I2,O]`: Emits a value `h` followed by a continuation process `tl: Tee[I,I2,O]`, defaulting to `haltT[I,I2,O]`. 

Two specific `Tee` combinators were then defined:

1.  **`zipWith[I,I2,O]`**: This combines two inputs by awaiting input `i` from the left stream and then awaiting input `i2` from the right stream, followed by emitting the result of the function `f(i, i2)`: `awaitL[I,I2,O](i => awaitR(i2 => emitT(f(i,i2)))) repeat`.
2.  **`zip[I,I2]`**: This is a specific case of `zipWith` where the output type `O` is the tuple `(I, I2)`: `zipWith((_,_))`.

This `zip` transducer halts when either input stream is exhausted, similar to `zip` on a `List`.

For general process chaining, a function `tee[O2,O3](p2: Process[F,O2])(t: Tee[O,O2,O3]): Process[F,O3]` combines two processes, `p2` and `t`. This function proceeds by analyzing the structure of the `t` process: if `t` halts, both inputs (`this` and `p2`) are gracefully killed, propagating the halt exception. If `t` emits a value, it recursively calls `tee` with the emitted value and the tail of `t` and `p2`. If `t` awaits input from the left side, the function executes `await(reqL)(recvL andThen (this2 => this2.tee(p2)(t)))`.

If `t` awaits input from the right side, the function executes `await(reqR)(recvR andThen (p3 => this.tee(p3)(t)))`. These implementations are analogous to how the `tee` operation works when integrating with two processes.
