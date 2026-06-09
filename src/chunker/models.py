from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass
class Page:
    number: int  # 1-based page number, in document order
    text: str  # extracted text layer (may be "" for image-only pages)
    image_path: str  # absolute path to the rendered PNG on disk (NOT bytes)

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "text": self.text,
            "image_path": self.image_path,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict) -> Page:
        return cls(
            number=data["number"],
            text=data["text"],
            image_path=data["image_path"],
        )

    @classmethod
    def from_json(cls, raw: str) -> Page:
        return cls.from_dict(json.loads(raw))


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
    # (start, end) 1-based inclusive page range; None in text mode
    page_span: tuple[int, int] | None = None
    # rendered page PNG paths covered by this chunk; [] in text mode
    image_paths: list[str] = field(default_factory=list)

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
            "page_span": list(self.page_span) if self.page_span else None,
            "image_paths": self.image_paths,
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
            page_span=tuple(data["page_span"]) if data.get("page_span") else None,
            image_paths=data.get("image_paths", []),
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
