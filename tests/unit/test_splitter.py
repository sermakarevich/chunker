import pytest

from chunker.config import MODEL_PROFILES, ChunkerConfig, estimate_tokens
from chunker.splitter import CursorWindow, TextSplitter


class TestTextSplitter:
    def test_valid_strategies(self):
        for strategy in ("sentences", "paragraphs", "words"):
            TextSplitter(strategy)

    def test_invalid_strategy_raises(self):
        with pytest.raises(ValueError, match="sentences.*paragraphs.*words"):
            TextSplitter("invalid")

    def test_sentence_split_simple(self):
        text = "Hello world. The next. Final."
        splitter = TextSplitter("sentences")
        boundaries = splitter.split_from(text, 0)
        assert boundaries == [13, 23]

    def test_sentence_split_various_punctuation(self):
        text = "Wow! Really? Yes."
        splitter = TextSplitter("sentences")
        boundaries = splitter.split_from(text, 0)
        assert boundaries == [5, 13]

    def test_sentence_split_from_nonzero_start(self):
        text = "Hello world. The next. Final."
        splitter = TextSplitter("sentences")
        boundaries = splitter.split_from(text, 13)
        assert boundaries == [23]

    def test_sentence_split_no_boundaries(self):
        text = "no punctuation here"
        splitter = TextSplitter("sentences")
        assert splitter.split_from(text, 0) == []

    def test_sentence_split_fixture(self, agentic_rag_text):
        splitter = TextSplitter("sentences")
        boundaries = splitter.split_from(agentic_rag_text, 0)
        assert len(boundaries) > 10
        assert all(0 < b <= len(agentic_rag_text) for b in boundaries)
        assert boundaries == sorted(boundaries)

    def test_paragraph_split(self):
        text = "First paragraph.\n\nSecond paragraph.\n\nThird."
        splitter = TextSplitter("paragraphs")
        boundaries = splitter.split_from(text, 0)
        assert boundaries == [18, 37]

    def test_paragraph_split_from_nonzero(self):
        text = "First paragraph.\n\nSecond paragraph.\n\nThird."
        splitter = TextSplitter("paragraphs")
        boundaries = splitter.split_from(text, 18)
        assert boundaries == [37]

    def test_word_split(self):
        text = "one two three four"
        splitter = TextSplitter("words")
        boundaries = splitter.split_from(text, 0)
        assert boundaries == [4, 8, 14]

    def test_word_split_from_nonzero(self):
        text = "one two three four"
        splitter = TextSplitter("words")
        boundaries = splitter.split_from(text, 8)
        assert boundaries == [14]


class TestCursorWindow:
    @pytest.fixture()
    def config(self):
        return ChunkerConfig(min_chunk_tokens=10)

    @pytest.fixture()
    def splitter(self):
        return TextSplitter("sentences")

    def test_source_span_invariant(self, agentic_rag_text, config, splitter):
        window = CursorWindow(agentic_rag_text, 0, splitter, config)
        assert agentic_rag_text[window.start : window.end] == window.text

    def test_initial_expansion_to_min_tokens(self, agentic_rag_text, config, splitter):
        window = CursorWindow(agentic_rag_text, 0, splitter, config)
        assert window.token_count >= config.min_chunk_tokens
        assert window.start == 0
        assert window.end > 0

    def test_expand_returns_true_when_more_text(
        self, agentic_rag_text, config, splitter
    ):
        window = CursorWindow(agentic_rag_text, 0, splitter, config)
        initial_end = window.end
        result = window.expand()
        assert result is True
        assert window.end > initial_end

    def test_expand_through_boundaries_to_end(self):
        text = "one two three"
        config = ChunkerConfig(min_chunk_tokens=0)
        splitter = TextSplitter("words")
        window = CursorWindow(text, 0, splitter, config)

        assert window.expand() is True
        assert window.end == 4
        assert window.expand() is True
        assert window.end == 8
        assert window.expand() is True
        assert window.end == 13
        assert window.expand() is False

    def test_set_end(self, agentic_rag_text, config, splitter):
        window = CursorWindow(agentic_rag_text, 0, splitter, config)
        window.set_end(100)
        assert window.end == 100
        assert window.text == agentic_rag_text[0:100]

    def test_token_count_uses_estimate_tokens(self):
        text = "one two three four five six seven eight nine ten"
        config = ChunkerConfig.from_model("qwen3:32b", min_chunk_tokens=0)
        splitter = TextSplitter("words")
        window = CursorWindow(text, 0, splitter, config)
        window.set_end(len(text))
        factor = MODEL_PROFILES["qwen3:32b"].token_factor
        expected = estimate_tokens(text, factor)
        assert window.token_count == expected

    def test_last_sentence_boundary(self):
        text = "First sentence. Second sentence. Third sentence."
        config = ChunkerConfig(min_chunk_tokens=0)
        splitter = TextSplitter("sentences")
        window = CursorWindow(text, 0, splitter, config)
        while window.expand():
            pass
        assert window.last_sentence_boundary() == 33

    def test_last_sentence_boundary_returns_start_when_none(self):
        text = "no punctuation here at all"
        config = ChunkerConfig(min_chunk_tokens=0)
        splitter = TextSplitter("sentences")
        window = CursorWindow(text, 0, splitter, config)
        while window.expand():
            pass
        assert window.last_sentence_boundary() == window.start

    def test_last_sentence_boundary_with_paragraph_strategy(self):
        text = "First sentence. Second sentence.\n\nThird paragraph."
        config = ChunkerConfig(min_chunk_tokens=0)
        splitter = TextSplitter("paragraphs")
        window = CursorWindow(text, 0, splitter, config)
        while window.expand():
            pass
        boundary = window.last_sentence_boundary()
        assert boundary > window.start

    def test_source_span_invariant_after_multiple_expands(
        self, agentic_rag_text, config, splitter
    ):
        window = CursorWindow(agentic_rag_text, 0, splitter, config)
        for _ in range(5):
            if not window.expand():
                break
            assert agentic_rag_text[window.start : window.end] == window.text

    def test_continuation_from_nonzero_cursor(self, agentic_rag_text, splitter):
        config = ChunkerConfig(min_chunk_tokens=10)
        window1 = CursorWindow(agentic_rag_text, 0, splitter, config)
        cursor = window1.end
        window2 = CursorWindow(agentic_rag_text, cursor, splitter, config)
        assert window2.start == cursor
        assert window2.token_count >= config.min_chunk_tokens
        assert agentic_rag_text[window2.start : window2.end] == window2.text
