from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class ModelProfile:
    context_window: int
    max_chunk_tokens: int
    context_budget_tokens: int
    token_factor: float


MODEL_PROFILES: dict[str, ModelProfile] = {
    "qwen3:32b": ModelProfile(
        context_window=32768,
        max_chunk_tokens=4000,
        context_budget_tokens=20000,
        token_factor=1.3,
    ),
    "gemma4:26b": ModelProfile(
        context_window=16384,
        max_chunk_tokens=4000,
        context_budget_tokens=20000,
        token_factor=1.2,
    ),
    "gemma4:latest": ModelProfile(
        context_window=16384,
        max_chunk_tokens=4000,
        context_budget_tokens=20000,
        token_factor=1.2,
    ),
}


@dataclass
class ChunkerConfig:
    split_strategy: str = "sentences"
    min_chunk_tokens: int = 2000
    max_chunk_tokens: int = 4000
    max_expansion_attempts: int = 5

    summary_aggregation_threshold: int = 4000
    summary_count_threshold: int = 8
    min_group_size: int = 2
    max_group_size: int = 5

    context_budget_tokens: int = 20000

    checkpoint_path: str = "checkpoint.json"
    output_dir: str = "output"
    model: str = "qwen3:32b"
    ollama_base_url: str = "http://localhost:11434"

    @classmethod
    def from_model(cls, model: str, **overrides) -> ChunkerConfig:
        profile = MODEL_PROFILES.get(model)
        kwargs: dict = {"model": model}
        if profile is not None:
            kwargs["max_chunk_tokens"] = profile.max_chunk_tokens
            kwargs["context_budget_tokens"] = profile.context_budget_tokens
        kwargs.update(overrides)
        return cls(**kwargs)


def estimate_tokens(text: str, factor: float) -> int:
    words = text.split()
    if not words:
        return 0
    return math.ceil(len(words) * factor)
