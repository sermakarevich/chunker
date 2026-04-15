# domain-languages-and-coding-vocabulary

**Parent:** [[content/L1/development-methodologies-prototyping-dsls-and-estimation|development-methodologies-prototyping-dsls-and-estimation]] — System development relies on key methodologies, distinguishing disposable prototypes (for risk assessment) from functional, persistent tracer code (for architectural skeletons). It also details advanced techniques like using domain-specific languages (DSLs) and structured methods for project estimation to ensure project feasibility and system design integrity.

When analyzing problems, developers should consider the influence of domain languages. Computer languages influence how a person thinks about a problem, and the limits of one's language determine the limits of one's ability to communicate. Every language world contains a specific set of features, such as buzzwords like static versus dynamic typing, early versus late binding, functional versus object-oriented (OO), inheritance models, mixins, or macros. Designing a solution using C++ will yield different results than basing a solution on Haskell-style thinking, and vice versa. Importantly, the language of the problem domain can also suggest a programming solution. Therefore, programmers should always attempt to write code using the vocabulary of the application domain (refer to Maintain a Glossary). In some advanced cases, programmers can write code that actually uses the vocabulary, syntax, and semantics—the language—of the domain.

**Examples of Real-World Domain Languages**

*   **RSpec:** RSpec[19] is a testing library for Ruby that inspired similar versions for most other modern languages. An RSpec test is meant to reflect the expected behavior of the code. For example, the following test structure is provided:
    ```
describe BowlingScore do
it "totals 12 if you score 3 four times" do
score = BowlingScore.new
4.times { score.add_pins(3) }
expect(score.total).to eq(12)
end
end
```
*   **Cucumber:** Cucumber[20] offers a programming-language neutral method for specifying tests. Running the tests requires a version of Cucumber appropriate to the language being used. Because Cucumber supports natural-language like syntax, specific matchers must be written to recognize phrases and extract parameters for the tests. The structure is defined using a Feature, Background, Scenario, Given, And, and Then keywords, for instance:
    ```
    Feature: Scoring
    Background:
    Given an empty scorecard
    Scenario: bowling a lot of 3s
    Given I throw a 3
    And I throw a 3
    And I throw a 3
    And I throw a 3
    Then the score should be 12
    ```
    Cucumber tests were designed for consumption by software customers, although this practice happens infrequently in professional practice. 
*   **Phoenix Routes:** Many web frameworks include a routing facility that maps incoming HTTP requests to handler functions in the code. One example from Phoenix is provided:
    ```
    scope "/", HelloPhoenix do
    pipe_through :browser # Use the default browser stack
    get "/", PageController, :index
    resources "/users", UserController
    end
    ```
    This code specifies that requests beginning with “/” will be processed through a series of filters appropriate for browsers. A request to “/” itself will be handled by the index function within the PageController module. Additionally, the UsersController implements the functions necessary to manage a resource accessible via the URL /users.
*   **Ansible:** Ansible[22] is a tool that configures software, typically on numerous remote servers. Ansible reads a specification provided by the user and executes the necessary actions on the servers to ensure they mirror that specification. The specification can be written in YAML, a language that builds data structures from text descriptions. For example, to ensure the latest version of Nginx is installed, running and configured to start automatically, and setting up a provided configuration file, the following YAML specification is used:
    ```yaml
    --- name: install nginx
    apt: name=nginx state=latest
    - name: ensure nginx is running (and enable it at boot)
    service: name=nginx state=started enabled=yes
    - name: write the nginx config file
    template: src=templates/nginx.conf.j2 dest=/etc/nginx/nginx.conf
    notify:
    - restart nginx
    ```

**Characteristics and Trade-offs of Domain Languages**

When examining these examples more closely, RSpec and the Phoenix router are written in their respective host languages (Ruby and Elixir). These examples use fairly complex code, including metaprogramming and macros, but ultimately compile and run as regular code. Conversely, Cucumber tests and Ansible configurations are written in their own dedicated languages. A Cucumber test is converted into code or a data structure ready to be run, while Ansible specifications are always converted into a data structure that Ansible uses. As a result, RSpec and the router code constitute internal domain languages, meaning they are embedded into the code that runs. In contrast, Cucumber and Ansible utilize external domain languages, where the host language reads the code and converts it into a form the code can use.

**Comparing Internal and External Domain Languages**

Generally, an internal domain language benefits from the features of its host language, making the domain language more powerful at no additional cost. For instance, one can use Ruby code to automatically create multiple RSpec tests, such as a test for calculating scores when there are no spares or strikes:
    ```
describe BowlingScore do
(0..4).each do |pins| 
(1..20).each do |throws| 
    target = pins * throws
    it "totals #{target} if you score #{pins} #{throws} times" do
    score = BowlingScore.new
    throws.times { score.add_pins(pins) }
    expect(score.total).to eq(target)
end
end
end
```

The drawback of internal domain languages is that the programmer remains bound by the syntax and semantics of the host language. Although some languages are remarkably flexible in this aspect, the programmer must compromise between the desired language and the implementable language. Ultimately, any code written must remain valid syntax in the target language; languages featuring macros, such as Elixir, Clojure, and Crystal, offer more flexibility, but syntax remains syntax.

External languages, however, carry no such restrictions. As long as the programmer can write a parser for the language, the language is viable. While it is sometimes possible to reuse an existing parser (as Ansible did with YAML), this situation still necessitates compromise. Writing a good parser is not simple and typically requires adding new libraries and possibly tools to the application. The author advises that programmers should not spend more effort than they save when considering creating a domain language; writing a domain language adds cost to the project, and developers must be convinced of offsetting, potentially long-term, savings.

**Recommendation:** The general recommendation is to use existing external languages, such as YAML, JSON, or CSV, if possible. If external languages are not available, programmers should consider internal languages. The author suggests using external languages only in scenarios where the application's users will write the language. For a cost-effective internal domain language, developers can avoid complex metaprogramming and instead use simple functions to execute the necessary work. This approach, which RSpec uses, makes functions like `describe`, `it`, `expect`, `to`, and `eq` simply methods within the host language (Ruby), meaning the entire process relies on standard code execution and plumbing of objects.
