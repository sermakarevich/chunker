# Task 4: Update aggregation sweeper for block synthesis

## Trace
- **FR-IDs:** FR-06, FR-07
- **Depends on:** task-2

## Files
- `src/chunker/nodes/aggregation.py` — modify
- `tests/unit/test_aggregation.py` — update (interface change)

## Architecture

### Components
- `AggregationSweeper`: groups pending summaries and creates blocks via LLM — modified

### Data Flow
**Grouping (unchanged, uses short summaries):**
`state.pending_summaries[level]` → `_get_summary()` returns short `summary` → `LLMService.group_summaries()` → validated groups

**Block creation (changed, uses full contexts):**
For each group: `_get_context()` collects children's `context` fields → `_build_metadata()` assembles previous context + higher-level block contexts → `LLMService.synthesize_block(children_contexts, metadata, min_tokens, max_tokens)` → `BlockContextResult` → `SummaryBlock(context=..., summary=..., filename=...)`

## Contracts

### Internal Interfaces
- `AggregationSweeper.sweep(state: PipelineState) -> None`: unchanged signature
  - Pre: state has pending summaries at one or more levels
  - Post: blocks created with `context`, `summary`, `filename` from LLM synthesis
- `AggregationSweeper._get_summary(state, item_id) -> str`: returns short `summary` field — unchanged semantics
  - Pre: item_id exists in chunks or blocks
  - Post: returns the 1-2 sentence `summary` string (used for grouping and threshold checks)
- `AggregationSweeper._get_context(state, item_id) -> str`: **new** — returns full `context` field
  - Pre: item_id exists in chunks or blocks
  - Post: returns the full `context` string (used for block synthesis input)
- `AggregationSweeper._build_metadata(state, group_ids, level) -> str`: **new** — assembles metadata for synthesis
  - Pre: group_ids is a non-empty list, level is current aggregation level
  - Post: returns formatted string with previous item's context + latest higher-level block contexts
- `AggregationSweeper._create_blocks(state, level, groups, pending_ids) -> None`: modified
  - Pre: groups resolved, level known
  - Post: each group produces a SummaryBlock with `context`, `summary`, `filename` from `synthesize_block`

## Design Decisions

### Metadata assembly: inline in AggregationSweeper
- **Chosen:** `_build_metadata` as a private method on AggregationSweeper
- **Rationale:** Block synthesis metadata needs (predecessor context + higher-level blocks) are specific to aggregation. No need to extend ContextBuilder which serves chunk rewriting.
- **Rejected:** Extending ContextBuilder — couples two unrelated concerns

### Grouping still uses short summaries (FR-07)
- **Chosen:** `_get_summary` continues to return the short `summary` field for grouping decisions and threshold token estimation
- **Rationale:** FR-07 explicitly requires grouping to operate on short summaries, not full contexts. This keeps the grouping prompt input small and focused.
- **Rejected:** Using `context` for grouping — violates FR-07, wastes tokens on grouping decisions

## Acceptance Criteria

### FR-06: Block context generation
- GIVEN a block being generated from 3 child chunks
- WHEN the block context prompt runs
- THEN it SHALL receive children's `context` fields, the previous chunk/block's context, and latest higher-level block contexts as metadata

- GIVEN `min_chunk_tokens=2000` and `max_chunk_tokens=4000`
- WHEN the block context prompt runs
- THEN the prompt SHALL instruct the LLM to produce context in the 2000-4000 token range

- GIVEN the prompt completes
- THEN the block SHALL have `context`, `summary`, and `filename`
- AND `context` length SHALL approximate the chunk token range

### FR-07: Grouping on summaries
- GIVEN 8 pending chunks with `summary` fields
- WHEN the grouping prompt runs
- THEN it SHALL receive only the `summary` fields (1-2 sentences each), not the full `context`

## Done Criteria
- [ ] `_create_blocks` calls `synthesize_block` with children's `context` fields + metadata + token range
- [ ] `_get_context` helper method returns full `context` from chunks or blocks
- [ ] `_build_metadata` assembles predecessor context + higher-level block contexts
- [ ] Created `SummaryBlock` has `context`, `summary`, `filename` from `BlockContextResult`
- [ ] `_get_summary` still returns short `summary` for grouping and threshold checks
- [ ] `_thresholds_exceeded` estimates tokens from short `summary` (not `context`)
- [ ] `group_summaries` input uses short `summary` text (not `context`)
- [ ] `test_aggregation.py` passes with updated block creation and new metadata assembly
- [ ] No reference to `summarize_group` remains in `aggregation.py` or its tests
