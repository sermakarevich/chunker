from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass
class Chunk:
    id: str
    source_span: tuple[int, int]
    original_text: str
    rewritten_text: str
    summary: str
    parent_block_id: str | None
    forced_split: bool
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source_span": list(self.source_span),
            "original_text": self.original_text,
            "rewritten_text": self.rewritten_text,
            "summary": self.summary,
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
            rewritten_text=data["rewritten_text"],
            summary=data["summary"],
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
    summary: str
    child_ids: list[str]
    parent_block_id: str | None
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "level": self.level,
            "summary": self.summary,
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
            summary=data["summary"],
            child_ids=data["child_ids"],
            parent_block_id=data["parent_block_id"],
            metadata=data["metadata"],
        )

    @classmethod
    def from_json(cls, raw: str) -> SummaryBlock:
        return cls.from_dict(json.loads(raw))
