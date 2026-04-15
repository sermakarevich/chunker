# Requirements: mdstructure

## 1. Project

- Path: `.`

---

## 2. Purpose

Restructure the chunker's data model and output to maximize information density at every level of the hierarchy -- replacing brief summaries with chunk-sized synthesized contexts, unifying chunk and block structures, and producing human-readable markdown files named by content rather than ID.

---

## 3. User Stories

- As an AI model, I want every chunk and block file to contain a full, self-sufficient context (~2000-4000 tokens) so that I can extract detailed knowledge from any single node without navigating to its children.
- As an AI model, I want wiki-links to display information-dense summaries (1-2 sentences) so that I can decide which child to explore based on factual content, not vague labels.
- As a knowledge engineer, I want chunk and block files named by their content (e.g., `attention-mechanism-overview.md`) rather than IDs, so that I can browse the output directory and understand the structure at a glance.
- As a knowledge engineer, I want to configure larger chunk sizes (2000-4000 tokens) so that each chunk captures more complete logical units from the source text.
- As a knowledge engineer, I want model profile defaults to scale coherently with the new chunk sizes (context budget, aggregation thresholds, etc.) so that increasing chunk tokens doesn't require manually adjusting every related parameter.

---

## 4. Functional Requirements

### Data Model

- **FR-01**: Chunk SHALL have fields: `id`, `source_span`, `original_text`, `context` (self-sufficient LLM rewrite replacing `rewritten_text`), `summary` (1-2 sentence information-dense summary), `filename` (LLM-generated descriptive slug), `parent_block_id`, `forced_split`, `metadata`.
- **FR-02**: SummaryBlock SHALL have fields: `id`, `level`, `context` (chunk-sized synthesis replacing the old brief `summary`), `summary` (1-2 sentence information-dense summary), `filename` (LLM-generated descriptive slug), `child_ids`, `parent_block_id`, `metadata`.

### Configuration

- **FR-03**: Default `min_chunk_tokens` SHALL be 2000 and `max_chunk_tokens` SHALL be 4000.
- **FR-04**: Model profile defaults SHALL scale coherently with chunk size changes -- `context_budget_tokens`, `summary_aggregation_threshold`, and other dependent parameters SHALL be updated proportionally.

### LLM Prompts & Schemas

- **FR-05**: Chunk rewrite prompt SHALL produce `context`, `summary`, and `filename`, and SHALL instruct the LLM to preserve all specific facts, numbers, names, and relationships -- not generalize or omit details.
- **FR-06**: Block context generation SHALL take children's `context` fields plus metadata (previous chunk/block + latest higher-level blocks) as input, SHALL include the target token range (`min_chunk_tokens` to `max_chunk_tokens`) in the prompt, and SHALL produce `context`, `summary`, and `filename`.
- **FR-07**: Block grouping decisions SHALL operate on chunk/block `summary` fields (the short 1-2 sentence versions), not on full `context`.
- **FR-08**: All LLM prompts that produce `context` or `summary` SHALL include explicit information-persistence directives instructing the model to preserve all relevant facts, numbers, names, and relationships.

### Markdown Output

- **FR-09**: Markdown files SHALL be named using the `filename` field (LLM-generated descriptive slug) instead of the node ID.
- **FR-10**: Chunk `.md` files SHALL contain only: title, parent wiki-link, and `context` body. Summary and original text sections SHALL be removed.
- **FR-11**: Block `.md` files SHALL contain only: title, parent wiki-link, `context` body, and child wiki-links.
- **FR-12**: Wiki-links SHALL display the target node's `summary` as the link label (e.g., `[[path|summary text]]`).

### JSON Output

- **FR-13**: JSON export SHALL use updated field names (`context` instead of `rewritten_text`) and SHALL include `summary` and `filename` fields for both chunks and blocks.

### Prohibitions

- **FR-14**: LLM prompts SHALL NOT allow omission of relevant facts from `context` or `summary` -- information persistence is a hard requirement at every level.
- **FR-15**: System SHALL NOT use node IDs as markdown filenames -- only `filename` field values.

---

## 5. Acceptance Criteria

### FR-01: Chunk data model

**Happy path:**
- GIVEN a chunk is extracted and rewritten
- WHEN stored in state
- THEN it SHALL have `original_text`, `context` (self-sufficient rewrite), `summary` (1-2 sentences, fact-dense), and `filename` (descriptive slug like `attention-mechanism-overview`)
- AND `rewritten_text` field SHALL NOT exist

**Round-trip serialization:**
- GIVEN a Chunk with all new fields
- WHEN serialized via `to_dict()` and deserialized via `from_dict()`
- THEN all fields including `context`, `summary`, and `filename` SHALL round-trip exactly

### FR-02: SummaryBlock data model

**Happy path:**
- GIVEN a block is created from aggregation
- WHEN stored in state
- THEN it SHALL have `context` (chunk-sized synthesis), `summary` (1-2 sentences, fact-dense), and `filename` (descriptive slug)
- AND the old single `summary` field (which was the long-form summary) SHALL NOT exist as the sole text field

**Round-trip serialization:**
- GIVEN a SummaryBlock with all new fields
- WHEN serialized via `to_dict()` and deserialized via `from_dict()`
- THEN all fields including `context`, `summary`, and `filename` SHALL round-trip exactly

### FR-03: Chunk size defaults

**Default config:**
- GIVEN a ChunkerConfig created with no overrides
- THEN `min_chunk_tokens` SHALL be 2000
- AND `max_chunk_tokens` SHALL be 4000

**Model profile defaults:**
- GIVEN `ChunkerConfig.from_model("qwen3:32b")`
- THEN `max_chunk_tokens` SHALL be 4000

### FR-04: Scaled dependent defaults

**Context budget:**
- GIVEN default `max_chunk_tokens` is 4000
- THEN `context_budget_tokens` SHALL be at least 5x `max_chunk_tokens` (i.e., >= 20000)

**Aggregation threshold:**
- GIVEN default `max_chunk_tokens` is 4000
- THEN `summary_aggregation_threshold` SHALL be scaled proportionally to the new chunk size

### FR-05: Chunk rewrite prompt

**Context output:**
- GIVEN a chunk with pronouns and implied references
- WHEN the rewrite prompt runs
- THEN the `context` field SHALL resolve references and be self-sufficient
- AND SHALL preserve all specific facts, numbers, names from the original

**Summary output:**
- GIVEN a rewritten chunk
- THEN the `summary` SHALL be 1-2 sentences
- AND SHALL contain specific facts, not vague generalizations

**Filename output:**
- GIVEN a rewritten chunk about attention mechanisms in transformers
- THEN the `filename` SHALL be a descriptive slug (e.g., `attention-mechanism-overview`)

### FR-06: Block context generation

**Input assembly:**
- GIVEN a block being generated from 3 child chunks
- WHEN the block context prompt runs
- THEN it SHALL receive children's `context` fields, the previous chunk/block's context, and latest higher-level block contexts as metadata

**Token target:**
- GIVEN `min_chunk_tokens=2000` and `max_chunk_tokens=4000`
- WHEN the block context prompt runs
- THEN the prompt SHALL instruct the LLM to produce context in the 2000-4000 token range

**Output:**
- GIVEN the prompt completes
- THEN the block SHALL have `context`, `summary`, and `filename`
- AND `context` length SHALL approximate the chunk token range

### FR-07: Grouping on summaries

**Input:**
- GIVEN 8 pending chunks with `summary` fields
- WHEN the grouping prompt runs
- THEN it SHALL receive only the `summary` fields (1-2 sentences each), not the full `context`

### FR-08: Information persistence directive

**All prompts:**
- GIVEN any LLM prompt that produces `context` or `summary`
- THEN the prompt text SHALL contain explicit instructions to preserve all relevant facts, numbers, names, and relationships

### FR-09: Filename-based markdown files

**Chunk file naming:**
- GIVEN a chunk with `filename="attention-mechanism-overview"`
- WHEN markdown is rendered
- THEN the file SHALL be `chunks/attention-mechanism-overview.md`

**Block file naming:**
- GIVEN a block with `filename="transformer-architecture-deep-dive"`
- WHEN markdown is rendered
- THEN the file SHALL be `blocks/transformer-architecture-deep-dive.md`

**Uniqueness:**
- GIVEN two nodes produce the same `filename`
- THEN the system SHALL append a disambiguator (e.g., `-2`) to avoid collisions

### FR-10: Simplified chunk markdown

**Content:**
- GIVEN a chunk with `context`, `summary`, and parent block
- WHEN rendered to markdown
- THEN the file SHALL contain: title, parent wiki-link, and `context` body
- AND SHALL NOT contain a "Summary" section
- AND SHALL NOT contain an "Original" section

### FR-11: Simplified block markdown

**Content:**
- GIVEN a block with `context`, `summary`, children, and parent
- WHEN rendered to markdown
- THEN the file SHALL contain: title, parent wiki-link, `context` body, and child wiki-links
- AND SHALL NOT contain a separate "Summary" section

### FR-12: Wiki-links with summary labels

**Link format:**
- GIVEN a block with child chunk `filename="attention-overview"` and `summary="Describes multi-head attention mechanism with scaled dot-product scoring."`
- WHEN child links are rendered
- THEN the link SHALL be `[[chunks/attention-overview|Describes multi-head attention mechanism with scaled dot-product scoring.]]`

### FR-13: JSON updated fields

**Chunk export:**
- GIVEN a chunk exported to JSON
- THEN it SHALL contain `context` (not `rewritten_text`), `summary`, and `filename` fields

**Block export:**
- GIVEN a block exported to JSON
- THEN it SHALL contain `context`, `summary`, and `filename` fields

### FR-14: Information persistence prohibition

**No vague generalizations:**
- GIVEN a chunk `context` produced by the LLM
- THEN it SHALL NOT reduce specific facts to vague generalizations (e.g., "discusses several approaches" when the source names specific approaches)

### FR-15: No ID-based filenames

**Enforcement:**
- GIVEN any markdown rendering
- THEN no file SHALL be named `chunk-001.md` or `block-L1-001.md`
- AND all files SHALL use the `filename` field value

---

## 6. Constraints

### In Scope

- Unified data model: Chunk (`original_text`/`context`/`summary`/`filename`) and Block (`context`/`summary`/`filename`)
- Chunk size increase: min 2000, max 4000 tokens with proportionally scaled dependent defaults
- LLM-generated descriptive filenames for all nodes
- Information-persistence directives in all content-producing prompts
- Block context generation as chunk-sized synthesis from children's contexts + metadata
- Grouping based on short summaries, block context from full children contexts
- Simplified markdown output: context + links only, no summary/original sections
- Wiki-links with summary text as labels
- Updated JSON export with new field names
- Updated LLM schemas (`RewriteResult`, `BlockSummaryResult` -> unified output with context/summary/filename)
- Full TDD

### Out of Scope

- Changing the chunking pipeline flow (cursor, completeness checking, boundary validation) -- unchanged from chunker
- Changing the aggregation sweep logic (dual-trigger thresholds, contiguous grouping) -- unchanged beyond operating on new summary fields
- Adding new LLM providers -- unchanged from chunker
- Checkpoint format migration -- old checkpoints will be incompatible (acceptable for this stage)

### Prohibitions

- SHALL NOT use vague or generic language in summaries or contexts -- all output must be information-dense
- SHALL NOT use node IDs as filenames in markdown output
- SHALL NOT include "Summary" or "Original" sections in chunk markdown files
- SHALL NOT pass full `context` fields to the grouping prompt -- only short `summary` fields

### Testing Approach

- Full TDD -- write failing tests first, then implement to pass
