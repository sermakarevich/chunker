# Task 2: Create LLM service with structured output and retry logic

## Trace
- **FR-IDs:** FR-12, FR-15
- **Depends on:** task-1

## Files
- `src/chunker/llm/__init__.py` — create
- `src/chunker/llm/service.py` — create
- `src/chunker/llm/schemas.py` — create
- `src/chunker/llm/prompts.py` — create
- `tests/unit/test_llm_service.py` — create

## Architecture

### Components
- `LLMService`: wraps LangChain `BaseChatModel` with domain-specific methods, retry logic, and structured logging — new
- `CompletenessResult`, `RewriteResult`, `GroupingResult`, `BlockSummaryResult`: Pydantic response schemas for structured output — new
- Prompt templates: string templates for each LLM call type — new

### Data Flow
`LLMService.check_completeness(text, context)` → build prompt from template → `ChatOllama.with_structured_output(CompletenessResult)` → validate → retry with error feedback if invalid → return `CompletenessResult` + emit structured log entry

## Contracts

### LLMService
```python
class LLMService:
    def __init__(self, model: BaseChatModel, config: ChunkerConfig): ...

    def check_completeness(self, window_text: str, context_text: str) -> CompletenessResult
    def rewrite_chunk(self, chunk_text: str, context_text: str) -> RewriteResult
    def group_summaries(self, summaries: list[dict], min_size: int, max_size: int) -> GroupingResult
    def summarize_group(self, summaries: list[str]) -> str
```

Each method:
1. Builds prompt from template + inputs
2. Calls model with structured output schema
3. On schema validation failure: retries up to 3 times with exponential backoff, appending validation error to prompt
4. Emits structured log entry (event type, token counts, response, warnings)

### Response Schemas
```python
class CompletenessResult(BaseModel):
    complete: bool
    boundary_phrase: str | None

class RewriteResult(BaseModel):
    rewritten_text: str
    summary: str

class GroupingResult(BaseModel):
    groups: list[list[int]]

class BlockSummaryResult(BaseModel):
    summary: str
```

## Design Decisions

### LLM retry: own retry loop with error feedback
- **Chosen:** Custom retry loop (max 3 attempts, exponential backoff) that appends validation error message to the re-prompt
- **Rationale:** FR-12 requires "include validation error feedback in the retry prompt." LangChain's `.with_retry()` just repeats the same prompt without error context.
- **Rejected:** LangChain built-in retry — no error feedback in re-prompt

### Structured logging format
- **Chosen:** Python `logging` module with JSON-formatted structured entries
- **Rationale:** FR-15 requires structured log entries with: event type, chunk/block ID, token counts, model response, context items, warnings. Standard logging with a JSON formatter keeps it simple.
- **Rejected:** Custom logging framework — unnecessary complexity

## Acceptance Criteria

### FR-12: Provider-agnostic LLMClient
- GIVEN no explicit provider configuration
- WHEN the system starts
- THEN it SHALL use the Ollama implementation (ChatOllama)

- GIVEN a response schema
- WHEN the LLM responds with invalid JSON or schema-violating output
- THEN the system SHALL retry with exponential backoff (up to 3 attempts)
- AND include validation error feedback in the retry prompt

### FR-15: Structured logging
- GIVEN any LLM call
- THEN a structured log entry SHALL be emitted with: event type, chunk/block ID, token counts, model response, context items injected, and any warnings

## Done Criteria
- [ ] `LLMService` class with 4 domain methods
- [ ] Pydantic schemas for all 4 response types
- [ ] Retry loop: max 3 attempts, exponential backoff, validation error appended to re-prompt
- [ ] Structured log entry emitted for every LLM call
- [ ] Prompt templates for: completeness check, chunk rewrite, summary grouping, group summarization
- [ ] Unit tests with mock `BaseChatModel` covering: valid response, retry on invalid JSON, retry exhaustion, all 4 methods
- [ ] All tests pass
