# Task 10: Wire JsonExporter and MarkdownRenderer into Pipeline and CLI

## Trace
- **FR-IDs:** FR-10, FR-11
- **Depends on:** task-8, task-9

## Files
- `src/chunker/pipeline.py` — modify
- `src/chunker/cli.py` — modify
- `tests/unit/test_pipeline.py` — modify
- `tests/integration/test_pipeline_e2e.py` — modify

## Architecture

### Components
- `Pipeline`: add output generation after processing loop completes — modified
- CLI `run_command`: pass `output_dir` to pipeline, call exporters — modified
- CLI `resume_command`: same output generation after resume — modified

### Data Flow
```
Pipeline._process(state) → ProcessingResult
  → JsonExporter().write(state, output_dir / "hierarchy.json")
  → MarkdownRenderer().render(state, output_dir)
```

## Contracts

### Pipeline
```python
class Pipeline:
    def run(self, text: str, document_id: str) -> ProcessingResult:
        # ... existing processing loop ...
        self._write_output(state)
        return ProcessingResult.from_state(state)

    def _write_output(self, state: PipelineState) -> None:
        output_dir = Path(self._config.output_dir)
        JsonExporter().write(state, output_dir / "hierarchy.json")
        MarkdownRenderer().render(state, output_dir)
```

## Design Decisions

### Output generation in Pipeline vs CLI
- **Chosen:** Pipeline calls exporters in `_process()` after the loop
- **Rationale:** Both `run` and `resume` should produce output. Placing it in `_process()` covers both paths without duplication.
- **Rejected:** CLI calls exporters — duplicates logic across `run_command` and `resume_command`

## Acceptance Criteria

### FR-10: JSON output
- GIVEN processing completes
- WHEN `Pipeline.run()` returns
- THEN `output_dir/hierarchy.json` SHALL exist with correct schema

### FR-11: Linked markdown rendering
- GIVEN processing completes
- WHEN `Pipeline.run()` returns
- THEN `output_dir/` SHALL contain `index.md`, `chunks/`, and `blocks/` directories with one file per node

## Done Criteria
- [ ] `Pipeline._process()` calls `JsonExporter.write()` and `MarkdownRenderer.render()` after loop
- [ ] `output_dir/hierarchy.json` produced with correct schema
- [ ] `output_dir/index.md`, `chunks/`, `blocks/` directories created
- [ ] `resume` path also produces output
- [ ] Unit tests verify output files are created after pipeline run
- [ ] Integration test verifies output files contain correct data
- [ ] All tests pass
