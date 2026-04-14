# Requirements: Chunker

## 1. Project

- Path: `.`

---

## 2. Purpose

Process documents into a hierarchical tree of self-sufficient chunks and multi-level summaries, enabling AI models to navigate from broad concepts to fine-grained details via progressive disclosure — without reading the entire document.

---

## 3. User Stories

- As an AI model, I want to read a root-level summarries of a processed document, so that I can determine if the document is relevant and which section to explore first.
- As an AI model, I want to follow links from a summary node to its children, so that I can progressively drill into finer-grained details without loading the entire document.
- As a knowledge engineer, I want to feed an AI paper (txt or pdf format) into the system and get a directory of linked markdown files, so that I can add it to my knowledge base for model-assisted exploration.
- As a knowledge engineer, I want processing to resume from a checkpoint after interruption, so that long documents don't need to be reprocessed from scratch.
- As a knowledge engineer, I want to configure the system for different local models (Qwen3, Gemma4, etc.), so that I can use whichever model performs best for my hardware and document type.

---

## 4. Functional Requirements

### Core Pipeline

- **FR-01**: System SHALL advance a cursor through the source text, producing candidate chunk windows one at a time using a configurable split strategy (words, paragraphs, sentences) as the unit of expansion.
- **FR-02**: System SHALL perform LLM-based completeness checking on each candidate chunk boundary to determine if the chunk ends at a logically complete point, using injected metadata context and explicit topic-shift indicators (new subject, transition phrases, section breaks).
- **FR-03**: System SHALL validate LLM-returned boundary phrases against the source text verbatim, with one retry on mismatch (re-prompting for exact phrasing) and sentence-boundary fallback if retry fails.
- **FR-04**: System SHALL rewrite each confirmed chunk to be self-sufficient (resolving pronouns, clarifying implied subjects, prepending minimal framing) so the rewritten chunk can be consumed on its own without additional context and produce a short summary (1-3 sentences).
- **FR-05**: System SHALL force-split at the last sentence boundary when `max_chunk_tokens` is reached or `max_expansion_attempts` is exhausted, marking the chunk `forced_split: true` and logging `WARN: forced_split`.

### Hierarchy Building

- **FR-06**: System SHALL trigger summary aggregation when EITHER cumulative token count of pending summaries exceeds `summary_aggregation_threshold` OR pending summary count exceeds `summary_count_threshold` — whichever fires first.
- **FR-07**: System SHALL enforce `min_group_size` as a hard constraint and `max_group_size` as a soft hint during LLM-driven grouping, rejecting groups below minimum, re-prompting for oversized groups, and falling back to even-sized grouping after two consecutive hard validation failures (logging `WARN: grouping_fallback`).
- **FR-08**: System SHALL recursively aggregate SummaryBlocks level by level until one root block remains or neither aggregation threshold is exceeded.

### Context Injection

- **FR-09**: System SHALL inject metadata context into every LLM call following this priority order: (1) same-level immediate predecessor, (2) latest summary from each higher level up to root, (3) earlier same-level context walking backwards — respecting `context_budget_tokens` as a hard ceiling with no partial insertion of items.

### Output

- **FR-10**: System SHALL produce a JSON document containing the complete hierarchy with bidirectional parent/child links, source spans, original text, rewritten text, and summaries.
- **FR-11**: System SHALL render the JSON hierarchy into a directory of linked markdown files — one file per node, with wiki-style links between parent and child nodes, and a root index file linking to top-level SummaryBlocks.

### Infrastructure

- **FR-12**: System SHALL abstract all LLM calls behind a provider-agnostic `LLMClient` protocol with structured JSON response validation. Adding a new provider SHALL require implementing a single class. Ollama SHALL be the default implementation.
- **FR-13**: System SHALL checkpoint the full `ProcessingState` after each completed Chunk or SummaryBlock, enabling resumption from the last checkpoint on restart.
- **FR-14**: System SHALL support model-dependent configuration profiles (token limits, context windows, default parameters) extensible to new models without code changes beyond the profile definition.
- **FR-15**: System SHALL log every LLM call with a structured entry including: event type, chunk/block ID, token counts, model response, context items injected, and any warnings.

### Prohibitions

- **FR-16**: System SHALL NOT perform fuzzy or approximate string matching on boundary phrases — verbatim match or sentence-boundary fallback only.
- **FR-17**: System SHALL NOT produce non-contiguous groupings during summary aggregation — all groups must be contiguous runs of the ordered summary list.

### Source Tracking

- **FR-18**: System SHALL track `source_span` (start_char, end_char) for every chunk, preserving exact character-position mapping to the original document text.

---

## 5. Acceptance Criteria

### FR-01: Cursor-driven splitting

**Happy path:**
- GIVEN a document and "sentences" split strategy
- WHEN the system starts processing
- THEN it SHALL produce a candidate window starting at cursor position 0 containing at least `min_chunk_tokens` worth of text, expanded one sentence at a time

**Continuation:**
- GIVEN a confirmed chunk ending at char position 412
- WHEN the next candidate is requested
- THEN the cursor SHALL start at position 412 and the new window SHALL begin from that exact position

**Strategy switch:**
- GIVEN the same document processed with "paragraphs" vs "sentences" strategy
- WHEN processing begins
- THEN the expansion unit SHALL match the configured strategy

### FR-02: LLM completeness checking

**Complete boundary:**
- GIVEN a candidate window ending at a topic transition
- WHEN the LLM checks completeness
- THEN it SHALL return `complete: true` with a `boundary_phrase` marking where the next chunk begins

**Incomplete boundary:**
- GIVEN a candidate window ending mid-thought
- WHEN the LLM checks completeness
- THEN it SHALL return `complete: false`
- AND the system SHALL expand the window by one split unit and re-check

### FR-03: Boundary phrase validation

**Phrase found:**
- GIVEN the LLM returns a `boundary_phrase`
- WHEN the phrase is searched in the remaining text
- THEN it SHALL match verbatim as a substring

**Retry succeeds:**
- GIVEN a `boundary_phrase` not found verbatim
- WHEN the LLM is re-prompted with explicit verbatim instruction
- THEN if the retry phrase matches, that position SHALL be used

**Retry fails:**
- GIVEN both attempts fail to produce a matching phrase
- THEN the system SHALL split at the last sentence boundary
- AND log `WARN: phrase_not_found`

### FR-04: Chunk rewrite and summary

**Self-sufficiency:**
- GIVEN a chunk containing pronouns referencing prior text ("they", "this approach")
- WHEN rewritten
- THEN the rewritten text SHALL resolve those references to explicit subjects

**Both artifacts preserved:**
- GIVEN a confirmed chunk
- WHEN rewriting completes
- THEN both `original_text` (verbatim source) and `rewritten_text` SHALL be stored
- AND a 1-3 sentence `summary` SHALL be produced

### FR-05: Force-split

**Max tokens reached:**
- GIVEN expansion reaches `max_chunk_tokens`
- THEN the system SHALL force-split at the last sentence boundary
- AND mark `forced_split: true`
- AND log `WARN: forced_split`

**Max attempts exhausted:**
- GIVEN `max_expansion_attempts` completeness checks all return `complete: false`
- THEN the same force-split behaviour SHALL apply

### FR-06: Dual-trigger aggregation

**Token trigger:**
- GIVEN cumulative tokens of pending summaries exceed `summary_aggregation_threshold`
- THEN aggregation SHALL begin

**Count trigger:**
- GIVEN pending summary count exceeds `summary_count_threshold`
- THEN aggregation SHALL begin even if token threshold is not reached

**Below both thresholds:**
- GIVEN both thresholds are not exceeded after Phase 1 completes
- THEN no aggregation SHALL occur
- AND the output SHALL be a flat list of chunks with no SummaryBlock layer

### FR-07: Group size constraints

**Min group violation:**
- GIVEN the LLM proposes a group with fewer than `min_group_size` summaries
- THEN the system SHALL reject the response and re-prompt with the constraint stated explicitly

**Max group soft hint:**
- GIVEN the LLM proposes a group exceeding `max_group_size`
- THEN the system SHALL re-prompt asking for subdivision
- AND accept the original response if the model declines to subdivide

**Fallback:**
- GIVEN two consecutive hard validation failures
- THEN the system SHALL fall back to even-sized grouping (ceil(n/4) contiguous groups)
- AND log `WARN: grouping_fallback`

### FR-08: Recursive aggregation

**Recursion continues:**
- GIVEN level N blocks are produced and their summaries exceed either aggregation threshold
- THEN the system SHALL aggregate them into level N+1 blocks

**Recursion terminates:**
- GIVEN level N blocks are produced and their summaries fall below both thresholds
- THEN recursion SHALL stop
- AND those blocks SHALL be the root blocks

**Single root:**
- GIVEN aggregation reduces to a single block
- THEN that block SHALL be the root
- AND recursion SHALL stop

### FR-09: Context injection

**Immediate predecessor priority:**
- GIVEN a chunk being processed and a prior chunk exists
- WHEN context is assembled
- THEN the predecessor's rewritten_text or summary SHALL be the first item injected

**Higher-level summaries:**
- GIVEN L1 and L2 summary blocks exist
- WHEN context is assembled for a chunk
- THEN the latest summary from each level SHALL be included after the predecessor

**Budget enforcement:**
- GIVEN `context_budget_tokens` is set
- WHEN the next candidate context item would exceed the budget
- THEN that item SHALL be skipped entirely (no partial insertion)
- AND the builder SHALL try the next priority item

**Early processing (no hierarchy yet):**
- GIVEN no higher-level summaries exist yet (first chunks being processed)
- WHEN context is assembled
- THEN the builder SHALL silently omit unavailable levels without error

### FR-10: JSON output

**Structure:**
- GIVEN processing completes
- WHEN JSON is exported
- THEN it SHALL contain `document_id`, `root_blocks`, `blocks` dict, and `chunks` dict with all specified fields

**Bidirectional links:**
- GIVEN any chunk or block in the output
- WHEN traversing `parent_block_id` upward and `child_ids` downward
- THEN the links SHALL be consistent (parent's child_ids includes the node, node's parent_block_id matches the parent)

### FR-11: Linked markdown rendering

**One file per node:**
- GIVEN a completed hierarchy
- WHEN markdown is rendered
- THEN each Chunk and SummaryBlock SHALL produce its own `.md` file

**Wiki-links:**
- GIVEN a SummaryBlock with 3 children
- WHEN its markdown is rendered
- THEN it SHALL contain links to all 3 child files
- AND a link to its parent (if any)

**Root entry point:**
- GIVEN the rendering completes
- THEN a root/index file SHALL exist linking to top-level SummaryBlocks

**Full traversal:**
- GIVEN a reader starting at the root file
- WHEN following child links recursively
- THEN it SHALL be possible to reach every leaf chunk in the hierarchy

### FR-12: Provider-agnostic LLMClient

**Protocol adherence:**
- GIVEN a new LLM provider
- WHEN implementing `LLMClient`
- THEN only the `complete()` method needs to be implemented

**Ollama default:**
- GIVEN no explicit provider configuration
- WHEN the system starts
- THEN it SHALL use the Ollama implementation

**Structured output with retries:**
- GIVEN a response schema
- WHEN the LLM responds with invalid JSON or schema-violating output
- THEN the system SHALL retry with exponential backoff (up to 3 attempts)
- AND include validation error feedback in the retry prompt

### FR-13: Checkpointing

**After each chunk:**
- GIVEN a chunk is confirmed and rewritten
- THEN the full `ProcessingState` SHALL be serialized to `checkpoint_path` before advancing the cursor

**Resumability:**
- GIVEN an existing checkpoint for `document_id`
- WHEN the system starts
- THEN it SHALL restore state and resume from `cursor_position`

**After each block:**
- GIVEN a SummaryBlock is created
- THEN the state SHALL be checkpointed

### FR-14: Model-dependent configuration

**Profile loading:**
- GIVEN model "qwen3:32b" is configured
- WHEN defaults are loaded
- THEN token limits and context window SHALL match that model's profile

**Extensibility:**
- GIVEN a new model is added
- WHEN a profile is registered
- THEN the system SHALL use it without code changes beyond the profile definition

### FR-15: Structured logging

**Every LLM call logged:**
- GIVEN any LLM call (completeness check, chunk rewrite, summary grouping, block summary)
- THEN a structured log entry SHALL be emitted with: event type, chunk/block ID, token counts (prompt + completion), model response, context items injected, and any warnings

### FR-16: No fuzzy matching

**Verbatim only:**
- GIVEN a boundary phrase that does not match verbatim in the source text
- THEN the system SHALL NOT attempt approximate, fuzzy, or similarity-based matching
- AND SHALL follow the retry-then-fallback flow from FR-03

### FR-17: Contiguous groups only

**Validation:**
- GIVEN a grouping response from the LLM
- WHEN groups are validated
- THEN no group SHALL contain non-contiguous summaries
- AND reordering or skipping summaries SHALL NOT be permitted

### FR-18: Source span tracking

**Accuracy:**
- GIVEN a chunk with `source_span: (start, end)`
- WHEN extracting `source_text[start:end]`
- THEN the result SHALL exactly match `original_text` character for character

---

## 6. Constraints

### In Scope

- Two-phase processing pipeline (chunking + summary aggregation)
- Cursor-driven LLM boundary detection with completeness checking
- Chunk rewriting for self-sufficiency and summary generation
- Hierarchical summary tree built bottom-up with contiguous grouping
- Context injection with priority ordering and token budget
- JSON canonical output with bidirectional traversal links
- Linked markdown rendering (Obsidian-style wiki-links) as Step 2
- Checkpointing and resumability after each chunk/block
- Provider-agnostic LLMClient protocol with Ollama as default implementation
- Model-dependent configuration profiles (Qwen3, Gemma4 as initial models)
- Structured logging of all LLM calls
- Full TDD — tests written before implementation for all components

### Out of Scope

- Incremental/partial document reprocessing — full reprocess on update (v2 candidate)
- Embedding generation — consumer's responsibility
- Search/retrieval interface — output is consumed by external systems
- PDF/HTML parsing — input is plain text; format conversion is a preprocessing step outside this system
- Cloud LLM provider implementations — the protocol supports them, but no v1 implementation is included
- Concurrent/parallel chunk processing — sequential cursor-driven processing by design

### Prohibitions

- SHALL NOT use fuzzy or approximate string matching for boundary phrases
- SHALL NOT produce non-contiguous summary groupings
- SHALL NOT partially insert context items — whole items or nothing
- SHALL NOT hardcode model-specific values — all thresholds via named configuration parameters

### Configuration Constraints

- `context_budget_tokens` SHOULD be at least 5x `max_chunk_tokens` to provide sufficient context for LLM decisions
- Total prompt size (context + chunk + instructions + response headroom) SHALL NOT exceed the configured model's context window
- All thresholds SHALL be named configuration parameters — no magic numbers in code
- Model profiles SHALL define at minimum: context window size, default max_chunk_tokens, default context_budget_tokens

### Testing Approach

- Full TDD — write failing tests first, then implement to pass
- Mock `LLMClient` in unit tests for deterministic, fast test execution
- Integration tests against a real Ollama instance for end-to-end validation
- Every functional requirement has testable acceptance criteria defined above
