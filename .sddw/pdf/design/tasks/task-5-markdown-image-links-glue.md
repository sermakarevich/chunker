# Task 5: Markdown page-image links + glue

## Trace
- **FR-IDs:** FR-12
- **Depends on:** task-1, task-4

## Files
- `src/chunker/nodes/output.py` — modify (`MarkdownRenderer._write_chunk` links page images for pdf chunks)
- `justfile` — modify (add `run-pdf`; drop `pdftotext` from `run-fixture`)
- `README.md` — modify (PDF usage section)
- `tests/unit/test_output.py` — update (interface: chunk markdown gains an image section for pdf chunks)

## Architecture

Final polish so a human reading the rendered markdown can view the original page figures,
plus a `just` target that runs a PDF directly (no lossy `pdftotext` pre-pass). Only the
chunk renderer changes; block rendering, the index, and the JSON exporter are untouched.

### Components
- `MarkdownRenderer._write_chunk`: appends a "Source pages" section linking each page image
  when the chunk has `image_paths` — modified
- `justfile`: `run-pdf` target feeding a PDF straight to `chunker run` — modified

### Data Flow
```
MarkdownRenderer.render(state, output_dir)
  per chunk → _write_chunk(chunk, state, content_dir)
     existing: "# {filename}", parent link, chunk.context
     NEW (only if chunk.image_paths):
        "## Source pages"
        per image_path: "![Page N](<relpath from this .md to the PNG>)"
```

## Contracts

### Internal Interfaces
- `MarkdownRenderer._write_chunk(chunk, state, content_dir) -> None` (modified)
  - Post: when `chunk.image_paths` is non-empty, the written `.md` ends with a
    `## Source pages` section containing one markdown image embed per image, with paths
    computed **relative** to the chunk's markdown file location
    (`content/L0/<file>.md` → the PNG under `<output_dir>/pages/`) via `os.path.relpath`.
    When `image_paths` is empty (text chunks), the output is byte-for-byte unchanged.

## Data Models
No model changes. Reads `Chunk.image_paths` (added in Task 1).

## Design Decisions

### Relative image links via `os.path.relpath`
- **Chosen:** store absolute `image_paths` on the chunk (Task 1) and compute a relative link
  from the chunk's `.md` file to the PNG at render time.
- **Rationale:** relative links keep the rendered output directory portable/movable and render
  in common markdown viewers; the chunk markdown lives at `content/L{level}/` while images live
  at `<output_dir>/pages/`.
- **Rejected:** absolute `file://` links (not portable) and copying images next to each
  markdown file (duplicates megabytes per shared page).

### Embed vs link
- **Chosen:** markdown image embed `![Page N](relpath)` under a dedicated `## Source pages`
  heading, kept separate from the wiki-style `[[path|name]]` navigation links.
- **Rationale:** satisfies FR-12 ("a link or reference to the source page image(s)") and lets a
  viewer render the figure inline without disturbing the existing navigation link scheme.

### `run-pdf` drops `pdftotext`
- **Chosen:** add a `run-pdf` target that calls `chunker run <pdf> --model <vision> --output-dir <dir>`
  directly; update `run-fixture` to use it instead of the `pdftotext ... report.txt` flatten.
- **Rationale:** the lossy pre-pass that discarded every figure is exactly what this feature
  removes; the default model is a `vision`-capable one (e.g. `gemma4:latest`).

## Acceptance Criteria

### FR-12: Page-image links in markdown
- GIVEN a rendered chunk markdown file for a pdf-derived chunk (non-empty `image_paths`)
- WHEN a human opens it
- THEN it SHALL contain a link/reference to the chunk's source page image(s)
- GIVEN a chunk from a text document (empty `image_paths`)
- THEN its markdown SHALL contain no "Source pages" section (no-regression for the text path)

## Done Criteria
- [ ] `_write_chunk` adds a `## Source pages` section with one `![Page N](relpath)` per image
      for pdf chunks; relative paths resolve from the `.md` location to `<output_dir>/pages/`
- [ ] Text chunks render exactly as before (test asserts no "Source pages" section)
- [ ] `justfile` has a `run-pdf` target; `run-fixture` no longer calls `pdftotext`
- [ ] `README.md` documents PDF usage (`chunker run report.pdf --vision-model ...`, `--pdf-dpi`)
- [ ] `test_output.py` covers both a pdf chunk (image section present, links correct) and a text
      chunk (unchanged)
- [ ] `just test` and `just lint` are green
