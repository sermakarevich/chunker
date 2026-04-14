# Task 6: Implement summary aggregation with grouping and recursive level sweep

## Trace
- **FR-IDs:** FR-06, FR-07, FR-08, FR-17
- **Depends on:** task-1, task-2

## Files
- `src/chunker/nodes/aggregation.py` — create
- `tests/unit/test_aggregation.py` — create

## Architecture

### Components
- `AggregationSweeper`: checks all levels bottom-up after each chunk, triggers aggregation where thresholds exceeded — new
- `GroupValidator`: validates contiguity, min/max group size constraints — new

### Data Flow
```
PipelineState.pending_summaries[level] → check thresholds
  → (exceeded) → LLMService.group_summaries(summaries, constraints) → GroupingResult
    → GroupValidator.validate(groups) 
      → (valid) → LLMService.summarize_group(group) per group → create SummaryBlocks
        → add block summaries to pending_summaries[level+1]
        → clear pending_summaries[level]
      → (invalid: min_size) → re-prompt with constraint
      → (invalid: max_size) → re-prompt asking for subdivision, accept if declined
      → (2 consecutive hard failures) → even_split_fallback → create SummaryBlocks
  → (below both) → skip, move to next level
```

Sweep is bottom-up: check level 0 first, then level 1, etc. A newly created level N+1 block is immediately available for the next level's threshold check in the same sweep.

## Contracts

### AggregationSweeper
```python
class AggregationSweeper:
    def __init__(self, llm_service: LLMService, config: ChunkerConfig): ...

    def sweep(self, state: PipelineState) -> None
```

Mutates `state` in place: creates `SummaryBlock` entries in `state.blocks`, updates `pending_summaries`, sets `parent_block_id` on children.

### GroupValidator
```python
class GroupValidator:
    def __init__(self, min_size: int, max_size: int): ...

    def validate(self, groups: list[list[str]], ordered_ids: list[str]) -> ValidationResult
```

Checks:
1. All groups are contiguous runs of `ordered_ids` (FR-17)
2. No group has fewer than `min_size` items (hard constraint)
3. Groups exceeding `max_size` flagged as soft violation

```python
@dataclass
class ValidationResult:
    valid: bool
    hard_violations: list[str]
    soft_violations: list[str]
```

### Even-split fallback
```python
def even_split_fallback(ids: list[str], target_size: int = 4) -> list[list[str]]
```
Splits `ids` into `ceil(len(ids) / target_size)` contiguous groups of roughly equal size.

## Design Decisions

### Aggregation sweep: interleaved with chunking
- **Chosen:** After every chunk extraction, sweep all levels bottom-up checking thresholds
- **Rationale:** Builds hierarchy incrementally. Later chunks benefit from higher-level context (FR-09). Simpler main loop than two-phase separation.
- **Rejected:** Two-phase (all chunks first, then aggregate) — delays hierarchy building, worse context for later chunks

### Group validation: hard vs soft constraints
- **Chosen:** `min_group_size` is hard (reject and re-prompt), `max_group_size` is soft (re-prompt but accept if model declines). After 2 consecutive hard failures, fall back to even-sized grouping.
- **Rationale:** Matches FR-07 exactly. Even-split fallback ensures progress.

### Contiguity validation
- **Chosen:** Validate that each group is a contiguous slice of the ordered summary list by checking that flattened groups == original ordered list
- **Rationale:** FR-17 prohibits non-contiguous or reordered groupings. Flattening and comparing to original order catches both violations in one check.

## Acceptance Criteria

### FR-06: Dual-trigger aggregation
- GIVEN cumulative tokens of pending summaries exceed `summary_aggregation_threshold`
- THEN aggregation SHALL begin

- GIVEN pending summary count exceeds `summary_count_threshold`
- THEN aggregation SHALL begin even if token threshold is not reached

- GIVEN both thresholds are not exceeded after all chunks processed
- THEN no aggregation SHALL occur
- AND the output SHALL be a flat list of chunks with no SummaryBlock layer

### FR-07: Group size constraints
- GIVEN the LLM proposes a group with fewer than `min_group_size` summaries
- THEN the system SHALL reject and re-prompt with the constraint stated explicitly

- GIVEN the LLM proposes a group exceeding `max_group_size`
- THEN the system SHALL re-prompt asking for subdivision
- AND accept the original if the model declines

- GIVEN two consecutive hard validation failures
- THEN the system SHALL fall back to even-sized grouping
- AND log `WARN: grouping_fallback`

### FR-08: Recursive aggregation
- GIVEN level N blocks are produced and their summaries exceed either aggregation threshold
- THEN the system SHALL aggregate them into level N+1 blocks

- GIVEN level N blocks' summaries fall below both thresholds
- THEN recursion SHALL stop and those blocks SHALL be the root blocks

- GIVEN aggregation reduces to a single block
- THEN that block SHALL be the root and recursion SHALL stop

### FR-17: Contiguous groups only
- GIVEN a grouping response from the LLM
- WHEN groups are validated
- THEN no group SHALL contain non-contiguous summaries
- AND reordering or skipping SHALL NOT be permitted

## Done Criteria
- [ ] `AggregationSweeper.sweep()` checks all levels bottom-up
- [ ] Token threshold trigger works (`summary_aggregation_threshold`)
- [ ] Count threshold trigger works (`summary_count_threshold`)
- [ ] No aggregation when both thresholds not exceeded
- [ ] `GroupValidator` rejects non-contiguous groups
- [ ] `GroupValidator` rejects groups below `min_group_size`
- [ ] `GroupValidator` flags groups above `max_group_size` as soft violation
- [ ] Re-prompt on hard violation with explicit constraint
- [ ] Re-prompt on soft violation, accept if model declines subdivision
- [ ] Even-split fallback after 2 consecutive hard failures, logs `WARN: grouping_fallback`
- [ ] SummaryBlocks created with correct `level`, `child_ids`, `parent_block_id`
- [ ] Children's `parent_block_id` updated when block created
- [ ] Recursive aggregation continues until single root or thresholds not exceeded
- [ ] Unit tests with mock LLMService: threshold triggers, grouping validation, retry flows, fallback, recursive levels
- [ ] All tests pass
