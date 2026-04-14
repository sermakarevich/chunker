# Task 8 Completion: Implement pipeline orchestration and CLI entry point

## Summary
Created `Pipeline` class orchestrating ChunkExtractor, ChunkRewriter, AggregationSweeper, and Checkpointer in a main processing loop, plus `ProcessingResult` dataclass. Implemented CLI with `run` and `resume` subcommands using argparse, with model profile support.

## Commits
- `29aa7c6` test(chunker): add failing tests for pipeline orchestration and CLI (FR-01, FR-06, FR-08, FR-12, FR-13, FR-14)
- `af26da3` feat(chunker): implement pipeline orchestration and CLI entry point (FR-01, FR-06, FR-08, FR-12, FR-13, FR-14)

## Deviations
- **Rule 3: Blocking** — `PipelineState` uses `create()` factory method, not `initial()` as task spec stated. Used `create()` to match existing codebase.
- **Rule 3: Blocking** — `PipelineState` has no `add_chunk()` method. Added chunks directly to `state.chunks[chunk.id]` and `state.pending_summaries.setdefault(0, []).append(chunk.id)`, matching the pattern used by other components.
- **Rule 3: Blocking** — Package not installed in editable mode; `uv pip install -e .` was needed for `chunker` CLI entry point to work.

## Difficulties
- Integration test required careful calibration of mock LLM responses to match real CursorWindow sentence-splitting behavior (6 sentences produced 4 chunks, not 3 as initially assumed).

## Notes
- Justfile `run` target already existed and works correctly with the new CLI.
- `ProcessingResult.from_state()` identifies root blocks as those with `parent_block_id is None`.
