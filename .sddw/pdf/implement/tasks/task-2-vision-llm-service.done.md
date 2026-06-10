# Task 2 Completion: Vision-capable LLM service

## Summary
Taught the single `LLMService` abstraction to (a) judge page-window boundaries
from text via a new text-only `check_page_completeness` returning
`PageCompletenessResult(complete, split_after_page)`, and (b) read page images
during rewrite — `_call` now accepts `image_paths` and builds a multimodal
`HumanMessage` (one text part + one `image_url` data-URL part per image), with
`rewrite_chunk` forwarding the images. Added the `page_completeness.txt` prompt
and vision transcription rules to `rewrite.txt`. When no images are passed the
message content is the bare prompt string, so the text path is unchanged.

## Commits
- `5c2c40b` feat(pdf): add vision-capable LLM service for page boundaries and image rewrite (FR-04, FR-05)

## Deviations
- **Rule 3: Blocking** — the new prompt template
  `src/chunker/llm/prompt_templates/page_completeness.txt` is matched by the
  `*.txt` rule at `.gitignore:18`, so `git add` skipped it. Force-added with
  `git add -f` as essential source (the already-tracked `completeness.txt` /
  `rewrite.txt` / etc. predate that ignore rule). Mentioned in the commit message.

## Difficulties
- **Smoke script import path** — running the manual smoke script from `/tmp`
  failed with `ModuleNotFoundError: chunker` because the package is resolved via
  pytest's `pythonpath=src`, not an editable install. Resolved by running with
  `PYTHONPATH=src uv run python ...`.

## Notes
- **Smoke-test result (real model, `gemma4:latest`):** PASSED both gates.
  `with_structured_output(..., include_raw=True)` worked *with* image content —
  **the documented JSON-`format` fallback was NOT needed** and was not
  implemented. On AI-Index page 17 (a chart page) the rewritten `context`
  captured chart data-labels (Canada=1, France=1, Hong Kong=1, Singapore=1,
  UK=0) that are absent from the 416-word text layer, demonstrating FR-05. The
  smoke script was run manually and not committed (per the chosen option).
- **Image content format:** followed the design literally —
  `{"type": "image_url", "image_url": "data:image/<fmt>;base64,<b64>"}` (flat
  string, not the nested `{"url": ...}` form). Confirmed accepted by
  langchain-ollama + `gemma4:latest`.
- **Contract for Task 3 (extractor):** `check_page_completeness` expects the
  window text to delimit pages with `=== Page N ===` markers and returns
  `split_after_page` as the 1-based number of the chunk's **last** page (`None`
  ⇒ end at the window's last page). Task 3 must emit those page markers and
  clamp out-of-range `split_after_page` values to the window range.
- `_call` retry/correction messages remain text-only by design (images are sent
  once on the first attempt); structured output, `MAX_RETRIES`, and logging are
  untouched. JPEG paths map to `image/jpeg`; all other suffixes pass through
  (default `png`).
- `just test` (277 passed) and `just lint` are green.
