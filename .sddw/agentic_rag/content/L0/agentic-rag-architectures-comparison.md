# agentic-rag-architectures-comparison

**Parent:** [[content/L1/agentic-rag-architecture-taxonomy|What is the boiling point of water?"]]

This section reviews specialized agentic architectures within Retrieval-Augmented Generation (RAG): the Adaptive RAG, the Graph-Based Agentic RAG (Agent-G), and the Graph-Enhanced Agent for Retrieval-Augmented Generation (GeAR). 

**Adaptive RAG System Architecture**
The Adaptive RAG system operates using three primary components: a Classifier Role, Dynamic Strategy Selection, and LLM Integration.

1. **Classifier Role:** A smaller language model analyzes the input query to predict the query's complexity. This classifier is trained using automatically labeled datasets, which are derived from past model outcomes and observed query patterns.
2. **Dynamic Strategy Selection:** The system employs different retrieval strategies based on the assessed query complexity:
    *   **Straightforward Queries:** For fact-based questions that require no additional retrieval, the system bypasses unnecessary retrieval and directly utilizes the Large Language Model (LLM) for response generation.
    *   **Simple Queries:** For moderately complex tasks requiring minimal context, the system performs a single-step retrieval process to fetch relevant context.
    *   **Complex Queries:** For highly complex tasks, the system activates multi-step retrieval to ensure iterative refinement and enhanced reasoning.
3. **LLM Integration:** The LLM synthesizes all retrieved information into a coherent response. For complex queries, the LLM and the classifier interact iteratively, enabling further refinement.

Key features and advantages of Adaptive RAG include **Dynamic Adaptability** (adjusting retrieval strategies based on query complexity to optimize both computational efficiency and response accuracy), **Resource Efficiency** (minimizing overhead for simple queries while maintaining thorough processing for complex ones), **Enhanced Accuracy** (ensuring complex queries are resolved with high precision through iterative refinement), and **Flexibility** (allowing extension to incorporate additional pathways, such as domain-specific tools or external APIs).

**Agent-G: Agentic Framework for Graph RAG**

Agent-G introduces a novel agentic architecture that integrates graph knowledge bases with unstructured document retrieval. By combining structured and unstructured data sources, the Agent-G framework enhances RAG systems with improved reasoning and retrieval accuracy. The framework utilizes modular retriever banks, dynamic agent interaction, and feedback loops to ensure high-quality outputs.

**Key Idea of Agent-G:** The core principle of Agent-G is the ability to dynamically assign retrieval tasks to specialized agents, leveraging both graph knowledge bases and textual documents. The Agent-G system adjusts its retrieval strategy through the following steps:

*   **Graph Knowledge Bases:** Structured data is used to extract relationships, hierarchies, and connections (for example, disease-to-symptom mappings in healthcare).
*   **Unstructured Documents:** Traditional text retrieval systems provide contextual information to complement the structured graph data.
*   **Critic Module:** The Critic Module evaluates the relevance and quality of the retrieved information, ensuring alignment with the original query.
*   **Feedback Loops:** These loops refine retrieval and synthesis through iterative validation and re-querying.

**Agent-G Workflow:** The Agent-G system is built on four primary components:

1. **Retriever Bank:** A modular set of specialized agents designed to retrieve either graph-based or unstructured data. These agents dynamically select relevant sources based on the specific requirements of the query.
2. **Critic Module:** This module validates all retrieved data for both relevance and quality, flagging low-confidence results for subsequent re-retrieval or refinement.
3. **Dynamic Agent Interaction:** Task-specific agents collaborate to integrate diverse data types, thereby ensuring cohesive retrieval and synthesis across both graph and text sources.
4. **LLM Integration:** The LLM synthesizes the validated data into a coherent response, ensuring that the iterative feedback from the Critic Module maintains alignment with the query’s intent.

Key features of Agent-G include **Enhanced Reasoning** (combining structured relationships from graphs with contextual information from unstructured documents), **Dynamic Adaptability** (adjusting retrieval strategies dynamically based on query requirements), **Improved Accuracy** (using the Critic module to reduce the risk of irrelevant or low-quality data), and **Scalable Modularity** (supporting the addition of new agents for specialized tasks, enhancing overall scalability).

**GeAR: Graph-Enhanced Agent for Retrieval-Augmented Generation**

GeAR introduces an agentic framework that enhances traditional RAG systems by incorporating graph-based retrieval mechanisms. By leveraging graph expansion techniques and an agent-based architecture, GeAR addresses challenges in multi-hop retrieval scenarios, thereby improving the system’s ability to handle complex queries.

**Key Idea of GeAR:** GeAR advances RAG performance through two primary innovations:

*   **Graph Expansion:** This technique enhances conventional base retrievers (such as BM25) by expanding the retrieval process to include graph-structured data. This enables the system to capture complex relationships and dependencies between entities.
*   **Agent Framework:** This framework incorporates an agent-based architecture that uses graph expansion to manage retrieval tasks more effectively, allowing for dynamic and autonomous decision-making throughout the retrieval process.

**GeAR Workflow:** The GeAR system operates through three primary components:

1. **Graph Expansion Module:** This module integrates graph-based data into the retrieval process, enabling the system to consider relationships between entities during retrieval. Furthermore, it enhances the base retriever’s capability to handle multi-hop queries by expanding the search space to include connected entities.
2. **Agent-Based Retrieval:** This component employs an agent framework to manage the retrieval process. This framework enables the dynamic selection and combination of retrieval strategies based on the query’s complexity. Agents can autonomously decide to utilize graph-expanded retrieval paths to improve the relevance and accuracy of retrieved information.
3. **LLM Integration:** The LLM combines the retrieved information, which has been enriched by graph expansion, with the capabilities of a Large Language Model (LLM) to generate coherent and contextually relevant responses. This integration ensures that the generative process is informed by both unstructured documents and structured graph data.
