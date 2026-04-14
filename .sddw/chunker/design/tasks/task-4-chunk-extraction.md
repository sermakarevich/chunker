# Task 4: Implement chunk extraction with boundary detection and validation

## Trace
- **FR-IDs:** FR-02, FR-03, FR-05, FR-16, FR-18
- **Depends on:** task-2, task-3

## Files
- `src/chunker/nodes/__init__.py` — create
- `src/chunker/nodes/chunking.py` — create
- `tests/unit/test_chunking.py` — create

## Architecture

### Components
- `ChunkExtractor`: orchestrates the chunk extraction loop — completeness checking, boundary validation, force-split — new

### Data Flow
```
CursorWindow → LLMService.check_completeness() → CompletenessResult
  → (complete) → validate boundary_phrase in source_text
    → (found) → set window end at phrase position → build Chunk
    → (not found) → retry LLM with verbatim instruction
      → (found) → set window end → build Chunk
      → (not found) → last_sentence_boundary() → build Chunk + log WARN
  → (incomplete) → expand window
    → (max_tokens reached) → force_split at last_sentence_boundary → build Chunk + log WARN
    → (max_attempts exhausted) → force_split → build Chunk + log WARN
    → (can expand) → check_completeness again [loop]
```

### Components
- `ChunkExtractor`: manages the expand → check → validate → finalize loop — new
- Uses `CursorWindow` from task-3
- Uses `LLMService.check_completeness()` from task-2

## Contracts

### ChunkExtractor
```python
class ChunkExtractor:
    def __init__(self, llm_service: LLMService, config: ChunkerConfig): ...

    def extract_next(self, state: PipelineState) -> Chunk
```

`extract_next()`:
1. Creates `CursorWindow` from `state.cursor_position`
2. Expands to `min_chunk_tokens`
3. Calls `check_completeness` in a loop (max `max_expansion_attempts`)
4. On `complete: true`: validates `boundary_phrase` verbatim in `source_text[window.end:]`
5. On validation failure: retries LLM once with explicit verbatim instruction
6. On second failure: falls back to `last_sentence_boundary()`
7. On `complete: false` after max attempts or max tokens: force-splits
8. Returns `Chunk` with `source_span`, `original_text`, `forced_split` flag
9. Updates `state.cursor_position` to chunk end

### Boundary Validation
```python
def validate_boundary_phrase(phrase: str, remaining_text: str) -> int | None
```
Returns the character index where `phrase` starts in `remaining_text`, or `None` if not found. Uses `str.find()` — verbatim match only (FR-16).

## Design Decisions

### Boundary validation: str.find() only
- **Chosen:** `remaining_text.find(boundary_phrase)` — exact substring match
- **Rationale:** FR-16 prohibits fuzzy/approximate matching. `str.find()` is the simplest verbatim match.
- **Rejected:** regex matching, difflib, fuzzy search — all violate FR-16

### Retry prompt for boundary phrase
- **Chosen:** On first boundary validation failure, re-prompt the LLM with the explicit instruction: "Return a phrase that appears EXACTLY and VERBATIM in the following text." Include a snippet of the text around the expected boundary area.
- **Rationale:** FR-03 allows one retry. Making the verbatim requirement explicit improves success rate.

## Acceptance Criteria

### FR-02: LLM completeness checking
- GIVEN a candidate window ending at a topic transition
- WHEN the LLM checks completeness
- THEN it SHALL return `complete: true` with a `boundary_phrase`

- GIVEN a candidate window ending mid-thought
- WHEN the LLM checks completeness
- THEN it SHALL return `complete: false`
- AND the system SHALL expand the window by one split unit and re-check

### FR-03: Boundary phrase validation
- GIVEN the LLM returns a `boundary_phrase`
- WHEN the phrase is searched in the remaining text
- THEN it SHALL match verbatim as a substring

- GIVEN a `boundary_phrase` not found verbatim
- WHEN the LLM is re-prompted with explicit verbatim instruction
- THEN if the retry phrase matches, that position SHALL be used

- GIVEN both attempts fail to produce a matching phrase
- THEN the system SHALL split at the last sentence boundary
- AND log `WARN: phrase_not_found`

### FR-05: Force-split
- GIVEN expansion reaches `max_chunk_tokens`
- THEN the system SHALL force-split at the last sentence boundary
- AND mark `forced_split: true`
- AND log `WARN: forced_split`

- GIVEN `max_expansion_attempts` completeness checks all return `complete: false`
- THEN the same force-split behaviour SHALL apply

### FR-16: No fuzzy matching
- GIVEN a boundary phrase that does not match verbatim
- THEN the system SHALL NOT attempt approximate, fuzzy, or similarity-based matching

### FR-18: Source span tracking
- GIVEN a chunk with `source_span: (start, end)`
- WHEN extracting `source_text[start:end]`
- THEN the result SHALL exactly match `original_text` character for character

## Done Criteria
- [ ] `ChunkExtractor.extract_next()` produces a `Chunk` with correct source span
- [ ] Completeness check loops until complete or max attempts
- [ ] Boundary phrase validated with `str.find()` — no fuzzy matching
- [ ] One retry on boundary mismatch with explicit verbatim prompt
- [ ] Sentence-boundary fallback after retry failure, logs `WARN: phrase_not_found`
- [ ] Force-split at max_tokens, marks `forced_split: true`, logs `WARN: forced_split`
- [ ] Force-split at max_attempts exhaustion
- [ ] `source_text[span.start:span.end] == chunk.original_text` for every chunk
- [ ] State cursor_position updated after extraction
- [ ] Unit tests with mock LLMService covering: happy path, retry success, retry failure + fallback, force-split (tokens), force-split (attempts)
- [ ] All tests pass
