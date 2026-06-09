from __future__ import annotations

import logging
from unittest.mock import MagicMock

import pytest

from chunker.config import ChunkerConfig
from chunker.llm.schemas import PageCompletenessResult
from chunker.models import Page
from chunker.nodes.page_chunking import PageChunkExtractor, PageWindow
from chunker.state import PipelineState

# A model absent from MODEL_PROFILES → token_factor defaults to 1.0, so
# ``token_count`` equals the plain word count and test math is deterministic.
_TEST_MODEL = "test-model"


def _pages(
    count: int,
    *,
    tokens_per_page: int = 50,
    empty_indices: tuple[int, ...] = (),
) -> list[Page]:
    pages: list[Page] = []
    for i in range(count):
        number = i + 1
        text = "" if i in empty_indices else " ".join(["word"] * tokens_per_page)
        pages.append(
            Page(number=number, text=text, image_path=f"/img/page-{number:03d}.png")
        )
    return pages


def _config(**overrides) -> ChunkerConfig:
    params = {
        "model": _TEST_MODEL,
        "min_chunk_tokens": 10,
        "max_chunk_tokens": 100_000,
        "max_pages_per_chunk": 100,
        "max_expansion_attempts": 10,
    }
    params.update(overrides)
    return ChunkerConfig(**params)


def _state(pages: list[Page]) -> PipelineState:
    return PipelineState.create_from_pages("doc-001", pages)


# Each page block is "=== Page N ===" (4 words) + tokens_per_page words.
_MARKER_TOKENS = 4


class TestPageWindow:
    def test_text_has_page_markers(self):
        # min=100 forces growth to 2 pages (54 < 100 ≤ 108).
        window = PageWindow(_pages(2), 0, _config(min_chunk_tokens=100))
        assert window.page_count == 2
        assert "=== Page 1 ===" in window.text
        assert "=== Page 2 ===" in window.text

    def test_starts_on_single_page_when_min_is_tiny(self):
        window = PageWindow(
            _pages(3, tokens_per_page=50), 0, _config(min_chunk_tokens=1)
        )
        assert window.page_count == 1
        assert window.start_page == 1
        assert window.end_page == 1

    def test_grows_until_min_chunk_tokens(self):
        # 50 + 4 marker = 54 tokens/page → 1pg=54, 2pg=108, 3pg=162.
        window = PageWindow(
            _pages(5, tokens_per_page=50), 0, _config(min_chunk_tokens=120)
        )
        assert window.page_count == 3
        assert window.token_count == 162

    def test_does_not_grow_past_min(self):
        # Stops at the first page count that meets the minimum, not beyond.
        window = PageWindow(
            _pages(5, tokens_per_page=50), 0, _config(min_chunk_tokens=120)
        )
        assert window.page_count == 3  # 2pg=108 < 120 < 162 = 3pg

    def test_token_count_uses_marker_overhead(self):
        window = PageWindow(
            _pages(1, tokens_per_page=50), 0, _config(min_chunk_tokens=1)
        )
        assert window.token_count == 50 + _MARKER_TOKENS

    def test_image_paths_cover_window(self):
        window = PageWindow(
            _pages(4, tokens_per_page=50), 0, _config(min_chunk_tokens=120)
        )
        assert window.image_paths == [
            "/img/page-001.png",
            "/img/page-002.png",
            "/img/page-003.png",
        ]

    def test_start_and_end_page_are_one_based(self):
        window = PageWindow(
            _pages(4, tokens_per_page=50), 1, _config(min_chunk_tokens=120)
        )
        # start_index=1 → pages 2,3,4
        assert window.start_page == 2
        assert window.end_page == 4

    def test_expand_returns_false_at_last_page(self):
        window = PageWindow(
            _pages(2, tokens_per_page=50), 0, _config(min_chunk_tokens=1)
        )
        assert window.expand() is True  # to page 2
        assert window.expand() is False  # no page 3

    def test_set_end_to_page_clamps_window(self):
        window = PageWindow(
            _pages(4, tokens_per_page=50), 0, _config(min_chunk_tokens=160)
        )
        assert window.page_count == 3  # pages 1,2,3
        window.set_end_to_page(2)
        assert window.end_page == 2
        assert window.page_count == 2

    def test_set_end_to_page_out_of_range_is_noop(self):
        window = PageWindow(
            _pages(4, tokens_per_page=50), 0, _config(min_chunk_tokens=160)
        )
        before = window.page_count
        window.set_end_to_page(99)  # beyond end_page
        window.set_end_to_page(0)  # before start_page
        assert window.page_count == before

    def test_empty_text_page_still_represented(self):
        # FR-10: an empty-text page keeps its marker line and is counted.
        pages = _pages(2, tokens_per_page=50, empty_indices=(1,))
        window = PageWindow(pages, 0, _config(min_chunk_tokens=1))
        window.expand()
        assert "=== Page 2 ===" in window.text
        assert window.page_count == 2


class TestPageChunkExtractorHappyPath:
    def test_page_edge_split_via_split_after_page(self):
        # FR-04: complete=True, split_after_page=K → chunk ends at page K.
        state = _state(_pages(4, tokens_per_page=50))
        llm = MagicMock()
        llm.check_page_completeness.return_value = PageCompletenessResult(
            complete=True, split_after_page=2
        )
        extractor = PageChunkExtractor(llm, _config(min_chunk_tokens=120))

        chunk = extractor.extract_next(state)

        assert chunk.page_span == (1, 2)
        assert chunk.source_span == (0, 0)
        assert chunk.forced_split is False
        assert chunk.image_paths == ["/img/page-001.png", "/img/page-002.png"]
        assert "=== Page 3 ===" not in chunk.original_text
        assert state.cursor_page == 2  # advanced past page 2

    def test_extends_window_when_incomplete_then_complete(self):
        # FR-04: below-min candidate whose next page continues → window extends.
        state = _state(_pages(4, tokens_per_page=50))
        llm = MagicMock()
        llm.check_page_completeness.side_effect = [
            PageCompletenessResult(complete=False),
            PageCompletenessResult(complete=True, split_after_page=None),
        ]
        extractor = PageChunkExtractor(llm, _config(min_chunk_tokens=10))

        chunk = extractor.extract_next(state)

        assert llm.check_page_completeness.call_count == 2
        assert chunk.page_span == (1, 2)
        assert chunk.forced_split is False
        assert state.cursor_page == 2

    def test_complete_with_null_split_keeps_grown_window(self):
        state = _state(_pages(4, tokens_per_page=50))
        llm = MagicMock()
        llm.check_page_completeness.return_value = PageCompletenessResult(
            complete=True, split_after_page=None
        )
        extractor = PageChunkExtractor(llm, _config(min_chunk_tokens=120))

        chunk = extractor.extract_next(state)

        # constructor grew to 3 pages; null split leaves it intact
        assert chunk.page_span == (1, 3)
        assert state.cursor_page == 3

    def test_chunk_counter_and_id(self):
        state = _state(_pages(2, tokens_per_page=50))
        llm = MagicMock()
        llm.check_page_completeness.return_value = PageCompletenessResult(complete=True)
        extractor = PageChunkExtractor(llm, _config(min_chunk_tokens=10))

        chunk = extractor.extract_next(state)

        assert state.chunk_counter == 1
        assert chunk.id == "chunk-001"

    def test_context_summary_filename_empty(self):
        state = _state(_pages(2, tokens_per_page=50))
        llm = MagicMock()
        llm.check_page_completeness.return_value = PageCompletenessResult(complete=True)
        extractor = PageChunkExtractor(llm, _config(min_chunk_tokens=10))

        chunk = extractor.extract_next(state)

        assert chunk.context == ""
        assert chunk.summary == ""
        assert chunk.filename == ""
        assert chunk.parent_block_id is None

    def test_single_page_document_produces_one_chunk(self):
        # FR-02 edge case: single-page PDF yields a chunk covering that page.
        state = _state(_pages(1, tokens_per_page=50))
        llm = MagicMock()
        llm.check_page_completeness.return_value = PageCompletenessResult(complete=True)
        extractor = PageChunkExtractor(llm, _config(min_chunk_tokens=10))

        chunk = extractor.extract_next(state)

        assert chunk.page_span == (1, 1)
        assert state.cursor_page == 1
        assert state.has_more_pages is False

    def test_sequential_extraction_advances_cursor(self):
        state = _state(_pages(4, tokens_per_page=50))
        llm = MagicMock()
        llm.check_page_completeness.return_value = PageCompletenessResult(
            complete=True, split_after_page=None
        )
        extractor = PageChunkExtractor(llm, _config(min_chunk_tokens=10))

        first = extractor.extract_next(state)
        second = extractor.extract_next(state)

        assert first.page_span == (1, 1)
        assert second.page_span == (2, 2)
        assert second.id == "chunk-002"
        assert state.cursor_page == 2

    def test_extract_next_without_pages_raises(self):
        state = PipelineState.create("doc-001", "plain text")
        extractor = PageChunkExtractor(MagicMock(), _config())
        with pytest.raises(ValueError):
            extractor.extract_next(state)


class TestPageChunkExtractorForceSplit:
    def test_force_split_max_pages(self, caplog):
        # FR-09: window never completes → max_pages cap force-splits.
        state = _state(_pages(5, tokens_per_page=50))
        llm = MagicMock()
        llm.check_page_completeness.return_value = PageCompletenessResult(
            complete=False
        )
        extractor = PageChunkExtractor(
            llm, _config(min_chunk_tokens=10, max_pages_per_chunk=2)
        )

        with caplog.at_level(logging.WARNING):
            chunk = extractor.extract_next(state)

        assert chunk.forced_split is True
        assert chunk.page_span == (1, 2)
        assert any('"reason": "max_pages"' in r.message for r in caplog.records)

    def test_force_split_max_tokens_multi_page(self, caplog):
        # 54 tokens/page: 1pg=54 < min(60) → grow to 2pg=108 ≥ max(80).
        state = _state(_pages(5, tokens_per_page=50))
        llm = MagicMock()
        llm.check_page_completeness.return_value = PageCompletenessResult(
            complete=False
        )
        extractor = PageChunkExtractor(
            llm, _config(min_chunk_tokens=60, max_chunk_tokens=80)
        )

        with caplog.at_level(logging.WARNING):
            chunk = extractor.extract_next(state)

        assert chunk.forced_split is True
        assert chunk.page_span == (1, 2)
        # cap hit before any completeness call
        assert llm.check_page_completeness.call_count == 0
        assert any('"reason": "max_tokens"' in r.message for r in caplog.records)

    def test_force_split_max_attempts(self, caplog):
        state = _state(_pages(6, tokens_per_page=50))
        llm = MagicMock()
        llm.check_page_completeness.return_value = PageCompletenessResult(
            complete=False
        )
        extractor = PageChunkExtractor(
            llm, _config(min_chunk_tokens=10, max_expansion_attempts=2)
        )

        with caplog.at_level(logging.WARNING):
            chunk = extractor.extract_next(state)

        assert chunk.forced_split is True
        assert llm.check_page_completeness.call_count == 2
        assert any('"reason": "max_attempts"' in r.message for r in caplog.records)

    def test_force_split_cannot_expand(self, caplog):
        # Runs out of pages before any other cap fires.
        state = _state(_pages(2, tokens_per_page=50))
        llm = MagicMock()
        llm.check_page_completeness.return_value = PageCompletenessResult(
            complete=False
        )
        extractor = PageChunkExtractor(llm, _config(min_chunk_tokens=10))

        with caplog.at_level(logging.WARNING):
            chunk = extractor.extract_next(state)

        assert chunk.forced_split is True
        assert chunk.page_span == (1, 2)
        assert state.cursor_page == 2
        assert any('"reason": "cannot_expand"' in r.message for r in caplog.records)

    def test_oversized_single_page(self, caplog):
        # FR-09 edge case: one page over max_chunk_tokens accepted + warned.
        state = _state(_pages(1, tokens_per_page=200))
        llm = MagicMock()
        llm.check_page_completeness.return_value = PageCompletenessResult(
            complete=False
        )
        extractor = PageChunkExtractor(
            llm, _config(min_chunk_tokens=10, max_chunk_tokens=100)
        )

        with caplog.at_level(logging.WARNING):
            chunk = extractor.extract_next(state)

        assert chunk.page_span == (1, 1)
        assert chunk.forced_split is True
        assert llm.check_page_completeness.call_count == 0
        assert any('"oversized_page"' in r.message for r in caplog.records)


class TestPageChunkExtractorEmptyText:
    def test_empty_text_page_included_with_image(self, caplog):
        # FR-10: empty-text page does not crash, is chunked, image carried.
        pages = _pages(3, tokens_per_page=50, empty_indices=(1,))
        state = _state(pages)
        llm = MagicMock()
        llm.check_page_completeness.side_effect = [
            PageCompletenessResult(complete=False),
            PageCompletenessResult(complete=True, split_after_page=None),
        ]
        extractor = PageChunkExtractor(llm, _config(min_chunk_tokens=10))

        with caplog.at_level(logging.WARNING):
            chunk = extractor.extract_next(state)

        assert chunk.page_span == (1, 2)
        assert "/img/page-002.png" in chunk.image_paths
        assert "=== Page 2 ===" in chunk.original_text


def test_page_chunk_extractor_exported_from_nodes():
    from chunker.nodes import PageChunkExtractor as Exported

    assert Exported is PageChunkExtractor
