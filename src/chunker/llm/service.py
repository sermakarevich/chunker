from __future__ import annotations

import json
import logging
import time
from typing import TypeVar

from langchain_core.exceptions import OutputParserException
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from chunker.config import ChunkerConfig
from chunker.llm.prompts import (
    completeness_prompt,
    grouping_prompt,
    rewrite_prompt,
    summarize_prompt,
)
from chunker.llm.schemas import (
    BlockSummaryResult,
    CompletenessResult,
    GroupingResult,
    RewriteResult,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

MAX_RETRIES = 3


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

    def rewrite_chunk(
        self,
        chunk_text: str,
        context_text: str,
        *,
        chunk_id: str | None = None,
    ) -> RewriteResult:
        prompt = rewrite_prompt(chunk_text, context_text)
        return self._call(prompt, RewriteResult, "rewrite_chunk", chunk_id)

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

    def summarize_group(
        self,
        summaries: list[str],
        *,
        block_id: str | None = None,
    ) -> str:
        summaries_text = "\n".join(f"- {s}" for s in summaries)
        prompt = summarize_prompt(summaries_text)
        result = self._call(prompt, BlockSummaryResult, "summarize_group", block_id)
        return result.summary

    def _call(
        self,
        prompt: str,
        schema: type[T],
        event: str,
        entity_id: str | None,
    ) -> T:
        messages = [HumanMessage(content=prompt)]
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
