# non-blocking-asynchronous-io

**Parent:** [[content/L1/advanced-fp-algebraic-design|advanced-fp-algebraic-design]] — Advanced functional programming mandates using algebraic structures (ADTs, Functor, Applicative, Monad) to treat computation as a first-class value, ensuring type safety and referential transparency by encapsulating side effects. Effect management is achieved using the `Free[F, A]` monad, where $F$ is the protocol, enabling interpreters (e.g., `runConsolePar`) to translate abstract I/O (like `ConsoleIO[A]`) into concrete structures (`Par[A]`) suitable for both trampolined and non-blocking asynchronous execution.

When extending the discussion on external effects and I/O to handle non-blocking or asynchronous I/O, a problem with the original `IO` monad is encountered: the inability to manage I/O operations that take a long time to complete without blocking the CPU. Such operations include accepting a network connection from a server socket, reading a chunk of bytes from an input stream, or writing a large number of bytes to a file. The approach involves considering how these requirements impact the implementation of the `Free` interpreter. When the `runConsole` function, for example, encounters a `Suspend(s)` structure, the variable `s` will be of type `Console`, and the interpreter will utilize a translation function `f` that maps the `Console` type to the target monad. To accommodate non-blocking asynchronous I/O, the target monad must be changed from `Function0` to a concurrency monad, such as `Par` or `scala.concurrent.Future`. This ensures that just as developers could write both pure and effectful interpreters for `Console`, they can also write both blocking and non-blocking interpreters simply by varying the target monad.

For example, the function `runConsolePar` will translate the `Console` requests into `Par` actions and then combine them into a single `Par[A]`. This process is analogous to a compilation, replacing the abstract `Console` requests with concrete `Par` requests that will actually read from and write to the standard input and output streams when the resulting `Par` value is run. The following code block illustrates this:

```scala
def p: ConsoleIO[Unit] = for {
|
_ <- printLn("What's your name?")
|
n <- readLn
|
_ <- n match {
|
case Some(n) => printLn(s"Hello, $n!")
|
case None => printLn(s"Fine, be that way.")
|
}
|
} yield ()
p: ConsoleIO[Unit] = FlatMap(Suspend(PrintLine(What's your name?)),<function1>)
val q = runConsolePar(p)
q: Par[Unit] = <function1>
```

Although this simple example runs within `Par`, which permits asynchronous actions in principle, the use of `readLine` and `println` still involves blocking I/O operations. However, dedicated I/O libraries exist that support non-blocking I/O directly, and the `Par` monad can facilitate binding to these libraries. For instance, a non-blocking source of bytes might feature an interface like this:

```scala
trait Source {
def readBytes(
numBytes: Int,
callback: Either[Throwable, Array[Byte]] => Unit): Unit
}
```

Here, it is assumed that `readBytes` returns immediately, accepting a callback function that specifies the action to perform when the result becomes available or when the I/O subsystem encounters an error. Because the `Par` monad developed in Chapter 7 does not inherently handle exception handling, the provided answer source code includes an example of an asynchronous I/O monad with proper exception handling.

Since directly using such a library is complex, developers seek to program against a compositional monadic interface that abstracts over the details of the underlying non-blocking I/O library. Fortunately, the `Par` type allows wrapping these callbacks. The internal representation of `Future` is similar to `Source`, featuring a single method that returns immediately but accepts a callback or continuation $k$ which it will invoke once the value of type $A$ is available. Developers must add a primitive to the `Par` algebra: `def async[A](run: (A => Unit) => Unit): Par[A] = es => new Future { def apply(k: A => Unit) = run(k) }`.

With this primitive, the asynchronous `readBytes` function can be wrapped into the monadic interface of `Par`:

```scala
def nonblockingRead(source: Source, numBytes: Int): Par[Either[Throwable,Array[Byte]]] = 
  async { (cb: Either[Throwable,Array[Byte]] => Unit) =>
    source.readBytes(numBytes, cb)
  }
def readPar(source: Source, numBytes: Int): Free[Par,Either[Throwable,Array[Byte]]] = 
  Suspend(nonblockingRead(source, numBytes))
```

Using this structure, developers can construct chains of non-blocking computations using regular `for`-comprehensions:

```scala
val src: Source = ...
val prog: Free[Par,Unit] = for {
chunk1 <- readPar(src, 1024)
chunk2 <- readPar(src, 1024)
...}
```

As a practical exercise, developers are tasked with implementing the function `read` using an `AsynchronousFileChannel` (API at `http://mng.bz/X30L`): `def read(file: AsynchronousFileChannel, fromPosition: Long, numBytes: Int): Par[Either[Throwable, Array[Byte]]]`. Note that `runConsoleReader` and `runConsoleState` are not stack-safe as implemented, for the same reason that `runConsoleFunction0` was not stack-safe; this issue can be fixed by changing the representations to `String => TailRec[A]` for `ConsoleReader` and `Buffers => TailRec[(A,Buffers)]` for `ConsoleState`.
