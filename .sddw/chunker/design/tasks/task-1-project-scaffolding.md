# Task 1: Create project scaffolding, config, and domain models

## Trace
- **FR-IDs:** FR-14
- **Depends on:** none

## Files
- `pyproject.toml` — create
- `justfile` — create
- `src/chunker/__init__.py` — create
- `src/chunker/config.py` — create
- `src/chunker/models.py` — create
- `src/chunker/state.py` — create
- `tests/__init__.py` — create
- `tests/conftest.py` — create
- `tests/unit/__init__.py` — create
- `tests/unit/test_config.py` — create
- `tests/unit/test_models.py` — create
- `tests/unit/test_state.py` — create
- `tests/fixtures/agentic_rag_excerpt.txt` — create

## Architecture

### Components
- `ChunkerConfig`: all pipeline configuration with sensible defaults — new
- `ModelProfile`: per-model settings (context window, token limits, factor) — new
- `MODEL_PROFILES`: dict of known model profiles — new
- `Chunk`: represents an extracted chunk with source span, original/rewritten text, summary — new
- `SummaryBlock`: represents an aggregation node with level, children, summary — new
- `PipelineState`: mutable state tracked across the entire pipeline run — new

### Data Flow
CLI args / YAML → `ChunkerConfig` → passed to all components
`PipelineState` created at pipeline start → mutated by chunking/aggregation → serialized for checkpointing

## Data Models

### ChunkerConfig
```python
@dataclass
class ChunkerConfig:
    split_strategy: str = "sentences"
    min_chunk_tokens: int = 100
    max_chunk_tokens: int = 500
    max_expansion_attempts: int = 5

    summary_aggregation_threshold: int = 2000
    summary_count_threshold: int = 8
    min_group_size: int = 2
    max_group_size: int = 5

    context_budget_tokens: int = 2500

    checkpoint_path: str = "checkpoint.json"
    output_dir: str = "output"
    model: str = "qwen3:32b"
    ollama_base_url: str = "http://localhost:11434"
```

### ModelProfile
```python
@dataclass
class ModelProfile:
    context_window: int
    max_chunk_tokens: int
    context_budget_tokens: int
    token_factor: float
```

### MODEL_PROFILES
```python
MODEL_PROFILES: dict[str, ModelProfile] = {
    "qwen3:32b": ModelProfile(
        context_window=32768,
        max_chunk_tokens=500,
        context_budget_tokens=2500,
        token_factor=1.3,
    ),
    "gemma4:12b": ModelProfile(
        context_window=16384,
        max_chunk_tokens=400,
        context_budget_tokens=2000,
        token_factor=1.2,
    ),
}
```

### Chunk
```python
@dataclass
class Chunk:
    id: str
    source_span: tuple[int, int]
    original_text: str
    rewritten_text: str
    summary: str
    parent_block_id: str | None
    forced_split: bool
    metadata: dict
```

### SummaryBlock
```python
@dataclass
class SummaryBlock:
    id: str
    level: int
    summary: str
    child_ids: list[str]
    parent_block_id: str | None
    metadata: dict
```

### PipelineState
```python
@dataclass
class PipelineState:
    document_id: str
    source_text: str
    cursor_position: int
    chunks: dict[str, Chunk]
    blocks: dict[str, SummaryBlock]
    pending_summaries: dict[int, list[str]]
    chunk_counter: int
    block_counters: dict[int, int]
```

## Design Decisions

### Token counting: word approximation
- **Chosen:** `len(text.split()) * token_factor` where `token_factor` comes from model profile
- **Rationale:** Thresholds are heuristics; exact counts not needed. Zero external dependencies. Per-model factor allows tuning.
- **Rejected:** LangChain `get_num_tokens()` — adds model dependency to a utility function; tiktoken — irrelevant for local models

### Model profiles: Python dict
- **Chosen:** `MODEL_PROFILES` dict in `config.py`
- **Rationale:** Simple, no file parsing. Adding a model = adding a dict entry.
- **Rejected:** YAML config file — adds parsing complexity for a small data structure

## Acceptance Criteria

### FR-14: Model-dependent configuration
- GIVEN model "qwen3:32b" is configured
- WHEN defaults are loaded
- THEN token limits and context window SHALL match that model's profile

- GIVEN a new model is added
- WHEN a profile is registered
- THEN the system SHALL use it without code changes beyond the profile definition

## Done Criteria
- [ ] `uv init` project with `pyproject.toml` including dependencies: `langchain-ollama`, `pydantic`, `pytest`
- [ ] `justfile` with targets: `test`, `lint`, `run`
- [ ] `ChunkerConfig` dataclass with all fields and defaults
- [ ] `ModelProfile` dataclass and `MODEL_PROFILES` dict with qwen3:32b and gemma4:12b
- [ ] `ChunkerConfig.from_model()` class method that applies profile defaults
- [ ] `estimate_tokens(text, factor)` utility function
- [ ] `Chunk` and `SummaryBlock` dataclasses with all fields
- [ ] `PipelineState` dataclass with factory method for initial state
- [ ] `PipelineState.has_more_text` property
- [ ] All models are JSON-serializable (for checkpointing)
- [ ] Test fixture: `agentic_rag_excerpt.txt` with ~2000 words extracted from the Agentic RAG paper
- [ ] All tests pass with `uv run pytest`
