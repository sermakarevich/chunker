from __future__ import annotations

import base64
import json
import logging
import time
from pathlib import Path
from typing import TypeVar

from langchain_core.exceptions import OutputParserException
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from chunker.config import ChunkerConfig
from chunker.llm.prompts import (
    completeness_prompt,
    grouping_prompt,
    page_completeness_prompt,
    rewrite_prompt,
    synthesize_prompt,
)
from chunker.llm.schemas import (
    BlockContextResult,
    CompletenessResult,
    GroupingResult,
    PageCompletenessResult,
    RewriteResult,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

MAX_RETRIES = 3


def _image_mime_subtype(path: str) -> str:
    suffix = Path(path).suffix.lower().lstrip(".")
    if suffix in {"jpg", "jpeg"}:
        return "jpeg"
    return suffix or "png"


def _image_data_url(path: str) -> str:
    encoded = base64.b64encode(Path(path).read_bytes()).decode("ascii")
    return f"data:image/{_image_mime_subtype(path)};base64,{encoded}"


def _build_content(prompt: str, image_paths: list[str] | None):
    """Build a langchain message content for ``prompt`` plus optional images.

    With no images the content is the bare prompt string — byte-for-byte the
    pre-feature text path. With images it is a content list: one text part
    followed by one ``image_url`` data-URL part per image.
    """
    if not image_paths:
        return prompt
    content: list[dict] = [{"type": "text", "text": prompt}]
    for path in image_paths:
        content.append({"type": "image_url", "image_url": _image_data_url(path)})
    return content


class LLMValidationError(Exception):
    pass


class LLMService:
    def __init__(self, model: BaseChatModel, config: ChunkerConfig) -> None:
        self._model = model
        self._config = config

    def check_completeness(
        self,
        window_text: str,
        context_text: str,
        *,
        chunk_id: str | None = None,
    ) -> CompletenessResult:
        prompt = completeness_prompt(window_text, context_text)
        return self._call(prompt, CompletenessResult, "check_completeness", chunk_id)

    def check_page_completeness(
        self,
        window_text: str,
        *,
        chunk_id: str | None = None,
    ) -> PageCompletenessResult:
        """Decide whether a candidate page window ends at a page-edge boundary.

        Text-only: the window's extracted text is reasoned over directly and no
        image is ever sent to the model (page boundaries are detectable from
        text/headings; vision tokens are paid for only at rewrite).
        """
        prompt = page_completeness_prompt(window_text)
        return self._call(
            prompt, PageCompletenessResult, "check_page_completeness", chunk_id
        )

    def rewrite_chunk(
        self,
        chunk_text: str,
        context_text: str,
        *,
        image_paths: list[str] | None = None,
        chunk_id: str | None = None,
    ) -> RewriteResult:
        prompt = rewrite_prompt(
            chunk_text, context_text, self._config.rewrite_instructions
        )
        return self._call(
            prompt, RewriteResult, "rewrite_chunk", chunk_id, image_paths=image_paths
        )

    def group_summaries(
        self,
        summaries: list[dict],
        min_size: int,
        max_size: int,
        *,
        block_id: str | None = None,
    ) -> GroupingResult:
        summaries_text = "\n".join(
            f"[{i}] {s['summary']}" for i, s in enumerate(summaries)
        )
        prompt = grouping_prompt(summaries_text, min_size, max_size)
        return self._call(prompt, GroupingResult, "group_summaries", block_id)

    def synthesize_block(
        self,
        children_contexts: list[str],
        metadata_text: str,
        min_tokens: int,
        max_tokens: int,
        *,
        block_id: str | None = None,
    ) -> BlockContextResult:
        children_text = "\n\n---\n\n".join(children_contexts)
        prompt = synthesize_prompt(
            children_text,
            metadata_text,
            min_tokens,
            max_tokens,
            self._config.rewrite_instructions,
        )
        return self._call(prompt, BlockContextResult, "synthesize_block", block_id)

    def _call(
        self,
        prompt: str,
        schema: type[T],
        event: str,
        entity_id: str | None,
        *,
        image_paths: list[str] | None = None,
    ) -> T:
        messages = [HumanMessage(content=_build_content(prompt, image_paths))]
        last_error: str | None = None

        for attempt in range(MAX_RETRIES):
            if attempt > 0:
                time.sleep(2**attempt)
                messages.append(
                    HumanMessage(
                        content=(
                            f"Your previous response was invalid: {last_error}. "
                            "Please respond with valid JSON matching the required schema."
                        )
                    )
                )

            try:
                structured = self._model.with_structured_output(
                    schema, include_raw=True
                )
                response = structured.invoke(messages)
                parsed: T = response["parsed"]
                raw = response["raw"]

                self._log_call(event, entity_id, raw, parsed)
                return parsed

            except (OutputParserException, Exception) as exc:
                if isinstance(exc, LLMValidationError):
                    raise
                last_error = str(exc)
                logger.warning(
                    json.dumps(
                        {
                            "event": f"{event}_retry",
                            "entity_id": entity_id,
                            "attempt": attempt + 1,
                            "error": last_error,
                        }
                    )
                )

        raise LLMValidationError(
            f"LLM validation failed after {MAX_RETRIES} attempts: {last_error}"
        )

    def _log_call(
        self,
        event: str,
        entity_id: str | None,
        raw: object,
        parsed: BaseModel,
    ) -> None:
        token_usage = {}
        if hasattr(raw, "response_metadata"):
            token_usage = raw.response_metadata.get("token_usage", {})

        logger.info(
            json.dumps(
                {
                    "event": event,
                    "entity_id": entity_id,
                    "token_usage": token_usage,
                    "response": parsed.model_dump(),
                }
            )
        )
