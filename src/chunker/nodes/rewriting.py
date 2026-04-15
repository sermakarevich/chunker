from __future__ import annotations

from chunker.context import ContextBuilder
from chunker.llm.service import LLMService
from chunker.models import Chunk
from chunker.state import PipelineState


class ChunkRewriter:
    def __init__(
        self, llm_service: LLMService, context_builder: ContextBuilder
    ) -> None:
        self._llm = llm_service
        self._context = context_builder

    def rewrite(self, chunk: Chunk, state: PipelineState) -> Chunk:
        items = self._context.build(state)
        context_text = self._context.format_context(items)
        result = self._llm.rewrite_chunk(
            chunk.original_text, context_text, chunk_id=chunk.id
        )
        chunk.context = result.context
        chunk.summary = result.summary
        chunk.filename = result.filename
        return chunk
