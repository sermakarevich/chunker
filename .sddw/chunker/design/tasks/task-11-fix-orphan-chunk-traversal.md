# Task 11: Fix markdown index to include orphaned chunks in traversal

## Trace
- **FR-IDs:** FR-11
- **Depends on:** task-9

## Files
- `src/chunker/nodes/output.py` — modify
- `tests/unit/test_output.py` — modify

## Architecture

### Components
- `MarkdownRenderer._write_index()`: must also link chunks that have no `parent_block_id` when blocks exist — modified

### Data Flow
```
state.chunks → filter chunks where parent_block_id is None → add to index links
Index links = root_block_ids + orphan_chunk_ids
```

## Contracts

### MarkdownRenderer._write_index()
Current behavior: if blocks exist, link only to root blocks. If no blocks, link to all chunks.

Required behavior: always link to root blocks AND any chunks with `parent_block_id is None`.

```python
def _write_index(self, state: PipelineState, output_dir: Path) -> None:
    root_block_ids = [
        bid for bid, block in state.blocks.items() if block.parent_block_id is None
    ]
    orphan_chunk_ids = [
        cid for cid, chunk in state.chunks.items() if chunk.parent_block_id is None
    ]
    # Link to both root blocks and orphan chunks
```

## Design Decisions

### Mixed index: blocks + orphan chunks
- **Chosen:** Index lists root blocks first, then orphan chunks in a separate section
- **Rationale:** FR-11 requires "it SHALL be possible to reach every leaf chunk." Orphan chunks (those arriving after the last aggregation sweep) must be reachable from the index. A separate "Ungrouped Chunks" section makes the mixed case clear.
- **Rejected:** Force a final aggregation sweep — this would change pipeline behavior, not just rendering

## Acceptance Criteria

### FR-11: Full traversal
- GIVEN a hierarchy with blocks AND orphan chunks (chunks with no parent_block_id)
- WHEN following child links recursively from index.md
- THEN it SHALL be possible to reach every chunk including orphans

## Done Criteria
- [ ] `_write_index()` includes orphan chunks when blocks exist
- [ ] Orphan chunks listed in a distinct section (e.g., "## Ungrouped Chunks")
- [ ] New test fixture: mixed state with blocks + 1 orphan chunk
- [ ] Traversal test verifies orphan chunk is reachable from index
- [ ] Existing traversal tests still pass
- [ ] All tests pass
