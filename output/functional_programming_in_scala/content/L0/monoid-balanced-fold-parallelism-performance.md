# monoid-balanced-fold-parallelism-performance

**Parent:** [[content/L1/Est',|Est',]] — Hic

When a monoid's operation is associative, users have flexibility in choosing how they fold a data structure, such as a list. While operations can be sequentially associated to the left using `foldLeft` or to the right using `foldRight`, a more efficient approach is to use a balanced fold, which also enables parallelism. For example, if a user has a sequence of elements $a, b, c, d$ that they wish to reduce using a monoid, the combination process can be structured as follows: 

Right fold: `op(a, op(b, op(c, d)))`

Left fold: `op(op(op(a, b), c), d)`

Balanced fold: `op(op(a, b), op(c, d))`

The balanced fold is beneficial because the two inner `op` calls are independent and can be run simultaneously, allowing for parallelism. Furthermore, the balanced tree structure can be more efficient when the cost of each operation (`op`) is proportional to the size of its arguments. Consider the runtime performance of evaluating `List("lorem", "ipsum", "dolor", "sit").foldLeft("")(_ + _)`: at every step of the fold, the system allocates the full intermediate String only to discard it and allocate a larger string in the next step. This is because String values are immutable, and evaluating `a + b` for strings $a$ and $b$ requires allocating a fresh character array and copying both $a$ and $b$ into this new array. The time taken for this operation is proportional to `a.length + b.length`. 

A trace of the provided expression demonstrates the creation and discarding of intermediate strings:
1. `List("lorem", "ipsum", "dolor", "sit").foldLeft("")(_ + _)`
2. `List("ipsum", "dolor", "sit").foldLeft("lorem")(_ + _)`
3. `List("dolor", "sit").foldLeft("loremipsum")(_ + _)`
4. `List("sit").foldLeft("loremipsumdolor")(_ + _)`
5. `List().foldLeft("loremipsumdolorsit")(_ + _)`
6. Result: `
