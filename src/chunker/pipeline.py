from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from langchain_ollama import ChatOllama

from chunker.checkpoint import Checkpointer
from chunker.config import ChunkerConfig
from chunker.context import ContextBuilder
from chunker.llm.service import LLMService
from chunker.metrics import Metrics
from chunker.nodes.aggregation import AggregationSweeper
from chunker.nodes.chunking import ChunkExtractor
from chunker.nodes.output import JsonExporter, MarkdownRenderer
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
            bid for bid, block in state.blocks.items() if block.parent_block_id is None
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
        metrics = Metrics()
        if self._checkpointer.exists():
            state = self._checkpointer.load(expected_document_id=document_id)
            metrics.resumed_chunks = len(state.chunks)
            logger.info(
                "Checkpoint found — resuming from chunk %d, position %d/%d",
                state.chunk_counter,
                state.cursor_position,
                len(state.source_text),
            )
        else:
            state = PipelineState.create(document_id, text)
        return self._process(state, metrics)

    def resume(self) -> ProcessingResult:
        metrics = Metrics()
        state = self._checkpointer.load()
        metrics.resumed_chunks = len(state.chunks)
        logger.info(
            "Resuming from chunk %d, position %d/%d",
            state.chunk_counter,
            state.cursor_position,
            len(state.source_text),
        )
        return self._process(state, metrics)

    def _process(self, state: PipelineState, metrics: Metrics) -> ProcessingResult:
        while state.has_more_text:
            with metrics.track("extraction", chunk_id=f"chunk-{state.chunk_counter + 1:03d}"):
                chunk = self._extractor.extract_next(state)

            with metrics.track("rewriting", chunk_id=chunk.id):
                chunk = self._rewriter.rewrite(chunk, state)

            state.chunks[chunk.id] = chunk
            state.pending_summaries.setdefault(0, []).append(chunk.id)

            with metrics.track("aggregation"):
                self._sweeper.sweep(state)

            with metrics.track("checkpointing"):
                self._checkpointer.save(state)

            pct = state.cursor_position / len(state.source_text) * 100
            logger.info(
                "Completed %s — position %d/%d (%.1f%%)",
                chunk.id,
                state.cursor_position,
                len(state.source_text),
                pct,
            )

        with metrics.track("output"):
            self._write_output(state)

        result = ProcessingResult.from_state(state)
        logger.info(metrics.report(result.total_chunks, result.total_blocks))
        return result

    def _write_output(self, state: PipelineState) -> None:
        output_dir = Path(self._config.output_dir)
        JsonExporter().write(state, output_dir / "hierarchy.json")
        MarkdownRenderer().render(state, output_dir)
