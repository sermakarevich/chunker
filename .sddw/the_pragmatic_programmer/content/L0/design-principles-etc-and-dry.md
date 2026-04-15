# design-principles-etc-and-dry

**Parent:** [[content/L1/developer-pragmatic-principles-communication-design|developer-pragmatic-principles-communication-design]] — Developers must employ second-order thinking, treating natural language as a programming language and applying principles like DRY and ETC, to ensure that all knowledge, including business rules and APIs, has a single, authoritative source representation across code, documentation, and specifications, while tailoring communication pitches to the specific needs of the target audience.

Regarding effective software design, the authors caution against relying on general principles and gurus for guidance, stating that a well-designed system should adapt to the people who use it. For computer code, this means the design must adapt by changing, leading the authors to champion the ETC principle: Easier to Change. This concept suggests that every design principle can be considered a special case of ETC. For example, decoupling is beneficial because isolating concerns makes each concern easier to change, and the single responsibility principle is useful because a change in requirements is mirrored by modifying only one module. Similarly, good naming makes code easier to read, which in turn makes the code easier to change.

The authors emphasize that ETC is a guiding *value*, not a strict *rule*. As a value, ETC helps guide decision-making when choosing between different software development paths. The authors recommend actively reinforcing this value by spending time deliberately asking, when writing code, testing, or fixing bugs, whether the action taken makes the overall system easier or harder to change. While a developer might often use common sense to guess the easiest path for future changes, some times common sense is insufficient. In those instances, developers should take two actions: First, to prepare for unknown future change, developers should make the code replaceable, ensuring that the chunk of code will not become a future roadblock; this fundamentally means keeping the code decoupled and cohesive. Second, developers should treat this process as a way to develop instincts by documenting the situation, the available choices, and potential guesses about change in the engineering daybook and leaving a tag in the source code. This allows the developer to review their own reasoning later when the code must change.

The core principle guiding all design elements mentioned in the related sections—including Topic 9 (DRY—The Evils of Duplication), Topic 10 (Orthogonality), Topic 11 (Reversibility), Topic 14 (Domain Languages), Topic 28 (Decoupling), Topic 30 (Transforming Programming), and Topic 31 (Inheritance Tax)—is ETC. 

Beyond the design structure, the concept of duplication itself requires attention. The authors explain that while programmers gather, organize, maintain, and harness knowledge using specifications, running code, and testing, this knowledge is inherently unstable and changes quickly (e.g., due to client meetings, government regulations, or test failures). This instability forces developers to spend significant time in maintenance mode, reorganizing and re-expressing knowledge within the system.

Many people wrongly believe that maintenance only begins after an application is released, defining it as merely fixing bugs and enhancing features. However, the authors argue that programmers are constantly in maintenance mode, as their own understanding changes daily, and new or evolving requirements may appear, regardless of the environment changes. When performing maintenance, developers must modify representations of things—the knowledge embedded in the application. The problem arises because developers often duplicate knowledge in the specifications, processes, and programs they develop. This duplication creates a maintenance nightmare that begins before the application even ships. To reliably develop software and make development easier to understand and maintain, the authors propose adhering to the DRY principle: Every piece of knowledge must have a single, unambiguous, authoritative representation within a system.

**DRY (Don't Repeat Yourself)**

The alternative to DRY is having the same piece of knowledge expressed in two or more locations. If a developer changes one instance, the developer must remember to change all others, or, failing that, the program will fail due to contradiction. The authors warn that the failure is not a question of whether the developer will remember, but of when the developer will forget. The DRY principle is considered one of the most important tools in the pragmatic programmer's toolbox. Importantly, DRY is not confined to code; the principle refers to the duplication of *knowledge* or *intent*. It means expressing the same thing in two different places, potentially in two totally different ways.

**Testing the DRY Principle**

To determine if a system is DRY, the developer should ask: when a single aspect of the code needs to change, does the developer find themselves making that change in multiple locations and in multiple different formats? If the developer must change code, documentation, a database schema, or a data structure, the system is not considered DRY.

**Example of Code Duplication:**

The following pseudocode illustrates code duplication:
```pseudocode
def print_balance(account)
printf "Debits: %10.2f\n", account.debits
printf "Credits: %10.2f\n", account.credits
if account.fees < 0
printf "Fees: %10.2f-\n", -account.fees
else
printf "Fees: %10.2f\n", account.fees

end
printf "\n-----\n"
if account.balance < 0
printf "Balance: %10.2f-\n", -account.balance
else
printf "Balance: %10.2f\n", account.balance
end
end
```

Analyzing this pseudocode reveals several instances of duplication, for example, the handling of negative numbers. This duplication can be remedied by creating a function to format the amount: 

```pseudocode
def format_amount(value)
result = sprintf("%10.2f", value.abs)
if value < 0
result + "-"
else
result + " "
end
end
def print_balance(account)
printf "Debits: %10.2f\n", account.debits
printf "Credits: %10.2f\n", account.credits
printf "Fees: %s\n", format_amount(account.fees)
printf "\n-----\n"
printf "Balance: %s\n", format_amount(account.balance)
end
```
