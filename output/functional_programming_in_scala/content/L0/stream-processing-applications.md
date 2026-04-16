# stream-processing-applications

**Parent:** [[content/L1/advanced-functional-architecture-overview|advanced-functional-architecture-overview]] — The synthesis describes a robust functional architecture relying on Algebraic Data Types (ADTs) and higher-order functions to achieve referential transparency. Key mechanisms include `Stream[+A]` for memory-efficient lazy data processing, `Option` and `Either` for controlled flow, `Par[A]` and the Actor model for non-blocking concurrency, and the `Free[F[_],A]` type for generalized effect modeling, exemplified by `IO` using trampolining.

Stream processing is a highly applicable abstraction, making it possible to model a surprising number of programs. This applicability can be observed across various functional domains:

1. **Handling External Effects and I/O**: The process of I/O can be modeled using stream processors. For instance, to process data from `fahrenheits.txt` and write the resulting Celsius values to a single file named `celsius.txt`, the specific computation written using the `Process` type is: `val convertAll: Process[IO,Unit] = (for { out <- fileW("celsius.txt").once; file <- lines("fahrenheits.txt"); _ <- lines(file).map(line => fahrenheitToCelsius(line.toDouble)).flatMap(celsius => out(celsius.toString)).} yield ()) drain`.

2. **Multi-Sink Processing**: To write transformed data to multiple files—specifically, by appending `.celsius` to the original input file name—the program structure must switch the order of `flatMap` calls. The resulting code is: `val convertMultisink: Process[IO,Unit] = (for { file <- lines("fahrenheits.txt"); _ <- lines(file).map(line => fahrenheitToCelsius(line.toDouble)).map(_ toString).to(fileW(file + ".celsius"))} yield ()) drain`.

3. **Filtering and Advanced Transformations**: Stream processing allows developers to attach additional transformations at any point. For example, filtering lines that do not start with `#` and simultaneously filtering for temperatures greater than 0 (to exclude below zero temperatures) is achieved by combining mapping and filtering steps: `val convertMultisink2: Process[IO,Unit] = (for { file <- lines("fahrenheits.txt"); _ <- lines(file).filter(!_.startsWith("#")).map(line => fahrenheitToCelsius(line.toDouble)).filter(_ > 0).map(_ toString).to(fileW(file + ".celsius"))} yield ()) drain`.

These principles of stream processing and incremental I/O are widely applicable, as detailed in the `15.4 Applications` section.
