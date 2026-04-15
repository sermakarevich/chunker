## Codebase Analysis

### Relevant Patterns

- **Pipeline orchestration**: Single `Pipeline` class (`src/chunker/pipeline.py`) runs a cursor-based state machine loop: extract -> rewrite -> add to state -> sweep -> checkpoint -> write output. All nodes are composed via constructor injection.
- **Node-based processing**: Each processing step is an independent class (`ChunkExtractor`, `ChunkRewriter`, `AggregationSweeper`, `JsonExporter`, `MarkdownRenderer`) in `src/chunker/nodes/`. Pipeline composes them; nodes are stateless beyond their injected dependencies.
- **Dataclass domain models**: `Chunk`, `SummaryBlock`, `PipelineState` are `@dataclass` with manual `to_dict`/`from_dict`/`to_json`/`from_json` round-trip serialization. Pydantic `BaseModel` is reserved exclusively for LLM structured output schemas.
- **LLM abstraction via structured output**: `LLMService` (`src/chunker/llm/service.py`) wraps langchain's `with_structured_output()`, returning typed Pydantic schemas. Includes retry with exponential backoff (max 3 attempts). All LLM interactions go through this single service.
- **Prompt template loading**: Prompts are `.txt` files in `src/chunker/llm/prompt_templates/` loaded and cached by `prompts.py` using Python `.format()` interpolation.
- **Cursor-window expansion**: `TextSplitter` + `CursorWindow` (`src/chunker/splitter.py`) progressively expand a text window using configurable split strategies (sentences, paragraphs, words) with regex-based boundary detection.
- **Bottom-up aggregation**: `AggregationSweeper` groups pending summaries level by level with LLM-based grouping, `GroupValidator` validation (hard/soft violations with separate handling), and `even_split_fallback` when LLM fails after 2 consecutive hard violations.
- **Atomic checkpoint/resume**: `Checkpointer` (`src/chunker/checkpoint.py`) writes state via `tempfile.mkstemp()` + `Path.replace()` for crash safety. Supports document ID verification on load.
- **Config-driven model profiles**: `ModelProfile` + `ChunkerConfig.from_model()` (`src/chunker/config.py`) set model-specific defaults for token limits, context budgets, and token estimation factors.

### Key Interfaces

- **`Chunk`** (`src/chunker/models.py`): `id: str`, `source_span: tuple[int, int]`, `original_text: str`, `rewritten_text: str`, `summary: str`, `parent_block_id: str | None`, `forced_split: bool`, `metadata: dict`. Serializable via `to_dict()/from_dict()/to_json()/from_json()`.
- **`SummaryBlock`** (`src/chunker/models.py`): `id: str`, `level: int`, `summary: str`, `child_ids: list[str]`, `parent_block_id: str | None`, `metadata: dict`. Same serialization interface as `Chunk`.
- **`PipelineState`** (`src/chunker/state.py`): `document_id`, `source_text`, `cursor_position`, `chunks: dict[str, Chunk]`, `blocks: dict[str, SummaryBlock]`, `pending_summaries: dict[int, list[str]]`, `chunk_counter`, `block_counters`. Factory: `PipelineState.create(document_id, source_text)`. Property: `has_more_text`.
- **`LLMService`** (`src/chunker/llm/service.py`): `check_completeness(window_text, context_text) -> CompletenessResult`, `rewrite_chunk(chunk_text, context_text) -> RewriteResult`, `group_summaries(summaries, min_size, max_size) -> GroupingResult`, `summarize_group(summaries) -> str`.
- **`ChunkExtractor.extract_next(state) -> Chunk`** (`src/chunker/nodes/chunking.py`): Advances cursor, returns new chunk. Mutates `state.cursor_position` and `state.chunk_counter`.
- **`ChunkRewriter.rewrite(chunk, state) -> Chunk`** (`src/chunker/nodes/rewriting.py`): Mutates chunk with rewritten text and summary via LLM.
- **`AggregationSweeper.sweep(state) -> None`** (`src/chunker/nodes/aggregation.py`): Mutates state by creating `SummaryBlock`s from pending summaries across levels.
- **`JsonExporter.export(state) -> dict`** and **`.write(state, path)`** (`src/chunker/nodes/output.py`): Exports full hierarchy as JSON with root_block_ids, blocks, and chunks.
- **`MarkdownRenderer.render(state, output_dir)`** (`src/chunker/nodes/output.py`): Writes linked markdown files -- `chunks/`, `blocks/`, and `index.md` with wiki-style `[[path]]` links.
- **`Pipeline.run(text, document_id) -> ProcessingResult`** and **`.resume() -> ProcessingResult`** (`src/chunker/pipeline.py`): Entry points for processing and checkpoint recovery.
- **LLM schemas** (`src/chunker/llm/schemas.py`): `CompletenessResult(complete: bool, boundary_phrase: str | None)`, `RewriteResult(rewritten_text: str, summary: str)`, `GroupingResult(groups: list[list[int]])`, `BlockSummaryResult(summary: str)`.

### Existing Flows

- **Main pipeline flow**: `Pipeline.run(text, doc_id)` -> `PipelineState.create()` -> while `state.has_more_text`: { `extractor.extract_next(state)` -> `rewriter.rewrite(chunk, state)` -> store chunk in `state.chunks` -> append to `state.pending_summaries[0]` -> `sweeper.sweep(state)` -> `checkpointer.save(state)` } -> `_write_output(state)` -> `ProcessingResult.from_state(state)`.
- **Chunk extraction flow**: Create `CursorWindow` at cursor -> auto-expand to `min_chunk_tokens` -> loop up to `max_expansion_attempts`: { if exceeds `max_chunk_tokens` -> force split at last sentence boundary; else ask LLM for completeness -> if complete, resolve boundary phrase (with one retry including verbatim snippet context) -> if phrase not found, sentence fallback; if not complete, expand window } -> create `Chunk` -> advance `cursor_position`.
- **Aggregation sweep flow**: Start at level 0 -> check if pending summaries exceed token threshold OR count threshold -> if yes: LLM groups summaries -> validate groups via `GroupValidator` (hard/soft violations, up to 5 attempts, fallback after 2 consecutive hard failures) -> create `SummaryBlock` per group -> set parent links on children -> promote blocks to next level's pending list -> repeat at next level until thresholds not met or single root remains.
- **Output flow**: `Pipeline._write_output(state)` -> `JsonExporter().write(state, output_dir/hierarchy.json)` -> `MarkdownRenderer().render(state, output_dir)` which creates `chunks/` dir, `blocks/` dir, writes one `.md` per chunk (title, parent link, summary, content, original sections), one `.md` per block (title, parent link, summary, children links), and `index.md` (root blocks in "Top-Level Summaries" section; orphan chunks either as top-level entries when no blocks exist, or in "Ungrouped Chunks" section when blocks also exist).
- **Resume flow**: `Pipeline.resume()` -> `checkpointer.load()` -> `_process(restored_state)` -> continues the main loop from where `cursor_position` left off, preserving all previously extracted chunks and blocks.

### Conventions

- **`from __future__ import annotations`** at the top of every `.py` file.
- **`@dataclass` for domain models and config** (`Chunk`, `SummaryBlock`, `PipelineState`, `ChunkerConfig`, `ModelProfile`, `ContextItem`, `ProcessingResult`, `ValidationResult`). Pydantic `BaseModel` only for LLM output schemas.
- **Manual JSON serialization** via `to_dict()/from_dict()/to_json()/from_json()` classmethods on all serializable dataclasses.
- **Private methods prefixed with `_`** consistently across all classes.
- **Structured JSON logging** -- all log messages use `json.dumps({...})` for machine-readable output via `logging.getLogger(__name__)`.
- **Explicit re-exports in `__init__.py`** -- subpackages (`nodes/`, `llm/`) define `__all__` with public names.
- **ID naming scheme** -- chunks: `chunk-NNN` (zero-padded 3 digits), blocks: `block-L{level}-NNN` (zero-padded 3 digits).
- **Wiki-style links `[[path]]`** without `.md` extensions in markdown output.
- **Dependency direction** -- `models` <- `state` <- `nodes` <- `pipeline` <- `cli`. No circular imports.
- **Testing conventions** -- pytest with test classes per feature (`TestJsonExporterExport`, `TestChunkMarkdown`, etc.), `_chunk()`/`_block()` helper factories for test data, `unittest.mock.MagicMock` + `patch` for isolating LLM/pipeline internals, `tmp_path` fixture for file I/O tests.
- **Tooling** -- `uv` package manager, `ruff` for linting/formatting, `just` for task running (`just test`, `just lint`, `just run`). Python 3.12+.
- **No docstrings, no `# type: ignore`** -- relies on type annotations and clear naming for readability.
- **Constructor injection** -- `Pipeline.__init__` creates and wires all node instances; nodes receive `LLMService`, `ChunkerConfig`, and/or `ContextBuilder` via constructor parameters.
