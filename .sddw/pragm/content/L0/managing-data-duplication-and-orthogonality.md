# managing-data-duplication-and-orthogonality

**Parent:** [[content/L1/principle-of-dry-knowledge-representation|principle-of-dry-knowledge-representation]] — The DRY principle mandates that every piece of knowledge must have a single, authoritative representation, extending beyond code to data structures and external interfaces; failure to follow DRY invites maintenance nightmares, illustrated by the risk of data structure duplication (e.g., storing calculated line length) and the necessity of centralized knowledge sharing to prevent dangerous inter-developer duplication, such as the discovery of over 10,000 distinct SSN validation codes in U.S. governmental systems.

In a system, data structures can represent knowledge, and these structures must adhere to the DRY (Don't Repeat Yourself) principle. For instance, consider a `Line` class designed as follows:
```
class Line {
Point start;
Point end;
double length;
};
```
Although this initial class appears reasonable because a line naturally has a start point, an end point, and a length (even if the length is zero), this structure contains duplication. Because the length is inherently determined by the start and end points, changing one of the points necessitates a corresponding change in the length. Therefore, it is better practice to calculate the length rather than storing it as a field:
```
class Line {
Point start;
Point end;
double length() { return start.distanceTo(end); } 
};
```
However, during development, a developer may choose to violate the DRY principle for performance reasons, such as when the system needs to cache data to avoid repeating expensive operations. In these cases, the key is to localize the impact of the violation, ensuring that the violation is not exposed to the outside world. Only the methods within the class must manage the state correctly, as shown in this example:
```
class Line {
private double length;
private Point start;
private Point end;
public Line(Point start, Point end) {
this.start = start;
this.end = end;
calculateLength();
}
// public
void setStart(Point p) { this.start = p; calculateLength(); }
void setEnd(Point p) { this.end = p; calculateLength(); }
Point getStart()
Point getEnd()
double getLength()
{
return start;
}
{
return end;
}
{
return length;
}
private void calculateLength() {
this.length = start.distanceTo(end);
}
};
```
This example further illustrates an important concept: when a module exposes a data structure, the module couples all the code that uses that structure to the module's internal implementation. Developers should always use accessor functions to read and write object attributes whenever possible, as this strategy simplifies future functionality additions. This use of accessor functions connects to Meyer’s Uniform Access principle, described in *Object-Oriented Software Construction* (Mey97). This principle states that all services offered by a module should be accessible through a uniform notation, regardless of whether the services are implemented through storage or computation.

### REPRESENTATIONAL DUPLICATION

When writing code, the code interfaces with the outside world—whether through other libraries via APIs, remote calls to other services, or data from external sources. Each of these interfaces potentially introduces a DRY violation, requiring the programmer's code to possess knowledge that is also present in the external entity. Specifically, the code must know the API, the schema, the meaning of error codes, or similar representations. The duplication here is that both the programmer’s code and the external entity must independently maintain knowledge of the representation of their interface. A change at one end will cause the other end to break. Although this duplication is unavoidable, strategies can mitigate the risk. 

**Strategies for Mitigating Duplication:**

*   **Across Internal APIs:** Programmers should search for tools that allow specifying the API in a neutral format. These tools typically generate documentation, mock APIs, functional tests, and API clients, with the latter available in multiple languages. Ideally, the tool should centralize all APIs in a single repository, allowing sharing across teams.
*   **Across External APIs:** Public APIs are increasingly documented formally using standards like OpenAPI. Using such specifications allows developers to import the API specification into local API tools, thereby integrating more reliably with the service.
*   **If a Specification is Lacking:** If formal specifications cannot be found, programmers should consider creating one and publishing it. Publishing the specification not only helps other developers but may also facilitate assistance in maintaining it.
*   **With Data Sources:** Many data sources allow programmers to introspect on their data schema. This capability can minimize the duplication between the data source and the application code. Instead of manually writing code to store the data, developers can generate the necessary containers directly from the schema. Many persistence frameworks handle this process automatically.
*   **Alternative Data Structure Strategy:** An alternative approach involves avoiding fixed structures (such as an instance of a struct or class) for external data. Instead, programmers can load the data into a key/value data structure (a map, hash, dictionary, or object, depending on the programming language). While this approach is inherently risky because it reduces the security of knowing the exact data structure, a developer should implement a second layer of defense: a simple table-driven validation suite. This suite must verify that the created map contains at least the required data, in the required format. The API documentation tool might be able to generate this validation suite.

### INTER-DEVELOPER DUPLICATION

Perhaps the most difficult type of duplication to detect and handle occurs between different developers on a project. Entire sets of functionality may be inadvertently duplicated, and this duplication could remain undetected for years, leading to significant maintenance problems. For instance, an audit of U.S. governmental computer systems for Y2K compliance discovered over 10,000 programs, each containing a different version of Social Security Number validation code.

Addressing this requires two levels of effort. At a high level, the team should build strong, tightly knit teams with good communication practices. At the module level, the problem is more insidious, as commonly needed functionality or data that does not fit into an obvious area of responsibility may be implemented multiple times. The best method for dealing with inter-developer duplication is encouraging active and frequent communication among developers. Practical steps include: setting up daily scrum standup meetings; establishing forums (such as Slack channels) to discuss common problems, providing a nonintrusive way of communication across multiple sites while maintaining a permanent record; appointing a team member as the project librarian whose role is to facilitate knowledge exchange; establishing a central place in the source tree where utility routines and scripts can be deposited; and consistently reading other people’s source code and documentation, either informally or during code reviews. The developer must remember that the access is reciprocal, meaning the developer should also allow other team members to examine their code.
