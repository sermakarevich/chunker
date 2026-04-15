# Task 1: Update data model and config defaults

## Trace
- **FR-IDs:** FR-01, FR-02, FR-03, FR-04
- **Depends on:** none

## Files
- `src/chunker/models.py` — modify
- `src/chunker/config.py` — modify
- `src/chunker/state.py` — modify (transitive serialization)
- `tests/unit/test_models.py` — update (interface change)
- `tests/unit/test_config.py` — update (interface change)
- `tests/unit/test_state.py` — update (interface change)
- `tests/unit/test_pipeline.py` — update (interface change: creates mock Chunk/SummaryBlock)
- `tests/integration/test_pipeline_e2e.py` — update (interface change: creates mock Chunk/SummaryBlock)

## Architecture

### Components
- `Chunk` dataclass: domain model for extracted text chunks — modified
- `SummaryBlock` dataclass: domain model for aggregated blocks — modified
- `ChunkerConfig` dataclass: pipeline configuration — modified
- `ModelProfile` dataclass: model-specific defaults — modified
- `PipelineState` dataclass: serialization depends on Chunk/SummaryBlock — modified (transitive)

### Data Flow
`Chunk`/`SummaryBlock` field changes propagate through `to_dict()`/`from_dict()` serialization → `PipelineState.to_dict()`/`from_dict()` → checkpoint save/load

## Contracts

### Internal Interfaces
- `Chunk(id, source_span, original_text, context, summary, filename, parent_block_id, forced_split, metadata)`: domain chunk with self-sufficient context, info-dense summary, and descriptive slug filename
  - Pre: all fields provided at construction
  - Post: `to_dict()`/`from_dict()` round-trips all fields exactly
- `SummaryBlock(id, level, context, summary, filename, child_ids, parent_block_id, metadata)`: aggregated block with chunk-sized synthesis, short summary, and descriptive slug filename
  - Pre: all fields provided at construction
  - Post: `to_dict()`/`from_dict()` round-trips all fields exactly
- `ChunkerConfig` defaults: `min_chunk_tokens=2000`, `max_chunk_tokens=4000`, `context_budget_tokens=20000`, `summary_aggregation_threshold=4000`
  - Pre: no overrides provided
  - Post: all dependent defaults scaled proportionally
- `ChunkerConfig.from_model(model)`: creates config with model-specific profile defaults
  - Pre: model name exists in MODEL_PROFILES
  - Post: `max_chunk_tokens=4000`, `context_budget_tokens=20000`

## Data Models

### Chunk (modified)
- `id: str` — unchanged
- `source_span: tuple[int, int]` — unchanged
- `original_text: str` — unchanged
- `context: str` — **replaces `rewritten_text`**. Self-sufficient LLM rewrite resolving references
- `summary: str` — unchanged semantics (now explicitly 1-2 sentence, info-dense)
- `filename: str` — **new**. LLM-generated descriptive slug (e.g., `attention-mechanism-overview`)
- `parent_block_id: str | None` — unchanged
- `forced_split: bool` — unchanged
- `metadata: dict` — unchanged

### SummaryBlock (modified)
- `id: str` — unchanged
- `level: int` — unchanged
- `context: str` — **new**. Chunk-sized synthesis (2000-4000 tokens) from children's contexts
- `summary: str` — semantics changed: now 1-2 sentence info-dense summary (was the sole long-form text)
- `filename: str` — **new**. LLM-generated descriptive slug
- `child_ids: list[str]` — unchanged
- `parent_block_id: str | None` — unchanged
- `metadata: dict` — unchanged

### ChunkerConfig (modified defaults)
- `min_chunk_tokens`: 400 → **2000**
- `max_chunk_tokens`: 2000 → **4000**
- `context_budget_tokens`: 10000 → **20000** (5x max_chunk_tokens)
- `summary_aggregation_threshold`: 2000 → **4000** (proportional 2x with chunk size doubling)

### ModelProfile entries (all profiles)
- `max_chunk_tokens`: 2000 → **4000**
- `context_budget_tokens`: 10000 → **20000**

## Design Decisions

### Field rename strategy: direct rename vs deprecation alias
- **Chosen:** Direct rename (`rewritten_text` → `context`, no alias)
- **Rationale:** Old checkpoints are explicitly declared incompatible (constraints). No backward-compat needed.
- **Rejected:** Deprecation alias with fallback in `from_dict` — adds complexity for a breaking change that's already accepted

## Acceptance Criteria

### FR-01: Chunk data model
- GIVEN a chunk is extracted and rewritten
- WHEN stored in state
- THEN it SHALL have `original_text`, `context` (self-sufficient rewrite), `summary` (1-2 sentences, fact-dense), and `filename` (descriptive slug like `attention-mechanism-overview`)
- AND `rewritten_text` field SHALL NOT exist

- GIVEN a Chunk with all new fields
- WHEN serialized via `to_dict()` and deserialized via `from_dict()`
- THEN all fields including `context`, `summary`, and `filename` SHALL round-trip exactly

### FR-02: SummaryBlock data model
- GIVEN a block is created from aggregation
- WHEN stored in state
- THEN it SHALL have `context` (chunk-sized synthesis), `summary` (1-2 sentences, fact-dense), and `filename` (descriptive slug)
- AND the old single `summary` field (which was the long-form summary) SHALL NOT exist as the sole text field

- GIVEN a SummaryBlock with all new fields
- WHEN serialized via `to_dict()` and deserialized via `from_dict()`
- THEN all fields including `context`, `summary`, and `filename` SHALL round-trip exactly

### FR-03: Chunk size defaults
- GIVEN a ChunkerConfig created with no overrides
- THEN `min_chunk_tokens` SHALL be 2000
- AND `max_chunk_tokens` SHALL be 4000

- GIVEN `ChunkerConfig.from_model("qwen3:32b")`
- THEN `max_chunk_tokens` SHALL be 4000

### FR-04: Scaled dependent defaults
- GIVEN default `max_chunk_tokens` is 4000
- THEN `context_budget_tokens` SHALL be at least 5x `max_chunk_tokens` (i.e., >= 20000)

- GIVEN default `max_chunk_tokens` is 4000
- THEN `summary_aggregation_threshold` SHALL be scaled proportionally to the new chunk size

## Done Criteria
- [ ] `Chunk` dataclass has `context` and `filename` fields; `rewritten_text` removed
- [ ] `SummaryBlock` dataclass has `context` and `filename` fields
- [ ] `to_dict()`/`from_dict()`/`to_json()`/`from_json()` round-trip all new fields for both models
- [ ] `PipelineState` serialization works with updated Chunk/SummaryBlock
- [ ] `ChunkerConfig` defaults: min=2000, max=4000, context_budget=20000, aggregation_threshold=4000
- [ ] All `ModelProfile` entries updated: max_chunk_tokens=4000, context_budget_tokens=20000
- [ ] `ChunkerConfig.from_model("qwen3:32b")` returns max_chunk_tokens=4000
- [ ] `test_models.py`, `test_config.py`, `test_state.py` pass with updated fields
- [ ] `test_pipeline.py`, `test_pipeline_e2e.py` mock objects updated for new field names
- [ ] No reference to `rewritten_text` remains in models, state, config, or their tests
