from __future__ import annotations

from pathlib import Path

_TEMPLATE_DIR = Path(__file__).parent / "prompt_templates"

_cache: dict[str, str] = {}


def _load(name: str) -> str:
    if name not in _cache:
        _cache[name] = (_TEMPLATE_DIR / f"{name}.txt").read_text()
    return _cache[name]


def completeness_prompt(window_text: str, context_text: str) -> str:
    return _load("completeness").format(
        window_text=window_text, context_text=context_text
    )


def rewrite_prompt(chunk_text: str, context_text: str) -> str:
    return _load("rewrite").format(chunk_text=chunk_text, context_text=context_text)


def grouping_prompt(summaries_text: str, min_size: int, max_size: int) -> str:
    return _load("grouping").format(
        summaries_text=summaries_text, min_size=min_size, max_size=max_size
    )


def synthesize_prompt(
    children_text: str, metadata_text: str, min_tokens: int, max_tokens: int
) -> str:
    return _load("synthesize").format(
        children_text=children_text,
        metadata_text=metadata_text,
        min_tokens=min_tokens,
        max_tokens=max_tokens,
    )
