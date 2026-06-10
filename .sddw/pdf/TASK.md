# Design: PDF + Image (Vision) Support for Chunker

## Verdict

**Yes — feasible, and a good architectural fit.** The chunker's value (semantic
boundaries → self-contained rewrites → bottom-up hierarchy) lives in layers that
operate on *summaries and contexts*, which are plain text. Those layers do not
care where the chunks came from. Only the **front of the pipeline** (loading,
boundary detection, rewrite) is coupled to "a single continuous string of text".

We can add a parallel PDF/vision front-end that produces the same `Chunk`
objects, and the entire back half — aggregation, context injection, output,
checkpointing — runs unchanged. This matches the user's framing exactly:
*"split pdf into pages, iterate over pages as we go with chunks, the rest the same."*

This also fixes a concrete pain point already in the repo: `just run-fixture`
currently does `pdftotext ai_index_report_2026.pdf report.txt` — flattening a
24 MB visual report (charts, tables, diagrams) to text and discarding every
figure before chunking even starts.

---

## 1. Current Architecture: what is coupled to text

The pipeline is a clean line: `load → extract → rewrite → aggregate → output`,
with checkpointing after every chunk. The coupling to "flat text" is narrow and
localized:

| Component | Text coupling | Survives PDF? |
|-----------|---------------|---------------|
| `cli.run_command` | `input_path.read_text()` | **No** — needs a loader |
| `PipelineState` | `source_text: str`, `cursor_position: int` (char offset) | **No** — needs a page cursor |
| `splitter.CursorWindow` / `TextSplitter` | regex over chars, `source_text[start:end]` | **No** — replaced by page window |
| `nodes/chunking.ChunkExtractor` | verbatim `boundary_phrase` via `str.find()` | **No** — replaced by page-index boundary |
| `Chunk.source_span: (int,int)` | char offsets | **Extended** — add page span + image refs |
| `llm/service.LLMService._call` | `HumanMessage(content=prompt)` — text only | **Extended** — accept images |
| `nodes/rewriting.ChunkRewriter` | passes `original_text` only | **Extended** — pass page images |
| `nodes/aggregation.AggregationSweeper` | operates on `.summary` / `.context` strings | **Yes — unchanged** |
| `context.ContextBuilder` | operates on chunk/block text | **Yes — unchanged** |
| `nodes/output.*` | renders `.context` / `.summary` strings | **Yes — unchanged** (optional image links) |
| `checkpoint.Checkpointer` | JSON of `state.to_dict()` | **Yes — unchanged** (state schema grows) |
| `metrics.Metrics` | timing only | **Yes — unchanged** |

**Key insight:** the back half of the pipeline consumes `Chunk.context`,
`Chunk.summary`, and `Chunk.filename` — all text the *rewrite* step produces.
If the rewrite step "sees" the page image and writes the visual content into
`context`, every downstream layer inherits that visual data for free, with zero
changes. The image is captured into text exactly once, at the rewrite boundary.

---

## 2. The Core Decision

There are two faithful ways to add vision. They differ in *where* the page image
is turned into text.

### Option A — Page-windowed vision chunking  ✅ RECOMMENDED

The page becomes the unit of iteration. A cursor walks page-by-page; a window of
consecutive pages grows until it's chunk-sized; the rewrite step feeds the page
**images** to a vision model that writes tables/figures/charts into the
self-contained context. Boundaries are chosen at page granularity.

- Matches "iterate over pages as we go with chunks" literally.
- Visual data captured at rewrite time, with the original image in hand.
- **Simplifies** the most fragile part of today's system: the verbatim
  `boundary_phrase` + `str.find()` dance is replaced by a discrete
  `split_after_page` integer — no string matching, no fuzzy fallback.
- One vision call per chunk (see §5 — completeness stays text-only).

### Option B — Vision transcription pre-pass (documented alternative)

A pre-pass sends every page image to a vision model and transcribes it to rich
markdown (tables → markdown tables, charts → described prose with the numbers).
Concatenate transcriptions → `source_text`, then run **today's pipeline 100%
unchanged**.

- Smallest diff: the core pipeline is literally untouched; only a loader is added.
- But it transcribes *everything up front* rather than "as we go", and flattens
  the image to text before chunking, so the rewrite step can no longer
  re-examine the page. Two full passes over the document (transcribe + chunk).

### Recommendation

**Option A.** It is the literal reading of the request, preserves the original
page image up to the rewrite step (higher fidelity), and *reduces* complexity in
the boundary logic. Option B is the lower-risk fallback if vision throughput or
structured-output support turns out to be a problem on the available models — it
can even be shipped first as a "Phase 0" to de-risk, since it reuses everything.

> Decision owner: confirm Option A before implementation. The rest of this doc
> specifies Option A.

---

## 3. Target Architecture (Option A)

### Data flow (PDF path)

```
input.pdf
  └─ PdfLoader (PyMuPDF)
       ├─ per page: extract text   → Page.text
       └─ per page: render → PNG   → Page.image_path   (output_dir/pages/page-0001.png)
  → PipelineState(pages=[Page...], cursor_page=0)

LOOP while state.has_more_pages:
  PageChunkExtractor.extract_next(state)
     PageWindow grows from cursor_page until est_tokens(window.text) >= min_chunk_tokens
     LLMService.check_page_completeness(window.text)        # TEXT-only, cheap
        → complete? + split_after_page: int|None
     resolve end page (or force-split at max tokens / max pages / max attempts)
     → Chunk(page_span, original_text=Σ page texts, image_paths=[...])
  ChunkRewriter.rewrite(chunk, state)
     LLMService.rewrite_chunk(text, context, images=chunk.image_paths)  # VISION
        → context (tables/figures written in), summary, filename
  AggregationSweeper.sweep(state)        # UNCHANGED
  Checkpointer.save(state)               # UNCHANGED mechanics

→ JsonExporter / MarkdownRenderer        # UNCHANGED (optional: link page images)
```

Text/markdown inputs keep their **existing** char-cursor path untouched. The
pipeline branches once, on input type, into one of two extractors that share the
`extract_next(state) -> Chunk` contract.

### New / changed modules

```
src/chunker/
  loaders.py            NEW  Page, DocumentLoader, PdfLoader, TextLoader, load_document()
  models.py             EDIT Chunk gains page_span, image_paths
  state.py              EDIT pages, cursor_page, has_more_pages, mode discriminator
  config.py             EDIT pdf_dpi, vision_model, max_pages_per_chunk, image format; vision profiles
  pipeline.py           EDIT branch text-vs-page extractor; thread images into rewrite
  cli.py                EDIT detect .pdf; --pdf-dpi / --vision-model flags
  nodes/page_chunking.py NEW PageChunkExtractor, PageWindow
  nodes/rewriting.py    EDIT pass chunk.image_paths to rewrite_chunk
  llm/service.py        EDIT _call accepts images; new check_page_completeness; rewrite_chunk images
  llm/schemas.py        EDIT PageCompletenessResult { complete, split_after_page }
  llm/prompts.py        EDIT page_completeness_prompt; vision-aware rewrite
  llm/prompt_templates/
    page_completeness.txt NEW
    rewrite.txt           EDIT add "transcribe tables, describe charts with numbers" rules
pyproject.toml          EDIT add "pymupdf"
justfile                EDIT run-pdf target (no pdftotext)
```

Untouched: `aggregation.py`, `context.py`, `output.py`, `checkpoint.py`,
`metrics.py`, `GroupingResult`/`BlockContextResult`/`RewriteResult` schemas.

---

## 4. Data Model Changes

### `Page` (new, in `loaders.py`)
```python
@dataclass
class Page:
    number: int          # 1-based page number
    text: str            # extracted text layer (may be empty for image-only pages)
    image_path: str      # path to rendered PNG on disk (NOT inlined bytes)
```

### `Chunk` (extended)
```python
@dataclass
class Chunk:
    id: str
    source_span: tuple[int, int]     # KEEP: char span (text mode) — (0,0) for pdf mode
    page_span: tuple[int, int] | None # NEW: (start_page, end_page) for pdf mode
    image_paths: list[str]            # NEW: page images for this chunk ([] for text mode)
    original_text: str
    context: str
    summary: str
    filename: str
    parent_block_id: str | None
    forced_split: bool
    metadata: dict
```
`to_dict`/`from_dict`/`from_json` updated; new fields default empty so **old
checkpoints still load** (`data.get("page_span")`, `data.get("image_paths", [])`).

### `PipelineState` (extended)
```python
pages: list[Page] | None = None       # NEW: present in pdf mode
cursor_page: int = 0                  # NEW
# source_text / cursor_position retained for text mode

@property
def has_more_pages(self) -> bool:
    return self.pages is not None and self.cursor_page < len(self.pages)
```
`mode` is implied by `pages is not None`. `to_dict`/`from_dict` serialize pages
(text + image **paths**, never bytes — keeps checkpoint small; note today's
checkpoint is already ~1 MB because it stores the full source string).

---

## 5. Key Design Decisions

### D1 — Page-granular boundaries (drop verbatim phrase matching for PDFs)
- **Chosen:** completeness returns `split_after_page: int | None`. The window
  ends at a page boundary.
- **Rationale:** page boundaries are discrete and unambiguous; no
  `str.find()` verbatim match, no retry-with-snippet, no fuzzy fallback. This
  deletes the most failure-prone code path in the current extractor.
- **Trade-off:** cannot split mid-page. With `min_chunk_tokens=2000`, a chunk is
  typically 2–4 dense pages, so page granularity is acceptable. A single page
  exceeding `max_chunk_tokens` is accepted as an oversized forced chunk (logged).
- **Rejected:** mapping a returned phrase back to char offsets within a page —
  reintroduces the fragility we are removing.

### D2 — Completeness is TEXT-only; rewrite is VISION
- **Chosen:** `check_page_completeness` reasons over the window's *extracted
  text*; only `rewrite_chunk` sends images.
- **Rationale:** topic boundaries are detectable from text/headings. Vision
  tokens are expensive and slow; sending images on every expansion attempt would
  multiply cost. We pay for vision exactly once per chunk, where fidelity matters
  (transcribing tables/charts into the self-contained context).
- **Mitigation for image-heavy pages:** a `max_pages_per_chunk` cap prevents a
  run of low-text (figure-only) pages from growing an unbounded window; optional
  `vision_completeness` flag can include images in completeness when text density
  is very low.

### D3 — PyMuPDF for load + render
- **Chosen:** `pymupdf` (fitz) — one dependency, does both text extraction and
  page→PNG rasterization, pure-wheel, no system packages.
- **Rejected:** `pdf2image` (needs poppler system binary), `pdfminer`+`Pillow`
  (two libs, no rasterization), shelling out to `pdftotext`/`pdftoppm` (external
  process, current lossy approach).

### D4 — Images on disk, referenced by path
- **Chosen:** render to `output_dir/pages/page-NNNN.png`; `Chunk.image_paths`
  and `Page.image_path` store paths.
- **Rationale:** base64-inlining images into the checkpoint JSON would bloat it
  by megabytes per page and break resumability ergonomics. Paths keep the
  checkpoint lean and let output optionally link the originals.

### D5 — Two extractors behind one contract; text path untouched
- **Chosen:** keep `ChunkExtractor` (char cursor) for `.txt`/`.md`; add
  `PageChunkExtractor` (page cursor) for `.pdf`. Pipeline selects on input type.
- **Rationale:** routing text through a page-chunker would regress fine-grained
  semantic splitting that text files benefit from. Honors "the rest the same"
  for existing inputs while adding a clean new mode.

### D6 — Vision model configuration
- **Chosen:** `vision_model` config (defaults to `model` if it is multimodal).
  Add vision entries to `MODEL_PROFILES`.
- **Rationale:** the boundary model can stay a fast text model while a separate
  multimodal model handles rewrite, or one multimodal model does both.
- **Image transport:** `HumanMessage(content=[{"type":"text","text":prompt},
  {"type":"image_url","image_url":"data:image/png;base64,<...>"}, ...])` —
  langchain-ollama's multimodal content format.

---

## 6. Risks & Open Questions

1. **Vision + structured output on Ollama (highest risk).** `with_structured_output`
   must work alongside image content on the chosen model. *Mitigation:* spike
   this first (§7 Phase 1); if a model supports vision but not structured output,
   fall back to JSON `format` + manual parse inside the existing `_call` retry
   loop. Confirm a multimodal tag is available — repo has `gemma4:*` and
   `qwen3.x` families; the exact vision-capable tag must be verified with
   `ollama show <model>` / a one-page smoke test before committing.
2. **Throughput / cost.** A 200-page report → ~50–100 vision rewrite calls;
   vision calls are slower and image tokens are heavy. *Mitigation:* text-only
   completeness (D2), tune `pdf_dpi` (start 150), downscale long edge, checkpoint
   already makes long runs resumable.
3. **Scanned / no-text-layer PDFs.** `Page.text` may be empty → text completeness
   is blind. *Mitigation:* `max_pages_per_chunk` cap + optional vision
   completeness when density is low; full OCR is out of scope for v1.
4. **Token estimation for pages.** `estimate_tokens` is word-count based and
   ignores image tokens, so windows may under-estimate. *Mitigation:* the page
   cap is the real safety valve, not the token estimate.
5. **Output fidelity for humans.** Rewritten context describes figures, but the
   reader may want the original. *Mitigation (Phase 3):* link page PNGs from the
   chunk markdown.

---

## 7. Phased Implementation Plan

**Phase 1 — De-risk vision (spike, ~½ day).** Prove a local multimodal model can
(a) accept a rendered PDF page image via langchain-ollama and (b) return
structured output. Pick the model; record the working content format. Gate for
the rest.

**Phase 2 — Loader + data model.** `loaders.py` (`Page`, `PdfLoader`, `TextLoader`,
`load_document`), add `pymupdf`, extend `Chunk` + `PipelineState` (+ migration-safe
`from_dict`). Tests: load the existing `ai_index_report_2026.pdf` / fixture PDF,
assert page count, non-empty text, PNGs written.

**Phase 3 — Page chunking + vision rewrite.** `PageChunkExtractor` + `PageWindow`,
`check_page_completeness` (+ schema + prompt), `_call` image support, vision-aware
`rewrite.txt`. Wire the pipeline/CLI branch. Tests with a mocked `LLMService`:
window growth, page-boundary split, force-split (max tokens / max pages /
max attempts), images threaded to rewrite.

**Phase 4 — Glue + polish.** `justfile` `run-pdf` target (drop `pdftotext`),
README section, optional output image links, end-to-end run on the AI Index report.

---

## 8. Acceptance Criteria

- **AC1 (load):** `chunker run report.pdf` renders one PNG per page under
  `output/pages/` and extracts per-page text; no `pdftotext` involved.
- **AC2 (iterate as we go):** chunks are produced page-window by page-window with
  a checkpoint after each — interrupting and resuming continues mid-document.
- **AC3 (boundaries):** chunk boundaries fall on page edges via `split_after_page`;
  no verbatim-phrase matching runs in PDF mode.
- **AC4 (visual data preserved):** for a page containing a table or chart, the
  resulting `Chunk.context` contains the table content / chart figures-and-numbers
  — i.e. data that `pdftotext` drops is present.
- **AC5 (the rest is the same):** aggregation, context injection, JSON + markdown
  output, and checkpoint format are produced by the **unchanged** modules; a
  `.txt` input behaves exactly as before (no regression).
- **AC6 (safety valves):** an oversized single page and a run of image-only pages
  both terminate via documented force-split / `max_pages_per_chunk`, each logged.
- **AC7 (tests):** loader + page-extractor + vision-service unit tests pass with a
  mocked LLM; lint clean.

---

## 9. Effort & Reuse Summary

- **Reused unchanged:** aggregation, context builder, output renderer,
  checkpointer mechanics, metrics, 3 of 4 LLM schemas — i.e. the entire
  "navigable tree" engine, the project's actual IP.
- **New:** ~1 loader module, 1 page-extractor module, 1 schema, 1 prompt,
  1 dependency.
- **Edited (additively):** `Chunk`, `PipelineState`, `LLMService._call`,
  rewriter, pipeline branch, CLI, config.
- **Removed complexity:** verbatim boundary-phrase matching + fuzzy fallback (for
  the PDF path).

Net: a contained front-end addition, not a rewrite. The page-by-page model the
user proposed is the right grain, and it happens to make the boundary logic
*simpler* than the text path it sits beside.
