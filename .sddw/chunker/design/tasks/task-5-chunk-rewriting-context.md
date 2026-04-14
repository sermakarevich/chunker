# Task 5: Implement chunk rewriting and context injection

## Trace
- **FR-IDs:** FR-04, FR-09
- **Depends on:** task-1, task-2

## Files
- `src/chunker/context.py` — create
- `src/chunker/nodes/rewriting.py` — create
- `tests/unit/test_context.py` — create
- `tests/unit/test_rewriting.py` — create

## Architecture

### Components
- `ContextBuilder`: assembles context items for LLM calls following priority ordering and token budget — new
- `ChunkRewriter`: calls LLMService to produce self-sufficient rewritten text and summary — new

### Data Flow
```
PipelineState → ContextBuilder.build(state) → list[ContextItem] → format as text
  → LLMService.rewrite_chunk(chunk_text, context_text) → RewriteResult
  → Chunk.rewritten_text = result.rewritten_text
  → Chunk.summary = result.summary
```

## Contracts

### ContextItem
```python
@dataclass
class ContextItem:
    source: str
    text: str
    token_count: int
```
`source` identifies origin, e.g. "predecessor:chunk-003", "summary:L1:block-L1-002".

### ContextBuilder
```python
class ContextBuilder:
    def __init__(self, config: ChunkerConfig): ...

    def build(self, state: PipelineState) -> list[ContextItem]
    def format_context(self, items: list[ContextItem]) -> str
```

`build()` assembles items in priority order:
1. Same-level immediate predecessor (rewritten_text or summary of previous chunk)
2. Latest summary from each higher level, ascending (L1, L2, ... root)
3. Earlier same-level context walking backwards from predecessor

Budget enforcement: `context_budget_tokens` is a hard ceiling. Each item is included whole or skipped entirely (no partial insertion). If an item would exceed budget, skip it and try the next priority item.

Early processing: when no higher-level summaries exist yet, silently omit unavailable levels.

### ChunkRewriter
```python
class ChunkRewriter:
    def __init__(self, llm_service: LLMService, context_builder: ContextBuilder): ...

    def rewrite(self, chunk: Chunk, state: PipelineState) -> Chunk
```

Returns the chunk with `rewritten_text` and `summary` populated.

## Design Decisions

### Context budget: hard ceiling with skip-and-try-next
- **Chosen:** When the next priority item exceeds remaining budget, skip it entirely and try the next item in priority order. Continue until budget exhausted or all items tried.
- **Rationale:** FR-09 says "no partial insertion of items" but doesn't say stop at first skip. Trying lower-priority items that fit maximizes context utilization.
- **Rejected:** Stop at first budget violation — wastes budget when one large item blocks smaller useful items behind it.

### Context text formatting
- **Chosen:** Each context item formatted as a labeled block: `[Source: predecessor:chunk-003]\n{text}\n---`
- **Rationale:** Gives the LLM clear signal about what each context block represents. Separator prevents blending.

## Acceptance Criteria

### FR-04: Chunk rewrite and summary
- GIVEN a chunk containing pronouns referencing prior text ("they", "this approach")
- WHEN rewritten
- THEN the rewritten text SHALL resolve those references to explicit subjects

- GIVEN a confirmed chunk
- WHEN rewriting completes
- THEN both `original_text` (verbatim) and `rewritten_text` SHALL be stored
- AND a 1-3 sentence `summary` SHALL be produced

### FR-09: Context injection
- GIVEN a chunk being processed and a prior chunk exists
- WHEN context is assembled
- THEN the predecessor's rewritten_text or summary SHALL be the first item injected

- GIVEN L1 and L2 summary blocks exist
- WHEN context is assembled for a chunk
- THEN the latest summary from each level SHALL be included after the predecessor

- GIVEN `context_budget_tokens` is set
- WHEN the next candidate context item would exceed the budget
- THEN that item SHALL be skipped entirely (no partial insertion)
- AND the builder SHALL try the next priority item

- GIVEN no higher-level summaries exist yet (first chunks being processed)
- WHEN context is assembled
- THEN the builder SHALL silently omit unavailable levels without error

## Done Criteria
- [ ] `ContextBuilder.build()` returns items in correct priority order
- [ ] Priority 1: immediate predecessor (rewritten_text or summary)
- [ ] Priority 2: latest summary from each higher level, ascending
- [ ] Priority 3: earlier same-level context walking backwards
- [ ] Budget enforced as hard ceiling — no partial items, skip-and-try-next
- [ ] Early processing: omits unavailable levels without error
- [ ] `ChunkRewriter.rewrite()` populates `rewritten_text` and `summary`
- [ ] Unit tests: context ordering, budget enforcement, empty state, partial hierarchy
- [ ] Unit tests: rewrite with mock LLMService verifying pronoun resolution prompt
- [ ] All tests pass
