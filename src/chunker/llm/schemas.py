from __future__ import annotations

from pydantic import BaseModel


class CompletenessResult(BaseModel):
    complete: bool
    boundary_phrase: str | None = None


class RewriteResult(BaseModel):
    context: str
    summary: str
    filename: str


class GroupingResult(BaseModel):
    groups: list[list[int]]


class BlockContextResult(BaseModel):
    context: str
    summary: str
    filename: str
