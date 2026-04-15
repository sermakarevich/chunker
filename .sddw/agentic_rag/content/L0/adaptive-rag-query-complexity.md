# adaptive-rag-query-complexity

**Parent:** [[content/L1/agentic-rag-architecture-taxonomy|What is the boiling point of water?"]]

In Adaptive Retrieval-Augmented Generation (Adaptive RAG), the system dynamically adjusts the query handling strategy based on the complexity of the incoming query. The system uses a classifier to assess the query complexity, determining the most appropriate process. The handling strategies range from single-step retrieval to multi-step reasoning, and may even involve bypassing retrieval entirely for straightforward queries. Specifically, the system handles different types of queries based on complexity:

*   **Straightforward Queries:** For fact-based questions that require no additional retrieval (for example, asking, "What is the boiling point of water?"), the system directly generates an answer using pre-existing knowledge.
*   **Simple Queries:** For moderately complex tasks requiring minimal context (for example, asking, "What is the status of my latest electricity bill?"), the system performs a single-step retrieval to fetch the relevant details.
*   **Complex Queries:** For multi-layered queries requiring iterative reasoning (for example, asking, "How has the population of City X changed over the past decade, and what are the contributing factors?"), the system employs multi-step retrieval, progressively refining intermediate results to provide a comprehensive answer.
