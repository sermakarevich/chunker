# Task 1: PDF loading, page data-model, and config foundation

## Trace
- **FR-IDs:** FR-01, FR-02, FR-03, FR-07, FR-10, FR-11
- **Depends on:** none

## Files
- `src/chunker/loaders.py` — create (`LoadedDocument`, `load_document`, `_load_pdf`, `_load_text`)
- `src/chunker/models.py` — modify (add `Page`; extend `Chunk` with `page_span`, `image_paths`)
- `src/chunker/state.py` — modify (add `pages`, `cursor_page`, `has_more_pages`, `has_more_input`, `create_from_pages`; serialize pages)
- `src/chunker/config.py` — modify (add `pdf_dpi`, `vision_model`, `max_pages_per_chunk`, `image_format`)
- `pyproject.toml` — modify (add `pymupdf` dependency)
- `tests/unit/test_loaders.py` — create
- `tests/unit/test_models.py` — update (interface change: `Chunk` gains fields; new `Page`)
- `tests/unit/test_state.py` — update (interface change: `PipelineState` gains fields/properties)
- `tests/unit/test_config.py` — update (interface change: `ChunkerConfig` gains fields)
- `tests/unit/test_checkpoint.py` — update (interface change: state serialization grows; old-checkpoint load)

## Architecture

This task adds the data foundation so a PDF can be represented as an ordered list
of rendered pages and carried through the existing pipeline state, with images
referenced by path (never inlined). No LLM and no chunking logic is touched here.

### Components
- `Page`: a single PDF page — page number, extracted text, and the path to its
  rendered PNG — new (in `models.py`, beside `Chunk`/`SummaryBlock`)
- `LoadedDocument`: the result of loading an input file; carries either
  `source_text` (text mode) or `pages` (pdf mode) — new (in `loaders.py`)
- `load_document(path, config)`: dispatches on file type, returns a
  `LoadedDocument` — new
- `Chunk`: extended with `page_span` and `image_paths` (empty/`None` for text mode) — modified
- `PipelineState`: extended with `pages`, `cursor_page`, page-mode properties — modified
- `ChunkerConfig`: extended with PDF/vision settings — modified

### Data Flow
```
input.{pdf,txt,md}
  └─ load_document(path, config)
       ├─ .pdf  → PyMuPDF (fitz) opens doc
       │           per page: page.get_text()          → Page.text
       │           per page: render at config.pdf_dpi → PNG at
       │                      <output_dir>/pages/page-NNNN.png → Page.image_path
       │         → LoadedDocument(document_id, source_text=None, pages=[Page...])
       └─ else  → path.read_text()
                 → LoadedDocument(document_id, source_text=<text>, pages=None)
```
The pipeline (Task 4) turns a `LoadedDocument` into a `PipelineState` via
`PipelineState.create(...)` (text) or `PipelineState.create_from_pages(...)` (pdf).

## Contracts

### Internal Interfaces
- `load_document(path: str, config: ChunkerConfig) -> LoadedDocument`: load an input file.
  - Pre: `path` is a filesystem path string.
  - Post: returns a `LoadedDocument`. For `.pdf`, renders one PNG per page under
    `<config.output_dir>/pages/` and extracts per-page text (text may be empty).
    For any other suffix, reads the file as text (preserves today's behavior).
  - Errors: raises a clear, actionable error (e.g., `FileNotFoundError` with the
    path, or `ValueError` wrapping a PyMuPDF open failure for a corrupt/unsupported
    PDF). SHALL NOT return a partial `LoadedDocument`.
- `Page.to_dict() -> dict` / `Page.from_dict(data: dict) -> Page`: round-trip a page
  by **path** (never image bytes).
- `PipelineState.create_from_pages(document_id: str, pages: list[Page]) -> PipelineState`:
  build initial pdf-mode state (`source_text=""`, `cursor_position=0`, `pages=pages`,
  `cursor_page=0`).
  - Post: `state.has_more_pages is True` when `pages` is non-empty.
- `PipelineState.has_more_pages -> bool`: `pages is not None and cursor_page < len(pages)`.
- `PipelineState.has_more_input -> bool`: `has_more_text or has_more_pages` — the
  mode-agnostic loop condition used by the pipeline.

## Data Models

### `Page` (new, `models.py`)
```python
@dataclass
class Page:
    number: int        # 1-based page number, in document order
    text: str          # extracted text layer (may be "" for image-only pages)
    image_path: str    # absolute path to the rendered PNG on disk (NOT bytes)
```
With `to_dict`/`from_dict`/`to_json`/`from_json` following the existing manual-
serialization convention used by `Chunk`/`SummaryBlock`.

### `Chunk` (extended, `models.py`)
Add two trailing fields with defaults (so existing positional/keyword construction
and old checkpoints keep working):
```python
page_span: tuple[int, int] | None = None   # (start_page, end_page), 1-based inclusive; None in text mode
image_paths: list[str] = field(default_factory=list)  # page PNG paths; [] in text mode
```
- `to_dict`: add `"page_span": list(self.page_span) if self.page_span else None`,
  `"image_paths": self.image_paths`.
- `from_dict`: **migration-safe** — `page_span = tuple(data["page_span"]) if data.get("page_span") else None`,
  `image_paths = data.get("image_paths", [])`. (The current `from_dict` uses direct
  key access; new fields MUST use `.get()` so checkpoints written before this feature
  still load.)

### `PipelineState` (extended, `state.py`)
Add two trailing fields with defaults:
```python
pages: list[Page] | None = None   # present in pdf mode
cursor_page: int = 0              # 0-based index of the next unprocessed page
```
- `source_text`/`cursor_position`/`has_more_text` are retained unchanged for text mode.
- `create` (text) is unchanged.
- `to_dict`: add `"pages": [p.to_dict() for p in self.pages] if self.pages else None`,
  `"cursor_page": self.cursor_page`. (Stores text + image **paths** only — never bytes —
  keeping checkpoints lean per the prohibition.)
- `from_dict`: **migration-safe** —
  `pages = [Page.from_dict(p) for p in data["pages"]] if data.get("pages") else None`,
  `cursor_page = data.get("cursor_page", 0)`.

### `ChunkerConfig` (extended, `config.py`)
Add fields with defaults (FR-11 documented defaults):
```python
pdf_dpi: int = 150                 # page-render resolution
vision_model: str | None = None    # multimodal model for pdf rewrite; falls back to `model`
max_pages_per_chunk: int = 8       # safety cap (FR-09 force-split trigger)
image_format: str = "png"          # rendered page image format
```
`from_model` continues to work unchanged (these fields pass through `**overrides`).

## Design Decisions

### D3 — PyMuPDF for load + render
- **Chosen:** `pymupdf` (`fitz`) — one pure-wheel dependency that does both text
  extraction and page→PNG rasterization, no system packages.
- **Rationale:** single dependency, no external binaries; replaces the lossy
  `pdftotext` flatten in `just run-fixture`.
- **Rejected:** `pdf2image` (needs the poppler system binary); `pdfminer`+`Pillow`
  (two libs, no rasterization); shelling out to `pdftotext`/`pdftoppm` (external
  process, the current lossy approach).

### `Page` lives in `models.py`, not `loaders.py` (deviation from TASK.md)
- **Chosen:** put the `Page` dataclass in `models.py` beside `Chunk`/`SummaryBlock`;
  keep `LoadedDocument` + `load_document` in `loaders.py`.
- **Rationale:** `Page` is a serializable domain model and the codebase convention is
  that such dataclasses (with manual `to_dict`/`from_dict`) live in `models.py`. It also
  keeps the import direction clean (`state.py` already imports from `models.py`; making
  `state.py` import `Page` from `loaders.py` would invert `models <- state`).
- **Rejected:** `Page` in `loaders.py` (as TASK.md sketched) — would force `state.py` to
  depend on `loaders.py` and split domain models across two modules.

### D4 — Images on disk, referenced by absolute path
- **Chosen:** render to `<output_dir>/pages/page-NNNN.png`; `Page.image_path` and
  `Chunk.image_paths` store absolute path strings.
- **Rationale:** base64-inlining into the checkpoint JSON would bloat it by megabytes
  per page and break resumability; paths keep checkpoints lean and let output link the
  originals (Task 5). Absolute paths resolve cleanly for same-machine resume and for the
  vision rewrite that reads the bytes (Task 2).
- **Rejected:** inlining image bytes into the checkpoint (violates the prohibition).

### Mode discriminator
- **Chosen:** mode is implied by `pages is not None` (pdf) vs `None` (text). No separate
  enum field.
- **Rationale:** one source of truth; old checkpoints (no `pages` key) deserialize to
  `pages=None` → text mode, exactly as before.

## Acceptance Criteria

### FR-01: Direct PDF input (load side)
- GIVEN a readable PDF file
- WHEN `load_document(path, config)` is called
- THEN it SHALL return a `LoadedDocument` with `pages` populated and `source_text=None`
- AND SHALL NOT require any prior `pdftotext`/text-extraction step
- GIVEN a path that is missing, corrupt, or an unsupported PDF
- WHEN `load_document` is called
- THEN it SHALL raise a clear, actionable error and SHALL NOT return partial output

### FR-02: Page splitting and ordering
- GIVEN a multi-page PDF
- WHEN loaded
- THEN `LoadedDocument.pages` SHALL contain one `Page` per page, in document order
  (`pages[0].number == 1`, ascending)
- GIVEN a single-page PDF
- WHEN loaded
- THEN `pages` SHALL contain exactly one `Page`

### FR-03: Page rendering
- GIVEN a PDF page
- WHEN loaded
- THEN a PNG SHALL be written under `<output_dir>/pages/` and `Page.image_path` SHALL
  point to it (file exists on disk)

### FR-07: Checkpoint round-trip (state side)
- GIVEN a pdf-mode `PipelineState` with pages and chunks carrying `page_span`/`image_paths`
- WHEN `to_dict()`/`from_dict()` round-trip it
- THEN all fields SHALL be restored and the JSON SHALL contain image **paths**, not bytes
- GIVEN a checkpoint JSON written before this feature (no `pages`/`page_span`/`image_paths` keys)
- WHEN `PipelineState.from_dict` / `Chunk.from_dict` load it
- THEN they SHALL load successfully with `pages=None`, `page_span=None`, `image_paths=[]`

### FR-10: Pages with little or no text (load side)
- GIVEN a PDF page whose extractable text is empty
- WHEN loaded
- THEN loading SHALL NOT fail; the `Page` SHALL have `text == ""` and a valid `image_path`

### FR-11: Configurable resolution and model (config side)
- GIVEN `--pdf-dpi`/`--vision-model` are not supplied
- THEN `ChunkerConfig` SHALL use documented defaults (`pdf_dpi=150`, `vision_model=None`)
- GIVEN a configured `pdf_dpi`
- WHEN a PDF is loaded
- THEN pages SHALL be rendered at that resolution

## Done Criteria
- [ ] `pymupdf` is added to `pyproject.toml` dependencies and installs via `uv`
- [ ] `models.Page` exists with all three fields and round-trips via `to_dict`/`from_dict`
- [ ] `Chunk` has `page_span` + `image_paths` with safe defaults; `from_dict` uses `.get()` for them
- [ ] `PipelineState` has `pages`, `cursor_page`, `has_more_pages`, `has_more_input`, `create_from_pages`
- [ ] `ChunkerConfig` has `pdf_dpi`, `vision_model`, `max_pages_per_chunk`, `image_format` with defaults
- [ ] `load_document` returns text mode for `.txt`/`.md` and pdf mode for `.pdf`; raises a clear error on a bad path
- [ ] `test_loaders.py` loads `.sddw/chunker/test_fixture_agentic_rag.pdf`: asserts page count ≥ 1, pages in order, PNGs written, empty-text page tolerated
- [ ] Updated `test_models`/`test_state`/`test_config`/`test_checkpoint` pass, including an explicit "old checkpoint (no new keys) still loads" case
- [ ] `just test` and `just lint` are green
