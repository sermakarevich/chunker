# Task 3: Implement text splitting strategies and cursor management

## Trace
- **FR-IDs:** FR-01, FR-18
- **Depends on:** task-1

## Files
- `src/chunker/splitter.py` — create
- `tests/unit/test_splitter.py` — create

## Architecture

### Components
- `TextSplitter`: produces split units (sentences, paragraphs, words) from source text — new
- `CursorWindow`: manages the current candidate window with expansion — new

### Data Flow
`source_text` + `cursor_position` → `TextSplitter.split_from(cursor)` → list of unit boundaries
`CursorWindow.expand()` → advances end boundary by one unit → returns updated window text

## Contracts

### TextSplitter
```python
class TextSplitter:
    def __init__(self, strategy: str): ...

    def split_from(self, text: str, start: int) -> list[int]
```
Returns a sorted list of character positions where split boundaries occur, starting from `start`. For "sentences", these are positions after sentence-ending punctuation. For "paragraphs", positions after double newlines. For "words", positions after whitespace.

### CursorWindow
```python
class CursorWindow:
    def __init__(self, source_text: str, cursor: int, splitter: TextSplitter, config: ChunkerConfig): ...

    @property
    def text(self) -> str
    @property
    def start(self) -> int
    @property
    def end(self) -> int
    @property
    def token_count(self) -> int

    def expand(self) -> bool
    def set_end(self, position: int) -> None
    def last_sentence_boundary(self) -> int
```

- `expand()`: advances end to next split boundary. Returns `False` if no more text.
- `set_end(position)`: sets end to a specific character position (used after boundary validation).
- `last_sentence_boundary()`: returns the last sentence-ending position within the current window (for force-split fallback).
- `token_count`: uses `estimate_tokens(window_text, token_factor)` from config.
- Initial window: expand until `min_chunk_tokens` is reached.

## Design Decisions

### Sentence detection: regex
- **Chosen:** `re.compile(r'(?<=[.!?])\s+(?=[A-Z])')` for sentence boundaries
- **Rationale:** Handles 95%+ of academic paper text. Zero dependencies. Edge cases (abbreviations like "Dr.", "U.S.") are rare in the primary input domain (AI papers).
- **Rejected:** nltk `sent_tokenize` — heavyweight dependency for marginal improvement

### Split strategy as enum
- **Chosen:** String literal ("sentences", "paragraphs", "words") validated at init
- **Rationale:** Simple, matches config field type. No need for enum ceremony with 3 values.
- **Rejected:** Enum class — more boilerplate, same result

## Acceptance Criteria

### FR-01: Cursor-driven splitting
- GIVEN a document and "sentences" split strategy
- WHEN the system starts processing
- THEN it SHALL produce a candidate window starting at cursor position 0 containing at least `min_chunk_tokens` worth of text, expanded one sentence at a time

- GIVEN a confirmed chunk ending at char position 412
- WHEN the next candidate is requested
- THEN the cursor SHALL start at position 412 and the new window SHALL begin from that exact position

- GIVEN the same document processed with "paragraphs" vs "sentences" strategy
- WHEN processing begins
- THEN the expansion unit SHALL match the configured strategy

### FR-18: Source span tracking
- GIVEN a window with `start` and `end` positions
- WHEN extracting `source_text[start:end]`
- THEN the result SHALL exactly match `window.text` character for character

## Done Criteria
- [ ] `TextSplitter` with "sentences", "paragraphs", "words" strategies
- [ ] Sentence regex correctly splits academic paper text
- [ ] `CursorWindow` with expand, set_end, last_sentence_boundary
- [ ] Window initializes to `min_chunk_tokens` via repeated expansion
- [ ] `token_count` property uses `estimate_tokens` with model's `token_factor`
- [ ] Source span tracking: `source_text[start:end] == window.text` always holds
- [ ] Expansion returns `False` at end of text
- [ ] Tests using `agentic_rag_excerpt.txt` fixture for realistic splitting
- [ ] All tests pass
