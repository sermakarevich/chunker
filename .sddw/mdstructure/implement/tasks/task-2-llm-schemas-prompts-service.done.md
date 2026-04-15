# Task 2 Completion: Update LLM schemas, prompts, and service

## Summary
Updated `RewriteResult` and replaced `BlockSummaryResult` with `BlockContextResult`, both now with `context`/`summary`/`filename` fields. Replaced `summarize.txt`/`summarize_prompt`/`summarize_group` with `synthesize.txt`/`synthesize_prompt`/`synthesize_block`. Added info-persistence directives to both content-producing prompt templates.

## Commits
- `d47c38d` test(mdstructure): add failing tests for LLM schema and service changes (FR-05, FR-06, FR-08, FR-14)
- `bd97cd7` feat(mdstructure): update LLM schemas, prompts, and service (FR-05, FR-06, FR-08, FR-14)
- `27a42c7` chore(mdstructure): remove orphaned summarize.txt template (FR-06)

## Deviations
- **Rule 3: Blocking** — `rewriting.py`: `result.rewritten_text` → `result.context`, added `chunk.filename = result.filename`
- **Rule 3: Blocking** — `aggregation.py`: `summarize_group(child_summaries)` → `synthesize_block(child_contexts, metadata_text, min_tokens, max_tokens)`, added `_get_context()` helper, mapped all 3 result fields to block
- **Rule 3: Blocking** — `test_rewriting.py`: updated `RewriteResult` fixture to use `context`/`filename`
- **Rule 3: Blocking** — `test_aggregation.py`: updated `_mock_llm` to mock `synthesize_block` returning `BlockContextResult`
- **Rule 3: Blocking** — `test_pipeline_e2e.py`: updated all 3 mock setups to use new schemas and method names

## Difficulties
None
