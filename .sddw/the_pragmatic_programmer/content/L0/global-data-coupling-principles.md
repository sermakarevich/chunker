# global-data-coupling-principles

**Parent:** [[content/L1/professional-mastery-and-system-design|professional-mastery-and-system-design]] — Professional competency requires mastery of multifaceted tools, from physical implements and sophisticated editor proficiencies to advanced architectural patterns like PubSub and Event Streams; techniques range from PERT and Iterative Estimation to using 'chop' for debugging and enforcing API wrappers for resources to prevent global state coupling.

Globally accessible data presents a subtle but serious source of coupling between application components. Every piece of global data effectively grants every method within the application an additional, unlisted parameter, as this data is available inside every method.

Global data causes coupling for several reasons. The most straightforward reason is that any change to the implementation of the global data structure has the potential to affect all code in the system. However, the actual impact is usually limited; the real problem lies in knowing every location that requires modification.

Global data also complicates the process of decomposing code. While code reuse has many benefits, developers should treat making code reusable not as a primary goal, but rather as an integral part of the coding routine. Making code reusable requires giving it clean interfaces, thereby decoupling it from the rest of the code. This clean separation allows a developer to extract a method or module without having to drag along the entire system. Using global data, however, makes splitting the code out difficult.

This problem becomes apparent when a developer writes unit tests for code that relies on global data, forcing the developer to write considerable setup code simply to create a global environment for the test to run.

**Recommendations for Global Data:**

1.  **Avoid Global Data:** Developers must actively avoid using global data. This includes considering that **Singletons** are not a solution; if a singleton object contains multiple exported instance variables, that structure still constitutes global data, regardless of the name or how it is wrapped.
2.  **Wrapping Configuration:** If a singleton initially uses exported instance variables (e.g., `Config.log_level`), developers can improve the design by hiding all data behind methods (e.g., `Config.getLogLevel()`). This improves the design because it means the global data has internal intelligence, allowing the developer to maintain compatibility by mapping between new and old representations within the Configuration API, while still maintaining a single set of configuration data.
3.  **External Resources:** Any mutable external resource (such as a database, datastore, file system, or service API) functions as global data if the application uses it. The solution is to ensure that developers always wrap these external resources behind a controlled code layer, creating a dedicated API for interaction.

**Inheritance and Coupling:**
The misuse of subclassing, where a class inherits both state and behavior from another class, introduces coupling (discussed further in the dedicated topic, Topic 31: Inheritance Tax). Coupled code is inherently difficult to change because alterations in one location can create secondary effects elsewhere in the code, often in hard-to-find locations that only emerge months later during production.

To maintain decoupled applications, developers must keep their code 'shy,' meaning the code should only deal with things it directly knows about. This helps decouple applications and makes them more amenable to change. 

The concept of global data emphasizes the need for abstraction by recommending that if a resource is important enough to be global, developers must wrap it in an explicit API.
