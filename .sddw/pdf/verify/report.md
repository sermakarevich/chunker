# Verification Report: pdf

## Summary
- **Date:** 2026-06-09
- **FRs:** 12/12 passed, 0 failed, 0 partial
- **Tests:** 322 passed, 0 failed, 0 skipped
- **Result:** PASS (with warnings — one packaging defect was found and fixed inline during verification; fix is uncommitted)

## Test Execution
- **Runner:** pytest (via `just test` → `uv run pytest`; `pythonpath=src`)
- **Command:** `uv run pytest -q`
- **Duration:** ~1.76s
- **Lint:** `ruff check` + `ruff format --check` on `src/ tests/` — green (41 files formatted)
- **Live vision run (`just run-fixture`):** NOT executed this session (user chose `just test only`). FR-05 visual-capture substance relies on the documented task-2 manual smoke test.

### Failures
- None.

## FR Verification

### FR-01: Direct PDF input — PASS (fixed during verify)
**Acceptance Criteria:**
- [x] Happy: readable PDF processed directly, no `pdftotext` step — `TestLoadPdf::*`, `TestRunCommand::test_run_routes_pdf_and_resolves_vision_model`, `TestLoadRealFixture::test_loads_real_multipage_pdf`; `justfile` `run-pdf` feeds the PDF straight to `chunker run`.
- [x] Failure: missing/corrupt PDF → clear error, no partial output — `test_missing_pdf_raises_file_not_found`, `test_corrupt_pdf_raises_value_error` (loader raises before the pipeline runs).

**Issues:**
- **Found & fixed during verify:** the shipped `chunker` console script could not launch. `pyproject.toml` had no `[build-system]`, so `uv` installed only the dependencies into `.venv` and never built the `[project.scripts]` entry point — there was no `.venv/bin/chunker`. `uv run chunker` fell back to a stale conda install (`/home/sergii/miniconda3/bin/chunker`) whose Python lacks `pymupdf` (added for this feature in `9b96f56`), producing `Failed to spawn: chunker` / `ModuleNotFoundError: No module named 'pymupdf'`. The internal pipeline is fully tested (passes), but no test exercised the installed entry point, so the suite did not catch this. **Fix applied (uncommitted):** added a `hatchling` build backend + `[tool.hatch.build.targets.wheel] packages = ["src/chunker"]`. Validated: `uv run chunker --help` → exit 0, `.venv/bin/chunker` now present, 322 tests still pass, lint green.

### FR-02: Page splitting and ordering — PASS
**Acceptance Criteria:**
- [x] Happy: one unit per page, document order — `test_returns_pages_in_document_order`, e2e `test_pdf_run_produces_same_outputs_as_text` (4 pages → 4 chunks).
- [x] Edge: single-page PDF → ≥1 chunk — `test_single_page_pdf`, `test_single_page_document_produces_one_chunk`.

**Issues:** None.

### FR-03: Page rendering — PASS
**Acceptance Criteria:**
- [x] Happy: image per page, available to rewrite step — `test_writes_png_per_page`, `TestPage::test_serializes_path_not_bytes`, e2e asserts `seen_images[0][0].endswith("page-0001.png")`.

**Issues:** None.

### FR-04: Page-edge chunk boundaries — PASS
**Acceptance Criteria:**
- [x] Happy: chunk ends at the page-K edge — `test_page_edge_split_via_split_after_page`.
- [x] Boundary: below-min chunk at a page edge whose next page continues → extend — `test_extends_window_when_incomplete_then_complete`, `test_grows_until_min_chunk_tokens`.
- [x] Constraint: never begins/ends mid-page — page-granular by construction (`PageWindow` grows/clamps by whole pages; `=== Page N ===` markers); `test_set_end_to_page_clamps_window`.

**Issues:** None.

### FR-05: Visual data preserved in context — PASS (with warning)
**Acceptance Criteria:**
- [x] Plumbing: page images become multimodal rewrite input — `TestRewriteChunkVision::*` (one `image_url` part per image, jpg→jpeg MIME, text-only when no images), `test_rewriting.py::test_pdf_chunk_passes_its_image_paths`.
- [~] Happy (table/chart capture) & Contrast (vs `pdftotext`): NOT covered by automated tests — inherently requires a live vision model. Demonstrated once via the documented task-2 manual smoke test (`gemma4:latest` captured chart data-labels Canada=1/France=1/Hong Kong=1/Singapore=1/UK=0 absent from the 416-word text layer).

**Issues:**
- No automated regression guard for actual visual capture; the live `just run-fixture` contrast check was not re-run this session (user choice). Classification confirmed as PASS-with-warning by the user. See Warnings.

### FR-06: Same outputs as text — PASS
**Acceptance Criteria:**
- [x] Happy: JSON hierarchy + index + level-organized markdown, same structure as text — e2e `test_pdf_run_produces_same_outputs_as_text` asserts `hierarchy.json`, `index.md`, `content/L0` (4 files), and ≥1 higher-level file.

**Issues:** None (see Warning re: JSON exporter not surfacing page provenance).

### FR-07: Checkpoint and resume — PASS
**Acceptance Criteria:**
- [x] Happy: resume continues from chunk N+1 without reprocessing — e2e `test_pdf_resume_continues_from_checkpoint` (retains first 2 chunks, `cursor_page == len(pages)`, only pages 3–4 re-extracted), `TestPipelinePdfMode::test_run_document_resumes_existing_checkpoint`, `TestPdfCheckpointRoundtrip::*`.
- [x] Failure: resume against a different document → identity-mismatch error — `Checkpointer.load(expected_document_id=...)` raises `ValueError` (`checkpoint.py:28`), called on resume at `pipeline.py:81`; covered by `test_load_raises_on_document_id_mismatch`. `document_id = Path(path).stem` (`loaders.py:37`) is distinct per PDF, so the check is reachable for PDFs.

**Issues:** None blocking (see Warning re: mismatch test runs in text mode only).

### FR-08: No regression to the text path — PASS
**Acceptance Criteria:**
- [x] Happy: existing `.txt`/`.md` output equivalent to pre-feature; no PDF path for text input — full suite green; `test_output.py::test_text_chunk_bytes_unchanged` (byte-for-byte markdown), `test_state.py::test_text_mode_has_no_pages`, `test_rewriting.py::test_text_chunk_passes_empty_image_paths`, `test_models.py::test_page_fields_default_to_text_mode`, `test_from_dict_migrates_old_checkpoint_without_pdf_keys`. Mode dispatch is on `state.pages` (None ⇒ text).

**Issues:** None within the supported `uv`/`just` workflow (see Warning re: unconditional `import pymupdf` affecting stale non-uv installs).

### FR-09: Safety limits and force-split — PASS
**Acceptance Criteria:**
- [x] Happy (caps): force-split at page edge, mark forced, log event — `test_force_split_max_pages`, `test_force_split_max_tokens_multi_page`, `test_force_split_max_attempts`, `test_force_split_cannot_expand` (all four reasons logged).
- [x] Edge (oversized page): accept oversized single-page chunk + warn — `test_oversized_single_page` (distinct `oversized_page` log event).

**Issues:** None.

### FR-10: Pages with little or no text — PASS
**Acceptance Criteria:**
- [x] Happy: empty-text page does not crash, still included in a chunk, image passed to rewrite — `test_empty_text_page_tolerated` (loader), `test_empty_text_page_still_represented` (window), `test_empty_text_page_included_with_image` (extractor).

**Issues:** None.

### FR-11: Configurable resolution and model — PASS
**Acceptance Criteria:**
- [x] Happy: chosen DPI + chosen vision model used — `test_dpi_controls_render_resolution`, `test_from_model_passes_pdf_overrides`, parser flags (`test_run_with_pdf_dpi`, `test_run_with_vision_model`, `test_resume_with_model_and_vision_model`), `test_run_routes_pdf_and_resolves_vision_model`, `test_resume_promotes_vision_model`.
- [x] Edge (defaults): documented defaults when no options given — `test_pdf_defaults` (`pdf_dpi=150`, `vision_model=None` ⇒ falls back to `model`); documented in README.

**Issues:** None.

### FR-12: Page-image links in markdown — PASS
**Acceptance Criteria:**
- [x] Happy: rendered chunk markdown references source page image(s) — `TestChunkSourcePages::test_pdf_chunk_has_source_pages_section`, `test_pdf_chunk_image_links_relative_and_numbered`, `test_pdf_chunk_image_links_resolve_on_disk`, `test_source_pages_is_last_section`; text chunks unaffected (`test_text_chunk_has_no_source_pages_section`, `test_text_chunk_bytes_unchanged`).

**Issues:** None for the "human reader" scope (see Warning re: JSON exporter).

## Deviations
(from completion reports + this verification)
- **NEW (verify):** Missing build backend in `pyproject.toml` — the `chunker` console script was not installable, breaking the documented command interface. **Status: fixed inline (uncommitted)** by adding a `hatchling` build-system. No remediation task created (user choice). Action required: commit `pyproject.toml`.
- Task 1: gitignored fixture `tests/fixtures/agentic_rag_excerpt.txt` (matched by `*.txt`) is hard-required by `test_splitter.py` and `TestPipelineState.test_json_roundtrip` with no skip guard. **Status: unresolved (minor)** — present locally so the suite passed, but a fresh clone would error. Pre-existing, not introduced by this feature.
- Task 2: prompt template `page_completeness.txt` matched by `*.txt` ignore rule; force-added with `git add -f`. **Status: resolved.**
- Task 3: per-page delimiter aligned to the `=== Page N ===` contract in the Task-2 prompt (spec example used `--- Page N ---`). **Status: resolved** (cross-task contract alignment).
- Tasks 1/4: cosmetic ruff reflows and mock-signature updates for the `image_paths` interface change. **Status: resolved.**

## Remediation Tasks
None — all FRs pass; the one defect found was fixed inline during verification and the user opted not to create a tracked remediation task or regression test.

## Warnings
- **Build-system fix is uncommitted.** Commit `pyproject.toml` (the `[build-system]` + `[tool.hatch...]` block) to persist the entry-point fix; otherwise `chunker` / `just run*` will break again on a clean checkout.
- **Test blind spot:** no test invokes the installed `chunker` console script, so the broken entry point passed the full suite. A subprocess smoke test (`chunker --help` / a tiny end-to-end CLI run) would guard this — declined this session.
- **FR-05 has no automated guard** for actual visual capture (table values, chart figures, and the `pdftotext` contrast). It is verified only by the documented task-2 manual smoke test; re-run `just run-fixture` against a vision model after any prompt/model change to re-confirm. Your local `justfile` uses `gemma4:31b`; the vision-verified default is `gemma4:latest` — fall back to it if the image-rewrite step errors.
- **Stale conda entry point:** `/home/sergii/miniconda3/bin/chunker` exists but its env lacks `pymupdf`. Prefer `uv run chunker` / `just` (now uses `.venv`). If you want a working bare `chunker`, reinstall it in that env with `pymupdf` present, or remove the stale script.
- **Unconditional `import pymupdf`** at the top of `loaders.py` (imported by `cli.py` on every invocation) means any environment without `pymupdf` breaks the text command too, not just PDF. Within the `uv`/`just` workflow this is fine (pymupdf is in `.venv`).
- **FR-07 mismatch coverage** runs in text mode only (`test_load_raises_on_document_id_mismatch`); the mechanism is mode-agnostic and PDF state carries `document_id` (roundtrip-tested), so it is functionally covered — but there is no PDF-specific mismatch test.
- **JSON exporter gap (FR-06/FR-12):** `hierarchy.json` does not surface `page_span`/`image_paths`. FR-12 targets the human-readable markdown (satisfied), but programmatic consumers cannot see page provenance. Documented out-of-scope follow-up in the task-5 completion report.
