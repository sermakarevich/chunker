# generate-non-empty-lists

**Parent:** [[content/L1/pbt-dependency-refinement-and-parallelism-testing|pbt-dependency-refinement-and-parallelism-testing]] — The Prop structure was refined to accept `MaxSize` in addition to `TestCases` and `RNG`, changing the signature from `(TestCases, RNG) => Result` to `(MaxSize, TestCases, RNG) => Result`. This adaptation was necessary to correctly structure property generation for `forAll` and ensure proper handling of constraints like non-empty lists and parallel computations.

To generate a non-empty list, one must define a generator function, `listOf1`, and subsequently update the property definition for the `max` function to utilize this new generator. This exercise focuses on generating lists and ensuring that the derived property generator correctly handles the non-empty constraint.
