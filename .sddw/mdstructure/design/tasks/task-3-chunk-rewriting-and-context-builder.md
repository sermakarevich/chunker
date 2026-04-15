# Task 3: Update chunk rewriting node and context builder

## Trace
- **FR-IDs:** FR-05
- **Depends on:** task-2

## Files
- `src/chunker/nodes/rewriting.py` — modify
- `src/chunker/context.py` — modify
- `tests/unit/test_rewriting.py` — update (interface change)
- `tests/unit/test_context.py` — update (interface change)

## Architecture

### Components
- `ChunkRewriter`: applies LLM rewrite to extracted chunks — modified
- `ContextBuilder`: assembles context window for chunk rewriting — modified

### Data Flow
`ContextBuilder.build(state)` → context items (uses `chunk.context` instead of `chunk.rewritten_text`) → `ContextBuilder.format_context()` → context string → `ChunkRewriter.rewrite(chunk, state)` → `LLMService.rewrite_chunk()` → `RewriteResult` → sets `chunk.context`, `chunk.summary`, `chunk.filename`

## Contracts

### Internal Interfaces
- `ChunkRewriter.rewrite(chunk: Chunk, state: PipelineState) -> Chunk`: unchanged signature
  - Pre: chunk has `original_text`, state has prior chunks/blocks
  - Post: chunk has `context`, `summary`, `filename` set from LLM result
- `ContextBuilder._predecessor(state) -> ContextItem | None`: uses `chunk.context` for predecessor text
  - Pre: state has at least one chunk
  - Post: returns context item with predecessor's `context` field (falls back to `summary` then `original_text`)
- `ContextBuilder._earlier_chunks(state) -> list[ContextItem]`: uses `chunk.context` for earlier chunk text
  - Pre: state has at least 2 chunks
  - Post: returns context items with each chunk's `context` field (falls back to `summary` then `original_text`)

## Acceptance Criteria

### FR-05: Chunk rewrite integration
- GIVEN a chunk with `original_text` and a state with prior context
- WHEN `ChunkRewriter.rewrite(chunk, state)` is called
- THEN chunk SHALL have `context` set (not `rewritten_text`)
- AND chunk SHALL have `filename` set from LLM result
- AND chunk SHALL have `summary` set from LLM result

### Context builder field references
- GIVEN a state with chunks that have `context` fields
- WHEN `ContextBuilder.build(state)` is called
- THEN predecessor item text SHALL come from `chunk.context`
- AND earlier chunk items SHALL come from `chunk.context`

## Done Criteria
- [ ] `ChunkRewriter.rewrite()` sets `chunk.context` and `chunk.filename` from `RewriteResult`
- [ ] No reference to `rewritten_text` in `rewriting.py`
- [ ] `ContextBuilder._predecessor()` reads `chunk.context` instead of `chunk.rewritten_text`
- [ ] `ContextBuilder._earlier_chunks()` reads `chunk.context` instead of `chunk.rewritten_text`
- [ ] `test_rewriting.py` passes with updated field assertions
- [ ] `test_context.py` passes with chunks using `context` field
- [ ] No reference to `rewritten_text` remains in `context.py`, `rewriting.py`, or their tests
