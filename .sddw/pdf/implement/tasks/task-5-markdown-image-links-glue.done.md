# Task 5 Completion: Markdown page-image links + glue

## Summary
`MarkdownRenderer._write_chunk` now appends a `## Source pages` section linking
each source page image (`![Page N](relpath)`) for pdf-derived chunks, with paths
computed relative to the chunk's `.md` location via `os.path.relpath`. Text chunks
render byte-for-byte unchanged. The `justfile` gained a `run-pdf` target and
`run-fixture` now feeds the PDF directly to `chunker run` (no `pdftotext`), and the
README documents PDF usage. This is the final task of the PDF feature.

## Commits
- `a56b4f6` feat(pdf): link source page images in chunk markdown (FR-12)

## Deviations
None. (No Rule 1-4 deviations — no bugs, missing-critical, blockers, or
architectural changes were encountered.)

## Difficulties
- `ruff format --check` flagged a multi-line `assert ... , (...)` in the new test
  class after the first pass — resolved by running `uv run ruff format` (cosmetic
  reflow only; tests unaffected).

## Notes
- **Page-number derivation:** the task spec says `![Page N](relpath)` without
  defining `N`. `N` is computed as `page_span[0] + offset` (the window's pages are
  contiguous and 1-based in document order, so `image_paths[i]` maps to page
  `start_page + i`). A defensive fallback of `start_page = 1` is used if `page_span`
  is `None` (not expected for pdf chunks, which always carry a span from
  `PageChunkExtractor`).
- **`run-pdf` delegates to `run`:** rather than duplicating the bash body, `run-pdf`
  calls the existing `run` recipe (`just run <pdf> <model> <output>`). The CLI uses
  the passed `--model` directly for a PDF when `--vision-model` is absent
  (`config.vision_model` defaults to `None`, so no model promotion overrides it),
  so `chunker run report.pdf --model gemma4:latest` is the effective invocation —
  exactly what the design decision specifies.
- **`run-fixture` default model changed** `gemma4:31b` → `gemma4:latest`, per the
  design decision that the fixture run use a vision-capable default now that the
  lossy `pdftotext` flatten is gone.
- **JsonExporter left untouched** per the task scope ("block rendering, the index,
  and the JSON exporter are untouched"). Note the JSON export does not currently
  surface `image_paths`/`page_span`; if programmatic consumers need them, that is a
  follow-up outside FR-12's "human reader" scope.
- **Verification:** `just test` → 322 passed (was 316; +6 new tests); `just lint`
  green. Live vision behavior on a real PDF can be exercised via `just run-fixture`
  (per the requirements' test-after approach) but was not run here as it needs a
  local Ollama vision model.
