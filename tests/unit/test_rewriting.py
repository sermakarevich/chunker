from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from chunker.config import ChunkerConfig
from chunker.context import ContextBuilder
from chunker.llm.schemas import RewriteResult
from chunker.models import Chunk
from chunker.nodes.rewriting import ChunkRewriter
from chunker.state import PipelineState


def _make_chunk(chunk_id: str = "chunk-001", original: str = "Original text.") -> Chunk:
    return Chunk(
        id=chunk_id,
        source_span=(0, len(original)),
        original_text=original,
        rewritten_text="",
        summary="",
        parent_block_id=None,
        forced_split=False,
        metadata={},
    )


def _empty_state() -> PipelineState:
    return PipelineState(
        document_id="doc-001",
        source_text="x" * 500,
        cursor_position=0,
        chunks={},
        blocks={},
        pending_summaries={},
        chunk_counter=0,
        block_counters={},
    )


class TestChunkRewriter:
    @pytest.fixture()
    def config(self):
        return ChunkerConfig(context_budget_tokens=10000)

    @pytest.fixture()
    def mock_llm(self):
        llm = MagicMock()
        llm.rewrite_chunk.return_value = RewriteResult(
            rewritten_text="The researchers used a novel approach to solve the problem.",
            summary="Researchers applied a novel problem-solving approach.",
        )
        return llm

    def test_populates_rewritten_text(self, config, mock_llm):
        context_builder = ContextBuilder(config)
        rewriter = ChunkRewriter(mock_llm, context_builder)
        chunk = _make_chunk()
        state = _empty_state()

        result = rewriter.rewrite(chunk, state)

        assert (
            result.rewritten_text
            == "The researchers used a novel approach to solve the problem."
        )

    def test_populates_summary(self, config, mock_llm):
        context_builder = ContextBuilder(config)
        rewriter = ChunkRewriter(mock_llm, context_builder)
        chunk = _make_chunk()
        state = _empty_state()

        result = rewriter.rewrite(chunk, state)

        assert result.summary == "Researchers applied a novel problem-solving approach."

    def test_returns_same_chunk_object(self, config, mock_llm):
        context_builder = ContextBuilder(config)
        rewriter = ChunkRewriter(mock_llm, context_builder)
        chunk = _make_chunk()
        state = _empty_state()

        result = rewriter.rewrite(chunk, state)

        assert result is chunk

    def test_passes_original_text_to_llm(self, config, mock_llm):
        context_builder = ContextBuilder(config)
        rewriter = ChunkRewriter(mock_llm, context_builder)
        chunk = _make_chunk(original="They applied the method to new data.")
        state = _empty_state()

        rewriter.rewrite(chunk, state)

        call_args = mock_llm.rewrite_chunk.call_args
        assert call_args.args[0] == "They applied the method to new data."

    def test_passes_chunk_id_to_llm(self, config, mock_llm):
        context_builder = ContextBuilder(config)
        rewriter = ChunkRewriter(mock_llm, context_builder)
        chunk = _make_chunk(chunk_id="chunk-042")
        state = _empty_state()

        rewriter.rewrite(chunk, state)

        call_args = mock_llm.rewrite_chunk.call_args
        assert call_args.kwargs["chunk_id"] == "chunk-042"

    def test_passes_context_from_builder(self, config, mock_llm):
        prev = Chunk(
            id="chunk-001",
            source_span=(0, 10),
            original_text="Previous.",
            rewritten_text="Previous rewritten.",
            summary="Prev summary.",
            parent_block_id=None,
            forced_split=False,
            metadata={},
        )
        state = _empty_state()
        state.chunks = {"chunk-001": prev}
        state.chunk_counter = 1

        context_builder = ContextBuilder(config)
        rewriter = ChunkRewriter(mock_llm, context_builder)
        chunk = _make_chunk(chunk_id="chunk-002")

        rewriter.rewrite(chunk, state)

        call_args = mock_llm.rewrite_chunk.call_args
        context_text = call_args.args[1]
        assert "predecessor:chunk-001" in context_text
        assert "Previous rewritten." in context_text

    def test_preserves_original_text(self, config, mock_llm):
        context_builder = ContextBuilder(config)
        rewriter = ChunkRewriter(mock_llm, context_builder)
        chunk = _make_chunk(original="They used this approach extensively.")
        state = _empty_state()

        result = rewriter.rewrite(chunk, state)

        assert result.original_text == "They used this approach extensively."
