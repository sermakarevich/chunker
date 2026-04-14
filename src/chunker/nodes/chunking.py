from __future__ import annotations

import json
import logging

from chunker.config import ChunkerConfig
from chunker.llm.service import LLMService
from chunker.models import Chunk
from chunker.splitter import CursorWindow, TextSplitter
from chunker.state import PipelineState

logger = logging.getLogger(__name__)


def validate_boundary_phrase(phrase: str, remaining_text: str) -> int | None:
    """Return the index where *phrase* starts in *remaining_text*, or None."""
    idx = remaining_text.find(phrase)
    return idx if idx >= 0 else None


class ChunkExtractor:
    def __init__(self, llm_service: LLMService, config: ChunkerConfig) -> None:
        self._llm = llm_service
        self._config = config

    def extract_next(self, state: PipelineState) -> Chunk:
        splitter = TextSplitter(self._config.split_strategy)
        window = CursorWindow(
            state.source_text, state.cursor_position, splitter, self._config
        )

        state.chunk_counter += 1
        chunk_id = f"chunk-{state.chunk_counter:03d}"
        forced_split = False
        attempts = 0

        while attempts < self._config.max_expansion_attempts:
            if window.token_count >= self._config.max_chunk_tokens:
                forced_split = True
                self._force_split(window, chunk_id, "max_tokens")
                break

            result = self._llm.check_completeness(
                window.text, "", chunk_id=chunk_id
            )
            attempts += 1

            if result.complete:
                if result.boundary_phrase:
                    boundary = self._resolve_boundary(
                        window, state.source_text, result.boundary_phrase, chunk_id
                    )
                    if boundary is not None:
                        window.set_end(boundary)
                        break
                    # Both validation attempts failed — sentence fallback
                    self._sentence_fallback(window)
                    logger.warning(
                        json.dumps(
                            {"event": "phrase_not_found", "chunk_id": chunk_id}
                        )
                    )
                break
            else:
                if not window.expand():
                    forced_split = True
                    self._force_split(window, chunk_id, "cannot_expand")
                    break
        else:
            # max_expansion_attempts exhausted
            forced_split = True
            self._force_split(window, chunk_id, "max_attempts")

        original_text = state.source_text[window.start : window.end]
        chunk = Chunk(
            id=chunk_id,
            source_span=(window.start, window.end),
            original_text=original_text,
            rewritten_text="",
            summary="",
            parent_block_id=None,
            forced_split=forced_split,
            metadata={},
        )
        state.cursor_position = window.end
        return chunk

    def _resolve_boundary(
        self,
        window: CursorWindow,
        source_text: str,
        phrase: str,
        chunk_id: str,
    ) -> int | None:
        remaining = source_text[window.start :]
        idx = validate_boundary_phrase(phrase, remaining)
        if idx is not None:
            return window.start + idx

        # Retry with explicit verbatim instruction
        snippet_start = max(window.start, window.end - 200)
        snippet_end = min(len(source_text), window.end + 200)
        snippet = source_text[snippet_start:snippet_end]
        retry_context = (
            "Return a phrase that appears EXACTLY and VERBATIM "
            "in the following text. "
            f"Text near the boundary:\n{snippet}"
        )
        retry_result = self._llm.check_completeness(
            window.text, retry_context, chunk_id=chunk_id
        )
        if retry_result.boundary_phrase:
            idx = validate_boundary_phrase(retry_result.boundary_phrase, remaining)
            if idx is not None:
                return window.start + idx
        return None

    def _force_split(
        self, window: CursorWindow, chunk_id: str, reason: str
    ) -> None:
        end = window.last_sentence_boundary()
        if end <= window.start:
            end = window.end
        window.set_end(end)
        logger.warning(
            json.dumps(
                {"event": "forced_split", "chunk_id": chunk_id, "reason": reason}
            )
        )

    @staticmethod
    def _sentence_fallback(window: CursorWindow) -> None:
        end = window.last_sentence_boundary()
        if end <= window.start:
            end = window.end
        window.set_end(end)
