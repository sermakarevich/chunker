# Task 4 Completion: Pipeline + CLI integration

## Summary
Wired pdf mode into the existing orchestration. `Pipeline._process` is now
mode-agnostic (loops on `state.has_more_input`, dispatches the page vs text
extractor per iteration on `state.pages`); a new `Pipeline.run_document` builds
text or page state and resumes from an existing checkpoint, with `run()` kept as
a back-compat wrapper. The rewriter threads `chunk.image_paths` into
`rewrite_chunk`, and the CLI routes `.pdf` via `load_document`, exposes
`--pdf-dpi`/`--vision-model` (run) and `--model`/`--vision-model` (resume), and
promotes the vision model to the effective model before the Pipeline is built.
The text path is unchanged (FR-08 holds by construction).

## Commits
- `f7f882a` feat(pdf): wire pdf mode through pipeline and CLI (FR-01, FR-06, FR-07, FR-08, FR-10, FR-11)

## Deviations
- **Rule 3: Blocking** — the three `rewrite_side_effect` mocks in
  `test_pipeline_e2e.py` had signature `(chunk_text, context_text, *, chunk_id)`
  and broke once `ChunkRewriter` began passing `image_paths=`. Updated all three
  to accept `image_paths=None` (the interface change the task file pre-flagged
  under Files). Same for the new e2e PDF mock.
- **Rule 3: Blocking** — `TestRunCommand` asserted `pipeline.run(...)`; switched
  the three CLI tests to `run_document` and assert on the `LoadedDocument`
  passed, matching the new entry point.
- Added a small `_log_progress` helper alongside the spec-named `_progress_pct`
  to keep the per-chunk completion log mode-aware (text → position, pdf → page).
  Implementation detail, not a spec change.

## Difficulties
- Vision-model resolution on `resume`: mode is only known after the checkpoint
  loads, but `Pipeline.__init__` builds `ChatOllama` from `config.model` first.
  Resolved by promoting `--vision-model` to `config.model` unconditionally when
  supplied on resume (the user explicitly opts in for a PDF resume), mirroring
  the run-path promotion. Consistent with the task's stated intent.

## Notes
- PDF e2e is deterministic and Ollama-free: a synthetic 4-page PDF is rendered by
  the real `load_document`, while `check_page_completeness` and `rewrite_chunk`
  are mocked (`min_chunk_tokens=3` makes one page == one chunk). Real PNGs are
  written under `output_dir/pages` but never read (rewrite is mocked).
- The page-image path is threaded end-to-end but not yet surfaced in the rendered
  markdown — that is Task 5 (FR-12), the last remaining task. `output.py`
  (JsonExporter/MarkdownRenderer) was intentionally left untouched here.
- `_progress_pct` returns 100.0 for a zero-length text body or empty page list,
  so the completion log never divides by zero.
