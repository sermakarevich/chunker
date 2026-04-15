# data-flow-transformational-model

**Parent:** [[content/L1/software-engineering-workflows-and-architecture|software-engineering-workflows-and-architecture]] — Professional proficiency requires mastering tools and workflows, utilizing techniques like PERT (requiring optimistic, most likely, and pessimistic estimates) and iterative development (which demands formal schedule refinement and detailed logging of prediction errors over 50% inaccuracy). Furthermore, complex systems should be designed using a data-flow transformational model, not isolated components, and developers must mitigate the coupling risks associated with inheritance by favoring Interfaces, Delegation, and Mixins/traits.

The principle of passing data as a continuous flow, rather than storing it in isolated pools across a system, is a transformational model for data management. In this model, data becomes a peer to functionality, forming a pipeline structure: code $\to$ data $\to$ code $\to$ data, and the data itself is not tied to a specific class definition. This approach allows for a significant reduction in coupling, making a function reusable anywhere its parameters match the output of another function. While a residual degree of coupling remains, the text suggests this form of coupling is more manageable than Object-Oriented (OO)-style command and control.

If the developer is using a language with type checking, the language will generate compile-time warnings if the developer attempts to connect two incompatible elements.

When using this transformational model, the developer must also handle error conditions. The basic convention is to never pass raw values between transformations. Instead, developers must wrap the values in a data structure (or type) that explicitly signals whether the contained value is valid. Languages like Haskell use this wrapper, called `Maybe`, while F# and Scala use `Option`.

In general, developers can implement this concept using two basic methods: handling error checking within the individual transformations or managing it outside the transformations. 

When establishing a representation for the wrapper—the data structure carrying either a value or an error indication—developers can utilize language conventions. For instance, Elixir commonly returns a tuple containing either `{:ok, value}` or `{:error, reason}`. For example, `File.open("/etc/passwd")` returns `{:ok, #PID<0.109.0>}`, and `File.open("/etc/wombat")` returns `{:error, :enoent}`.

One approach involves handling errors inside each transformation. If the first parameter of a function is an `{:ok, content}` tuple, the function proceeds to find matching lines; otherwise, the function executes a second version, which simply returns the error tuple, thus propagating the error down the pipeline. This pattern was demonstrated using the function `find_matching_lines`:

```elixir
defp find_matching_lines({:ok, content}, pattern) do
content
|> String.split(~r/\n/)
|> Enum.filter(&String.match?(&1, pattern))
|> ok_unless_empty()
end
defp find_matching_lines(error, _), do: error
```

When handling errors within the pipeline itself, the goal is to defer running pipeline functions until previous steps are confirmed successful. This requires changing function calls into function values that can be called later, leading to the use of an `and_then` bind function:

```elixir
defmodule Grep1 do
def and_then({:ok, value }, func), do: func.(value)
def and_then(anything_else, _func), do: anything_else

def find_all(file_name, pattern) do
File.read(file_name)
|> and_then(&find_matching_lines(&1, pattern))
|> and_then(&truncate_lines(&1))
end
```

The concept of viewing code as a series of transformations is a powerful approach that leads to cleaner, shorter, and flatter code, which the original text encourages developers to adopt.
