# agentic-rag-workflows-taxonomy

**Parent:** [[content/L1/agentic-rag-system-taxonomy|Agentic RAG is a paradigm shift from traditional RAG, addressing static data limitations by integrating autonomous agents using workflow patterns (e.g., Orchestrator-Workers, Multi-Agent Collaboration). Architecturally, Single-Agent systems centralize decision-making to select between Structured Databases (PostgreSQL/MySQL via Text-to-SQL), Semantic Search, Web Search, and Recommendation Systems. Advanced RAG evolves through paradigms like Naïve, Advanced (using Dense Vector Search/DPR), Modular (hybrid strategies/tool integration), and Graph RAG (modeling relationships for diagnostics/legal research).]]

Multi-agent collaboration is a key design pattern within agentic workflows that facilitates task specialization and parallel processing. Through communication and the sharing of intermediate results, this pattern ensures that the overall workflow remains efficient and coherent. Specifically, by distributing subtasks among specialized agents, this pattern improves the scalability and adaptability of complex workflows. Multi-agent systems allow developers to decompose intricate tasks into smaller, manageable subtasks assigned to different agents. This approach enhances task performance and provides a robust framework for managing complex interactions. Every agent within a multi-agent system operates with its own memory and workflow, which can incorporate tools, reflection, or planning, thus enabling dynamic and collaborative problem-solving. While multi-agent collaboration offers significant potential, the design pattern is less predictable than more mature workflows like Reflection and Tool Use. However, emerging frameworks, such as AutoGen, Crew AI, and LangGraph, provide new avenues for implementing effective multi-agent solutions.

These design patterns form the foundation for the success of Agentic RAG systems. By structuring workflows—ranging from simple, sequential steps to complex, adaptive, collaborative processes—these patterns enable systems to dynamically adapt their retrieval and generative strategies to the diverse and ever-changing demands of real-world environments. Leveraging these patterns, agents are capable of handling iterative, context-aware tasks that significantly exceed the capabilities of traditional RAG systems.

Agentic workflow patterns structure Large Language Model (LLM)-based applications to optimize performance, accuracy, and efficiency, with different approaches suitable based on task complexity and processing requirements.

**Prompt Chaining:** This method decomposes a complex task into multiple sequential steps, where each subsequent step builds upon the preceding one. This structured approach improves accuracy by simplifying each subtask before proceeding. However, prompt chaining may increase latency due to the necessary sequential processing.
*   **When to Use:** This workflow is most effective when a task can be broken down into fixed subtasks, each contributing to the final output, particularly useful in scenarios where step-by-step reasoning enhances accuracy.
*   **Example Applications:** Generating marketing content in one language and subsequently translating it into another while preserving nuances, or structuring document creation by first generating an outline, verifying its completeness, and then developing the full text.

**Routing:** Routing involves classifying an input and directing it to an appropriate specialized prompt or process. This method ensures that distinct queries or tasks are handled separately, improving efficiency and response quality.
*   **When to Use:** Ideal for scenarios where different types of input require distinct handling strategies, ensuring optimized performance for each category.
*   **Example Applications:** Directing customer service queries into categories such as technical support, refund requests, or general inquiries, or assigning simple queries to smaller models for cost efficiency while routing complex requests to advanced models.

**Parallelization:** Parallelization divides a task into independent processes that run simultaneously. This significantly reduces latency and improves throughput. This technique can be categorized into two types: sectioning (independent subtasks) and voting (multiple outputs for accuracy).
*   **When to Use:** Useful when tasks can be executed independently to enhance speed, or when multiple outputs are required to improve confidence.
*   **Example Applications:** Using sectioning for tasks like content moderation, where one model screens input while another generates a response; or using voting by employing multiple models to cross-check code for vulnerabilities or analyze content moderation decisions.

**Orchestrator-Workers:** This workflow features a central orchestrator model that dynamically decomposes tasks into subtasks, assigns these subtasks to specialized worker models, and compiles the final results. Unlike parallelization, this workflow adapts to varying input complexity.
*   **When to Use:** Best suited for tasks requiring dynamic decomposition and real-time adaptation where subtasks are not predefined.
*   **Example Applications:** Automatically modifying multiple files in a codebase based on the nature of requested changes, or conducting real-time research by gathering and synthesizing relevant information from multiple sources.

**Evaluator-Optimizer:** The evaluator-optimizer workflow iteratively improves content by generating an initial output and subsequently refining that output based on feedback received from an evaluation model.
*   **When to Use:** Effective when iterative refinement significantly enhances response quality, particularly when clear evaluation criteria exist.
*   **Example Applications:** Improving literary translations through multiple evaluation and refinement cycles, or conducting multi-round research queries where additional iterations refine search results.

**Taxonomy of Agentic RAG Systems:**

Agentic Retrieval-Augmented Generation (RAG) systems can be categorized into distinct architectural frameworks based on their complexity and design principles, specifically including single-agent, multi-agent, and hierarchical agentic architectures. This section provides a detailed taxonomy of these architectures, highlighting their characteristics, strengths, and limitations.

**Single-Agent Agentic RAG: Router**

A Single-Agent Agentic RAG serves as a centralized decision-making system where a single agent manages the retrieval, routing, and integration of information. This architecture simplifies the system by consolidating these tasks into one unified agent, making it particularly effective for setups with a limited number of tools or data sources. The workflow proceeds through four steps:
1.  **Query Submission and Evaluation:** The process starts when a user submits a query. A coordinating agent (or master retrieval agent) receives and analyzes the query to determine the most suitable sources of information.
2.  **Knowledge Source Selection:** Based on the query’s type, the coordinating agent chooses from various retrieval options: Structured Databases (using a Text-to-SQL engine for queries needing tabular data access, interacting with databases like PostgreSQL or MySQL); Semantic Search (retrieving relevant documents—e.g., PDFs, books, or organizational records—using vector-based retrieval); Web Search (leveraging a web search tool for real-time or broad contextual information); and Recommendation Systems (tapping into recommendation engines for personalized or contextual queries).
3.  **Data Integration and LLM Synthesis:** Once relevant data is retrieved from the chosen sources, this data is passed to a Large Language Model (LLM). The LLM synthesizes the gathered information, integrating insights from multiple sources into a coherent and contextually relevant response.
4.  **Output Generation:** Finally, the system delivers a comprehensive, user-facing answer that addresses the original query. This response is presented in an actionable, concise format and may optionally include references or citations to the sources used.

*   **Key Features and Advantages:**
    *   **Centralized Simplicity:** A single agent handles all retrieval and routing tasks, making the architecture straightforward to design, implement, and maintain.
    *   **Efficiency & Resource Optimization:** Because fewer agents are involved and coordination is simpler, the system demands fewer computational resources and can handle queries more quickly.
    *   **Dynamic Routing:** The agent evaluates each query in real-time, selecting the most appropriate knowledge source (e.g., structured DB, semantic search, web search).
    *   **Versatility Across Tools:** Supports a variety of data sources and external APIs, enabling both structured and unstructured workflows.
    *   **Ideal for Simpler Systems:** Suited for applications with well-defined tasks or limited integration requirements (e.g., document retrieval, SQL-based workflows).
*   **Use Case Example (Customer Support):** If a user asks, 
