# Task 8: Implement pipeline orchestration and CLI entry point

## Trace
- **FR-IDs:** FR-01, FR-06, FR-08, FR-12, FR-13, FR-14
- **Depends on:** task-4, task-5, task-6, task-7

## Files
- `src/chunker/pipeline.py` — create
- `src/chunker/cli.py` — create
- `tests/unit/test_pipeline.py` — create
- `tests/integration/__init__.py` — create
- `tests/integration/test_pipeline_e2e.py` — create
- `justfile` — modify (add `run` target with actual command)

## Architecture

### Components
- `Pipeline`: main orchestrator — creates LLMService, ChunkExtractor, ChunkRewriter, AggregationSweeper, Checkpointer; runs the main processing loop — new
- CLI entry point: parses arguments, loads config, creates Pipeline, calls run/resume — new

### Data Flow
```
CLI → parse args → ChunkerConfig (apply model profile) → Pipeline
Pipeline.run(text, document_id):
  state = PipelineState.initial(text, document_id)
  while state.has_more_text:
    chunk = extractor.extract_next(state)           # Task 4
    chunk = rewriter.rewrite(chunk, state)           # Task 5
    state.add_chunk(chunk)                           # add to chunks dict + pending_summaries[0]
    sweeper.sweep(state)                             # Task 6
    checkpointer.save(state)                         # Task 7
  return ProcessingResult(state)

Pipeline.resume(checkpoint_path):
  state = checkpointer.load()
  # continue the same loop from restored cursor_position
```

## Contracts

### Pipeline
```python
class Pipeline:
    def __init__(self, config: ChunkerConfig): ...

    def run(self, text: str, document_id: str) -> ProcessingResult
    def resume(self) -> ProcessingResult
```

`__init__` wires up:
- `ChatOllama(model=config.model, base_url=config.ollama_base_url)`
- `LLMService(model, config)`
- `ChunkExtractor(llm_service, config)`
- `ChunkRewriter(llm_service, context_builder)`
- `AggregationSweeper(llm_service, config)`
- `Checkpointer(config.checkpoint_path)`

### ProcessingResult
```python
@dataclass
class ProcessingResult:
    state: PipelineState
    total_chunks: int
    total_blocks: int
    root_block_ids: list[str]
    warnings: list[str]
```

### CLI
```
chunker run <input_file> [--model MODEL] [--config CONFIG] [--output-dir DIR]
chunker resume <checkpoint_file> [--output-dir DIR]
```

Uses `argparse`. Reads input file as plain text. Applies model profile from `MODEL_PROFILES` if available.

## Design Decisions

### Pipeline as simple class with main loop
- **Chosen:** Plain Python class with a while loop, no framework
- **Rationale:** The orchestration is a single loop with an inner aggregation sweep. LangGraph would add complexity without benefit. All complexity lives inside the components (extractor, rewriter, sweeper), not in the flow.
- **Rejected:** LangGraph StateGraph — over-engineered for this flow shape

### Checkpoint on every iteration
- **Chosen:** `checkpointer.save(state)` after each chunk+sweep cycle completes
- **Rationale:** Covers FR-13's requirement for checkpoint after each chunk and each block (sweep may create blocks). One save per iteration captures both.

## Acceptance Criteria

### FR-01 + FR-06 + FR-08: End-to-end pipeline flow
- GIVEN a document text
- WHEN `Pipeline.run()` completes
- THEN all text SHALL be processed into chunks
- AND summary aggregation SHALL have been applied where thresholds were exceeded
- AND the result SHALL contain chunks, blocks (if any), and root block IDs

### FR-13: Resume from checkpoint
- GIVEN a pipeline that was interrupted after processing 5 chunks
- WHEN `Pipeline.resume()` is called with the checkpoint
- THEN processing SHALL continue from chunk 6 without reprocessing chunks 1-5

### FR-14: Model profile applied
- GIVEN `--model qwen3:32b` is passed
- WHEN config is created
- THEN `max_chunk_tokens`, `context_budget_tokens`, and `token_factor` SHALL use qwen3:32b profile values

## Done Criteria
- [ ] `Pipeline.__init__()` wires up all components
- [ ] `Pipeline.run()` processes all text through the main loop
- [ ] Main loop: extract → rewrite → add to state → sweep → checkpoint
- [ ] `Pipeline.resume()` restores state and continues processing
- [ ] `ProcessingResult` returned with correct counts and root block IDs
- [ ] CLI with `run` and `resume` subcommands
- [ ] CLI applies model profile when `--model` specified
- [ ] Unit tests with all components mocked: loop termination, resume from mid-document
- [ ] Integration test with mock LLM: full document → chunks + blocks → correct hierarchy
- [ ] `justfile` updated with working `run` target
- [ ] All tests pass
