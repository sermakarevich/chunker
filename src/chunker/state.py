from __future__ import annotations

import json
from dataclasses import dataclass

from chunker.models import Chunk, Page, SummaryBlock


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
    pages: list[Page] | None = None  # present in pdf mode
    cursor_page: int = 0  # 0-based index of the next unprocessed page

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

    @classmethod
    def create_from_pages(cls, document_id: str, pages: list[Page]) -> PipelineState:
        return cls(
            document_id=document_id,
            source_text="",
            cursor_position=0,
            chunks={},
            blocks={},
            pending_summaries={},
            chunk_counter=0,
            block_counters={},
            pages=pages,
            cursor_page=0,
        )

    @property
    def has_more_text(self) -> bool:
        return self.cursor_position < len(self.source_text)

    @property
    def has_more_pages(self) -> bool:
        return self.pages is not None and self.cursor_page < len(self.pages)

    @property
    def has_more_input(self) -> bool:
        return self.has_more_text or self.has_more_pages

    def to_dict(self) -> dict:
        return {
            "document_id": self.document_id,
            "source_text": self.source_text,
            "cursor_position": self.cursor_position,
            "chunks": {k: v.to_dict() for k, v in self.chunks.items()},
            "blocks": {k: v.to_dict() for k, v in self.blocks.items()},
            "pending_summaries": {str(k): v for k, v in self.pending_summaries.items()},
            "chunk_counter": self.chunk_counter,
            "block_counters": {str(k): v for k, v in self.block_counters.items()},
            "pages": [p.to_dict() for p in self.pages] if self.pages else None,
            "cursor_page": self.cursor_page,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict) -> PipelineState:
        return cls(
            document_id=data["document_id"],
            source_text=data["source_text"],
            cursor_position=data["cursor_position"],
            chunks={k: Chunk.from_dict(v) for k, v in data["chunks"].items()},
            blocks={k: SummaryBlock.from_dict(v) for k, v in data["blocks"].items()},
            pending_summaries={int(k): v for k, v in data["pending_summaries"].items()},
            chunk_counter=data["chunk_counter"],
            block_counters={int(k): v for k, v in data["block_counters"].items()},
            pages=[Page.from_dict(p) for p in data["pages"]]
            if data.get("pages")
            else None,
            cursor_page=data.get("cursor_page", 0),
        )

    @classmethod
    def from_json(cls, raw: str) -> PipelineState:
        return cls.from_dict(json.loads(raw))
