# Task 5: Update JSON exporter and markdown renderer

## Trace
- **FR-IDs:** FR-09, FR-10, FR-11, FR-12, FR-13, FR-15
- **Depends on:** task-1

## Files
- `src/chunker/nodes/output.py` — modify
- `tests/unit/test_output.py` — update (interface change)

## Architecture

### Components
- `JsonExporter`: exports hierarchy as JSON — modified
- `MarkdownRenderer`: renders linked markdown files — modified

### Data Flow
**JSON:** `PipelineState` → `JsonExporter.export()` → dict with `context`/`summary`/`filename` fields → `JsonExporter.write()` → `hierarchy.json`

**Markdown:** `PipelineState` → `MarkdownRenderer.render()` → resolves filenames (with dedup) → writes chunk `.md` files (title + parent link + context) → writes block `.md` files (title + parent link + context + child links with summary labels) → writes `index.md`

## Contracts

### Internal Interfaces
- `JsonExporter.export(state) -> dict`: unchanged signature
  - Pre: state has chunks and blocks with `context`, `summary`, `filename`
  - Post: chunk entries have `context` (not `rewritten_text`), `summary`, `filename`; block entries have `context`, `summary`, `filename`
- `MarkdownRenderer.render(state, output_dir) -> None`: unchanged signature
  - Pre: state has chunks and blocks with `context`, `summary`, `filename`
  - Post: files named by `filename` field (not IDs), with numeric dedup for collisions
- `MarkdownRenderer._resolve_filename(slug: str) -> str`: **new** — deduplicates filenames
  - Pre: slug is the raw LLM-generated filename
  - Post: returns slug if unique, or `slug-N` if collision detected
- `MarkdownRenderer._write_chunk(chunk, chunks_dir) -> None`: modified
  - Pre: chunk has `context`, `summary`, `filename`
  - Post: writes `{filename}.md` with title + parent link + context body (no Summary/Original sections)
- `MarkdownRenderer._write_block(block, state, blocks_dir) -> None`: modified
  - Pre: block has `context`, `summary`, `filename`, state has children
  - Post: writes `{filename}.md` with title + parent link + context body + child wiki-links with summary labels

## Design Decisions

### Filename deduplication in MarkdownRenderer
- **Chosen:** Dedup at render time with numeric suffix (`-2`, `-3`)
- **Rationale:** Filenames are an output concern. Models store the raw LLM slug. Renderer tracks used names per render call and appends suffix on collision.
- **Rejected:** Dedup in PipelineState — mixes output concern into domain model

### Wiki-link format with summary labels
- **Chosen:** `[[path/filename|summary text]]` — path uses filename (no `.md` extension), label is the target's `summary`
- **Rationale:** FR-12 requires summary as link label. Existing convention uses wiki-links without `.md` extension. `filename` replaces ID in the path.
- **Rejected:** Using `context` as label — too long; using title — not specified

### Index file wiki-links
- **Chosen:** Index wiki-links also use `filename` paths with `summary` labels, consistent with block/chunk files
- **Rationale:** Consistency across all markdown output. Index links to root blocks and orphan chunks should match the same `[[path/filename|summary]]` pattern.

## Acceptance Criteria

### FR-09: Filename-based markdown files
- GIVEN a chunk with `filename="attention-mechanism-overview"`
- WHEN markdown is rendered
- THEN the file SHALL be `chunks/attention-mechanism-overview.md`

- GIVEN a block with `filename="transformer-architecture-deep-dive"`
- WHEN markdown is rendered
- THEN the file SHALL be `blocks/transformer-architecture-deep-dive.md`

- GIVEN two nodes produce the same `filename`
- THEN the system SHALL append a disambiguator (e.g., `-2`) to avoid collisions

### FR-10: Simplified chunk markdown
- GIVEN a chunk with `context`, `summary`, and parent block
- WHEN rendered to markdown
- THEN the file SHALL contain: title, parent wiki-link, and `context` body
- AND SHALL NOT contain a "Summary" section
- AND SHALL NOT contain an "Original" section

### FR-11: Simplified block markdown
- GIVEN a block with `context`, `summary`, children, and parent
- WHEN rendered to markdown
- THEN the file SHALL contain: title, parent wiki-link, `context` body, and child wiki-links
- AND SHALL NOT contain a separate "Summary" section

### FR-12: Wiki-links with summary labels
- GIVEN a block with child chunk `filename="attention-overview"` and `summary="Describes multi-head attention mechanism with scaled dot-product scoring."`
- WHEN child links are rendered
- THEN the link SHALL be `[[chunks/attention-overview|Describes multi-head attention mechanism with scaled dot-product scoring.]]`

### FR-13: JSON updated fields
- GIVEN a chunk exported to JSON
- THEN it SHALL contain `context` (not `rewritten_text`), `summary`, and `filename` fields

- GIVEN a block exported to JSON
- THEN it SHALL contain `context`, `summary`, and `filename` fields

### FR-15: No ID-based filenames
- GIVEN any markdown rendering
- THEN no file SHALL be named `chunk-001.md` or `block-L1-001.md`
- AND all files SHALL use the `filename` field value

## Done Criteria
- [ ] `JsonExporter.export()` outputs `context` (not `rewritten_text`), `summary`, `filename` for chunks
- [ ] `JsonExporter.export()` outputs `context`, `summary`, `filename` for blocks
- [ ] `MarkdownRenderer` writes chunk files as `{filename}.md` (not `{id}.md`)
- [ ] `MarkdownRenderer` writes block files as `{filename}.md` (not `{id}.md`)
- [ ] Chunk `.md` contains only: title, parent wiki-link, context body (no Summary/Original sections)
- [ ] Block `.md` contains only: title, parent wiki-link, context body, child wiki-links
- [ ] Wiki-links use `[[path/filename|summary text]]` format
- [ ] `_resolve_filename` deduplicates with numeric suffix (`-2`, `-3`)
- [ ] Index file uses `filename` paths with `summary` labels for root blocks and orphan chunks
- [ ] `test_output.py` passes with all updated rendering and export logic
- [ ] No file is named by node ID; all files use `filename` field value
- [ ] No reference to `rewritten_text` remains in `output.py` or its tests
