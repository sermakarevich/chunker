# Task 11 Completion: Fix markdown index to include orphaned chunks in traversal

## Summary
Modified `_write_index()` to collect orphan chunks (those with `parent_block_id is None`) and list them in a separate "Ungrouped Chunks" section when blocks exist, ensuring all chunks are reachable from `index.md`.

## Commits
- `5f64395` test(chunker): add failing tests for orphan chunk traversal (FR-11)
- `3db1d80` feat(chunker): include orphan chunks in markdown index (FR-11)

## Deviations
None

## Difficulties
None
