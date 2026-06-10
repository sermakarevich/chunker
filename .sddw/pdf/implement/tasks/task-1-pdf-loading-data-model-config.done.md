# Task 1 Completion: PDF loading, page data-model, and config foundation

## Summary
Added the data foundation for direct PDF ingestion: a `load_document` loader
that renders one PNG per page via PyMuPDF and extracts per-page text (or reads
text mode for `.txt`/`.md`), a `Page` domain model, `Chunk`/`PipelineState`
extensions for page spans and page cursors, and four new `ChunkerConfig` PDF
fields. No LLM or chunking logic was touched. Images are referenced by absolute
path only — never inlined into checkpoints.

## Commits
- `9b96f56` chore(pdf): add pymupdf dependency (FR-01, FR-03)
- `02ba2ca` feat(pdf): add PDF loading, Page model, and state/config foundation (FR-01, FR-02, FR-03, FR-07, FR-10, FR-11)
- `62afa97` chore: ruff-format pre-existing unformatted files

## Deviations
- **Rule 1: Bug (self-introduced)** — My first edit to `tests/unit/test_state.py`
  inserted the new `TestPipelineStatePdfMode` class *before* the original
  `test_json_roundtrip` / `test_json_roundtrip_with_chunks_and_blocks` methods,
  silently re-nesting them into the wrong class. Detected via a stray ERROR in
  the verbose run; fixed by moving the new class to the end of the file so the
  original methods stay in `TestPipelineState`.
- **Rule 3: Blocking** — `just test` was already red on pristine HEAD: the
  `agentic_rag_text` fixture loads `tests/fixtures/agentic_rag_excerpt.txt`,
  which had been removed from tracking in `36a05c7` while `conftest.py` and
  `test_splitter.py` still depend on it. The file is matched by the `*.txt`
  `.gitignore` rule, so it is intentionally a local-only test asset. Restored it
  verbatim from `36a05c7^` into the working tree (git correctly refused to track
  it); the suite now passes locally.
- **Rule 3: Blocking** — `just lint` was already red on pristine HEAD:
  `metrics.py`, `pipeline.py`, and `test_pipeline.py` were unformatted. Applied
  `ruff format` (no behavior change) in a separate `chore` commit (`62afa97`) to
  keep the feature commit clean.
- **Rule 1: Bug (cosmetic)** — `ruff format` wrapped my inline field comments on
  `Chunk.page_span`/`image_paths` awkwardly (default value on its own line); moved
  the comments above the fields for readability. Within my own new code.

## Difficulties
- The "missing" fixture initially looked like accidental content loss, but
  `git check-ignore` showed it is covered by the `*.txt` ignore rule and was
  removed via `git rm --cached` — i.e. a deliberately untracked, local-only test
  asset. Resolved by restoring to the working tree only and amending the repair
  commit message to state that the fixture is intentionally not tracked.

## Notes
- The real-fixture loader test (`TestLoadRealFixture`) loads the 42-page AI Index
  report at `pdf_dpi=72` to stay fast, and is `skipif`-guarded on the PDF's
  presence so the suite stays green on machines without the (gitignored) fixture.
  The bulk of deterministic assertions (ordering, PNG-per-page, empty-text
  tolerance, DPI scaling, error paths) run on small synthetic PDFs built in-test
  with PyMuPDF, matching the requirements' "deterministic logic" testing approach.
- Pre-existing fragility for the verify step: `test_splitter.py` and the
  `TestPipelineState.test_json_roundtrip` case hard-require the gitignored
  `agentic_rag_excerpt.txt` with no skip guard — they will error on a fresh clone
  until that local fixture is present.
- Mode discriminator is `pages is not None` (pdf) vs `None` (text); old
  checkpoints without the new keys deserialize to text mode via `.get()` defaults.
- `vision_model` defaults to `None` (Task 2/4 fall back to `config.model`); page
  PNGs render to `<output_dir>/pages/page-NNNN.png` as absolute paths.
