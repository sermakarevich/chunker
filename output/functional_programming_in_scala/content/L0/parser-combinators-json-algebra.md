# parser-combinators-json-algebra

**Parent:** [[content/L1/functional-algebra-synthesis|functional-algebra-synthesis]] — The synthesis details how functional programming APIs are designed using algebras, detailing specific combinators and types like Option, Either, Stream, Par, and flatMap. It covers advanced topics such as managing non-strictness for optimal data transformation, resolving concurrency deadlocks using the Actor model, enabling context-sensitive parsing via `flatMap`, and structuring comprehensive error reporting mechanisms.


The introduction of `flatMap` serves as a new primitive combinator, enabling context-sensitive parsing and allowing the implementation of both `map` and `map2` combinators. This is not the first time `flatMap` has been used, but its inclusion significantly enhances the expressive power of the library. With `flatMap`, the set of primitives is reduced to six: `string`, `regex`, `slice`, `succeed`, `or`, and `flatMap`. This increased power means that the parser can parse not only general context-free grammars, such as JSON, but also more complex context-sensitive grammars, including languages like C++ and PERL.

To demonstrate this capability, the following section outlines the creation of a JSON parser. Although the JSON parser will be written before a concrete implementation of the `Parsers` algebra is available, and before any combinators for good error reporting are added, the JSON parser does not need to be aware of the internal details of how parsers are represented. The function to produce a JSON parser will accept a placeholder for the JSON parse result type and require the `Parsers` trait: `def jsonParser[Err, Parser[+_]](P: Parsers[Err, Parser]): Parser[JSON] = { ... }`. This design approach is typical in functional programming because defining an algebra first—before having a concrete implementation—allows the developer to refine the algebra's expressiveness and structure without committing to a specific implementation, simplifying the design phase.

After developing the JSON parser, the focus will shift to improving error reporting. This enhancement can be achieved without disturbing the overall API structure or significantly changing the JSON parser's implementation. Subsequently, the text will define a concrete, runnable representation for the `Parser` type. Critically, the JSON parser implemented in the next section will remain completely independent of this representation. 

**JSON Format Definition:**
JSON values can be one of several types. An object in JSON is a comma-separated sequence of key-value pairs enclosed in curly braces (`{}`). Keys must be strings (e.g., "Ticker", "Price"), and the values can be another JSON object, an array (e.g., `["HPQ", "IBM"...]` containing further values), or a literal value like a string ("MSFT"), boolean (`true`, `false`), `null`, or a number (e.g., 30.66).

To represent a parsed JSON document, a data type named `JSON` is introduced with the following structure:
```scala
trait JSON
object JSON {
case object JNull extends JSON
case class JNumber(get: Double) extends JSON
case class JString(get: String) extends JSON
case class JBool(get: Boolean) extends JSON
case class JArray(get: IndexedSeq[JSON]) extends JSON
case class JObject(get: Map[String, JSON]) extends JSON
}
```

**JSON Parser Primitives and Combinators:**
Developers recall that existing primitives include: `string(s)` (recognizing and returning a single String), `regex(s)` (recognizing a regular expression `s`), `slice(p)` (returning the portion of input inspected by parser `p` if successful), `succeed(a)` (always succeeding with value `a`), `flatMap(p)(f)` (running parser `p`, and then using its result `f` to select a second parser to run in sequence), and `or(p1, p2)` (choosing between two parsers, first attempting `p1`, and then `p2` if `p1` fails). These primitives were used to define combinators such as `map`, `map2`, `many`, and `many1`.

**Task: Building the JSON Parser:**
The reader is tasked with creating a `Parser[JSON]` from scratch using the defined primitives. The developer is encouraged to follow the existing developmental process: discovering additional general-purpose combinators and idioms, noticing and factoring out common patterns, and continually refining the design. If the developer gets stuck, they can consult provided answers.

**Error Reporting Design:**
Currently, no combinator addresses error reporting. The combinators only specify the grammar and the expected result upon successful parsing. For the purpose of advanced design, the user must consider adding capabilities to specify how the parser responds to unexpected input. The developer is guided by the following questions to design better error handling:
1. Given the parser "abra"." "".many"."cadabra", what error should be reported for the input "abra cAdabra" (where 'A' is capitalized)? Should the error message only be 'Expected a'? Or 'Expected 
