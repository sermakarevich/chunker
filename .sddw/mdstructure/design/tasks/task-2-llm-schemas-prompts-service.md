# Task 2: Update LLM schemas, prompts, and service

## Trace
- **FR-IDs:** FR-05, FR-06, FR-08, FR-14
- **Depends on:** task-1

## Files
- `src/chunker/llm/schemas.py` — modify
- `src/chunker/llm/prompt_templates/rewrite.txt` — modify
- `src/chunker/llm/prompt_templates/summarize.txt` — modify (rename to `synthesize.txt`)
- `src/chunker/llm/prompts.py` — modify
- `src/chunker/llm/service.py` — modify
- `tests/unit/test_llm_service.py` — update (interface change)

## Architecture

### Components
- `RewriteResult` (Pydantic schema): LLM output for chunk rewriting — modified
- `BlockContextResult` (Pydantic schema): LLM output for block synthesis — new (replaces `BlockSummaryResult`)
- `LLMService`: LLM interaction facade — modified
- Prompt templates: `.txt` files with format interpolation — modified

### Data Flow
Prompt template (`.txt`) → `prompts.py` loader → `LLMService` method → `langchain.with_structured_output(schema)` → Pydantic schema instance

## Contracts

### Internal Interfaces
- `RewriteResult(context: str, summary: str, filename: str)`: Pydantic schema for chunk rewrite output
  - Pre: LLM returns valid JSON matching schema
  - Post: `context` is self-sufficient rewrite, `summary` is 1-2 sentences, `filename` is descriptive slug
- `BlockContextResult(context: str, summary: str, filename: str)`: Pydantic schema for block synthesis output (replaces `BlockSummaryResult`)
  - Pre: LLM returns valid JSON matching schema
  - Post: `context` is chunk-sized synthesis, `summary` is 1-2 sentences, `filename` is descriptive slug
- `LLMService.rewrite_chunk(chunk_text: str, context_text: str) -> RewriteResult`: unchanged signature, updated return schema
  - Pre: chunk_text and context_text provided
  - Post: returns RewriteResult with `context`, `summary`, `filename`
- `LLMService.synthesize_block(children_contexts: list[str], metadata_text: str, min_tokens: int, max_tokens: int) -> BlockContextResult`: replaces `summarize_group`
  - Pre: children_contexts is non-empty list of context strings, min_tokens/max_tokens define target range
  - Post: returns BlockContextResult with chunk-sized `context`, short `summary`, descriptive `filename`
- `rewrite_prompt(chunk_text: str, context_text: str) -> str`: unchanged signature, updated template
- `synthesize_prompt(children_text: str, metadata_text: str, min_tokens: int, max_tokens: int) -> str`: replaces `summarize_prompt`

## Design Decisions

### Prompt template: inline info-persistence directives vs shared preamble
- **Chosen:** Inline directives in each content-producing prompt template
- **Rationale:** Only 2 content-producing prompts (rewrite, synthesize). Inline is explicit and avoids abstraction for 2 cases.
- **Rejected:** Shared preamble/suffix — premature abstraction for 2 templates

### Schema rename: BlockSummaryResult → BlockContextResult
- **Chosen:** Rename to `BlockContextResult` with `context`, `summary`, `filename` fields
- **Rationale:** The output is now a full context synthesis, not just a summary. Name should reflect the primary output.
- **Rejected:** Keep `BlockSummaryResult` name — misleading since `context` is the primary output

### Service method rename: summarize_group → synthesize_block
- **Chosen:** Rename to `synthesize_block` with expanded signature
- **Rationale:** The method now produces a full block context from children's contexts + metadata, not just a summary from summaries. Reflects the richer input/output.
- **Rejected:** Keep `summarize_group` name — misleading given the expanded behavior

## Acceptance Criteria

### FR-05: Chunk rewrite prompt
- GIVEN a chunk with pronouns and implied references
- WHEN the rewrite prompt runs
- THEN the `context` field SHALL resolve references and be self-sufficient
- AND SHALL preserve all specific facts, numbers, names from the original

- GIVEN a rewritten chunk
- THEN the `summary` SHALL be 1-2 sentences
- AND SHALL contain specific facts, not vague generalizations

- GIVEN a rewritten chunk about attention mechanisms in transformers
- THEN the `filename` SHALL be a descriptive slug (e.g., `attention-mechanism-overview`)

### FR-06: Block context generation
- GIVEN a block being generated from 3 child chunks
- WHEN the block context prompt runs
- THEN it SHALL receive children's `context` fields, the previous chunk/block's context, and latest higher-level block contexts as metadata

- GIVEN `min_chunk_tokens=2000` and `max_chunk_tokens=4000`
- WHEN the block context prompt runs
- THEN the prompt SHALL instruct the LLM to produce context in the 2000-4000 token range

- GIVEN the prompt completes
- THEN the block SHALL have `context`, `summary`, and `filename`

### FR-08: Information persistence directive
- GIVEN any LLM prompt that produces `context` or `summary`
- THEN the prompt text SHALL contain explicit instructions to preserve all relevant facts, numbers, names, and relationships

### FR-14: Information persistence prohibition
- GIVEN a chunk `context` produced by the LLM
- THEN it SHALL NOT reduce specific facts to vague generalizations

## Done Criteria
- [ ] `RewriteResult` has `context`, `summary`, `filename` fields; `rewritten_text` field removed
- [ ] `BlockContextResult` replaces `BlockSummaryResult` with `context`, `summary`, `filename` fields
- [ ] `rewrite.txt` template produces `context`/`summary`/`filename` with info-persistence directives
- [ ] `synthesize.txt` template (replaces `summarize.txt`) takes children's contexts + metadata + token range, produces `context`/`summary`/`filename` with info-persistence directives
- [ ] `prompts.py` has `synthesize_prompt()` replacing `summarize_prompt()`
- [ ] `LLMService.rewrite_chunk()` returns updated `RewriteResult`
- [ ] `LLMService.synthesize_block()` replaces `summarize_group()` with new signature
- [ ] Both content-producing prompt templates contain explicit info-persistence directives
- [ ] `test_llm_service.py` passes with updated schemas and method names
- [ ] No reference to `rewritten_text`, `BlockSummaryResult`, `summarize_group`, or `summarize_prompt` remains in LLM package or its tests
