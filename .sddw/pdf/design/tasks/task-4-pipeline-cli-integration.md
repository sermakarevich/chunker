# Task 4: Pipeline + CLI integration

## Trace
- **FR-IDs:** FR-01, FR-06, FR-07, FR-08, FR-10, FR-11
- **Depends on:** task-1, task-2, task-3

## Files
- `src/chunker/pipeline.py` — modify (mode dispatch, `has_more_input` loop, mode-aware progress, `run_document`, thread images to rewrite)
- `src/chunker/cli.py` — modify (detect `.pdf` via `load_document`, `--pdf-dpi`/`--vision-model` flags, route; add same flags to `resume`)
- `src/chunker/nodes/rewriting.py` — modify (pass `chunk.image_paths` to `rewrite_chunk`)
- `tests/unit/test_pipeline.py` — update (interface: loop condition, extractor dispatch, `run_document`)
- `tests/unit/test_rewriting.py` — update (interface: `rewrite_chunk` now called with `image_paths`)
- `tests/integration/test_pipeline_e2e.py` — update (add a PDF end-to-end case)

## Architecture

This task wires the pdf front-end into the existing orchestration so a `.pdf` flows through
the **unchanged** back half (aggregation → context → output → checkpoint). The pipeline loop
becomes mode-agnostic; the text path stays byte-for-byte the same.

### Components
- `Pipeline`: holds both extractors (`_extractor` text, `_page_extractor` pages); dispatches
  per iteration on `state.pages`; gains `run_document` — modified
- `ChunkRewriter`: passes `chunk.image_paths` into `rewrite_chunk` — modified
- `cli`: loads via `load_document`, routes pdf vs text, exposes new flags — modified

### Data Flow
```
cli.run_command:
  config = ChunkerConfig(... pdf_dpi, vision_model, output_dir ...)
  doc = load_document(input_path, config)            # Task 1
  if doc is pdf and config.vision_model:             # effective vision model
      config.model = config.vision_model             # so Pipeline builds a multimodal ChatOllama
  pipeline = Pipeline(config)
  pipeline.run_document(doc)

Pipeline.run_document(doc):
  if checkpointer.exists(): state = checkpointer.load(expected_document_id=doc.document_id)
  elif doc.pages is not None: state = PipelineState.create_from_pages(doc.document_id, doc.pages)
  else:                      state = PipelineState.create(doc.document_id, doc.source_text)
  _process(state)

Pipeline._process(state):                            # mode-agnostic
  while state.has_more_input:                         # text OR pages
     chunk = (state.pages is not None
              ? self._page_extractor : self._extractor).extract_next(state)
     chunk = self._rewriter.rewrite(chunk, state)     # passes chunk.image_paths
     state.chunks[chunk.id] = chunk
     state.pending_summaries.setdefault(0, []).append(chunk.id)
     self._sweeper.sweep(state)                        # UNCHANGED
     self._checkpointer.save(state)                    # UNCHANGED
     log progress via _progress_pct(state)
  self._write_output(state)                            # UNCHANGED
```

## Contracts

### CLI
- `chunker run <input_file> [--model M] [--output-dir D] [--rewrite-instructions S] [--pdf-dpi N] [--vision-model VM]`
  - `.pdf` input → pdf mode (no `pdftotext`); any other suffix → text mode (unchanged).
  - `--pdf-dpi` → `config.pdf_dpi`; `--vision-model` → `config.vision_model`.
  - `document_id` remains `input_path.stem` (drives checkpoint identity).
- `chunker resume <checkpoint_file> [--output-dir D] [--model M] [--vision-model VM]`
  - Mode is recovered from the checkpoint (`state.pages`). `--model`/`--vision-model` are
    added so a resumed PDF run can be given its multimodal model (a PDF resume needs a
    `vision`-capable model for rewrite).

### Internal Interfaces
- `Pipeline.run_document(document: LoadedDocument) -> ProcessingResult`: build/resume state
  from a `LoadedDocument`, then `_process`.
  - Pre: `document` came from `load_document`.
  - Post: produces a `ProcessingResult`; resumes from an existing checkpoint when present.
- `Pipeline.run(text: str, document_id: str) -> ProcessingResult`: retained as a thin
  back-compat wrapper (delegates to a text `LoadedDocument`) so existing tests/callers work.
- `Pipeline._progress_pct(state) -> float`: text → `cursor_position/len(source_text)`;
  pdf → `cursor_page/len(pages)`; guards against division by zero.
- `ChunkRewriter.rewrite(chunk, state) -> Chunk`: now calls
  `rewrite_chunk(chunk.original_text, context_text, image_paths=chunk.image_paths, chunk_id=chunk.id)`.
  - Post: for text chunks `image_paths == []` ⇒ identical text-only behavior (no regression).

## Data Models
No new models. Uses Task 1's extended `PipelineState`/`Chunk` and `LoadedDocument`, and
Task 2/3's vision service + page extractor.

## Design Decisions

### Mode-agnostic loop via `has_more_input` + per-iteration dispatch
- **Chosen:** `_process` loops on `state.has_more_input` and selects the extractor by
  `state.pages is not None` each iteration; `run`/`resume` share this single loop.
- **Rationale:** one orchestration path serves both modes and both fresh-run and resume,
  so checkpoint/resume (FR-07) works for PDFs with no separate loop. Avoids dividing by
  `len(source_text)` (empty in pdf mode) in the progress log.
- **Rejected:** a separate pdf loop/method — duplicates orchestration and the resume path.

### Effective vision model resolved in CLI
- **Chosen:** when the input is a PDF and `vision_model` is set, CLI sets `config.model` to
  it before constructing `Pipeline`, so the single injected `ChatOllama` is multimodal.
- **Rationale:** keeps `Pipeline`/`LLMService` single-model; `vision_model` defaults to the
  configured `model` (which must be multimodal for PDFs — documented; smoke-tested in Task 2).
- **Rejected:** two model instances inside the pipeline — unnecessary complexity for v1.

### No-regression guarantee (FR-08)
- **Chosen:** text inputs take the identical extractor, model, and rewrite path; the only
  shared edits (`_process` loop, rewriter passing `image_paths=[]`) are behavior-preserving
  for text.
- **Rationale:** the no-PDF-path-for-text and identical-output requirements (FR-08) hold by
  construction.

## Acceptance Criteria

### FR-01: Direct PDF input (end to end)
- GIVEN a readable PDF and `chunker run file.pdf`
- THEN the system SHALL process it directly with no `pdftotext`/extraction step

### FR-06: Same outputs as text
- GIVEN a fully processed PDF
- THEN output SHALL be a JSON hierarchy, an `index.md`, and level-organized markdown under
  `content/L*/`, with the same structure a text document produces (produced by the
  **unchanged** `JsonExporter`/`MarkdownRenderer`/`AggregationSweeper`/`ContextBuilder`)

### FR-07: Checkpoint and resume
- GIVEN a PDF run interrupted after N chunks
- WHEN resumed
- THEN it SHALL continue from chunk N+1 and SHALL NOT reprocess completed chunks
- GIVEN a checkpoint from a different document
- WHEN resumed against an unrelated PDF
- THEN it SHALL refuse with a document-identity mismatch error (existing `Checkpointer` check)

### FR-08: No regression to the text path
- GIVEN an existing `.txt`/`.md` input processed after this feature
- THEN output SHALL be equivalent to pre-feature behavior and no pdf-only path SHALL run

### FR-10 / FR-11 (wiring)
- A chunk's page images SHALL be passed to the rewrite step (`image_paths` threaded through).
- `--pdf-dpi`/`--vision-model` SHALL take effect; omitting them SHALL use documented defaults.

## Done Criteria
- [ ] `_process` loops on `has_more_input` and dispatches text vs page extractor by `state.pages`
- [ ] `run_document` builds text or pdf state and resumes from an existing checkpoint
- [ ] `Pipeline.run(text, document_id)` still works (back-compat wrapper); existing pipeline tests pass
- [ ] Progress logging is mode-aware and never divides by zero
- [ ] CLI: `.pdf` → pdf mode via `load_document`; `--pdf-dpi`/`--vision-model` wired; `resume` gains `--model`/`--vision-model`
- [ ] `ChunkRewriter.rewrite` passes `chunk.image_paths`; text chunks (`[]`) behave identically
- [ ] `test_pipeline_e2e.py`: existing text e2e still green (regression) + a PDF e2e on the fixture
      produces `hierarchy.json`, `index.md`, and `content/L*/` files; a mid-run resume continues correctly
- [ ] `just test` and `just lint` are green
