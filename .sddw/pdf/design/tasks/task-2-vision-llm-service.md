# Task 2: Vision-capable LLM service

## Trace
- **FR-IDs:** FR-04, FR-05
- **Depends on:** task-1

## Files
- `src/chunker/llm/service.py` — modify (`_call` accepts images; new `check_page_completeness`; `rewrite_chunk` accepts images)
- `src/chunker/llm/schemas.py` — modify (add `PageCompletenessResult`)
- `src/chunker/llm/prompts.py` — modify (add `page_completeness_prompt`)
- `src/chunker/llm/prompt_templates/page_completeness.txt` — create
- `src/chunker/llm/prompt_templates/rewrite.txt` — modify (add vision transcription rules)
- `tests/unit/test_llm_service.py` — update (interface change: `_call` signature, new method, image content format)

## Architecture

This task teaches the single LLM abstraction to (a) judge page-window boundaries from
text and (b) read page **images** during rewrite, writing tables/charts/figures into
the self-contained `context`. The image is turned into text exactly once, at rewrite —
every downstream layer inherits that visual data for free.

### Components
- `LLMService._call`: gains an optional `image_paths` argument; builds a multimodal
  `HumanMessage` when images are present — modified
- `LLMService.check_page_completeness`: new, **text-only** boundary check for page windows
- `LLMService.rewrite_chunk`: gains optional `image_paths`, forwarded to `_call` — modified
- `PageCompletenessResult`: new structured-output schema
- `page_completeness.txt`: new prompt; `rewrite.txt`: edited with vision rules

### Data Flow
```
# Boundary (text-only):
PageChunkExtractor → check_page_completeness(window_text)
   → _call(prompt, PageCompletenessResult, ...)  # no images
   → PageCompletenessResult(complete, split_after_page)

# Rewrite (vision):
ChunkRewriter → rewrite_chunk(text, context, image_paths=[png...])
   → _call(prompt, RewriteResult, ..., image_paths=[png...])
       HumanMessage(content=[{type:text,...}, {type:image_url, image_url:"data:image/png;base64,..."}...])
   → RewriteResult(context, summary, filename)  # tables/figures written into context
```

## Contracts

### Internal Interfaces
- `LLMService._call(prompt: str, schema: type[T], event: str, entity_id: str | None, *, image_paths: list[str] | None = None) -> T`
  - Pre: when `image_paths` is given, each path points to a readable image file.
  - Post: when `image_paths` is `None`/empty, behavior is byte-for-byte the current
    text-only path (no regression). When present, the first user message content is a
    list: one `{"type": "text", "text": prompt}` part followed by one
    `{"type": "image_url", "image_url": "data:image/<fmt>;base64,<b64>"}` part per image.
    The existing retry loop, `with_structured_output(schema, include_raw=True)`, logging,
    and `MAX_RETRIES` are preserved.
- `LLMService.check_page_completeness(window_text: str, *, chunk_id: str | None = None) -> PageCompletenessResult`
  - Pre: `window_text` is the concatenated extracted text of the candidate page window.
  - Post: returns whether the window ends at a complete topic boundary and, if so, the
    page after which to split. **Text-only** — never sends images.
- `LLMService.rewrite_chunk(chunk_text: str, context_text: str, *, image_paths: list[str] | None = None, chunk_id: str | None = None) -> RewriteResult`
  - Post: forwards `image_paths` to `_call`. With `image_paths=None`/`[]` (text chunks),
    output is identical to today (no regression).

### LLM Schemas
- `PageCompletenessResult(BaseModel)`:
  - `complete: bool`
  - `split_after_page: int | None = None` — the **1-based page number** that should be
    the *last* page of this chunk (the boundary inside the window). `None` ⇒ end at the
    window's current last page. The extractor (Task 3) clamps this to the window's page
    range; an out-of-range value is treated as "end at the current window".
- Existing `RewriteResult(context, summary, filename)` is reused unchanged for vision rewrite.

## Data Models
No dataclass changes. One new Pydantic schema (`PageCompletenessResult`) following the
existing `schemas.py` convention (Pydantic `BaseModel`, used only for structured output).

## Design Decisions

### D2 — Completeness is TEXT-only; rewrite is VISION
- **Chosen:** `check_page_completeness` reasons over the window's extracted text only;
  only `rewrite_chunk` sends images.
- **Rationale:** topic boundaries are detectable from text/headings; vision tokens are
  expensive and slow, and completeness is called on every window expansion. We pay for
  vision exactly once per chunk, where fidelity matters (transcribing tables/charts into
  the self-contained context).
- **Rejected:** a `vision_completeness` flag that feeds images into completeness — decided
  out of scope for v1 (extra call path + cost); the `max_pages_per_chunk` cap (Task 3) is
  the safety valve for runs of low-text pages instead.

### `split_after_page` integer replaces verbatim phrase matching (page analog of D1)
- **Chosen:** completeness returns a discrete page number, not a `boundary_phrase`.
- **Rationale:** page edges are discrete and unambiguous — no `str.find()`, no
  retry-with-snippet, no fuzzy fallback. This is the page-mode boundary contract that
  Task 3 consumes; it deletes the most failure-prone code path from the text extractor.

### Image transport via langchain-ollama multimodal content
- **Chosen:** base64-encode each image file and embed as a `data:image/<fmt>;base64,...`
  `image_url` content part in a `HumanMessage` content list.
- **Rationale:** this is langchain-ollama's multimodal message format; reading bytes from
  the on-disk path (Task 1's `Page.image_path`) keeps checkpoints byte-free.
- **Vision + structured-output risk / fallback:** the primary path keeps
  `with_structured_output(..., include_raw=True)`. If the chosen multimodal model rejects
  structured output when images are present, fall back to requesting JSON via the model's
  `format` option and parsing inside the existing `_call` retry loop. The smoke test below
  gates this before Task 3 depends on it.

### Single multimodal model for both calls
- **Chosen:** in pdf mode the same injected model serves text completeness and vision
  rewrite (a vision model handles plain text fine). Model selection (`vision_model` or
  `model`) happens at pipeline/CLI wiring (Task 4); this task assumes the injected model
  is multimodal in pdf mode.
- **Rationale:** avoids a second model instance and any change to `LLMService`'s
  single-model structure.

## Acceptance Criteria

### FR-04: Page-edge chunk boundaries (completeness contract)
- GIVEN a candidate page-window text
- WHEN `check_page_completeness(window_text)` is called
- THEN it SHALL return a `PageCompletenessResult` with `complete: bool` and, when complete,
  an integer `split_after_page` (or `None`)
- AND it SHALL NOT send any image to the model

### FR-05: Visual data preserved in context
- GIVEN a chunk whose `image_paths` include a page with a data table
- WHEN `rewrite_chunk(text, context, image_paths=[...])` is called against a vision model
- THEN the returned `RewriteResult.context` SHALL contain the table's actual values/rows,
  not merely a mention that a table exists
- GIVEN a page with a chart/figure
- THEN the rewritten context SHALL describe the figure with concrete numbers and labels
- CONTRAST: visual content present in this context SHALL be demonstrably absent from the
  text-only (`pdftotext`) extraction of the same page

## Done Criteria
- [ ] `_call` accepts `image_paths`; with none, the text path is unchanged (existing tests green)
- [ ] With `image_paths`, `_call` builds a content list with one text part + one `image_url`
      data-URL part per image (unit test asserts the message structure with a mocked model)
- [ ] `PageCompletenessResult` exists in `schemas.py`; `check_page_completeness` returns it and sends no images
- [ ] `rewrite_chunk` forwards `image_paths`; `page_completeness.txt` exists; `rewrite.txt`
      instructs the model to transcribe tables into markdown tables and describe charts/figures
      with their numbers and axis labels
- [ ] **Smoke test (real model):** render one page of `output/ai_report_2026/ai_index_report_2026.pdf`
      (or the fixture PDF) via Task 1's loader, call `rewrite_chunk` with a `vision`-capable model
      (`gemma4:latest`/`gemma4:26b`/`qwen3.6:latest`), and confirm a valid `RewriteResult` whose
      `context` includes a number/label visible only in the image. If structured output fails
      with images, the documented JSON-`format` fallback is implemented.
- [ ] `just test` and `just lint` are green
