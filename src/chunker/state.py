from __future__ import annotations

import json
from dataclasses import dataclass, field

from chunker.models import Chunk, SummaryBlock


@dataclass
class PipelineState:
    document_id: str
    source_text: str
    cursor_position: int
    chunks: dict[str, Chunk]
    blocks: dict[str, SummaryBlock]
    pending_summaries: dict[int, list[str]]
    chunk_counter: int
    block_counters: dict[int, int]

    @classmethod
    def create(cls, document_id: str, source_text: str) -> PipelineState:
        return cls(
            document_id=document_id,
            source_text=source_text,
            cursor_position=0,
            chunks={},
            blocks={},
            pending_summaries={},
            chunk_counter=0,
            block_counters={},
        )

    @property
    def has_more_text(self) -> bool:
        return self.cursor_position < len(self.source_text)

    def to_dict(self) -> dict:
        return {
            "document_id": self.document_id,
            "source_text": self.source_text,
            "cursor_position": self.cursor_position,
            "chunks": {k: v.to_dict() for k, v in self.chunks.items()},
            "blocks": {k: v.to_dict() for k, v in self.blocks.items()},
            "pending_summaries": {
                str(k): v for k, v in self.pending_summaries.items()
            },
            "chunk_counter": self.chunk_counter,
            "block_counters": {
                str(k): v for k, v in self.block_counters.items()
            },
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict) -> PipelineState:
        return cls(
            document_id=data["document_id"],
            source_text=data["source_text"],
            cursor_position=data["cursor_position"],
            chunks={
                k: Chunk.from_dict(v) for k, v in data["chunks"].items()
            },
            blocks={
                k: SummaryBlock.from_dict(v)
                for k, v in data["blocks"].items()
            },
            pending_summaries={
                int(k): v for k, v in data["pending_summaries"].items()
            },
            chunk_counter=data["chunk_counter"],
            block_counters={
                int(k): v for k, v in data["block_counters"].items()
            },
        )

    @classmethod
    def from_json(cls, raw: str) -> PipelineState:
        return cls.from_dict(json.loads(raw))
