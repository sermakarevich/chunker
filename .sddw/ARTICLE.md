I Processed a 600K-Character Book Into a Navigable Knowledge Tree. Here Is Why RAG Was Never the Right Answer.


A few days ago I ran an experiment. I fed the entire text of "The Pragmatic Programmer" (587,508 characters) through a tool I built called Chunker. What came out the other side was not a vector database. It was not a collection of embeddings. It was a tree of 86 self-sufficient chunks organized into 35 summary blocks across 3 levels of hierarchy, all linked together as plain markdown files. An AI agent can start at the root, read three one-paragraph summaries, pick the relevant branch, and drill down to the exact passage it needs. It never loads the full book. It navigates.

This article is about why I built this, what inspired it, and why I think the way we feed documents to AI models is fundamentally backwards.


THE PROBLEM WITH RAG

Retrieval-Augmented Generation has become the default answer to "how do I give my AI model access to documents." The idea sounds reasonable: split your documents into chunks, convert them to embeddings, store them in a vector database, and when a user asks a question, retrieve the most similar chunks and feed them to the model.

In practice, this approach has serious problems.

First, naive chunking destroys meaning. When you split a document every 500 tokens, you get fragments that start and end mid-thought. A chunk that begins with "they" and references "the approach described above" is useless without its neighbors. The context that makes the text meaningful gets severed at arbitrary boundaries.

Second, retrieval is a guessing game. The system converts your question into an embedding and hopes that cosine similarity will surface the right passages. But relevance is not similarity. A passage about "software entropy" might be exactly what you need when asking about code maintenance, but the embedding vectors might not be close enough to trigger retrieval. You are relying on a mathematical proxy for understanding.

Third, there is no structure. RAG treats a document as a bag of fragments. There is no table of contents, no hierarchy, no way for the model to understand where a passage fits in the broader argument. The model gets isolated pieces with no map of the territory.

Fourth, context pollution is real. Traditional RAG systems inject retrieved passages upfront. You might load 35,000 tokens into context, but only 2,000 of them (about 6%) are actually relevant to the question. The rest is noise that dilutes the model's attention and wastes your token budget.

Fifth, and this is perhaps the most fundamental issue, RAG rediscovers knowledge from scratch on every query. There is no accumulation. No compounding. Every question triggers the same retrieve-and-hope cycle.


WHAT INSPIRED A DIFFERENT APPROACH

Three things converged that pushed me to build something different.

The first was Andrej Karpathy's LLM Wiki pattern. Karpathy published an approach for building personal knowledge bases that bypasses RAG entirely. Instead of embeddings and vector search, he proposed having an LLM maintain a structured markdown wiki with an index file, cross-references, and summaries. The key insight was simple: at moderate scale (around 100 articles, 400K words), an LLM reading an index and following links is more reliable than embedding-based retrieval. As Karpathy put it, "The wiki is a persistent, compounding artifact. The cross-references are already there. The contradictions have already been flagged."

The second was the leaked Claude Code source code. In early 2026, Claude Code's internal architecture became public, revealing a three-layer memory system. At its core is a lightweight index of short pointers that is always loaded into context. Detailed project notes live in a separate layer and are pulled in on demand. Past session history is searched selectively rather than loaded wholesale. The design principle is progressive disclosure: show what exists first, let the agent decide what to fetch.

The third was the claude-mem framework and its formalization of progressive disclosure as a principle for AI context management. Claude-mem implements a three-layer workflow: first an index layer showing lightweight metadata (titles, types, token costs), then a context layer providing chronological surroundings, and finally a details layer with full content fetched only when the agent determines it is necessary. The results are striking: instead of loading 35,000 tokens with 6% relevance, you load an 800-token index, fetch only what matters, and achieve close to 100% relevance. The agent controls its own token budget rather than having the system make the decision for it.

These three influences pointed in the same direction. Documents should not be dumped into context or chopped into fragments. They should be organized into navigable structures where an intelligent reader (human or AI) can find what they need through progressive disclosure.


WHY PROGRESSIVE DISCLOSURE WORKS (FOR HUMANS AND AI)

Progressive disclosure is not a new idea. It comes from interface design: reveal complexity gradually rather than all at once. But it maps beautifully onto how both humans and AI models should consume long documents.

Think about how you read a nonfiction book. If you are honest, you have probably had this experience: you read 25% of a book before realizing it is not what you need. You invested hours into linear, page-by-page consumption only to discover the content does not match your question. This happens because books are organized for the author's narrative flow, not for the reader's information needs.

Now think about how you actually want to consume information. You want the big picture first. A table of contents. Chapter summaries. Then you want to pick the section that matters and go deeper. And deeper. Until you reach the specific paragraph you need. You never wanted to read linearly. You wanted to navigate.

This is exactly how progressive disclosure works for AI models. Instead of loading an entire document (full context) or retrieving random relevant-looking fragments (RAG), the model sees a concise overview, makes an intelligent decision about which branch is relevant, follows a link, reads a more detailed summary, decides again, and drills down until it reaches the source text. At every step, it loads only the nodes on its path. The model is not a passive recipient of whatever the retrieval system serves up. It is an active navigator making informed decisions at each level.

The advantages compound at scale. A 600K-character book might require 150,000 tokens to load in full. With progressive disclosure through a three-level hierarchy, the model might read the index (500 tokens), one L2 summary (1,000 tokens), one L1 summary (1,000 tokens), and one L0 chunk (1,000 tokens). That is roughly 3,500 tokens to reach the exact passage it needs, with full understanding of how that passage fits into the broader document. And every token it consumed was relevant.


WHAT CHUNKER DOES

Chunker is the tool I built to make this work. It takes a plain text document and transforms it into a navigable knowledge tree of self-sufficient chunks and multi-level summaries.

The approach has two phases.

Phase 1 is intelligent chunking. Instead of splitting at fixed token boundaries, a cursor advances through the text and an LLM finds semantically complete split points, places where a topic naturally ends and another begins. Each confirmed chunk then gets rewritten into a self-sufficient context: pronouns are resolved ("they" becomes "the research team"), implied subjects are made explicit, and all specific facts, numbers, and names are preserved. The original text is kept alongside the rewrite. Each chunk also gets a descriptive filename like "software-entropy-and-broken-windows" instead of "chunk-047."

Phase 2 is bottom-up aggregation. As chunks accumulate, the system groups them into thematically coherent clusters and builds summary blocks. Each summary block contains a chunk-sized synthesis of its children (not a brief abstract, but a dense, information-rich context that stands alone). These blocks become candidates for the next level of grouping. The process repeats until you get a small number of root-level summaries that capture the entire document.

The key design decision is that aggregation happens incrementally, not as a batch at the end. After every chunk is extracted, the system checks whether aggregation should trigger. This means later chunks benefit from the hierarchy already built by earlier ones.

Here is how that works in practice. Every LLM call, whether it is checking where a chunk should end, rewriting a chunk for self-sufficiency, or synthesizing a summary block, receives a carefully assembled context. That context has three components, injected in strict priority order. First, the immediate predecessor: the previous chunk's full context, giving the LLM continuity with what came right before. Second, higher-level summaries: the latest summary block from each level of the hierarchy built so far, giving the LLM a compressed view of the entire document up to this point. Third, earlier chunks: walking backwards through recent chunks to fill any remaining budget. A hard token budget (20,000 tokens) caps the total. Items that would exceed the budget are skipped entirely, no partial insertion, and the system moves to the next priority item.

This is where the interleaved aggregation pays off. By the time the system processes chunk 50, the hierarchy already contains L1 and L2 summary blocks covering chunks 1 through 40. So the LLM rewriting chunk 50 does not just see chunk 49. It sees a compressed representation of the entire first half of the document, all within a manageable token budget. The later you are in the document, the richer the context, and the better the output quality.

The output is a directory of linked markdown files organized by hierarchy level: L0 for leaf chunks, L1 for first-level aggregation, L2 for second-level, and so on. An index.md file serves as the entry point. Every link includes the target node's summary as the link label, so you can decide which branch to follow based on factual content, not vague titles. The format works directly in Obsidian or any wiki-link-aware tool, and it works as a knowledge base that an AI agent can navigate by following links.

All LLM calls run locally against Ollama, so there is zero API cost. The system checkpoints after every chunk and block, so processing a full book can survive interruptions without starting over.


THE RESULTS

Running Chunker on "The Pragmatic Programmer" produced:

86 chunks covering the full 587,508 characters with zero gaps
35 summary blocks across 3 hierarchy levels (27 at L0, 8 at L1)
121 linked markdown files, all navigable from a single index.md
Only 1 forced split out of 86 chunks (99% clean semantic boundaries)
Descriptive filenames like "pragmatic-programming-design-principles," "architectural-principles-and-risk-management," "collaboration-techniques-pair-and-mob-programming"

An earlier run on a 115,000-character academic paper about Agentic RAG produced 61 chunks and 21 blocks with full source coverage and similar quality metrics.

Here is what the entry point looks like for the Pragmatic Programmer run. The index shows eight root-level summaries covering the entire book: from the guide's structure and legal framing, through design principles like DRY and Orthogonality, to risk management with Tracers and Prototypes, to professional mastery workflows involving PERT estimation, editor fluency, and architectural patterns like PubSub and the Actor Model. Each summary is dense with specific concepts so an AI model can make an informed navigation decision without reading a single page of the original book.

To make this concrete, here is one branch of the actual tree. Imagine an AI agent asking "how does The Pragmatic Programmer talk about software design principles?"

It starts at index.md and sees eight root summaries. One of them reads: "Sustainable software development requires systemic control against software rot by prioritizing the fixing or containment of minor flaws, while individual developers must manage a knowledge portfolio through continuous investment in skills and diverse learning. Core architectural principles -- Orthogonality, Reversibility, and the DRY principle -- mandate that code must be built to be Easy to Change (ETC)." The agent follows this link.

Inside that L2 block (pragmatic-programming-design-principles), it finds three children:

(L1) software-entropy-and-knowledge-portfolio -- "Software quality demands continuous effort to prevent entropic decay, requiring that broken flaws are immediately addressed or contained."

(L1) developer-pragmatic-principles-communication-design -- "Developers must employ second-order thinking, treating natural language as a programming language and applying principles like DRY and ETC."

(L1) system-design-principles-orthogonality-reversibility -- "Designing systems using Orthogonality, Reversibility, and avoiding irreversible decisions."

The agent picks the third one. Inside it finds three leaf chunks:

(L0) orthogonality-principles -- "Orthogonality, a concept borrowed from geometry, describes a type of independence in computing where changes in one component do not affect others."

(L0) orthogonality-system-design -- "Orthogonality requires composing system modules such that each functionality is independent, meaning a change in one component does not require changes elsewhere."

(L0) reversibility-flexible-architecture -- "Reversibility advises that developers avoid making critical, irreversible decisions, recognizing that the real world constantly changes."

Three navigation steps. Three decisions made by the agent based on informative summaries. From 587,508 characters down to the exact passage about orthogonality in system design. No embeddings. No vector search. No luck required.


HOW IT WAS BUILT

I built Chunker using SDDW (Spec-Driven Development Workflow), a CLI tool for Claude Code that I also developed. SDDW enforces a structured approach: write requirements first, optionally analyze the existing codebase, then design task-by-task, implement each task separately with TDD, verify the result against the original requirements, and self-improve the workflow. The specifications become the primary artifact, reviewable and version-controlled before any code is generated.

For Chunker, this meant 18 functional requirements with acceptance criteria written before any implementation, 11 task-level design specs, and a verification step that checked every requirement against the running system. A second iteration (15 more requirements) restructured the data model to maximize information density, raising chunk sizes and replacing brief rewrites with full self-sufficient contexts.

This structured approach was not optional luxury. When you are building a system where an LLM calls another LLM to decide where to split text and how to summarize it, the failure modes are subtle. Having formal requirements like "boundary phrases must match source text verbatim" and "groups must be contiguous" caught issues that would have been invisible in ad-hoc development.


WHAT THIS MEANS FOR KNOWLEDGE WORK

I believe we are at an inflection point in how AI systems interact with documents. The current dominant paradigm, RAG with vector retrieval, was a reasonable first step. But it treats AI models as passive consumers of whatever the retrieval layer serves up. Progressive disclosure treats them as intelligent navigators capable of making informed decisions about what to read next.

This is not just better for AI. It is better for humans too. Anyone who has used Obsidian or a well-structured wiki knows the feeling: you start at an overview, follow the thread that matters, and reach the detail you need without wading through irrelevant pages. That is how knowledge should work. Top to bottom, broad to narrow, driven by the reader's needs rather than the author's sequence.

Chunker is one implementation of this idea. The concept is bigger than any single tool. As context windows grow and AI agents become more autonomous, the ability to navigate structured knowledge will matter more than the ability to retrieve fragments. The winners will not be the systems with the best embeddings. They will be the systems with the best maps.

The project is open source. You can find it at https://github.com/sermakarevich/chunker

Chunker was built with SDDW (Spec-Driven Development Workflow): https://github.com/sermakarevich/sddw

Progressive disclosure principle formalized by claude-mem: https://docs.claude-mem.ai/progressive-disclosure

Karpathy's LLM Wiki pattern: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
