# Verification Report: chunker

## Summary
- **Date:** 2026-04-14
- **FRs:** 18/18 passed, 0 failed, 0 partial
- **Tests:** 217 passed, 0 failed, 0 skipped
- **Lint:** clean (ruff check + ruff format)
- **Real pipeline run:** 61 chunks, 21 blocks, 10 roots — full coverage on agentic_rag_full.txt (115,471 chars), gemma4:latest
- **Result:** PASS

## Test Execution
- **Runner:** pytest (via `just test`)
- **Command:** `uv run pytest -v`
- **Duration:** 0.31s

### Failures
- None — all 217 tests pass (216 original + 1 new test for checkpoint path fix)

## Lint Execution
- **Runner:** ruff (via `just lint`)
- **Command:** `uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/`
- **Issues found:** 1 formatting issue in `src/chunker/nodes/output.py` (list comprehension style)
- **Resolution:** Auto-fixed with `ruff format`

## Real Pipeline Run
- **Input:** `tests/fixtures/agentic_rag_full.txt` (15,075 words, 115,471 chars)
- **Model:** gemma4:latest (Ollama, local)
- **Output dir:** `.sddw/agentic_rag`
- **Result:** 61 chunks, 21 blocks, 10 roots
- **Source span coverage:** [0, 115471] — full, no gaps, all 61 spans verified against source text (0 mismatches)
- **Forced splits:** chunk-019, chunk-061
- **Orphan chunks:** 7 (chunk-055 through chunk-061) — all linked in index.md "Ungrouped Chunks"
- **Full traversal:** all 61 chunks and 21 blocks reachable from index.md
- **Output files:** hierarchy.json (298KB), index.md, 61 chunk .md files, 21 block .md files
- **Observed behaviors:**
  - Cursor-driven chunking producing 61 chunks
  - LLM completeness checking with expansion on incomplete
  - Boundary phrase validation with retry
  - Force splits when max_expansion_attempts exhausted
  - Dual-trigger aggregation producing L0 and L1 blocks
  - Non-contiguous grouping correctly rejected and re-prompted (FR-17 validated)
  - Grouping fallback to even-split after two hard validation failures (FR-07 validated)
  - Structured logging of every LLM call
  - Checkpointing after each chunk
  - Output wiring (JSON + Markdown) confirmed in `Pipeline._write_output()`

## FR Verification

### FR-01: Cursor-driven splitting — PASS

**Acceptance Criteria:**
- [x] Happy path: window at cursor 0, min_chunk_tokens expansion — covered by `test_initial_expansion_to_min_tokens`
- [x] Continuation from confirmed chunk end — covered by `test_continuation_from_nonzero_cursor`
- [x] Strategy switch (sentences vs paragraphs) — covered by `test_sentence_split_simple`, `test_paragraph_split`

**Issues:** None

### FR-02: LLM completeness checking — PASS

**Acceptance Criteria:**
- [x] Complete boundary returns boundary_phrase — covered by `test_happy_path_complete_boundary`
- [x] Incomplete boundary triggers expansion — covered by `test_expand_on_incomplete`

**Issues:** None

### FR-03: Boundary phrase validation — PASS

**Acceptance Criteria:**
- [x] Phrase found verbatim — covered by `test_happy_path_complete_boundary`
- [x] Retry succeeds — covered by `test_retry_succeeds`
- [x] Retry fails, sentence fallback — covered by `test_boundary_retry_fails_sentence_fallback`

**Issues:** None

### FR-04: Chunk rewrite and summary — PASS

**Acceptance Criteria:**
- [x] Self-sufficiency: pronoun resolution — covered by `test_passes_context_from_builder`
- [x] Both original_text and rewritten_text stored, summary produced — covered by `test_populates_rewritten_text`, `test_populates_summary`, `test_preserves_original_text`

**Issues:** None

### FR-05: Force-split — PASS

**Acceptance Criteria:**
- [x] Max tokens → force-split — covered by `test_force_split_max_tokens`
- [x] Max attempts → force-split — covered by `test_force_split_max_attempts`

**Issues:** None

### FR-06: Dual-trigger aggregation — PASS

**Acceptance Criteria:**
- [x] Token trigger — covered by `test_token_threshold_triggers`
- [x] Count trigger — covered by `test_count_threshold_triggers`
- [x] Below both → no aggregation — covered by `test_no_aggregation_below_both_thresholds`

**Issues:** None

### FR-07: Group size constraints — PASS

**Acceptance Criteria:**
- [x] Min violation → reject and re-prompt — covered by `test_hard_violation_reprompts`
- [x] Max hint → re-prompt, accept if declined — covered by `test_soft_violation_reprompts_then_accepts`
- [x] Fallback after 2 hard failures — covered by `test_even_split_fallback_after_two_hard_failures`
- [x] Real pipeline: grouping_fallback triggered and logged — confirmed in live run

**Issues:** None

### FR-08: Recursive aggregation — PASS

**Acceptance Criteria:**
- [x] Recursion continues to next level — covered by `test_recursive_aggregation_through_levels`
- [x] Recursion terminates below thresholds — covered by `test_recursion_stops_below_thresholds`
- [x] Single root terminates — covered by `test_recursion_stops_single_block`

**Issues:** None

### FR-09: Context injection — PASS

**Acceptance Criteria:**
- [x] Immediate predecessor priority — covered by `test_predecessor_is_first_item`
- [x] Higher-level summaries — covered by `test_level_summaries_after_predecessor`
- [x] Budget enforcement, no partial insertion — covered by `test_item_exceeding_budget_skipped`, `test_skip_and_try_next`
- [x] Early processing, no error — covered by `test_empty_state_returns_empty`

**Issues:** None

### FR-10: JSON output — PASS

**Acceptance Criteria:**
- [x] Structure with all fields — covered by `test_top_level_keys`, `test_chunk_fields`, `test_block_fields`
- [x] Bidirectional links consistent — covered by `test_bidirectional_links`
- [x] Pipeline calls JsonExporter — covered by `test_full_pipeline_writes_json_output`, `test_run_creates_json_output`

**Issues:** None (remediation task-10 resolved this)

### FR-11: Linked markdown rendering — PASS

**Acceptance Criteria:**
- [x] One file per node — covered by `test_one_file_per_chunk`, `test_one_file_per_block`
- [x] Wiki-links to children and parent — covered by `test_child_links`, `test_parent_link`
- [x] Root index links to top-level blocks — covered by `test_links_to_root_blocks`
- [x] Full traversal reaches every leaf chunk — covered by `test_all_chunks_reachable_hierarchy`, `test_all_chunks_reachable_mixed`
- [x] Orphan chunks included in index — covered by `test_mixed_index_links_orphan_chunk`, `test_mixed_index_has_ungrouped_section`
- [x] Pipeline calls MarkdownRenderer — covered by `test_full_pipeline_writes_markdown_files`, `test_run_creates_markdown_index`

**Issues:** None (remediation tasks 10 and 11 resolved these)

### FR-12: Provider-agnostic LLMClient — PASS

**Acceptance Criteria:**
- [x] Protocol adherence (single class) — covered by `LLMService` design
- [x] Ollama default — covered by `test_init_creates_all_components`
- [x] Structured output with retries — covered by `test_retries_on_invalid_response`, `test_raises_after_max_retries`

**Issues:** None

### FR-13: Checkpointing — PASS

**Acceptance Criteria:**
- [x] After each chunk — covered by `test_run_calls_sweep_after_adding_chunk`
- [x] Resumability — covered by `test_resume_loads_checkpoint_and_continues`
- [x] After each block — covered (sweep + checkpoint in same loop iteration)

**Issues:** None

### FR-14: Model-dependent configuration — PASS

**Acceptance Criteria:**
- [x] Profile loading for known model — covered by `test_from_model_applies_profile`
- [x] Extensibility — covered by `test_from_model_unknown_uses_defaults`

**Issues:** None

### FR-15: Structured logging — PASS

**Acceptance Criteria:**
- [x] Every LLM call logged — covered by `test_logs_successful_call`, confirmed in real pipeline run (JSON log entries for every LLM call)

**Issues:** None

### FR-16: No fuzzy matching — PASS

**Acceptance Criteria:**
- [x] Verbatim only, no fuzzy — covered by `test_exact_match_required`

**Issues:** None

### FR-17: Contiguous groups only — PASS

**Acceptance Criteria:**
- [x] Non-contiguous rejected — covered by `test_non_contiguous_groups_hard_violation`
- [x] Real pipeline: non-contiguous grouping `[[0,1,2],[4,5,6],[3,7,8]]` rejected, re-prompted to `[[0,1,2],[3,4,5,6],[7,8]]` — confirmed

**Issues:** None

### FR-18: Source span tracking — PASS

**Acceptance Criteria:**
- [x] source_text[start:end] == original_text — covered by `test_source_span_invariant`

**Issues:** None

## Deviations
- Task 8: `PipelineState.create()` used instead of `initial()` — resolved, no impact
- Task 8: No `add_chunk()` method, chunks added directly — resolved, no impact
- Task 8: Package needed editable install for CLI — resolved, no impact

## Remediation Tasks
None — all checks passed.

## Bug Fix Applied During Verification
- **Checkpoint location bug:** `run_command` in `cli.py` did not set `checkpoint_path` inside `output_dir` when `--output-dir` was provided. Fixed by adding `checkpoint_path = str(Path(args.output_dir) / "checkpoint.json")` to `config_kwargs`. New test `test_run_places_checkpoint_in_output_dir` added.
- **Formatting:** `src/chunker/nodes/output.py` reformatted (list comprehension style).

## Warnings
- **Timing collection:** No timing metrics are collected during pipeline runs. For a 15K-word document, the pipeline takes significant time due to sequential LLM calls. Adding timing per-chunk and per-phase would help identify bottlenecks.
- **Stale output directory:** `./output/` exists from a previous run (not from `just run-fixture`). Consider adding `output/` to `.gitignore` or using the output_dir consistently.
- **Checkpoint in CWD for old runs:** Pipeline runs started before the checkpoint fix still write `checkpoint.json` to CWD. The fix only applies to new runs using `--output-dir`.
