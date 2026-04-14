from __future__ import annotations

import logging
from unittest.mock import MagicMock

import pytest

from chunker.config import ChunkerConfig
from chunker.llm.schemas import CompletenessResult
from chunker.nodes.chunking import ChunkExtractor, validate_boundary_phrase
from chunker.state import PipelineState


class TestValidateBoundaryPhrase:
    def test_found_returns_index(self):
        text = "Start of text. New section begins here."
        assert validate_boundary_phrase("New section", text) == text.find("New section")

    def test_not_found_returns_none(self):
        assert validate_boundary_phrase("missing", "Some other text.") is None

    def test_exact_match_required(self):
        assert validate_boundary_phrase("new section", "Text. New section here.") is None

    def test_returns_first_occurrence(self):
        text = "Word here. Word again."
        assert validate_boundary_phrase("Word", text) == 0


class TestChunkExtractorHappyPath:
    @pytest.fixture()
    def text(self):
        return (
            "First topic here. Second topic here. "
            "New section starts now. More content follows."
        )

    @pytest.fixture()
    def config(self):
        return ChunkerConfig(
            min_chunk_tokens=5, max_chunk_tokens=500, max_expansion_attempts=5
        )

    def _make_llm(self, **kwargs):
        return MagicMock(**kwargs)

    def test_returns_chunk_with_correct_span(self, text, config):
        state = PipelineState.create("doc-001", text)
        llm = self._make_llm()
        llm.check_completeness.return_value = CompletenessResult(
            complete=True, boundary_phrase="New section starts now."
        )
        extractor = ChunkExtractor(llm, config)

        chunk = extractor.extract_next(state)

        expected_end = text.find("New section starts now.")
        assert chunk.source_span == (0, expected_end)
        assert chunk.original_text == text[:expected_end]
        assert chunk.forced_split is False

    def test_source_span_matches_original_text(self, text, config):
        state = PipelineState.create("doc-001", text)
        llm = self._make_llm()
        llm.check_completeness.return_value = CompletenessResult(
            complete=True, boundary_phrase="New section starts now."
        )
        extractor = ChunkExtractor(llm, config)

        chunk = extractor.extract_next(state)

        assert text[chunk.source_span[0] : chunk.source_span[1]] == chunk.original_text

    def test_cursor_position_updated(self, text, config):
        state = PipelineState.create("doc-001", text)
        llm = self._make_llm()
        llm.check_completeness.return_value = CompletenessResult(
            complete=True, boundary_phrase="New section starts now."
        )
        extractor = ChunkExtractor(llm, config)

        chunk = extractor.extract_next(state)

        assert state.cursor_position == chunk.source_span[1]

    def test_chunk_counter_incremented(self, text, config):
        state = PipelineState.create("doc-001", text)
        llm = self._make_llm()
        llm.check_completeness.return_value = CompletenessResult(
            complete=True, boundary_phrase="New section starts now."
        )
        extractor = ChunkExtractor(llm, config)

        extractor.extract_next(state)

        assert state.chunk_counter == 1

    def test_rewrite_and_summary_empty(self, text, config):
        state = PipelineState.create("doc-001", text)
        llm = self._make_llm()
        llm.check_completeness.return_value = CompletenessResult(
            complete=True, boundary_phrase="New section starts now."
        )
        extractor = ChunkExtractor(llm, config)

        chunk = extractor.extract_next(state)

        assert chunk.rewritten_text == ""
        assert chunk.summary == ""


class TestChunkExtractorExpansion:
    def test_expands_window_on_incomplete(self):
        text = (
            "First sentence here. Second sentence here. "
            "Third sentence here. Fourth sentence here."
        )
        state = PipelineState.create("doc-001", text)
        llm = MagicMock()
        llm.check_completeness.side_effect = [
            CompletenessResult(complete=False),
            CompletenessResult(
                complete=True, boundary_phrase="Third sentence here."
            ),
        ]
        config = ChunkerConfig(
            min_chunk_tokens=3, max_chunk_tokens=500, max_expansion_attempts=5
        )
        extractor = ChunkExtractor(llm, config)

        chunk = extractor.extract_next(state)

        assert llm.check_completeness.call_count == 2
        expected_end = text.find("Third sentence here.")
        assert chunk.source_span[1] == expected_end


class TestChunkExtractorBoundaryRetry:
    def test_retry_succeeds(self):
        text = (
            "First part of text. Second part continues. "
            "A new topic emerges. Rest of document."
        )
        state = PipelineState.create("doc-001", text)
        llm = MagicMock()
        llm.check_completeness.side_effect = [
            CompletenessResult(complete=True, boundary_phrase="Not in text"),
            CompletenessResult(
                complete=True, boundary_phrase="A new topic emerges."
            ),
        ]
        config = ChunkerConfig(
            min_chunk_tokens=3, max_chunk_tokens=500, max_expansion_attempts=5
        )
        extractor = ChunkExtractor(llm, config)

        chunk = extractor.extract_next(state)

        assert llm.check_completeness.call_count == 2
        expected_end = text.find("A new topic emerges.")
        assert chunk.source_span[1] == expected_end
        assert chunk.forced_split is False

    def test_retry_fails_falls_back_to_sentence_boundary(self, caplog):
        text = "First sentence here. Second sentence here. Third sentence here."
        state = PipelineState.create("doc-001", text)
        llm = MagicMock()
        llm.check_completeness.side_effect = [
            CompletenessResult(complete=True, boundary_phrase="Not in text"),
            CompletenessResult(complete=True, boundary_phrase="Also missing"),
        ]
        config = ChunkerConfig(
            min_chunk_tokens=3, max_chunk_tokens=500, max_expansion_attempts=5
        )
        extractor = ChunkExtractor(llm, config)

        with caplog.at_level(logging.WARNING):
            chunk = extractor.extract_next(state)

        assert llm.check_completeness.call_count == 2
        assert chunk.source_span[0] < chunk.source_span[1]
        assert (
            text[chunk.source_span[0] : chunk.source_span[1]] == chunk.original_text
        )
        assert any("phrase_not_found" in r.message for r in caplog.records)


class TestChunkExtractorForceSplit:
    def test_force_split_max_tokens(self, caplog):
        sentences = [f"Topic {i} is discussed here in detail" for i in range(50)]
        text = ". ".join(sentences) + "."
        state = PipelineState.create("doc-001", text)
        llm = MagicMock()
        llm.check_completeness.return_value = CompletenessResult(complete=False)
        config = ChunkerConfig(
            min_chunk_tokens=3, max_chunk_tokens=15, max_expansion_attempts=50
        )
        extractor = ChunkExtractor(llm, config)

        with caplog.at_level(logging.WARNING):
            chunk = extractor.extract_next(state)

        assert chunk.forced_split is True
        assert any("forced_split" in r.message for r in caplog.records)
        assert (
            text[chunk.source_span[0] : chunk.source_span[1]] == chunk.original_text
        )

    def test_force_split_max_attempts(self, caplog):
        text = (
            "First sentence here. Second sentence here. "
            "Third sentence here. Fourth sentence here."
        )
        state = PipelineState.create("doc-001", text)
        llm = MagicMock()
        llm.check_completeness.return_value = CompletenessResult(complete=False)
        config = ChunkerConfig(
            min_chunk_tokens=3, max_chunk_tokens=5000, max_expansion_attempts=2
        )
        extractor = ChunkExtractor(llm, config)

        with caplog.at_level(logging.WARNING):
            chunk = extractor.extract_next(state)

        assert chunk.forced_split is True
        assert llm.check_completeness.call_count == 2
        assert any("forced_split" in r.message for r in caplog.records)

    def test_force_split_source_span_matches(self, caplog):
        sentences = [f"Topic {i} is discussed here in detail" for i in range(50)]
        text = ". ".join(sentences) + "."
        state = PipelineState.create("doc-001", text)
        llm = MagicMock()
        llm.check_completeness.return_value = CompletenessResult(complete=False)
        config = ChunkerConfig(
            min_chunk_tokens=3, max_chunk_tokens=15, max_expansion_attempts=50
        )
        extractor = ChunkExtractor(llm, config)

        with caplog.at_level(logging.WARNING):
            chunk = extractor.extract_next(state)

        assert (
            text[chunk.source_span[0] : chunk.source_span[1]] == chunk.original_text
        )
