# Verification Report: chunker

## Summary
- **Date:** 2026-04-14
- **FRs:** 16/18 passed, 2 failed, 0 partial
- **Tests:** 206 passed, 0 failed, 0 skipped
- **Lint:** clean (8 unused imports + 21 format issues auto-fixed)
- **Real pipeline run:** 19 chunks, 5 blocks, full text coverage on agentic_rag_excerpt.txt with gemma4:latest
- **Result:** FAIL

## Test Execution
- **Runner:** pytest (via `just test`)
- **Command:** `uv run pytest`
- **Duration:** 0.27s

### Failures
- None — all 206 tests pass

## Lint Execution
- **Runner:** ruff (via `just lint`)
- **Command:** `uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/`
- **Issues found:** 8 F401 (unused imports) in src + tests, 21 files needing reformat
- **Resolution:** Auto-fixed with `ruff check --fix` and `ruff format`

## Real Pipeline Run
- **Input:** `tests/fixtures/agentic_rag_excerpt.txt` (1,676 words, 12,271 chars)
- **Model:** gemma4:latest (Ollama, local)
- **Result:** 19 chunks, 5 L0 blocks, 5 roots
- **Source span coverage:** [0, 12271] — full, no gaps, all 19 spans verified
- **Forced splits:** chunk-001 (max_attempts)
- **Phrase not found:** chunk-019 (fell back to sentence boundary)
- **Grouping fallback:** 1 instance at level 0
- **Orphan chunks:** chunk-019 (no parent_block_id — arrived after final aggregation)
- **Output files produced:** None — exporters not wired into pipeline

## FR Verification

### FR-01: Cursor-driven splitting — PASS

**Acceptance Criteria:**
- [x] Happy path: window at cursor 0, min_chunk_tokens expansion — covered by `test_initial_expansion_to_min_tokens`
- [x] Continuation from confirmed chunk end — covered by `test_continuation_from_nonzero_cursor`
- [x] Strategy switch (sentences vs paragraphs) — covered by `test_sentence_split_simple`, `test_paragraph_split`

**Done Criteria** (from task-3):
- [x] TextSplitter with 3 strategies
- [x] CursorWindow with expand, set_end, last_sentence_boundary
- [x] Source span tracking holds

**Issues:**
- None

### FR-02: LLM completeness checking — PASS

**Acceptance Criteria:**
- [x] Complete boundary returns boundary_phrase — covered by `test_happy_path_complete_boundary`
- [x] Incomplete boundary triggers expansion — covered by `test_expand_on_incomplete`

**Done Criteria** (from task-4):
- [x] Completeness check loops until complete or max attempts
- [x] State cursor updated after extraction

**Issues:**
- None

### FR-03: Boundary phrase validation — PASS

**Acceptance Criteria:**
- [x] Phrase found verbatim — covered by `test_happy_path_complete_boundary`
- [x] Retry succeeds — covered by `test_boundary_retry_succeeds`
- [x] Retry fails, sentence fallback — covered by `test_boundary_retry_fails_sentence_fallback`

**Done Criteria** (from task-4):
- [x] Boundary validated with str.find()
- [x] One retry with verbatim prompt
- [x] Sentence-boundary fallback, logs WARN: phrase_not_found

**Issues:**
- None

### FR-04: Chunk rewrite and summary — PASS

**Acceptance Criteria:**
- [x] Self-sufficiency: pronoun resolution — covered by `test_passes_context_from_builder`
- [x] Both original_text and rewritten_text stored, summary produced — covered by `test_populates_rewritten_text`, `test_populates_summary`, `test_preserves_original_text`

**Done Criteria** (from task-5):
- [x] ChunkRewriter.rewrite() populates rewritten_text and summary
- [x] Original text preserved

**Issues:**
- None

### FR-05: Force-split — PASS

**Acceptance Criteria:**
- [x] Max tokens → force-split — covered by `test_force_split_at_max_tokens`
- [x] Max attempts → force-split — covered by `test_force_split_at_max_attempts`

**Done Criteria** (from task-4):
- [x] Force-split marks forced_split: true
- [x] Logs WARN: forced_split

**Issues:**
- None

### FR-06: Dual-trigger aggregation — PASS

**Acceptance Criteria:**
- [x] Token trigger — covered by `test_token_threshold_triggers_aggregation`
- [x] Count trigger — covered by `test_count_threshold_triggers_aggregation`
- [x] Below both → no aggregation — covered by `test_below_both_thresholds_no_aggregation`

**Done Criteria** (from task-6):
- [x] Token and count threshold triggers work
- [x] No aggregation when below both

**Issues:**
- None

### FR-07: Group size constraints — PASS

**Acceptance Criteria:**
- [x] Min violation → reject and re-prompt — covered by `test_min_group_size_hard_rejection`
- [x] Max hint → re-prompt, accept if declined — covered by `test_max_group_size_soft_hint`
- [x] Fallback after 2 hard failures — covered by `test_even_split_fallback_after_hard_failures`

**Done Criteria** (from task-6):
- [x] GroupValidator rejects min violations, flags max violations
- [x] Even-split fallback, logs WARN: grouping_fallback

**Issues:**
- None

### FR-08: Recursive aggregation — PASS

**Acceptance Criteria:**
- [x] Recursion continues to next level — covered by `test_recursive_aggregation_multiple_levels`
- [x] Recursion terminates below thresholds — covered by `test_recursion_stops_below_thresholds`
- [x] Single root terminates — covered by `test_single_block_is_root`

**Done Criteria** (from task-6):
- [x] Bottom-up sweep checks all levels
- [x] Recursive aggregation terminates correctly

**Issues:**
- None

### FR-09: Context injection — PASS

**Acceptance Criteria:**
- [x] Immediate predecessor priority — covered by `test_predecessor_first_priority`
- [x] Higher-level summaries — covered by `test_higher_level_summaries_included`
- [x] Budget enforcement, no partial insertion — covered by `test_budget_hard_ceiling`, `test_skip_and_try_next`
- [x] Early processing, no error — covered by `test_empty_state_no_context`

**Done Criteria** (from task-5):
- [x] Priority order correct
- [x] Budget enforced with skip-and-try-next
- [x] Early processing omits unavailable levels

**Issues:**
- None

### FR-10: JSON output — FAIL

**Acceptance Criteria:**
- [x] Structure with all fields — covered by `test_top_level_keys`, `test_chunk_fields`, `test_block_fields`
- [x] Bidirectional links consistent — covered by `test_bidirectional_links`

**Done Criteria** (from task-9):
- [x] JsonExporter.export() produces correct schema
- [x] Bidirectional links validated
- [x] JsonExporter.write() writes to file
- [ ] **Pipeline/CLI calls JsonExporter** — NOT WIRED

**Issues:**
- `JsonExporter` exists and works correctly in unit tests, but `Pipeline._process()` and `cli.py` never import or call it. Real pipeline run produces no `hierarchy.json`.

### FR-11: Linked markdown rendering — FAIL

**Acceptance Criteria:**
- [x] One file per node — covered by `test_one_file_per_chunk`, `test_one_file_per_block`
- [x] Wiki-links to children and parent — covered by `test_child_links`, `test_parent_link`
- [x] Root index links to top-level blocks — covered by `test_index_links_to_root_blocks`
- [ ] **Full traversal reaches every leaf chunk** — FAILS for orphan chunks in mixed state

**Done Criteria** (from task-9):
- [x] MarkdownRenderer.render() creates chunks/, blocks/, index.md
- [x] Wiki-links format correct
- [x] Flat output works
- [ ] **Pipeline/CLI calls MarkdownRenderer** — NOT WIRED
- [ ] **Index links orphan chunks when blocks exist** — NOT HANDLED

**Issues:**
- `MarkdownRenderer` exists and works in unit tests, but `Pipeline._process()` and `cli.py` never import or call it. Real pipeline run produces no markdown files.
- `_write_index()` only links to root blocks OR all chunks. When blocks exist but some chunks are orphaned (chunk-019 in real run), those chunks are unreachable from the index, violating the full traversal criterion.

### FR-12: Provider-agnostic LLMClient — PASS

**Acceptance Criteria:**
- [x] Protocol adherence (single class) — covered by `LLMService` design
- [x] Ollama default — covered by `test_init_creates_all_components`
- [x] Structured output with retries — covered by `test_retry_on_invalid_json`, `test_retry_exhaustion`

**Issues:**
- None

### FR-13: Checkpointing — PASS

**Acceptance Criteria:**
- [x] After each chunk — covered by `test_run_calls_sweep_after_adding_chunk` (checkpoint in loop)
- [x] Resumability — covered by `test_resume_loads_checkpoint_and_continues`
- [x] After each block — covered (sweep + checkpoint in same loop iteration)

**Issues:**
- None

### FR-14: Model-dependent configuration — PASS

**Acceptance Criteria:**
- [x] Profile loading for known model — covered by `test_from_model_known`
- [x] Extensibility — covered by `test_from_model_unknown`

**Issues:**
- None

### FR-15: Structured logging — PASS

**Acceptance Criteria:**
- [x] Every LLM call logged — covered by `test_structured_log_emitted`

**Issues:**
- None. Real run confirmed: JSON log entries for every check_completeness, rewrite_chunk, group_summaries, summarize_group call.

### FR-16: No fuzzy matching — PASS

**Acceptance Criteria:**
- [x] Verbatim only, no fuzzy — covered by `test_boundary_uses_str_find`

**Issues:**
- None

### FR-17: Contiguous groups only — PASS

**Acceptance Criteria:**
- [x] Non-contiguous rejected — covered by `test_non_contiguous_rejected`

**Issues:**
- None

### FR-18: Source span tracking — PASS

**Acceptance Criteria:**
- [x] source_text[start:end] == original_text — covered by `test_source_span_invariant`

**Issues:**
- None. Real run: all 19 spans verified against source text.

## Deviations
- Task 8: `PipelineState.create()` used instead of `initial()` — resolved, no impact
- Task 8: No `add_chunk()` method, chunks added directly — resolved, no impact
- Task 8: Package needed editable install for CLI — resolved, no impact

## Remediation Tasks
- task-10-fix-wire-output-exporters.md — wire JsonExporter and MarkdownRenderer into Pipeline._process() and CLI (FR-10, FR-11)
  - **Severity:** FAIL
  - **Origin:** design — task-8 (pipeline orchestration) did not include output generation in the main loop; task-9 (output rendering) implemented components without integration
  - **Evidence:** Real pipeline run produces no output files; `Pipeline._process()` and `cli.py` have no imports of JsonExporter or MarkdownRenderer
- task-11-fix-orphan-chunk-traversal.md — fix _write_index to include orphaned chunks when blocks exist (FR-11)
  - **Severity:** FAIL
  - **Origin:** design — task-9 handled flat and hierarchy cases but not the mixed case where some chunks have no parent after partial aggregation
  - **Evidence:** Real run: chunk-019 has parent_block_id=None while blocks exist; _write_index only links root blocks, making orphan chunks unreachable

## Warnings
- Lint: 8 unused imports and 21 formatting issues found and auto-fixed. These were cosmetic but indicate the implementation step did not run lint before completion.
