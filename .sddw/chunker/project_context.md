---
name: chunker-project-context
description: Key design decisions and context for the chunker project — Ollama-based, markdown output, progressive disclosure
type: project
---

Hierarchical document chunking system for AI-navigable knowledge bases.

**Key decisions:**
- LLM calls are local via Ollama (zero cost) — quality over efficiency
- Models: Qwen3 and Gemma4 initially, model-agnostic with profiles
- Output: JSON (canonical) → linked markdown (Obsidian-style) as two-step process
- Navigation: top-down progressive disclosure by AI models
- Input: primarily AI/ML papers, extensible to other formats
- Testing: full TDD
- Context budget: should be >= 5x chunk size; total prompt must fit model context window
- Aggregation: dual trigger (token count OR summary count)
- Splitting: cursor-driven (not batch), one candidate window at a time
- LLMClient: provider-agnostic protocol, Ollama as default implementation

**Design decisions (from design step):**
- Architecture: plain Python pipeline class with LangChain for LLM abstractions (ChatOllama). No LangGraph — flow is a simple loop, complexity is inside steps not between them.
- Interleaved processing: after every chunk extraction, immediately sweep all aggregation levels bottom-up. Builds hierarchy incrementally, gives later chunks better context.
- Config: single ChunkerConfig dataclass with separate named fields for chunk/summary/context concerns. Not unified — different operations despite shared topic-shift concept.
- Token counting: word approximation (len(text.split()) * token_factor), factor per model profile
- Sentence detection: regex-based (r'(?<=[.!?])\s+(?=[A-Z])'), no heavy dependencies
- Model profiles: Python dict (MODEL_PROFILES) in config.py, not YAML
- LLM retries: own retry loop (max 3, exponential backoff) with validation error feedback appended to re-prompt
- Checkpointing: JSON file with atomic write (temp + rename), after each chunk/block
- Code style: no comments, clean code principles
- Tooling: uv, pytest, justfile

**Why:** Sergii wants to build a knowledge base where an AI can navigate processed papers top-down — starting at root summaries, drilling into branches, reaching source text — without loading entire documents.

**How to apply:** All design decisions should favor navigation quality and summary discriminativeness over processing speed or token efficiency.
