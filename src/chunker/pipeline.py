from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from langchain_ollama import ChatOllama

from chunker.checkpoint import Checkpointer
from chunker.config import ChunkerConfig
from chunker.context import ContextBuilder
from chunker.llm.service import LLMService
from chunker.nodes.aggregation import AggregationSweeper
from chunker.nodes.chunking import ChunkExtractor
from chunker.nodes.rewriting import ChunkRewriter
from chunker.state import PipelineState

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    state: PipelineState
    total_chunks: int
    total_blocks: int
    root_block_ids: list[str]
    warnings: list[str] = field(default_factory=list)

    @classmethod
    def from_state(
        cls, state: PipelineState, warnings: list[str] | None = None
    ) -> ProcessingResult:
        root_ids = [
            bid
            for bid, block in state.blocks.items()
            if block.parent_block_id is None
        ]
        return cls(
            state=state,
            total_chunks=len(state.chunks),
            total_blocks=len(state.blocks),
            root_block_ids=sorted(root_ids),
            warnings=warnings or [],
        )


class Pipeline:
    def __init__(self, config: ChunkerConfig) -> None:
        self._config = config
        model = ChatOllama(model=config.model, base_url=config.ollama_base_url)
        llm_service = LLMService(model, config)
        context_builder = ContextBuilder(config)

        self._extractor = ChunkExtractor(llm_service, config)
        self._rewriter = ChunkRewriter(llm_service, context_builder)
        self._sweeper = AggregationSweeper(llm_service, config)
        self._checkpointer = Checkpointer(Path(config.checkpoint_path))

    def run(self, text: str, document_id: str) -> ProcessingResult:
        state = PipelineState.create(document_id, text)
        return self._process(state)

    def resume(self) -> ProcessingResult:
        state = self._checkpointer.load()
        return self._process(state)

    def _process(self, state: PipelineState) -> ProcessingResult:
        while state.has_more_text:
            chunk = self._extractor.extract_next(state)
            chunk = self._rewriter.rewrite(chunk, state)
            state.chunks[chunk.id] = chunk
            state.pending_summaries.setdefault(0, []).append(chunk.id)
            self._sweeper.sweep(state)
            self._checkpointer.save(state)

        return ProcessingResult.from_state(state)
