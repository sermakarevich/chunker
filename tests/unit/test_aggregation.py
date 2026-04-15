from __future__ import annotations

import logging
from unittest.mock import MagicMock


from chunker.config import ChunkerConfig
from chunker.llm.schemas import GroupingResult
from chunker.llm.service import LLMService
from chunker.models import Chunk
from chunker.nodes.aggregation import (
    AggregationSweeper,
    GroupValidator,
    even_split_fallback,
)
from chunker.state import PipelineState


LONG_SUMMARY = " ".join(["word"] * 20)  # 20 words → 26 tokens (factor 1.3)
SHORT_SUMMARY = "Short."  # 1 word → 2 tokens


def _config(**overrides) -> ChunkerConfig:
    defaults = dict(
        summary_aggregation_threshold=100,
        summary_count_threshold=5,
        min_group_size=2,
        max_group_size=4,
        model="qwen3:32b",
    )
    defaults.update(overrides)
    return ChunkerConfig(**defaults)


def _chunk(chunk_id: str, summary: str = LONG_SUMMARY) -> Chunk:
    return Chunk(
        id=chunk_id,
        source_span=(0, 100),
        original_text="Original",
        context="Rewritten",
        summary=summary,
        filename="",
        parent_block_id=None,
        forced_split=False,
        metadata={},
    )


def _state_with_pending(n: int, summary: str = LONG_SUMMARY) -> PipelineState:
    state = PipelineState.create("doc-1", "x" * 10000)
    ids = []
    for i in range(n):
        cid = f"chunk-{i + 1:03d}"
        state.chunks[cid] = _chunk(cid, summary)
        ids.append(cid)
    state.pending_summaries[0] = ids
    state.chunk_counter = n
    return state


def _mock_llm(groups=None, summary="Group summary."):
    svc = MagicMock(spec=LLMService)
    if groups is not None:
        svc.group_summaries.return_value = GroupingResult(groups=groups)
    svc.summarize_group.return_value = summary
    return svc


# ── GroupValidator ──────────────────────────────────────────────


class TestGroupValidator:
    def test_valid_contiguous_groups(self):
        v = GroupValidator(min_size=2, max_size=5)
        result = v.validate([["a", "b", "c"], ["d", "e"]], ["a", "b", "c", "d", "e"])
        assert result.valid is True
        assert result.hard_violations == []
        assert result.soft_violations == []

    def test_non_contiguous_groups_hard_violation(self):
        v = GroupValidator(min_size=2, max_size=5)
        result = v.validate([["a", "c"], ["b", "d"]], ["a", "b", "c", "d"])
        assert result.valid is False
        assert len(result.hard_violations) > 0

    def test_below_min_size_hard_violation(self):
        v = GroupValidator(min_size=2, max_size=5)
        result = v.validate([["a"], ["b", "c", "d"]], ["a", "b", "c", "d"])
        assert result.valid is False
        assert len(result.hard_violations) > 0

    def test_above_max_size_soft_violation(self):
        v = GroupValidator(min_size=2, max_size=3)
        result = v.validate(
            [["a", "b", "c", "d"], ["e", "f"]],
            ["a", "b", "c", "d", "e", "f"],
        )
        assert result.valid is True
        assert result.hard_violations == []
        assert len(result.soft_violations) > 0

    def test_missing_ids_hard_violation(self):
        v = GroupValidator(min_size=1, max_size=5)
        result = v.validate([["a", "b"]], ["a", "b", "c", "d"])
        assert result.valid is False

    def test_duplicate_ids_hard_violation(self):
        v = GroupValidator(min_size=1, max_size=5)
        result = v.validate([["a", "b", "a"], ["c"]], ["a", "b", "c"])
        assert result.valid is False


# ── even_split_fallback ─────────────────────────────────────────


class TestEvenSplitFallback:
    def test_even_split(self):
        result = even_split_fallback(
            ["a", "b", "c", "d", "e", "f", "g", "h"], target_size=4
        )
        assert result == [["a", "b", "c", "d"], ["e", "f", "g", "h"]]

    def test_uneven_split(self):
        result = even_split_fallback(["a", "b", "c", "d", "e"], target_size=4)
        assert len(result) == 2
        flat = [x for g in result for x in g]
        assert flat == ["a", "b", "c", "d", "e"]

    def test_fewer_than_target_single_group(self):
        result = even_split_fallback(["a", "b", "c"], target_size=4)
        assert result == [["a", "b", "c"]]

    def test_preserves_order(self):
        ids = ["z", "y", "x", "w", "v", "u"]
        flat = [x for g in even_split_fallback(ids, target_size=3) for x in g]
        assert flat == ids

    def test_custom_target_size(self):
        result = even_split_fallback(["a", "b", "c", "d", "e", "f"], target_size=3)
        assert len(result) == 2
        assert all(len(g) == 3 for g in result)


# ── AggregationSweeper: threshold triggers ──────────────────────


class TestAggregationSweeperThresholds:
    def test_no_aggregation_below_both_thresholds(self):
        # 3 chunks × 26 tokens = 78 < 100, count 3 ≤ 5
        state = _state_with_pending(3)
        llm = _mock_llm()
        sweeper = AggregationSweeper(llm, _config())

        sweeper.sweep(state)

        llm.group_summaries.assert_not_called()
        assert len(state.blocks) == 0
        assert state.pending_summaries[0] == [
            "chunk-001",
            "chunk-002",
            "chunk-003",
        ]

    def test_token_threshold_triggers(self):
        # 4 chunks × 26 tokens = 104 > 100
        state = _state_with_pending(4)
        llm = _mock_llm(groups=[[0, 1], [2, 3]])
        sweeper = AggregationSweeper(llm, _config())

        sweeper.sweep(state)

        llm.group_summaries.assert_called_once()
        assert len(state.blocks) == 2

    def test_count_threshold_triggers(self):
        # 6 chunks, each ~2 tokens (12 total < 100), count 6 > 5
        state = _state_with_pending(6, summary=SHORT_SUMMARY)
        llm = _mock_llm(groups=[[0, 1, 2], [3, 4, 5]])
        sweeper = AggregationSweeper(llm, _config())

        sweeper.sweep(state)

        llm.group_summaries.assert_called_once()
        assert len(state.blocks) == 2


# ── AggregationSweeper: block creation ──────────────────────────


class TestAggregationSweeperBlockCreation:
    def test_blocks_have_correct_level_and_children(self):
        state = _state_with_pending(4)
        llm = _mock_llm(groups=[[0, 1], [2, 3]], summary="Block summary.")
        sweeper = AggregationSweeper(llm, _config())

        sweeper.sweep(state)

        for block in state.blocks.values():
            assert block.level == 0
            assert len(block.child_ids) == 2
            assert block.summary == "Block summary."

    def test_children_parent_block_id_updated(self):
        state = _state_with_pending(4)
        llm = _mock_llm(groups=[[0, 1], [2, 3]])
        sweeper = AggregationSweeper(llm, _config())

        sweeper.sweep(state)

        for block in state.blocks.values():
            for child_id in block.child_ids:
                assert state.chunks[child_id].parent_block_id == block.id

    def test_pending_summaries_cleared_and_next_level_populated(self):
        state = _state_with_pending(4)
        llm = _mock_llm(groups=[[0, 1], [2, 3]])
        sweeper = AggregationSweeper(llm, _config())

        sweeper.sweep(state)

        assert 0 not in state.pending_summaries or state.pending_summaries[0] == []
        assert 1 in state.pending_summaries
        assert len(state.pending_summaries[1]) == 2


# ── AggregationSweeper: group validation / retry ────────────────


class TestAggregationSweeperGroupValidation:
    def test_hard_violation_reprompts(self):
        state = _state_with_pending(4)
        bad = GroupingResult(groups=[[0], [1, 2, 3]])
        good = GroupingResult(groups=[[0, 1], [2, 3]])
        llm = _mock_llm()
        llm.group_summaries.side_effect = [bad, good]
        sweeper = AggregationSweeper(llm, _config())

        sweeper.sweep(state)

        assert llm.group_summaries.call_count == 2
        assert len(state.blocks) == 2

    def test_even_split_fallback_after_two_hard_failures(self, caplog):
        state = _state_with_pending(6)
        bad = GroupingResult(groups=[[0], [1, 2, 3, 4, 5]])
        llm = _mock_llm()
        llm.group_summaries.return_value = bad
        sweeper = AggregationSweeper(llm, _config())

        with caplog.at_level(logging.WARNING):
            sweeper.sweep(state)

        assert llm.group_summaries.call_count == 2
        # even_split_fallback(6, target=4) → 2 groups of 3
        assert len(state.blocks) == 2
        assert any("grouping_fallback" in r.message for r in caplog.records)

    def test_soft_violation_reprompts_then_accepts(self):
        config = _config(max_group_size=3)
        state = _state_with_pending(6)
        oversized = GroupingResult(groups=[[0, 1, 2, 3], [4, 5]])
        llm = _mock_llm()
        llm.group_summaries.side_effect = [oversized, oversized]
        sweeper = AggregationSweeper(llm, config)

        sweeper.sweep(state)

        assert llm.group_summaries.call_count == 2
        assert len(state.blocks) == 2


# ── AggregationSweeper: recursion ───────────────────────────────


class TestAggregationSweeperRecursion:
    def test_recursive_aggregation_through_levels(self):
        config = _config(
            summary_aggregation_threshold=5,
            summary_count_threshold=1,
        )
        state = _state_with_pending(8)
        l0_groups = GroupingResult(groups=[[0, 1, 2, 3], [4, 5, 6, 7]])
        l1_groups = GroupingResult(groups=[[0, 1]])
        llm = _mock_llm()
        llm.group_summaries.side_effect = [l0_groups, l1_groups]
        llm.summarize_group.return_value = "Level summary."
        sweeper = AggregationSweeper(llm, config)

        sweeper.sweep(state)

        assert llm.group_summaries.call_count == 2
        levels = {b.level for b in state.blocks.values()}
        assert 0 in levels
        assert 1 in levels
        assert len(state.blocks) == 3

    def test_recursion_stops_below_thresholds(self):
        state = _state_with_pending(4)
        llm = _mock_llm(groups=[[0, 1], [2, 3]])
        sweeper = AggregationSweeper(llm, _config())

        sweeper.sweep(state)

        assert llm.group_summaries.call_count == 1
        levels = {b.level for b in state.blocks.values()}
        assert levels == {0}

    def test_recursion_stops_single_block(self):
        config = _config(
            summary_aggregation_threshold=5,
            summary_count_threshold=1,
        )
        state = _state_with_pending(4)
        llm = _mock_llm(groups=[[0, 1, 2, 3]])
        sweeper = AggregationSweeper(llm, config)

        sweeper.sweep(state)

        assert llm.group_summaries.call_count == 1
        assert len(state.blocks) == 1
