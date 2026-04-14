from __future__ import annotations

import pytest

from chunker.config import ChunkerConfig
from chunker.context import ContextBuilder, ContextItem
from chunker.models import Chunk, SummaryBlock
from chunker.state import PipelineState


def _make_chunk(
    chunk_id: str,
    original: str = "original",
    rewritten: str = "",
    summary: str = "",
) -> Chunk:
    return Chunk(
        id=chunk_id,
        source_span=(0, len(original)),
        original_text=original,
        rewritten_text=rewritten,
        summary=summary,
        parent_block_id=None,
        forced_split=False,
        metadata={},
    )


def _make_block(
    block_id: str,
    level: int,
    summary: str = "block summary",
) -> SummaryBlock:
    return SummaryBlock(
        id=block_id,
        level=level,
        summary=summary,
        child_ids=[],
        parent_block_id=None,
        metadata={},
    )


def _state_with(
    chunks: dict[str, Chunk] | None = None,
    blocks: dict[str, SummaryBlock] | None = None,
) -> PipelineState:
    return PipelineState(
        document_id="doc-001",
        source_text="x" * 1000,
        cursor_position=0,
        chunks=chunks or {},
        blocks=blocks or {},
        pending_summaries={},
        chunk_counter=len(chunks) if chunks else 0,
        block_counters={},
    )


class TestContextBuilderPriorityOrder:
    @pytest.fixture()
    def config(self):
        return ChunkerConfig(context_budget_tokens=10000)

    def test_predecessor_is_first_item(self, config):
        c1 = _make_chunk("chunk-001", rewritten="Rewritten first chunk.")
        state = _state_with(chunks={"chunk-001": c1})
        builder = ContextBuilder(config)

        items = builder.build(state)

        assert len(items) >= 1
        assert items[0].source == "predecessor:chunk-001"

    def test_predecessor_uses_rewritten_text(self, config):
        c1 = _make_chunk("chunk-001", rewritten="Rewritten.", summary="Summary.")
        state = _state_with(chunks={"chunk-001": c1})
        builder = ContextBuilder(config)

        items = builder.build(state)

        assert items[0].text == "Rewritten."

    def test_predecessor_falls_back_to_summary(self, config):
        c1 = _make_chunk("chunk-001", rewritten="", summary="Summary fallback.")
        state = _state_with(chunks={"chunk-001": c1})
        builder = ContextBuilder(config)

        items = builder.build(state)

        assert items[0].text == "Summary fallback."

    def test_level_summaries_after_predecessor(self, config):
        c1 = _make_chunk("chunk-001", rewritten="Rewritten chunk.")
        b1 = _make_block("block-L1-001", level=1, summary="L1 summary.")
        state = _state_with(
            chunks={"chunk-001": c1},
            blocks={"block-L1-001": b1},
        )
        builder = ContextBuilder(config)

        items = builder.build(state)

        sources = [i.source for i in items]
        assert sources.index("predecessor:chunk-001") < sources.index(
            "summary:L1:block-L1-001"
        )

    def test_level_summaries_ascending_order(self, config):
        c1 = _make_chunk("chunk-001", rewritten="Rewritten.")
        b1 = _make_block("block-L1-001", level=1, summary="L1 summary.")
        b2 = _make_block("block-L2-001", level=2, summary="L2 summary.")
        state = _state_with(
            chunks={"chunk-001": c1},
            blocks={"block-L1-001": b1, "block-L2-001": b2},
        )
        builder = ContextBuilder(config)

        items = builder.build(state)

        sources = [i.source for i in items]
        assert sources.index("summary:L1:block-L1-001") < sources.index(
            "summary:L2:block-L2-001"
        )

    def test_latest_block_per_level(self, config):
        c1 = _make_chunk("chunk-001", rewritten="Rewritten.")
        b1 = _make_block("block-L1-001", level=1, summary="Old L1.")
        b2 = _make_block("block-L1-002", level=1, summary="New L1.")
        state = _state_with(
            chunks={"chunk-001": c1},
            blocks={"block-L1-001": b1, "block-L1-002": b2},
        )
        builder = ContextBuilder(config)

        items = builder.build(state)

        l1_items = [i for i in items if i.source.startswith("summary:L1:")]
        assert len(l1_items) == 1
        assert l1_items[0].source == "summary:L1:block-L1-002"

    def test_earlier_chunks_after_summaries(self, config):
        c1 = _make_chunk("chunk-001", rewritten="First rewritten.")
        c2 = _make_chunk("chunk-002", rewritten="Second rewritten.")
        b1 = _make_block("block-L1-001", level=1, summary="L1 summary.")
        state = _state_with(
            chunks={"chunk-001": c1, "chunk-002": c2},
            blocks={"block-L1-001": b1},
        )
        builder = ContextBuilder(config)

        items = builder.build(state)

        sources = [i.source for i in items]
        assert sources[0] == "predecessor:chunk-002"
        assert "summary:L1:block-L1-001" in sources
        assert "earlier:chunk-001" in sources
        assert sources.index("summary:L1:block-L1-001") < sources.index(
            "earlier:chunk-001"
        )

    def test_earlier_chunks_walk_backwards(self, config):
        c1 = _make_chunk("chunk-001", rewritten="First.")
        c2 = _make_chunk("chunk-002", rewritten="Second.")
        c3 = _make_chunk("chunk-003", rewritten="Third.")
        state = _state_with(
            chunks={"chunk-001": c1, "chunk-002": c2, "chunk-003": c3},
        )
        builder = ContextBuilder(config)

        items = builder.build(state)

        sources = [i.source for i in items]
        assert sources[0] == "predecessor:chunk-003"
        assert sources.index("earlier:chunk-002") < sources.index("earlier:chunk-001")


class TestContextBuilderBudget:
    def test_items_within_budget_included(self):
        config = ChunkerConfig(context_budget_tokens=10000)
        c1 = _make_chunk("chunk-001", rewritten="Short text.")
        state = _state_with(chunks={"chunk-001": c1})
        builder = ContextBuilder(config)

        items = builder.build(state)

        assert len(items) >= 1

    def test_item_exceeding_budget_skipped(self):
        config = ChunkerConfig(context_budget_tokens=5)
        long_text = " ".join(["word"] * 100)
        c1 = _make_chunk("chunk-001", rewritten=long_text)
        state = _state_with(chunks={"chunk-001": c1})
        builder = ContextBuilder(config)

        items = builder.build(state)

        assert len(items) == 0

    def test_skip_and_try_next(self):
        config = ChunkerConfig(context_budget_tokens=10)
        long_text = " ".join(["word"] * 100)
        short_text = "Brief."
        c1 = _make_chunk("chunk-001", rewritten=short_text)
        c2 = _make_chunk("chunk-002", rewritten=long_text)
        b1 = _make_block("block-L1-001", level=1, summary=short_text)
        state = _state_with(
            chunks={"chunk-001": c1, "chunk-002": c2},
            blocks={"block-L1-001": b1},
        )
        builder = ContextBuilder(config)

        items = builder.build(state)

        # Predecessor (chunk-002) is too large, should be skipped.
        # L1 summary and earlier chunk-001 are small enough to fit.
        sources = [i.source for i in items]
        assert "predecessor:chunk-002" not in sources
        assert any(s.startswith("summary:L1:") for s in sources) or any(
            s.startswith("earlier:") for s in sources
        )

    def test_hard_ceiling_respected(self):
        config = ChunkerConfig(context_budget_tokens=5)
        c1 = _make_chunk("chunk-001", rewritten="A few words here.")
        c2 = _make_chunk("chunk-002", rewritten="More words over here.")
        state = _state_with(chunks={"chunk-001": c1, "chunk-002": c2})
        builder = ContextBuilder(config)

        items = builder.build(state)

        total = sum(i.token_count for i in items)
        assert total <= config.context_budget_tokens


class TestContextBuilderEmptyState:
    def test_empty_state_returns_empty(self):
        config = ChunkerConfig(context_budget_tokens=10000)
        state = _state_with()
        builder = ContextBuilder(config)

        items = builder.build(state)

        assert items == []

    def test_no_blocks_omits_level_summaries(self):
        config = ChunkerConfig(context_budget_tokens=10000)
        c1 = _make_chunk("chunk-001", rewritten="Rewritten.")
        state = _state_with(chunks={"chunk-001": c1})
        builder = ContextBuilder(config)

        items = builder.build(state)

        assert not any(i.source.startswith("summary:") for i in items)

    def test_single_chunk_no_earlier_items(self):
        config = ChunkerConfig(context_budget_tokens=10000)
        c1 = _make_chunk("chunk-001", rewritten="Rewritten.")
        state = _state_with(chunks={"chunk-001": c1})
        builder = ContextBuilder(config)

        items = builder.build(state)

        assert not any(i.source.startswith("earlier:") for i in items)


class TestContextBuilderTokenCount:
    def test_items_have_positive_token_count(self):
        config = ChunkerConfig(context_budget_tokens=10000)
        c1 = _make_chunk("chunk-001", rewritten="Some rewritten text here.")
        state = _state_with(chunks={"chunk-001": c1})
        builder = ContextBuilder(config)

        items = builder.build(state)

        assert all(i.token_count > 0 for i in items)


class TestFormatContext:
    def test_empty_items_returns_empty_string(self):
        config = ChunkerConfig()
        builder = ContextBuilder(config)

        assert builder.format_context([]) == ""

    def test_single_item_formatted(self):
        config = ChunkerConfig()
        builder = ContextBuilder(config)
        item = ContextItem(source="predecessor:chunk-001", text="Hello world.", token_count=2)

        result = builder.format_context([item])

        assert "[Source: predecessor:chunk-001]" in result
        assert "Hello world." in result
        assert result.strip().endswith("---")

    def test_multiple_items_separated(self):
        config = ChunkerConfig()
        builder = ContextBuilder(config)
        items = [
            ContextItem(source="predecessor:chunk-001", text="First.", token_count=1),
            ContextItem(source="summary:L1:block-L1-001", text="Second.", token_count=1),
        ]

        result = builder.format_context(items)

        assert "[Source: predecessor:chunk-001]" in result
        assert "[Source: summary:L1:block-L1-001]" in result
        assert result.count("---") == 2
