from __future__ import annotations

import json
import logging

from chunker.config import MODEL_PROFILES, ChunkerConfig, estimate_tokens
from chunker.llm.service import LLMService
from chunker.models import Chunk, Page
from chunker.state import PipelineState

logger = logging.getLogger(__name__)

_DEFAULT_TOKEN_FACTOR = 1.0
# The marker the page-completeness prompt (Task 2) is instructed to read.
_PAGE_MARKER = "=== Page {number} ==="


class PageWindow:
    """A growing window of consecutive pages over ``state.pages``.

    The pdf-mode counterpart of :class:`chunker.splitter.CursorWindow`: it starts
    on a single page and grows by whole pages until it reaches ``min_chunk_tokens``
    (or runs out of pages). Every boundary it exposes is a page edge, so a chunk
    built from it can never begin or end in the middle of a page.
    """

    def __init__(
        self, pages: list[Page], start_index: int, config: ChunkerConfig
    ) -> None:
        self._pages = pages
        self._start_index = start_index
        self._end_index = start_index  # 0-based inclusive index of the last page

        profile = MODEL_PROFILES.get(config.model)
        self._token_factor = profile.token_factor if profile else _DEFAULT_TOKEN_FACTOR
        self._min_chunk_tokens = config.min_chunk_tokens

        while self.token_count < self._min_chunk_tokens:
            if not self.expand():
                break

    @property
    def _window_pages(self) -> list[Page]:
        return self._pages[self._start_index : self._end_index + 1]

    @property
    def text(self) -> str:
        blocks = [
            f"{_PAGE_MARKER.format(number=p.number)}\n{p.text}"
            for p in self._window_pages
        ]
        return "\n\n".join(blocks)

    @property
    def token_count(self) -> int:
        return estimate_tokens(self.text, self._token_factor)

    @property
    def page_count(self) -> int:
        return self._end_index - self._start_index + 1

    @property
    def image_paths(self) -> list[str]:
        return [p.image_path for p in self._window_pages]

    @property
    def start_page(self) -> int:
        return self._pages[self._start_index].number

    @property
    def end_page(self) -> int:
        return self._pages[self._end_index].number

    def expand(self) -> bool:
        """Include the next page; return False if already at the last page."""
        if self._end_index >= len(self._pages) - 1:
            return False
        self._end_index += 1
        return True

    def set_end_to_page(self, page_number: int) -> None:
        """Clamp the window to end at *page_number* (1-based).

        No-op if *page_number* is outside the current ``[start_page, end_page]``.
        """
        if not (self.start_page <= page_number <= self.end_page):
            return
        for i in range(self._start_index, self._end_index + 1):
            if self._pages[i].number == page_number:
                self._end_index = i
                return


class PageChunkExtractor:
    """Produces the next page-bounded :class:`Chunk` for a pdf-mode run.

    Mirrors :class:`chunker.nodes.chunking.ChunkExtractor` but resolves chunk
    boundaries at page edges via the text-only page-completeness check, so a
    chunk never begins or ends in the middle of a page. The text path is left
    untouched (the pipeline selects the extractor by mode in Task 4).
    """

    def __init__(self, llm_service: LLMService, config: ChunkerConfig) -> None:
        self._llm = llm_service
        self._config = config

    def extract_next(self, state: PipelineState) -> Chunk:
        if state.pages is None:
            raise ValueError("PageChunkExtractor requires pages (pdf mode)")

        start_index = state.cursor_page
        window = PageWindow(state.pages, start_index, self._config)

        state.chunk_counter += 1
        chunk_id = f"chunk-{state.chunk_counter:03d}"
        forced_split = False
        attempts = 0

        while attempts < self._config.max_expansion_attempts:
            if window.token_count >= self._config.max_chunk_tokens:
                forced_split = True
                if window.page_count == 1:
                    # A single page already over budget cannot be shrunk further.
                    self._log_event("oversized_page", chunk_id)
                else:
                    self._force_split(chunk_id, "max_tokens")
                break
            if window.page_count >= self._config.max_pages_per_chunk:
                forced_split = True
                self._force_split(chunk_id, "max_pages")
                break

            result = self._llm.check_page_completeness(window.text, chunk_id=chunk_id)
            attempts += 1

            if result.complete:
                if result.split_after_page is not None:
                    window.set_end_to_page(result.split_after_page)
                break
            if not window.expand():
                forced_split = True
                self._force_split(chunk_id, "cannot_expand")
                break
        else:
            # max_expansion_attempts exhausted
            forced_split = True
            self._force_split(chunk_id, "max_attempts")

        chunk = Chunk(
            id=chunk_id,
            source_span=(0, 0),  # char span unused in pdf mode
            original_text=window.text,
            context="",
            summary="",
            filename="",
            parent_block_id=None,
            forced_split=forced_split,
            metadata={},
            page_span=(window.start_page, window.end_page),
            image_paths=window.image_paths,
        )
        state.cursor_page = start_index + window.page_count
        return chunk

    def _force_split(self, chunk_id: str, reason: str) -> None:
        # No window mutation: every window boundary is already a page edge, so a
        # force-split only records why growth stopped.
        logger.warning(
            json.dumps(
                {"event": "forced_split", "chunk_id": chunk_id, "reason": reason}
            )
        )

    def _log_event(self, event: str, chunk_id: str) -> None:
        logger.warning(json.dumps({"event": event, "chunk_id": chunk_id}))
