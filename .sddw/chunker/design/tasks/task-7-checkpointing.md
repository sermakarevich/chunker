# Task 7: Implement checkpointing and resumption

## Trace
- **FR-IDs:** FR-13
- **Depends on:** task-1

## Files
- `src/chunker/checkpoint.py` — create
- `tests/unit/test_checkpoint.py` — create

## Architecture

### Components
- `Checkpointer`: serializes/deserializes `PipelineState` to/from JSON file — new

### Data Flow
```
PipelineState → Checkpointer.save(state, path) → JSON file on disk
JSON file → Checkpointer.load(path) → PipelineState (restored)
```

## Contracts

### Checkpointer
```python
class Checkpointer:
    def __init__(self, path: Path): ...

    def save(self, state: PipelineState) -> None
    def load(self) -> PipelineState
    def exists(self) -> bool
```

`save()`:
- Serializes `PipelineState` to JSON (including all `Chunk` and `SummaryBlock` objects)
- Writes atomically (write to temp file, then rename) to prevent corruption on crash
- Called after each completed chunk and each completed SummaryBlock

`load()`:
- Deserializes JSON back to `PipelineState` with fully reconstructed `Chunk` and `SummaryBlock` objects
- Validates that `document_id` matches the current run

`exists()`:
- Returns `True` if a checkpoint file exists at the configured path

## Design Decisions

### Checkpoint format: JSON
- **Chosen:** JSON file with atomic write (temp file + rename)
- **Rationale:** Human-readable, easy to debug, state is not large enough to warrant binary format. Atomic write prevents corruption.
- **Rejected:** SQLite — overkill for a single state blob; pickle — not human-readable, security concerns

### Checkpoint granularity: after each chunk and block
- **Chosen:** Checkpoint after every completed chunk extraction/rewrite and after every SummaryBlock creation
- **Rationale:** FR-13 explicitly requires this granularity. Ensures minimal rework on resume.

### Serialization: dataclass to/from dict
- **Chosen:** Custom `to_dict()` / `from_dict()` methods on `PipelineState`, `Chunk`, `SummaryBlock`
- **Rationale:** Full control over serialization. Tuples (source_span) need explicit handling. No external serialization library needed.
- **Rejected:** Pydantic models for domain objects — adds coupling for a simple serialization need; dataclasses-json — extra dependency

## Acceptance Criteria

### FR-13: Checkpointing
- GIVEN a chunk is confirmed and rewritten
- THEN the full `PipelineState` SHALL be serialized to `checkpoint_path` before advancing the cursor

- GIVEN an existing checkpoint for `document_id`
- WHEN the system starts
- THEN it SHALL restore state and resume from `cursor_position`

- GIVEN a SummaryBlock is created
- THEN the state SHALL be checkpointed

## Done Criteria
- [ ] `Checkpointer.save()` serializes full state to JSON
- [ ] Atomic write: temp file + rename
- [ ] `Checkpointer.load()` deserializes back to `PipelineState` with all nested objects
- [ ] `source_span` tuples survive round-trip serialization
- [ ] `Checkpointer.exists()` checks file presence
- [ ] `to_dict()` and `from_dict()` on `PipelineState`, `Chunk`, `SummaryBlock`
- [ ] Round-trip test: save → load → compare equality
- [ ] Validation: document_id mismatch raises error on load
- [ ] All tests pass
