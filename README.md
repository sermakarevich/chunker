# Chunker

Transform documents into navigable knowledge trees.

Chunker processes a document into a hierarchy of self-sufficient chunks and multi-level summaries, producing a set of linked markdown files that an AI model (or a human) can explore through progressive disclosure -- starting from a high-level overview and drilling into details on demand, without ever loading the entire document.

## The Problem

When an AI model needs to work with a long document, the standard approaches are wasteful:

- **Full context loading** feeds the entire document into a prompt. This burns tokens, dilutes attention, and hits context window limits.
- **Naive chunking** (split every N tokens) produces fragments that start and end mid-thought. A chunk that begins with "they" and references "the approach described above" is useless without its neighbors.
- **Embedding-based retrieval** finds relevant passages but gives the model no way to understand the broader structure or decide which section to explore next.

All three approaches treat a document as either a monolith or a bag of fragments. Neither preserves the document's natural structure or gives the reader a way to navigate it.

## The Approach

Chunker takes a different path: it builds a **navigable tree** where every node is self-contained and every edge is a link the reader can follow.

### Phase 1: Intelligent Chunking

Instead of splitting at fixed token boundaries, Chunker advances a cursor through the text and uses an LLM to find **semantically complete** split points -- places where a topic naturally ends and another begins.

The process works like this:

1. **Expand a window** from the current cursor position, growing it one sentence (or paragraph) at a time until it reaches a minimum size.
2. **Ask the LLM**: "Does this window end at a complete thought?" If not, expand further.
3. **Validate the boundary**: the LLM returns a phrase marking where the next topic begins. This phrase must match the source text *verbatim* -- no fuzzy matching. If it doesn't match, retry once with explicit instructions; if that fails, fall back to the last sentence boundary.
4. **Rewrite for self-sufficiency**: each confirmed chunk gets rewritten so it can stand alone. Pronouns are resolved ("they" becomes "the research team"), implied subjects are made explicit, and minimal framing is added. The original text is preserved alongside the rewrite.
5. **Summarize**: a 1-3 sentence summary is generated for the chunk.

This produces chunks that are complete thoughts, not arbitrary slices. Each chunk carries its original text, its self-sufficient rewrite, and its summary.

Safety valves prevent runaway expansion: if the window hits a maximum token count or a maximum number of expansion attempts, the system force-splits at the last sentence boundary and logs a warning.

### Phase 2: Bottom-Up Aggregation

Once enough chunks accumulate, Chunker groups them into summary blocks and builds a hierarchy bottom-up.

Aggregation triggers when pending summaries cross either a **token threshold** or a **count threshold** -- whichever fires first. When triggered:

1. The LLM proposes how to **group** the pending summaries into thematically coherent clusters.
2. Groups must be **contiguous** (no reordering or skipping) and respect a minimum group size. Oversized groups get a soft nudge to subdivide. If the LLM fails validation twice, the system falls back to even-sized grouping.
3. Each group becomes a **SummaryBlock** with its own summary, and these blocks become the pending summaries for the next level.

This repeats recursively -- Level 0 blocks get grouped into Level 1 blocks, Level 1 into Level 2, and so on -- until the summaries fall below both thresholds or a single root block remains.

The result is a tree where leaves are chunks of original text and internal nodes are progressively broader summaries.

### Context Injection

Every LLM call receives carefully selected context to maintain coherence across the document. Context is assembled in strict priority order:

1. **Immediate predecessor** -- the previous chunk's rewritten text
2. **Higher-level summaries** -- the latest summary from each level of the hierarchy built so far
3. **Earlier chunks** -- walking backwards through recent chunks

A hard token budget caps the total context. Items that would exceed the budget are skipped entirely -- no partial insertion -- and the builder tries the next priority item.

This means later chunks benefit from the hierarchy built by earlier ones: the LLM sees not just the previous chunk but a compressed view of the entire document so far.

## The Output

Chunker produces two output formats:

### Linked Markdown

A directory of `.md` files with wiki-style links between them:

```
output/
  index.md              # Entry point, links to root blocks
  blocks/
    block-L1-001.md     # High-level summary, links to children
    block-L0-001.md     # Mid-level summary, links to chunks
    ...
  chunks/
    chunk-001.md        # Leaf node: summary, rewritten text, original
    chunk-002.md
    ...
```

Every block links down to its children and up to its parent. The index links to all root-level blocks. Starting from the index, you can reach every node in the tree by following links.

This format works directly in Obsidian, any wiki-link-aware viewer, or as a knowledge base that an AI model can navigate by following links.

### JSON Hierarchy

A single `hierarchy.json` with the complete tree: all chunks, all blocks, bidirectional parent/child links, source spans, original text, rewrites, and summaries. This is the canonical output for programmatic consumption.

## Why This Matters

**For AI models exploring a knowledge base:**

An AI model receiving a question can start at the root summaries, decide which branch is relevant, follow the link, read the next level of detail, and continue drilling until it reaches the specific passage it needs. It never loads the whole document -- it navigates a tree, reading only the nodes on its path.

This is progressive disclosure applied to document retrieval: broad context first, fine detail on demand.

**For knowledge engineers building RAG systems:**

Instead of embedding chunks and hoping the retrieval model finds the right one, you can give a model the tree structure and let it navigate. The hierarchy provides the "table of contents" that flat chunk collections lack. Each chunk's self-sufficient rewrite means retrieved passages make sense without their neighbors.

**Compared to naive chunking:**

| Aspect | Fixed-size chunks | Chunker |
|--------|-------------------|---------|
| Split points | Every N tokens | Semantic topic boundaries |
| Chunk independence | Fragments reference missing context | Self-sufficient rewrites |
| Navigation | Flat list, no structure | Hierarchical tree with links |
| Exploration | Load everything or guess | Progressive disclosure |
| Source fidelity | Original text only | Original + rewrite + summary at every level |

## Running

Requires [Ollama](https://ollama.com/) running locally with a model pulled.

```bash
# Process a document
chunker run document.txt --model gemma4:latest --output-dir output/

# Resume from checkpoint after interruption
chunker resume output/checkpoint.json --output-dir output/
```

The system checkpoints after every chunk and summary block, so long documents can survive interruptions without reprocessing from scratch.

## Configuration

All thresholds are named parameters -- no magic numbers:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `split_strategy` | sentences | Unit of window expansion: sentences, paragraphs, or words |
| `min_chunk_tokens` | 400 | Minimum chunk size before completeness checking begins |
| `max_chunk_tokens` | 2000 | Hard ceiling that triggers force-split |
| `max_expansion_attempts` | 5 | Maximum completeness checks before force-split |
| `summary_aggregation_threshold` | 2000 | Token count of pending summaries that triggers aggregation |
| `summary_count_threshold` | 8 | Number of pending summaries that triggers aggregation |
| `min_group_size` | 2 | Hard minimum for summary groups |
| `max_group_size` | 5 | Soft hint for maximum group size |
| `context_budget_tokens` | 10000 | Hard ceiling for context injected into LLM calls |

Model profiles (`qwen3:32b`, `gemma4:latest`, etc.) set sensible defaults for token limits and context windows. Adding a new model requires only a profile definition.
