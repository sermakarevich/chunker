from __future__ import annotations

from pydantic import BaseModel


class CompletenessResult(BaseModel):
    complete: bool
    boundary_phrase: str | None = None


class RewriteResult(BaseModel):
    rewritten_text: str
    summary: str


class GroupingResult(BaseModel):
    groups: list[list[int]]


class BlockSummaryResult(BaseModel):
    summary: str
