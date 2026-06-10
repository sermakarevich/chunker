# Task 3: Page-window chunk extractor

## Trace
- **FR-IDs:** FR-04, FR-09, FR-10
- **Depends on:** task-1, task-2

## Files
- `src/chunker/nodes/page_chunking.py` — create (`PageChunkExtractor`, `PageWindow`)
- `src/chunker/nodes/__init__.py` — modify (export `PageChunkExtractor`)
- `tests/unit/test_page_chunking.py` — create

## Architecture

The page extractor is the pdf-mode sibling of the existing `ChunkExtractor`. It walks a
page cursor, grows a window of consecutive pages until it is chunk-sized, asks the
text-only completeness check where to split, and emits a `Chunk` whose boundaries fall on
page edges. The existing text `ChunkExtractor` is **not** touched.

### Components
- `PageWindow`: a growing window of consecutive `Page`s over `state.pages` — new
- `PageChunkExtractor`: produces the next page-bounded `Chunk` — new; mirrors the
  `extract_next(state) -> Chunk` contract of `ChunkExtractor`

### Data Flow
```
PageChunkExtractor.extract_next(state)
  window = PageWindow(state.pages, start_index=state.cursor_page, config)
  auto-grow window until token_count >= min_chunk_tokens (or no more pages)
  loop up to max_expansion_attempts:
     if token_count >= max_chunk_tokens OR page_count >= max_pages_per_chunk:
        force-split at current window end (log reason)             # FR-09
     result = LLMService.check_page_completeness(window.text)      # TEXT-only (Task 2)
     if result.complete:
        if split_after_page within window: window.set_end_to_page(split_after_page)
        break
     else: if not window.expand(): force-split (cannot_expand); break
  else: force-split (max_attempts)
  → Chunk(source_span=(0,0), page_span=(start_page,end_page),
          image_paths=window.image_paths, original_text=window.text, forced_split=...)
  state.cursor_page = <index after end_page>
```

## Contracts

### Internal Interfaces
- `PageChunkExtractor.__init__(llm_service: LLMService, config: ChunkerConfig)` — mirrors `ChunkExtractor`.
- `PageChunkExtractor.extract_next(state: PipelineState) -> Chunk`
  - Pre: `state.pages is not None` and `state.has_more_pages` is True.
  - Post: returns a new `Chunk` whose `page_span` and `image_paths` cover one or more
    whole pages starting at `state.cursor_page`; increments `state.chunk_counter`; advances
    `state.cursor_page` to the index after the chunk's last page. Never splits mid-page.
- `PageWindow(pages: list[Page], start_index: int, config: ChunkerConfig)` with:
  - `text -> str`: page texts concatenated with a delimiter per page
    (e.g. `\n\n--- Page {number} ---\n` then `page.text`) so empty-text pages are still represented.
  - `token_count -> int`: `estimate_tokens(self.text, token_factor)` (same factor source as `CursorWindow`).
  - `page_count -> int`, `image_paths -> list[str]`, `start_page -> int` (1-based), `end_page -> int` (1-based).
  - `expand() -> bool`: include the next page; returns False if at the last page.
  - `set_end_to_page(page_number: int) -> None`: clamp the window end to that 1-based page
    (no-op if out of `[start_page, end_page]`).

## Data Models
No new persisted models. Builds the `Chunk` extended in Task 1:
- `source_span = (0, 0)` (char span unused in pdf mode)
- `page_span = (start_page, end_page)` — 1-based inclusive
- `image_paths = [p.image_path for p in window pages]`
- `original_text = window.text`
- `context/summary/filename = ""` (filled by the rewriter in Task 4)
- `forced_split` set when any cap triggers; `metadata = {}`

## Design Decisions

### D1 — Page-granular boundaries (no verbatim phrase matching)
- **Chosen:** the window ends at a page edge chosen by `PageCompletenessResult.split_after_page`.
- **Rationale:** page boundaries are discrete and unambiguous; no `str.find()`, no
  retry-with-snippet, no fuzzy fallback — the most failure-prone path of the text extractor
  is absent here.
- **Trade-off:** cannot split mid-page. With `min_chunk_tokens=2000` a chunk is typically
  2–4 dense pages, so page granularity is acceptable.
- **Rejected:** mapping a returned phrase back to a char offset within a page — reintroduces
  the fragility being removed.

### D5 — Separate extractor; text path untouched
- **Chosen:** add `PageChunkExtractor` alongside `ChunkExtractor`; the pipeline selects by mode (Task 4).
- **Rationale:** routing text through a page chunker would regress fine-grained semantic
  splitting that text files benefit from; honors the no-regression guarantee (FR-08).

### Force-split and oversized-page handling (FR-09 / FR-10)
- **Chosen:** force-split at the current page edge when any of: `token_count >= max_chunk_tokens`,
  `page_count >= max_pages_per_chunk`, or `max_expansion_attempts` exhausted, or the window
  cannot expand (end of document). Each event is logged as structured JSON
  (`{"event": "forced_split", "chunk_id": ..., "reason": "max_tokens|max_pages|max_attempts|cannot_expand"}`),
  matching `nodes/chunking.py`.
- **Oversized single page:** if a single page alone exceeds `max_chunk_tokens`, accept it as
  a one-page forced chunk (the window cannot shrink below one page) and log a warning
  (`{"event": "oversized_page", ...}`).
- **Empty/low-text pages:** `token_count` simply reflects the (possibly empty) text, so the
  window grows until the `max_pages_per_chunk` cap force-splits — no crash. The empty page is
  still included in a chunk and its image is carried in `image_paths` (FR-10).

## Acceptance Criteria

### FR-04: Page-edge chunk boundaries
- GIVEN a multi-page window where completeness returns `complete=True, split_after_page=K`
- WHEN the extractor resolves the boundary
- THEN the chunk SHALL end at page K (`page_span[1] == K`) and the cursor SHALL advance past K
- GIVEN a candidate chunk below `min_chunk_tokens` at a page edge whose next page continues the topic
- WHEN evaluated (completeness `complete=False`)
- THEN the window SHALL extend to include further pages
- CONSTRAINT: no produced chunk SHALL begin or end in the middle of a page

### FR-09: Safety limits and force-split
- GIVEN a run of pages whose window never satisfies completeness
- WHEN `max_pages_per_chunk` is reached
- THEN the extractor SHALL force-split at that page edge, set `forced_split=True`, and log the event
- GIVEN a single page exceeding `max_chunk_tokens`
- WHEN processed
- THEN it SHALL be accepted as an oversized one-page chunk and a warning SHALL be logged

### FR-10: Pages with little or no text
- GIVEN a page whose extractable text is empty
- WHEN processed
- THEN the extractor SHALL NOT crash, the page SHALL be included in a chunk, and its image
  path SHALL appear in the chunk's `image_paths`

## Done Criteria
- [ ] `PageChunkExtractor.extract_next` returns a `Chunk` with correct `page_span`/`image_paths`
      and advances `state.cursor_page` with no mid-page boundary
- [ ] `PageWindow` grows by whole pages, reports `token_count`/`page_count`, and clamps via `set_end_to_page`
- [ ] Force-split fires for `max_tokens`, `max_pages`, `max_attempts`, and `cannot_expand`, each logged
- [ ] Oversized single page accepted + warning logged; empty-text page included with its image path
- [ ] `test_page_chunking.py` (mocked `LLMService`) covers: window growth to `min_chunk_tokens`,
      page-edge split via `split_after_page`, each force-split reason, oversized page, empty-text page
- [ ] `PageChunkExtractor` is exported from `nodes/__init__.py`
- [ ] `just test` and `just lint` are green
