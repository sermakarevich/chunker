# Task 2 Completion: Create LLM service with structured output and retry logic

## Summary
Created `LLMService` class with 4 domain methods (check_completeness, rewrite_chunk, group_summaries, summarize_group), Pydantic response schemas, prompt templates as `.txt` files, custom retry loop with exponential backoff and error feedback, and structured JSON logging for every LLM call.

## Commits
- `a46f865` test(chunker): add failing tests for LLM service (FR-12, FR-15)
- `717390c` feat(chunker): implement LLM service with structured output and retry logic (FR-12, FR-15)

## Deviations
None

## Difficulties
None

## Notes
Prompt templates stored as plain `.txt` files in `src/chunker/llm/prompt_templates/` per user preference, loaded and cached by `prompts.py`.
