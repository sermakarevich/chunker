from __future__ import annotations

from dataclasses import dataclass

from chunker.config import MODEL_PROFILES, ChunkerConfig, estimate_tokens
from chunker.state import PipelineState

_DEFAULT_TOKEN_FACTOR = 1.0


@dataclass
class ContextItem:
    source: str
    text: str
    token_count: int


class ContextBuilder:
    def __init__(self, config: ChunkerConfig) -> None:
        self._config = config
        profile = MODEL_PROFILES.get(config.model)
        self._token_factor = profile.token_factor if profile else _DEFAULT_TOKEN_FACTOR

    def build(self, state: PipelineState) -> list[ContextItem]:
        budget = self._config.context_budget_tokens
        candidates = self._priority_candidates(state)
        items: list[ContextItem] = []
        used = 0
        for item in candidates:
            if used + item.token_count <= budget:
                items.append(item)
                used += item.token_count
        return items

    def format_context(self, items: list[ContextItem]) -> str:
        if not items:
            return ""
        blocks = []
        for item in items:
            blocks.append(f"[Source: {item.source}]\n{item.text}\n---")
        return "\n\n".join(blocks)

    def _priority_candidates(self, state: PipelineState) -> list[ContextItem]:
        candidates: list[ContextItem] = []

        predecessor = self._predecessor(state)
        if predecessor is not None:
            candidates.append(predecessor)

        candidates.extend(self._level_summaries(state))
        candidates.extend(self._earlier_chunks(state))

        return candidates

    def _predecessor(self, state: PipelineState) -> ContextItem | None:
        if not state.chunks:
            return None
        latest_id = max(state.chunks.keys())
        chunk = state.chunks[latest_id]
        text = chunk.context or chunk.summary or chunk.original_text
        if not text:
            return None
        return ContextItem(
            source=f"predecessor:{latest_id}",
            text=text,
            token_count=estimate_tokens(text, self._token_factor),
        )

    def _level_summaries(self, state: PipelineState) -> list[ContextItem]:
        if not state.blocks:
            return []
        latest_per_level: dict[int, tuple[str, str]] = {}
        for block in state.blocks.values():
            if not block.summary:
                continue
            current = latest_per_level.get(block.level)
            if current is None or block.id > current[0]:
                latest_per_level[block.level] = (block.id, block.summary)

        items: list[ContextItem] = []
        for level in sorted(latest_per_level.keys()):
            block_id, summary = latest_per_level[level]
            items.append(
                ContextItem(
                    source=f"summary:L{level}:{block_id}",
                    text=summary,
                    token_count=estimate_tokens(summary, self._token_factor),
                )
            )
        return items

    def _earlier_chunks(self, state: PipelineState) -> list[ContextItem]:
        if len(state.chunks) < 2:
            return []
        sorted_ids = sorted(state.chunks.keys(), reverse=True)
        items: list[ContextItem] = []
        for chunk_id in sorted_ids[1:]:
            chunk = state.chunks[chunk_id]
            text = chunk.context or chunk.summary or chunk.original_text
            if not text:
                continue
            items.append(
                ContextItem(
                    source=f"earlier:{chunk_id}",
                    text=text,
                    token_count=estimate_tokens(text, self._token_factor),
                )
            )
        return items
