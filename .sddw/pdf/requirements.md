# Requirements: PDF + Vision Support

> Step 1 of the sddw workflow. Companion design exploration: `.sddw/pdf/TASK.md`.

## 1. Project

- Path: `.`

The chunker project (current working directory). All subsequent steps
(code-analysis, design, implement) target this codebase.

---

## 2. Purpose

Chunker can only process plain text today, so PDFs must be flattened with
`pdftotext` before chunking — discarding tables, charts, and figures and losing
the data they carry. This feature lets Chunker ingest PDFs directly and preserve
that visual data in the resulting knowledge tree, by iterating over the document
page by page and letting a vision-capable model read each page while chunks are
built.

---

## 3. User Stories

- As an AI/ML engineer, I want to feed a PDF straight to Chunker, so that I do
  not have to pre-convert it with `pdftotext` and lose its figures.
- As an engineer processing a chart- and table-heavy report, I want the data in
  those visuals captured in each chunk's self-contained context, so that the
  knowledge tree reflects information that text extraction drops.
- As a user processing a long PDF, I want PDF runs to checkpoint and resume the
  same way text runs do, so that a large document survives interruption.
- As an existing user with text or markdown documents, I want my current
  workflow to behave exactly as before, so that adding PDF support does not
  regress anything.

---

## 4. Functional Requirements

- **FR-01:** A user SHALL be able to run Chunker on a PDF file directly, without
  any separate text-extraction step.
- **FR-02:** The system SHALL split a PDF into individual pages and process those
  pages in document order.
- **FR-03:** The system SHALL render each page as an image and retain that image
  for use during chunk processing.
- **FR-04:** The system SHALL group consecutive pages into semantically complete
  chunks, with every chunk boundary falling on a page edge.
- **FR-05:** The system SHALL capture the visual content of a chunk's pages —
  including tables, charts, and figures — into that chunk's self-contained
  context.
- **FR-06:** The system SHALL produce the same outputs for a PDF as for a text
  document: a multi-level summary hierarchy, linked markdown files, and a JSON
  hierarchy.
- **FR-07:** The system SHALL checkpoint after each chunk and SHALL be able to
  resume a PDF run from its checkpoint without reprocessing completed chunks.
- **FR-08:** The system SHALL preserve the existing text and markdown processing
  behavior, with no change to its output or its command interface.
- **FR-09:** The system SHALL enforce safety limits — a maximum number of pages
  per chunk, a maximum chunk size, and a maximum number of boundary-check
  attempts — and SHALL force-split at a page edge when a limit is reached,
  recording the event in the log.
- **FR-10:** The system SHALL process pages that have little or no extractable
  text without failing.
- **FR-11:** A user SHOULD be able to configure the page-render resolution and
  select the vision-capable model used for chunk rewriting.
- **FR-12:** The system SHOULD link each chunk's original page image(s) from the
  rendered markdown so that a human reader can view the source figures.

---

## 5. Acceptance Criteria

### FR-01: Direct PDF input

**Happy path:**
- GIVEN a readable PDF file
- WHEN the user runs Chunker with that file as input
- THEN the system SHALL process it directly (SHALL)
- AND it SHALL NOT require a prior `pdftotext` or other text-extraction step

**Failure path:**
- GIVEN a path that is not a readable PDF (missing, corrupt, or unsupported)
- WHEN the user runs Chunker with that path
- THEN the system SHALL fail with a clear, actionable error message
- AND SHALL NOT produce partial or misleading output

### FR-02: Page splitting and ordering

**Happy path:**
- GIVEN a multi-page PDF
- WHEN the system loads it
- THEN it SHALL produce one processing unit per page
- AND pages SHALL be processed in document order (first page first)

**Edge case:**
- GIVEN a single-page PDF
- WHEN processed
- THEN the system SHALL produce at least one chunk covering that page

### FR-03: Page rendering

**Happy path:**
- GIVEN a PDF page
- WHEN the system loads the document
- THEN it SHALL produce an image rendering of that page
- AND that image SHALL be available to the chunk-rewriting step

### FR-04: Page-edge chunk boundaries

**Happy path:**
- GIVEN a multi-page PDF where a topic concludes at the end of page K
- WHEN the system forms chunks
- THEN a chunk SHALL end at the page-K edge (SHALL)

**Boundary/edge case:**
- GIVEN a candidate chunk that is below the minimum chunk size at a page edge
- AND the following page continues the same topic
- WHEN the system evaluates the boundary
- THEN it SHALL extend the chunk to include further pages

**Constraint:**
- GIVEN any produced chunk
- THEN it SHALL NOT begin or end in the middle of a page

### FR-05: Visual data preserved in context

**Happy path (table):**
- GIVEN a page containing a data table
- WHEN the chunk covering that page is rewritten
- THEN the chunk's context SHALL contain the table's content (its values and
  rows), not merely a mention that a table exists

**Happy path (chart/figure):**
- GIVEN a page containing a chart or figure
- WHEN the chunk is rewritten
- THEN the chunk's context SHALL describe the figure with its concrete numbers
  and labels

**Contrast (headline verification):**
- GIVEN the same PDF processed through the legacy `pdftotext` text path
- WHEN the new PDF context is compared with the text-only extraction
- THEN visual content present in the new context (table values, chart figures)
  SHALL be demonstrably absent from the text-only extraction

### FR-06: Same outputs as text

**Happy path:**
- GIVEN a fully processed PDF
- WHEN output is written
- THEN the system SHALL emit a JSON hierarchy, an index file, and level-organized
  markdown files
- AND their structure SHALL match what a text document produces

### FR-07: Checkpoint and resume

**Happy path:**
- GIVEN a PDF run interrupted after N chunks
- WHEN the user resumes from the checkpoint
- THEN the system SHALL continue from chunk N+1
- AND SHALL NOT reprocess the already-completed chunks

**Failure path:**
- GIVEN a checkpoint created from a different document
- WHEN the user resumes it against an unrelated PDF
- THEN the system SHALL refuse with a document-identity mismatch error

### FR-08: No regression to the text path

**Happy path:**
- GIVEN an existing `.txt` or `.md` input
- WHEN it is processed after this feature ships
- THEN the output SHALL be equivalent to the pre-feature behavior
- AND no PDF-only processing path SHALL execute for that input

### FR-09: Safety limits and force-split

**Happy path (page cap):**
- GIVEN a run of pages whose combined window never satisfies the completeness
  check
- WHEN the maximum-pages-per-chunk limit is reached
- THEN the system SHALL force-split at that page edge
- AND mark the chunk as forced
- AND record the event in the log

**Edge case (oversized page):**
- GIVEN a single page that exceeds the maximum chunk size
- WHEN it is processed
- THEN the system SHALL accept it as an oversized single-page chunk
- AND record a warning in the log

### FR-10: Pages with little or no text

**Happy path:**
- GIVEN a page whose extractable text is empty (for example, a full-page image)
- WHEN it is processed
- THEN the system SHALL NOT crash
- AND the page SHALL still be included in a chunk
- AND its rendered image SHALL be passed to the rewriting step

### FR-11: Configurable resolution and model

**Happy path:**
- GIVEN a configured page-render resolution and a chosen vision-capable model
- WHEN the user runs Chunker on a PDF
- THEN pages SHALL be rendered at the chosen resolution
- AND the chosen model SHALL be used for chunk rewriting

**Edge case (defaults):**
- GIVEN no resolution or model option is supplied
- WHEN the user runs Chunker on a PDF
- THEN the system SHALL use documented default values

### FR-12: Page-image links in markdown

**Happy path:**
- GIVEN a rendered chunk markdown file for a PDF-derived chunk
- WHEN a human opens it
- THEN it SHALL contain a link or reference to the chunk's source page image(s)

---

## 6. Constraints

### In Scope
- Direct PDF ingestion: splitting into pages and rendering each page to an image.
- Page-windowed semantic chunking with boundaries on page edges.
- Vision-based chunk rewriting that captures tables, charts, and figures into the
  self-contained context.
- The same hierarchy, aggregation, and output (markdown + JSON) as the text path.
- Checkpointing and resuming PDF runs.
- Configurable page-render resolution and vision model selection.
- Linking original page images from the rendered markdown.
- Graceful handling of pages with little or no extractable text.

### Out of Scope
- OCR or full searchable-text reconstruction for scanned, image-only PDFs —
  boundary detection relies on the page's existing text layer; full OCR is a
  separate effort.
- The "vision transcription pre-pass" alternative (Option B in `TASK.md`) —
  rejected in favor of page-windowed chunking; retained only as a documented
  fallback.
- Standalone image files (`.png`, `.jpg`) as direct input — the unit of input is
  a PDF; single-image ingestion may be considered later.
- Splitting a chunk below page granularity (mid-page sub-chunks) — the page is
  the atomic boundary unit.
- Parallel or concurrent page processing and other throughput optimizations —
  long runs rely on the existing checkpoint/resume mechanism.
- Changes to retrieval or embedding — this feature only affects how a document is
  ingested and turned into chunks.

### Prohibitions
- The system SHALL NOT split a chunk in the middle of a page — boundaries are
  page-granular.
- The system SHALL NOT alter or regress the existing text/markdown processing
  path — the no-regression guarantee in FR-08.
- The system SHALL NOT inline image bytes into the checkpoint file — images are
  referenced by path so checkpoints stay small and resumable.
- The system SHALL NOT use fuzzy or approximate boundary matching — chunk
  boundaries are chosen as discrete page positions.
- The system SHALL NOT require any network or cloud service — Chunker runs
  against a local model, and vision processing SHALL remain local as well.

### Testing Approach
- Test-after — implement the feature first, then add unit and integration tests
  covering the functional requirements and acceptance criteria above. Unit tests
  follow the existing pattern (deterministic logic with a mocked model service);
  the live vision behavior is verified through an integration/manual run on a
  real visual PDF (for example, the AI Index report already in the repo).
