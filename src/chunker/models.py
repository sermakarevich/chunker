from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass
class Chunk:
    id: str
    source_span: tuple[int, int]
    original_text: str
    context: str
    summary: str
    filename: str
    parent_block_id: str | None
    forced_split: bool
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source_span": list(self.source_span),
            "original_text": self.original_text,
            "context": self.context,
            "summary": self.summary,
            "filename": self.filename,
            "parent_block_id": self.parent_block_id,
            "forced_split": self.forced_split,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict) -> Chunk:
        return cls(
            id=data["id"],
            source_span=tuple(data["source_span"]),
            original_text=data["original_text"],
            context=data["context"],
            summary=data["summary"],
            filename=data["filename"],
            parent_block_id=data["parent_block_id"],
            forced_split=data["forced_split"],
            metadata=data["metadata"],
        )

    @classmethod
    def from_json(cls, raw: str) -> Chunk:
        return cls.from_dict(json.loads(raw))


@dataclass
class SummaryBlock:
    id: str
    level: int
    context: str
    summary: str
    filename: str
    child_ids: list[str]
    parent_block_id: str | None
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "level": self.level,
            "context": self.context,
            "summary": self.summary,
            "filename": self.filename,
            "child_ids": self.child_ids,
            "parent_block_id": self.parent_block_id,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict) -> SummaryBlock:
        return cls(
            id=data["id"],
            level=data["level"],
            context=data["context"],
            summary=data["summary"],
            filename=data["filename"],
            child_ids=data["child_ids"],
            parent_block_id=data["parent_block_id"],
            metadata=data["metadata"],
        )

    @classmethod
    def from_json(cls, raw: str) -> SummaryBlock:
        return cls.from_dict(json.loads(raw))
