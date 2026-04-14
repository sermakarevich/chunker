# Task 9: Implement JSON export and linked markdown rendering

## Trace
- **FR-IDs:** FR-10, FR-11
- **Depends on:** task-1

## Files
- `src/chunker/nodes/output.py` — create
- `tests/unit/test_output.py` — create

## Architecture

### Components
- `JsonExporter`: produces the canonical JSON document from `PipelineState` — new
- `MarkdownRenderer`: produces a directory of linked markdown files from `PipelineState` — new

### Data Flow
```
PipelineState → JsonExporter.export(state) → dict → write to output_dir/hierarchy.json

PipelineState → MarkdownRenderer.render(state, output_dir)
  → for each Chunk: write output_dir/chunks/chunk-001.md
  → for each SummaryBlock: write output_dir/blocks/block-L1-001.md
  → write output_dir/index.md (root entry point)
```

## Contracts

### JsonExporter
```python
class JsonExporter:
    def export(self, state: PipelineState) -> dict
    def write(self, state: PipelineState, path: Path) -> None
```

Output schema:
```json
{
  "document_id": "...",
  "root_block_ids": ["block-L2-001"],
  "blocks": {
    "block-L1-001": {
      "id": "block-L1-001",
      "level": 1,
      "summary": "...",
      "child_ids": ["chunk-001", "chunk-002", "chunk-003"],
      "parent_block_id": "block-L2-001"
    }
  },
  "chunks": {
    "chunk-001": {
      "id": "chunk-001",
      "source_span": [0, 412],
      "original_text": "...",
      "rewritten_text": "...",
      "summary": "...",
      "parent_block_id": "block-L1-001",
      "forced_split": false
    }
  }
}
```

### MarkdownRenderer
```python
class MarkdownRenderer:
    def render(self, state: PipelineState, output_dir: Path) -> None
```

**Chunk file** (`chunks/chunk-001.md`):
```markdown
# Chunk 001

**Parent:** [[blocks/block-L1-001]]

## Summary
{summary}

## Content
{rewritten_text}

## Original
{original_text}
```

**Block file** (`blocks/block-L1-001.md`):
```markdown
# Summary Block L1-001

**Parent:** [[blocks/block-L2-001]]

## Summary
{summary}

## Children
- [[chunks/chunk-001]]
- [[chunks/chunk-002]]
- [[chunks/chunk-003]]
```

**Root index** (`index.md`):
```markdown
# {document_id}

## Top-Level Summaries
- [[blocks/block-L2-001]]
```

Wiki-links use `[[relative/path]]` format (Obsidian-compatible).

## Design Decisions

### Link style: Obsidian wiki-links
- **Chosen:** `[[path/to/file]]` without `.md` extension
- **Rationale:** FR-11 specifies "wiki-style links." Obsidian convention omits extensions. Matches the user story about knowledge base exploration.
- **Rejected:** Standard markdown links `[text](path.md)` — less clean for Obsidian use case

### Directory structure: chunks/ and blocks/ subdirectories
- **Chosen:** Separate `chunks/` and `blocks/` directories within the output directory
- **Rationale:** Clear separation of node types. Prevents name collisions. Easy to browse.
- **Rejected:** Flat directory — gets unwieldy with many files; nested by level — over-complicated

### Flat output when no aggregation
- **Chosen:** When no SummaryBlocks exist (thresholds never exceeded), the index links directly to chunk files
- **Rationale:** FR-06 acceptance criteria states "the output SHALL be a flat list of chunks with no SummaryBlock layer." Output rendering must handle this gracefully.

## Acceptance Criteria

### FR-10: JSON output
- GIVEN processing completes
- WHEN JSON is exported
- THEN it SHALL contain `document_id`, `root_block_ids`, `blocks` dict, and `chunks` dict with all specified fields

- GIVEN any chunk or block in the output
- WHEN traversing `parent_block_id` upward and `child_ids` downward
- THEN the links SHALL be consistent (parent's child_ids includes the node, node's parent_block_id matches the parent)

### FR-11: Linked markdown rendering
- GIVEN a completed hierarchy
- WHEN markdown is rendered
- THEN each Chunk and SummaryBlock SHALL produce its own `.md` file

- GIVEN a SummaryBlock with 3 children
- WHEN its markdown is rendered
- THEN it SHALL contain links to all 3 child files
- AND a link to its parent (if any)

- GIVEN the rendering completes
- THEN a root/index file SHALL exist linking to top-level SummaryBlocks

- GIVEN a reader starting at the root file
- WHEN following child links recursively
- THEN it SHALL be possible to reach every leaf chunk in the hierarchy

## Done Criteria
- [ ] `JsonExporter.export()` produces correct schema with all fields
- [ ] Bidirectional link consistency: parent→child and child→parent match
- [ ] `JsonExporter.write()` writes to file
- [ ] `MarkdownRenderer.render()` creates `chunks/`, `blocks/`, and `index.md`
- [ ] Each chunk gets its own `.md` file with parent link, summary, content, original
- [ ] Each block gets its own `.md` file with parent link, summary, children links
- [ ] Index file links to root blocks (or directly to chunks if no blocks)
- [ ] Wiki-links use `[[path]]` format without `.md` extension
- [ ] Flat output works: no blocks → index links to chunks directly
- [ ] Full traversal test: start at index, follow all links, reach every chunk
- [ ] Unit tests with hand-built state: hierarchy, flat, single-root, multi-root
- [ ] All tests pass
