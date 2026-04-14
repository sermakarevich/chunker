from __future__ import annotations

import re

from chunker.config import (
    MODEL_PROFILES,
    ChunkerConfig,
    estimate_tokens,
)

_SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")
_PARAGRAPH_PATTERN = re.compile(r"\n\n+")
_WORD_PATTERN = re.compile(r"\s+")

_STRATEGY_PATTERNS = {
    "sentences": _SENTENCE_PATTERN,
    "paragraphs": _PARAGRAPH_PATTERN,
    "words": _WORD_PATTERN,
}

_DEFAULT_TOKEN_FACTOR = 1.0


class TextSplitter:
    def __init__(self, strategy: str) -> None:
        if strategy not in _STRATEGY_PATTERNS:
            raise ValueError(
                f"Invalid strategy '{strategy}'. "
                f"Must be one of: sentences, paragraphs, words"
            )
        self._strategy = strategy
        self._pattern = _STRATEGY_PATTERNS[strategy]

    def split_from(self, text: str, start: int) -> list[int]:
        boundaries: list[int] = []
        for match in self._pattern.finditer(text):
            pos = match.end()
            if pos > start:
                boundaries.append(pos)
        return boundaries


class CursorWindow:
    def __init__(
        self,
        source_text: str,
        cursor: int,
        splitter: TextSplitter,
        config: ChunkerConfig,
    ) -> None:
        self._source_text = source_text
        self._start = cursor
        self._end = cursor
        self._boundaries = splitter.split_from(source_text, cursor)
        self._boundary_idx = 0

        profile = MODEL_PROFILES.get(config.model)
        self._token_factor = profile.token_factor if profile else _DEFAULT_TOKEN_FACTOR
        self._min_chunk_tokens = config.min_chunk_tokens

        while self.token_count < self._min_chunk_tokens:
            if not self.expand():
                break

    @property
    def text(self) -> str:
        return self._source_text[self._start : self._end]

    @property
    def start(self) -> int:
        return self._start

    @property
    def end(self) -> int:
        return self._end

    @property
    def token_count(self) -> int:
        return estimate_tokens(self.text, self._token_factor)

    def expand(self) -> bool:
        if self._end >= len(self._source_text):
            return False
        if self._boundary_idx < len(self._boundaries):
            self._end = self._boundaries[self._boundary_idx]
            self._boundary_idx += 1
            return True
        self._end = len(self._source_text)
        return True

    def set_end(self, position: int) -> None:
        self._end = position

    def last_sentence_boundary(self) -> int:
        sentence_splitter = TextSplitter("sentences")
        boundaries = sentence_splitter.split_from(self._source_text, self._start)
        last = self._start
        for b in boundaries:
            if b <= self._end:
                last = b
            else:
                break
        return last
