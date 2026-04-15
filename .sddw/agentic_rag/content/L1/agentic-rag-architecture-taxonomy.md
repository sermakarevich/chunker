# agentic-rag-architecture-taxonomy

**Parent:** [[index]]

The evolution of Retrieval-Augmented Generation (RAG) systems has driven the integration of autonomous agents, moving beyond the limitations of static traditional RAG. These agentic systems leverage sophisticated design patterns—including reflection, planning, and tool use—to facilitate dynamic decision-making and optimize workflows for complex, real-time, and multi-domain queries. The field has generated several specialized architectural types: Single-Agent, Multi-Agent, Hierarchical, Corrective, Adaptive, Agent-G, and GeAR. These architectures provide structured methodologies for enhancing retrieval accuracy, optimizing performance, and ensuring data coherence.

### **Conceptual Foundations of Agentic Workflows**

Agentic workflows, as a category of design patterns, structure Large Language Model (LLM)-based applications to optimize performance, accuracy, and efficiency. The underlying principle is that complex tasks are decomposed into smaller, manageable subtasks assigned to specialized units, enhancing task performance and providing a robust framework for managing intricate interactions. The choice of pattern depends heavily on the task's complexity and processing requirements. Key patterns include:

*   **Prompt Chaining:** Decomposes a complex task into multiple sequential steps, where each subsequent step builds directly upon the preceding one. This enhances accuracy by simplifying each subtask before proceeding, but it risks increasing latency due to the necessary sequential processing. It is ideal for fixed subtask scenarios, such as generating an outline, verifying its completeness, and then developing the full text, or generating content in one language and translating it into another while maintaining nuances.
*   **Routing:** Involves classifying an input and directing it to an appropriate specialized prompt or process. This ensures that distinct queries or tasks are handled separately, thereby improving efficiency and response quality. This is useful when different input types require distinct handling strategies, such as directing customer service queries into technical support, refund requests, or general inquiries, or allocating simple queries to smaller, cost-effective models while routing complex requests to advanced models.
*   **Parallelization:** Divides a task into independent processes that run simultaneously, significantly reducing latency and improving throughput. This technique can manifest in two forms: sectioning (independent subtasks) and voting (multiple outputs for accuracy). It is useful for enhancing speed or confidence, for example, using sectioning for content moderation (one model screens, another generates), or using voting to cross-check code for vulnerabilities.
*   **Orchestrator-Workers:** Features a central orchestrator model that dynamically decomposes tasks, assigns subtasks to specialized worker models, and compiles the final results. Unlike predefined parallelization, this workflow adapts to varying input complexity. It is best suited for tasks requiring dynamic decomposition and real-time adaptation, such as automatically modifying multiple files in a codebase based on requested changes, or conducting real-time research by gathering and synthesizing information from multiple sources.
*   **Evaluator-Optimizer:** This workflow iteratively improves content by generating an initial output and subsequently refining that output based on feedback from an evaluation model. It is effective when iterative refinement significantly enhances response quality and clear evaluation criteria exist, such as improving literary translations through multiple evaluation and refinement cycles, or conducting multi-round research queries.

### **Taxonomy of Agentic RAG Architectures**

Agentic RAG systems can be broadly categorized based on their complexity and design principles, moving from centralized single-agent models to highly collaborative multi-tiered structures.

#### **Single-Agent Agentic RAG: Router**

A Single-Agent Agentic RAG functions as a centralized decision-making system where one agent manages retrieval, routing, and information integration. This architecture simplifies the system by consolidating tasks, making it efficient for setups with a limited number of tools or data sources. The process involves four key steps:

1.  **Query Submission and Evaluation:** A coordinating agent receives and analyzes the user query to determine the most suitable sources of information.
2.  **Knowledge Source Selection:** Based on the query type, the agent selects from various options: **Structured Databases** (utilizing a Text-to-SQL engine for tabular data access, interacting with databases like PostgreSQL or MySQL); **Semantic Search** (retrieving relevant documents, such as PDFs, books, or organizational records, via vector-based retrieval); **Web Search** (leveraging a web search tool for real-time or broad contextual information); and **Recommendation Systems** (tapping into recommendation engines for personalized or contextual queries).
3.  **Data Integration and LLM Synthesis:** The retrieved data is passed to an LLM, which synthesizes the information, integrating insights from multiple sources into a coherent, contextually relevant response.
4.  **Output Generation:** The system delivers a comprehensive, actionable answer, which may optionally include citations to the sources used.

*Key Advantages:* This design offers **Centralized Simplicity**, demands fewer computational resources due to fewer agents, and provides **Dynamic Routing**, allowing real-time evaluation and selection of the most appropriate knowledge source. It is particularly suited for applications with well-defined tasks or limited integration requirements, such as document retrieval or SQL-based workflows.

#### **Multi-Agent Agentic RAG**

This architecture utilizes the parallel execution of multiple independent agents, allowing for efficient processing of diverse query types and greatly enhancing scalability. The workflow is highly modular:

*   **Parallel Execution:** Each agent operates autonomously, optimizing for a specific query type or data source. This specialized task distribution minimizes bottlenecks and significantly enhances performance for complex workflows.
*   **Data Integration and LLM Synthesis:** Once all agents complete their retrieval tasks, the collective data from every agent is passed to a Large Language Model (LLM). The LLM then performs the crucial synthesis, integrating all retrieved information into a cohesive and contextually relevant response.
*   **Output Generation:** The system generates a comprehensive, actionable answer for the user.

*Key Features and Advantages:* The primary benefits include **Modularity** (developers can easily add or remove agents), high **Scalability** (handling high query volumes via parallel processing), **Task Specialization** (improving both accuracy and retrieval relevance), and overall **Versatility**, making it suitable for domains spanning research, analytics, decision-making, and customer support.

#### **Hierarchical Agentic RAG Systems**

These systems utilize a structured, multi-tiered approach where agents are organized in a pyramid structure. Higher-level agents manage and direct lower-level agents, facilitating multi-level decision-making and enhancing strategic oversight. The workflow proceeds through specialized stages:

1.  **Query Reception and Top-Tier Assessment:** A user query is received by a top-tier agent, which is responsible for initial assessment and delegation.
2.  **Strategic Decision-Making:** The top-tier agent evaluates the query's complexity and determines which subordinate agents or data sources to prioritize, potentially deeming certain databases or APIs as more reliable based on the query's domain.
3.  **Delegation to Subordinate Agents:** The top-tier agent assigns specific tasks to lower-level agents that are specialized in particular retrieval methods (e.g., SQL databases, web search, or proprietary systems). These subordinate agents then execute their tasks independently.
4.  **Aggregation and Synthesis (Higher-Level Role):** The higher-level agent collects the results from the subordinate agents and synthesizes the information into a single, coherent response.
5.  **Response Delivery:** The final, synthesized answer is returned to the user, ensuring comprehensive and contextually relevant delivery.

*Key Advantages:* This structure provides **Strategic Prioritization** (data source or task prioritization based on query complexity/reliability), enhances **Scalability** for highly complex or multi-faceted queries, and improves overall accuracy through **Enhanced Decision-Making** via strategic oversight.

#### **Corrective RAG**

Corrective RAG introduces mechanisms for self-correction of retrieval results, aiming to improve document utilization and boost response generation quality. By embedding intelligent agents, it ensures iterative refinement of both context documents and responses, minimizing errors and maximizing relevance. Its core principle is the dynamic ability to evaluate retrieved documents, perform corrective actions, and refine queries.

The specific workflow steps involve specialized agents:

1.  **Context Retrieval Agent:** Retrieves initial context documents from a vector database.
2.  **Relevance Evaluation Agent:** Assesses documents for relevance; if they fall below a defined threshold, it triggers corrective steps.
3.  **Query Refinement Agent:** Leverages semantic understanding to rewrite queries, optimizing retrieval for better results.
4.  **External Knowledge Retrieval Agent:** If the initial context is insufficient, this agent performs web searches or accesses alternative data sources to supplement the retrieved documents.
5.  **Response Synthesis Agent:** Synthesizes all validated and refined information into the final, coherent response.

*Key Advantages:* The main benefit is **Iterative Correction**, which dynamically identifies and corrects irrelevant or ambiguous retrieval results, leading to high response accuracy. It also ensures **Factuality Assurance** by validating all retrieved and generated content, thereby minimizing the risk of hallucination or misinformation.

#### **Adaptive RAG**

Adaptive RAG enhances LLM flexibility by dynamically adjusting query handling strategies based on the complexity of the incoming query, moving beyond static workflows. This approach uses a specialized classifier to assess the query's complexity, determining the optimal process. The handling strategies scale from simple single-step retrieval to multi-step reasoning, or even bypassing retrieval entirely.

*   **Straightforward Queries:** For fact-based questions requiring no retrieval (e.g., 

## Children
- [[content/L0/agentic-rag-workflow-architectures|Agentic RAG systems are categorized into Multi-Agent, Hierarchical, Corrective, and Adaptive architectures, each designed to improve over traditional static RAG. Multi-Agent systems use parallel processing for scalability across specialized agents; Hierarchical systems use top-tier agents to oversee and delegate tasks to subordinate agents; Corrective RAG iteratively refines context by using agents to evaluate relevance and perform dynamic web searches; and Adaptive RAG uses a classifier to tailor the retrieval strategy based on query complexity.]]
- [[content/L0/adaptive-rag-query-complexity|Adaptive RAG dynamically adjusts query handling based on complexity, utilizing a classifier that determines if the system can use pre-existing knowledge for straightforward queries, single-step retrieval for simple queries, or multi-step, progressively refining retrieval for complex, multi-layered queries.]]
- [[content/L0/agentic-rag-architectures-comparison|The Adaptive RAG system uses a classifier to assess query complexity, choosing between single-step retrieval (for simple queries), multi-step retrieval (for complex queries), or direct LLM generation (for straightforward queries). Agent-G integrates graph knowledge bases with unstructured data using a Critic Module and Retriever Bank, while GeAR enhances traditional RAG by implementing Graph Expansion and an agent framework to handle complex, multi-hop queries.]]
