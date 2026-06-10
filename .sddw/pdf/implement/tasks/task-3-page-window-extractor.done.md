# Task 3 Completion: Page-window chunk extractor

## Summary
Added `PageChunkExtractor` and `PageWindow` (`src/chunker/nodes/page_chunking.py`),
the pdf-mode siblings of `ChunkExtractor`/`CursorWindow`. The window grows by whole
pages to `min_chunk_tokens`, the text-only `check_page_completeness` call (Task 2)
selects the page-edge split via `split_after_page`, and every produced chunk boundary
falls on a page edge — no mid-page splits, no phrase matching. `PageChunkExtractor`
is exported from `nodes/__init__.py`.

## Commits
- `3a29225` feat(pdf): add page-window chunk extractor (FR-04, FR-09, FR-10)

## Deviations
- **Rule 3: Blocking (contract alignment)** — The task spec (line 54) gave
  `\n\n--- Page {number} ---\n` as the per-page delimiter, but only as an example
  ("e.g."). The authoritative cross-task contract is the Task-2 prompt template
  `src/chunker/llm/prompt_templates/page_completeness.txt`, which instructs the model
  that "Each page begins with a marker line of the form `=== Page N ===`" and returns
  `split_after_page` keyed off that marker. `PageWindow.text` was implemented to emit
  `=== Page N ===` so the extractor and the completeness prompt interoperate. Without
  this, `split_after_page` resolution would be unreliable.
- **Rule 2: Missing Critical** — `extract_next` raises `ValueError` when
  `state.pages is None` (precondition guard) rather than failing later with an opaque
  `TypeError`. Not in the spec, but cheap and clarifying.

## Difficulties
- The first draft of `test_text_has_page_markers` used `min_chunk_tokens=10`, so the
  window stopped at one page (54 tokens ≥ 10) and the page-2 marker was absent. Fixed
  the test data (`min_chunk_tokens=100`) so the window grows to two pages; the
  implementation was correct.
- `ruff format` reformatted the new test file (multi-line `PageWindow(...)` calls);
  applied `ruff format` to bring it in line.

## Notes
- **Force-split vs. oversized-page:** the chunk's `forced_split` flag is set to `True`
  for the oversized single-page case as well, since the chunk breached
  `max_chunk_tokens`. The requirement only mandates "accept + warn"; the distinct
  `{"event": "oversized_page", ...}` warning (separate from the `forced_split`/reason
  events) is the signal that the page could not be shrunk. The four `forced_split`
  reasons (`max_tokens`, `max_pages`, `max_attempts`, `cannot_expand`) remain as
  specified.
- **Auto-grow location:** the grow-to-`min_chunk_tokens` loop lives in
  `PageWindow.__init__` (mirroring `CursorWindow`), not in `extract_next`. Behavior is
  identical to the task's data-flow pseudocode; the structure follows the existing
  text-path sibling.
- **Cursor advance:** `state.cursor_page = start_index + window.page_count`, which
  correctly reflects a window that was clamped back by `set_end_to_page` — clamped-away
  pages are reprocessed by the next `extract_next`.
- For Task 4: `extract_next` sets `source_span=(0, 0)` and leaves
  `context/summary/filename` empty; the rewriter fills these and passes
  `chunk.image_paths` to `rewrite_chunk(..., image_paths=...)`.

## Done Criteria
- [x] `extract_next` returns a `Chunk` with correct `page_span`/`image_paths`, advances
      `state.cursor_page`, no mid-page boundary
- [x] `PageWindow` grows by whole pages, reports `token_count`/`page_count`, clamps via
      `set_end_to_page`
- [x] Force-split fires for `max_tokens`, `max_pages`, `max_attempts`, `cannot_expand`,
      each logged
- [x] Oversized single page accepted + warning logged; empty-text page included with
      its image path
- [x] `test_page_chunking.py` (mocked `LLMService`) covers window growth, page-edge
      split, every force-split reason, oversized page, empty-text page (26 tests)
- [x] `PageChunkExtractor` exported from `nodes/__init__.py`
- [x] `just test` (303 passed) and `just lint` green
