import json

from chunker.config import (
    MODEL_PROFILES,
    ChunkerConfig,
    estimate_tokens,
)


class TestModelProfile:
    def test_has_required_fields(self):
        profile = MODEL_PROFILES["qwen3:32b"]
        assert profile.context_window == 32768
        assert profile.max_chunk_tokens == 4000
        assert profile.context_budget_tokens == 20000
        assert profile.token_factor == 1.3

    def test_gemma_profile(self):
        profile = MODEL_PROFILES["gemma4:26b"]
        assert profile.context_window == 16384
        assert profile.max_chunk_tokens == 4000
        assert profile.context_budget_tokens == 20000
        assert profile.token_factor == 1.2

    def test_is_json_serializable(self):
        profile = MODEL_PROFILES["qwen3:32b"]
        data = json.loads(json.dumps(profile.__dict__))
        assert data["context_window"] == 32768


class TestChunkerConfig:
    def test_defaults(self):
        config = ChunkerConfig()
        assert config.split_strategy == "sentences"
        assert config.min_chunk_tokens == 2000
        assert config.max_chunk_tokens == 4000
        assert config.max_expansion_attempts == 5
        assert config.summary_aggregation_threshold == 4000
        assert config.summary_count_threshold == 8
        assert config.min_group_size == 2
        assert config.max_group_size == 5
        assert config.context_budget_tokens == 20000
        assert config.checkpoint_path == "checkpoint.json"
        assert config.output_dir == "output"
        assert config.model == "qwen3:32b"
        assert config.ollama_base_url == "http://localhost:11434"

    def test_from_model_applies_profile(self):
        config = ChunkerConfig.from_model("gemma4:26b")
        assert config.model == "gemma4:26b"
        assert config.max_chunk_tokens == 4000
        assert config.context_budget_tokens == 20000

    def test_from_model_default(self):
        config = ChunkerConfig.from_model("qwen3:32b")
        assert config.model == "qwen3:32b"
        assert config.max_chunk_tokens == 4000
        assert config.context_budget_tokens == 20000

    def test_from_model_unknown_uses_defaults(self):
        config = ChunkerConfig.from_model("unknown-model:7b")
        assert config.model == "unknown-model:7b"
        assert config.max_chunk_tokens == 4000  # default

    def test_from_model_with_overrides(self):
        config = ChunkerConfig.from_model("gemma4:26b", min_chunk_tokens=200)
        assert config.min_chunk_tokens == 200
        assert config.max_chunk_tokens == 4000  # from profile

    def test_is_json_serializable(self):
        config = ChunkerConfig()
        data = json.loads(json.dumps(config.__dict__))
        assert data["model"] == "qwen3:32b"


class TestEstimateTokens:
    def test_basic(self):
        text = "one two three four five"
        assert estimate_tokens(text, factor=1.0) == 5

    def test_with_factor(self):
        text = "one two three four five"
        assert estimate_tokens(text, factor=1.3) == 7  # ceil(5 * 1.3) = 7

    def test_empty_string(self):
        assert estimate_tokens("", factor=1.3) == 0
