from __future__ import annotations

import base64
import json
import logging
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage

from chunker.config import ChunkerConfig
from chunker.llm.schemas import (
    BlockContextResult,
    CompletenessResult,
    GroupingResult,
    PageCompletenessResult,
    RewriteResult,
)
from chunker.llm.service import LLMService, LLMValidationError


def _make_ai_message(content: str, usage: dict | None = None) -> AIMessage:
    metadata = {}
    if usage:
        metadata["token_usage"] = usage
    return AIMessage(content=content, response_metadata=metadata)


def _mock_model_structured(parsed_result, raw_content: str = "{}"):
    """Create a mock BaseChatModel whose with_structured_output().invoke() returns parsed_result."""
    model = MagicMock()
    structured = MagicMock()
    structured.invoke.return_value = parsed_result
    model.with_structured_output.return_value = structured
    return model


def _mock_model_structured_raw(
    parsed_result, raw_content: str = "{}", usage: dict | None = None
):
    """Mock that returns include_raw=True format: dict with raw, parsed, parsing_error."""
    model = MagicMock()
    structured = MagicMock()
    structured.invoke.return_value = {
        "raw": _make_ai_message(raw_content, usage),
        "parsed": parsed_result,
        "parsing_error": None,
    }
    model.with_structured_output.return_value = structured
    return model


def _mock_model_failing_then_success(parsed_result, failures: int = 1):
    """Mock that raises OutputParserException `failures` times, then returns success."""
    from langchain_core.exceptions import OutputParserException

    model = MagicMock()

    call_count = 0
    structured_ok = MagicMock()
    structured_ok.invoke.return_value = {
        "raw": _make_ai_message("{}"),
        "parsed": parsed_result,
        "parsing_error": None,
    }

    structured_fail = MagicMock()
    structured_fail.invoke.side_effect = OutputParserException("Invalid JSON")

    def with_structured_output_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count <= failures:
            return structured_fail
        return structured_ok

    model.with_structured_output.side_effect = with_structured_output_side_effect
    return model


def _mock_model_always_failing():
    """Mock that always raises OutputParserException."""
    from langchain_core.exceptions import OutputParserException

    model = MagicMock()
    structured = MagicMock()
    structured.invoke.side_effect = OutputParserException("Invalid JSON")
    model.with_structured_output.return_value = structured
    return model


class TestCheckCompleteness:
    def test_returns_complete_result(self):
        expected = CompletenessResult(
            complete=True, boundary_phrase="Next section begins"
        )
        model = _mock_model_structured_raw(expected)
        svc = LLMService(model, ChunkerConfig())

        result = svc.check_completeness("some window text", "some context")

        assert result.complete is True
        assert result.boundary_phrase == "Next section begins"

    def test_returns_incomplete_result(self):
        expected = CompletenessResult(complete=False, boundary_phrase=None)
        model = _mock_model_structured_raw(expected)
        svc = LLMService(model, ChunkerConfig())

        result = svc.check_completeness("mid-thought text", "some context")

        assert result.complete is False
        assert result.boundary_phrase is None


class TestRewriteChunk:
    def test_returns_context_summary_filename(self):
        expected = RewriteResult(
            context="The transformer model uses attention.",
            summary="Explains transformer attention mechanism.",
            filename="transformer-attention-mechanism",
        )
        model = _mock_model_structured_raw(expected)
        svc = LLMService(model, ChunkerConfig())

        result = svc.rewrite_chunk("It uses attention.", "context about transformers")

        assert result.context == "The transformer model uses attention."
        assert result.summary == "Explains transformer attention mechanism."
        assert result.filename == "transformer-attention-mechanism"


class TestCheckPageCompleteness:
    def test_returns_complete_with_page_number(self):
        expected = PageCompletenessResult(complete=True, split_after_page=5)
        model = _mock_model_structured_raw(expected)
        svc = LLMService(model, ChunkerConfig())

        result = svc.check_page_completeness("=== Page 4 ===\nfoo\n=== Page 5 ===\nbar")

        assert result.complete is True
        assert result.split_after_page == 5

    def test_returns_incomplete(self):
        expected = PageCompletenessResult(complete=False, split_after_page=None)
        model = _mock_model_structured_raw(expected)
        svc = LLMService(model, ChunkerConfig())

        result = svc.check_page_completeness("=== Page 1 ===\nmid-thought")

        assert result.complete is False
        assert result.split_after_page is None

    def test_sends_no_images(self):
        """FR-04: page completeness is text-only and never attaches an image."""
        expected = PageCompletenessResult(complete=True, split_after_page=3)
        model = _mock_model_structured_raw(expected)
        svc = LLMService(model, ChunkerConfig())

        svc.check_page_completeness("=== Page 3 ===\ncontent")

        structured = model.with_structured_output.return_value
        messages = structured.invoke.call_args.args[0]
        # Text-only: the message content is a bare string, never a multimodal list.
        assert isinstance(messages[0].content, str)


class TestRewriteChunkVision:
    def test_with_image_paths_builds_multimodal_content(self, tmp_path):
        img = tmp_path / "page-0001.png"
        raw_bytes = b"\x89PNG\r\n\x1a\nFAKE-IMAGE-BYTES"
        img.write_bytes(raw_bytes)

        expected = RewriteResult(context="c", summary="s", filename="f")
        model = _mock_model_structured_raw(expected)
        svc = LLMService(model, ChunkerConfig())

        result = svc.rewrite_chunk("It uses attention.", "ctx", image_paths=[str(img)])

        assert result.context == "c"
        structured = model.with_structured_output.return_value
        messages = structured.invoke.call_args.args[0]
        content = messages[0].content
        assert isinstance(content, list)
        assert content[0]["type"] == "text"
        assert "It uses attention." in content[0]["text"]
        assert content[1]["type"] == "image_url"
        expected_b64 = base64.b64encode(raw_bytes).decode("ascii")
        assert content[1]["image_url"] == f"data:image/png;base64,{expected_b64}"

    def test_multiple_images_produce_one_part_each(self, tmp_path):
        img1 = tmp_path / "page-0001.png"
        img1.write_bytes(b"AAA")
        img2 = tmp_path / "page-0002.png"
        img2.write_bytes(b"BBB")

        expected = RewriteResult(context="c", summary="s", filename="f")
        model = _mock_model_structured_raw(expected)
        svc = LLMService(model, ChunkerConfig())

        svc.rewrite_chunk("t", "c", image_paths=[str(img1), str(img2)])

        content = model.with_structured_output.return_value.invoke.call_args.args[0][
            0
        ].content
        assert len(content) == 3  # one text part + two image parts
        assert content[1]["type"] == "image_url"
        assert content[2]["type"] == "image_url"
        assert content[1]["image_url"].startswith("data:image/png;base64,")
        assert content[2]["image_url"].startswith("data:image/png;base64,")

    def test_jpg_extension_maps_to_jpeg_mime(self, tmp_path):
        img = tmp_path / "scan.jpg"
        img.write_bytes(b"xyz")

        expected = RewriteResult(context="c", summary="s", filename="f")
        model = _mock_model_structured_raw(expected)
        svc = LLMService(model, ChunkerConfig())

        svc.rewrite_chunk("t", "c", image_paths=[str(img)])

        content = model.with_structured_output.return_value.invoke.call_args.args[0][
            0
        ].content
        assert content[1]["image_url"].startswith("data:image/jpeg;base64,")

    def test_without_images_content_is_plain_string(self):
        """FR-08: text chunks (no images) keep the byte-for-byte text path."""
        expected = RewriteResult(context="c", summary="s", filename="f")
        model = _mock_model_structured_raw(expected)
        svc = LLMService(model, ChunkerConfig())

        svc.rewrite_chunk("text", "context")

        messages = model.with_structured_output.return_value.invoke.call_args.args[0]
        assert isinstance(messages[0].content, str)

    def test_empty_image_list_is_text_only(self):
        expected = RewriteResult(context="c", summary="s", filename="f")
        model = _mock_model_structured_raw(expected)
        svc = LLMService(model, ChunkerConfig())

        svc.rewrite_chunk("text", "context", image_paths=[])

        messages = model.with_structured_output.return_value.invoke.call_args.args[0]
        assert isinstance(messages[0].content, str)


class TestGroupSummaries:
    def test_returns_groups(self):
        expected = GroupingResult(groups=[[0, 1, 2], [3, 4]])
        model = _mock_model_structured_raw(expected)
        svc = LLMService(model, ChunkerConfig())

        summaries = [
            {"id": "s0", "summary": "a"},
            {"id": "s1", "summary": "b"},
            {"id": "s2", "summary": "c"},
            {"id": "s3", "summary": "d"},
            {"id": "s4", "summary": "e"},
        ]
        result = svc.group_summaries(summaries, min_size=2, max_size=5)

        assert result.groups == [[0, 1, 2], [3, 4]]


class TestSynthesizeBlock:
    def test_returns_block_context_result(self):
        expected = BlockContextResult(
            context="Comprehensive synthesis of child contexts covering topics A, B, and C.",
            summary="Covers topics A, B, and C in detail.",
            filename="topics-a-b-c-overview",
        )
        model = _mock_model_structured_raw(expected)
        svc = LLMService(model, ChunkerConfig())

        result = svc.synthesize_block(
            children_contexts=["context about A", "context about B", "context about C"],
            metadata_text="parent block context",
            min_tokens=2000,
            max_tokens=4000,
        )

        assert isinstance(result, BlockContextResult)
        assert (
            result.context
            == "Comprehensive synthesis of child contexts covering topics A, B, and C."
        )
        assert result.summary == "Covers topics A, B, and C in detail."
        assert result.filename == "topics-a-b-c-overview"


class TestRetryLogic:
    @patch("chunker.llm.service.time.sleep")
    def test_retries_on_invalid_response(self, mock_sleep):
        expected = CompletenessResult(complete=True, boundary_phrase="Next")
        model = _mock_model_failing_then_success(expected, failures=1)
        svc = LLMService(model, ChunkerConfig())

        result = svc.check_completeness("text", "context")

        assert result.complete is True
        assert model.with_structured_output.call_count == 2
        mock_sleep.assert_called_once()

    @patch("chunker.llm.service.time.sleep")
    def test_retries_up_to_three_times(self, mock_sleep):
        expected = CompletenessResult(complete=True, boundary_phrase="Next")
        model = _mock_model_failing_then_success(expected, failures=2)
        svc = LLMService(model, ChunkerConfig())

        result = svc.check_completeness("text", "context")

        assert result.complete is True
        assert model.with_structured_output.call_count == 3

    @patch("chunker.llm.service.time.sleep")
    def test_raises_after_max_retries(self, mock_sleep):
        model = _mock_model_always_failing()
        svc = LLMService(model, ChunkerConfig())

        with pytest.raises(LLMValidationError):
            svc.check_completeness("text", "context")

        assert model.with_structured_output.call_count == 3


class TestStructuredLogging:
    def test_logs_successful_call(self, caplog):
        expected = CompletenessResult(complete=True, boundary_phrase="Next")
        usage = {"prompt_tokens": 100, "completion_tokens": 20}
        model = _mock_model_structured_raw(
            expected, raw_content='{"complete": true}', usage=usage
        )
        svc = LLMService(model, ChunkerConfig())

        with caplog.at_level(logging.INFO, logger="chunker.llm.service"):
            svc.check_completeness("text", "context", chunk_id="chunk-001")

        assert len(caplog.records) >= 1
        record = caplog.records[-1]
        log_data = json.loads(record.message)
        assert log_data["event"] == "check_completeness"
        assert log_data["entity_id"] == "chunk-001"
        assert "token_usage" in log_data

    @patch("chunker.llm.service.time.sleep")
    def test_logs_retry_warning(self, mock_sleep, caplog):
        expected = CompletenessResult(complete=True, boundary_phrase="Next")
        model = _mock_model_failing_then_success(expected, failures=1)
        svc = LLMService(model, ChunkerConfig())

        with caplog.at_level(logging.WARNING, logger="chunker.llm.service"):
            svc.check_completeness("text", "context")

        warning_records = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert len(warning_records) >= 1
