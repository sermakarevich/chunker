from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass

from chunker.config import MODEL_PROFILES, ChunkerConfig, estimate_tokens
from chunker.llm.service import LLMService
from chunker.models import SummaryBlock
from chunker.state import PipelineState

logger = logging.getLogger(__name__)

_DEFAULT_TOKEN_FACTOR = 1.0


@dataclass
class ValidationResult:
    valid: bool
    hard_violations: list[str]
    soft_violations: list[str]


class GroupValidator:
    def __init__(self, min_size: int, max_size: int) -> None:
        self._min_size = min_size
        self._max_size = max_size

    def validate(
        self, groups: list[list[str]], ordered_ids: list[str]
    ) -> ValidationResult:
        hard: list[str] = []
        soft: list[str] = []

        # Check contiguity: flattened groups must equal ordered_ids
        flat = [item for group in groups for item in group]
        if flat != ordered_ids:
            hard.append(
                f"Non-contiguous or incomplete grouping: "
                f"expected {len(ordered_ids)} ids, got {len(flat)} "
                f"(flattened groups do not match ordered list)"
            )

        for i, group in enumerate(groups):
            if len(group) < self._min_size:
                hard.append(
                    f"Group {i} has {len(group)} items, "
                    f"below min_group_size={self._min_size}"
                )
            if len(group) > self._max_size:
                soft.append(
                    f"Group {i} has {len(group)} items, "
                    f"above max_group_size={self._max_size}"
                )

        return ValidationResult(
            valid=len(hard) == 0,
            hard_violations=hard,
            soft_violations=soft,
        )


def even_split_fallback(ids: list[str], target_size: int = 4) -> list[list[str]]:
    n = len(ids)
    if n == 0:
        return []
    num_groups = math.ceil(n / target_size)
    base_size = n // num_groups
    remainder = n % num_groups
    groups: list[list[str]] = []
    start = 0
    for i in range(num_groups):
        size = base_size + (1 if i < remainder else 0)
        groups.append(ids[start : start + size])
        start += size
    return groups


class AggregationSweeper:
    def __init__(self, llm_service: LLMService, config: ChunkerConfig) -> None:
        self._llm = llm_service
        self._config = config
        profile = MODEL_PROFILES.get(config.model)
        self._token_factor = profile.token_factor if profile else _DEFAULT_TOKEN_FACTOR

    def sweep(self, state: PipelineState) -> None:
        level = 0
        while True:
            pending_ids = state.pending_summaries.get(level, [])
            if not pending_ids:
                break

            if not self._thresholds_exceeded(state, level, pending_ids):
                level += 1
                continue

            groups = self._resolve_groups(state, level, pending_ids)
            self._create_blocks(state, level, groups, pending_ids)

            state.pending_summaries[level] = []

            # If only one block was created, it's the root — stop
            if len(state.pending_summaries.get(level + 1, [])) <= 1:
                break

            level += 1

    def _thresholds_exceeded(
        self, state: PipelineState, level: int, pending_ids: list[str]
    ) -> bool:
        total_tokens = sum(
            estimate_tokens(self._get_summary(state, item_id), self._token_factor)
            for item_id in pending_ids
        )
        count = len(pending_ids)
        return (
            total_tokens > self._config.summary_aggregation_threshold
            or count > self._config.summary_count_threshold
        )

    def _get_summary(self, state: PipelineState, item_id: str) -> str:
        if item_id in state.chunks:
            return state.chunks[item_id].summary
        if item_id in state.blocks:
            return state.blocks[item_id].summary
        return ""

    def _get_context(self, state: PipelineState, item_id: str) -> str:
        if item_id in state.chunks:
            return state.chunks[item_id].context
        if item_id in state.blocks:
            return state.blocks[item_id].context
        return ""

    def _build_metadata(
        self,
        state: PipelineState,
        group_ids: list[str],
        level: int,
    ) -> str:
        parts: list[str] = []

        # Previous item's context (item immediately before this group)
        pending = state.pending_summaries.get(level, [])
        first_id = group_ids[0]
        try:
            idx = pending.index(first_id)
        except ValueError:
            idx = -1
        if idx > 0:
            prev_context = self._get_context(state, pending[idx - 1])
            if prev_context:
                parts.append(f"Previous context:\n{prev_context}")

        # Latest block context at each level above current
        higher_blocks: dict[int, str] = {}
        for block in state.blocks.values():
            if block.level > level:
                higher_blocks[block.level] = block.context
        for lvl in sorted(higher_blocks):
            parts.append(f"Level {lvl} context:\n{higher_blocks[lvl]}")

        return "\n\n".join(parts)

    def _resolve_groups(
        self,
        state: PipelineState,
        level: int,
        pending_ids: list[str],
    ) -> list[list[str]]:
        summaries = [
            {"id": item_id, "summary": self._get_summary(state, item_id)}
            for item_id in pending_ids
        ]
        validator = GroupValidator(
            self._config.min_group_size, self._config.max_group_size
        )

        consecutive_hard = 0
        max_attempts = 5

        for _ in range(max_attempts):
            if consecutive_hard >= 2:
                logger.warning(
                    json.dumps({"event": "grouping_fallback", "level": level})
                )
                return even_split_fallback(pending_ids)

            result = self._llm.group_summaries(
                summaries, self._config.min_group_size, self._config.max_group_size
            )
            groups = self._indices_to_ids(result.groups, pending_ids)
            validation = validator.validate(groups, pending_ids)

            if not validation.hard_violations and not validation.soft_violations:
                return groups

            if validation.hard_violations:
                consecutive_hard += 1
                continue

            # Soft violations only — re-prompt once, accept result
            result2 = self._llm.group_summaries(
                summaries, self._config.min_group_size, self._config.max_group_size
            )
            groups2 = self._indices_to_ids(result2.groups, pending_ids)
            validation2 = validator.validate(groups2, pending_ids)
            if not validation2.hard_violations:
                return groups2
            consecutive_hard += 1
            continue

        return even_split_fallback(pending_ids)

    @staticmethod
    def _indices_to_ids(
        index_groups: list[list[int]], ordered_ids: list[str]
    ) -> list[list[str]]:
        return [[ordered_ids[idx] for idx in group] for group in index_groups]

    def _create_blocks(
        self,
        state: PipelineState,
        level: int,
        groups: list[list[str]],
        pending_ids: list[str],
    ) -> None:
        for group_ids in groups:
            state.block_counters[level] = state.block_counters.get(level, 0) + 1
            block_id = f"block-L{level}-{state.block_counters[level]:03d}"

            child_contexts = [
                self._get_context(state, child_id) for child_id in group_ids
            ]
            metadata_text = self._build_metadata(state, group_ids, level)
            result = self._llm.synthesize_block(
                children_contexts=child_contexts,
                metadata_text=metadata_text,
                min_tokens=self._config.min_chunk_tokens,
                max_tokens=self._config.max_chunk_tokens,
                block_id=block_id,
            )

            block = SummaryBlock(
                id=block_id,
                level=level,
                context=result.context,
                summary=result.summary,
                filename=result.filename,
                child_ids=group_ids,
                parent_block_id=None,
                metadata={},
            )
            state.blocks[block_id] = block

            for child_id in group_ids:
                if child_id in state.chunks:
                    state.chunks[child_id].parent_block_id = block_id
                elif child_id in state.blocks:
                    state.blocks[child_id].parent_block_id = block_id

            state.pending_summaries.setdefault(level + 1, []).append(block_id)
