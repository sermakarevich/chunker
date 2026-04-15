# external-configuration-and-decoupling

**Parent:** [[content/L1/software-architecture-decoupling-concurrency|software-architecture-decoupling-concurrency]] — Software architecture demands decoupling through protocols/interfaces, delegation, and mixins to avoid coupling and manage ephemeral state, while reliable development requires adhering to DRY, utilizing external configuration services for dynamic parameters, and managing complex workflows using concurrency analysis via activity diagrams and semaphores.

### External Configuration and Decoupling

When application code depends on values that may change after the application has gone live, it is best practice to store those values externally, allowing each part of the application to adapt to different environments and potentially different customers. This process is called parameterizing the application. 

Common configuration data that developers should externalize includes: credentials for external services (such as databases or third-party APIs), logging levels and destinations, port numbers, IP addresses, machine names, and cluster names used by the application, environment-specific validation parameters, externally set parameters like tax rates, site-specific formatting details, and license keys. In general, developers should look for any value that is expected to change and express it outside the main body of code and place it into a configuration system.

**Static Configuration Methods:**

Many frameworks and custom applications store configuration in either flat files or database tables. If developers use flat files, the prevailing trend is to adopt an off-the-shelf plain-text format, with YAML and JSON being currently popular choices. Furthermore, applications written in scripting languages sometimes use special-purpose source-code files dedicated solely to containing configuration. If the information is highly structured and expected to change frequently by the customer (for instance, sales tax rates), storing the data in a database table may be preferable. Developers can use both methods simultaneously, allocating configuration information based on its intended use.

Regardless of the form used, the configuration information is read into the application as a data structure, typically when the application starts. Although it is common practice to make this data structure globally accessible, developers should avoid this approach. Instead, developers should wrap the configuration information behind a (thin) Application Programming Interface (API). Doing this step decouples the code from the specific details of the configuration's representation.

**Configuration-as-a-Service:**

While static configuration is widely used, the current preference is for an alternative approach: storing configuration data external to the application, but instead of using a flat file or database, utilizing a specialized service API. This method provides several critical benefits: multiple applications can share configuration information, with authentication and access control limiting what each application can see; configuration changes can be managed globally; the configuration data can be maintained via a specialized User Interface (UI); and crucially, the configuration data becomes dynamic. The point that configuration must be dynamic is critical when developing highly available applications because developers should not have to stop and restart the application merely to change a single parameter. By using a configuration service, components of the application can register for notifications of parameter updates, and the service can automatically send messages containing new values when the parameters change. The configuration data, regardless of its format, drives the runtime behavior of the application, meaning that when configuration values change, the developers do not need to rebuild the code.

### Concurrency and Parallelism

Concurrent and parallel code are essential for modern applications. Concurrency occurs when the execution of two or more pieces of code act as if they are running at the same time. Parallelism means that the code physically does run at the same time, requiring hardware such as multiple cores in a CPU, multiple CPUs in a computer, or multiple connected computers. To achieve concurrency, the operating environment must be capable of switching execution between different parts of the code while the code is running, often implemented using fibers, threads, or processes.

**Temporal Coupling and Shared State:**

Developers frequently discuss coupling between chunks of code, referring to dependencies that make changes difficult. However, another form of coupling is temporal coupling, which occurs when the code imposes a sequence on events that is not necessary to solve the problem. For example, depending on a 
