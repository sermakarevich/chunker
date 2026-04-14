from __future__ import annotations

from unittest.mock import MagicMock, patch

from chunker.cli import build_parser, run_command, resume_command
from chunker.config import ChunkerConfig
from chunker.models import Chunk, SummaryBlock
from chunker.pipeline import Pipeline, ProcessingResult
from chunker.state import PipelineState


def _config(**overrides) -> ChunkerConfig:
    defaults = dict(model="qwen3:32b", checkpoint_path="checkpoint.json")
    defaults.update(overrides)
    return ChunkerConfig(**defaults)


def _chunk(chunk_id: str, span: tuple[int, int] = (0, 10)) -> Chunk:
    return Chunk(
        id=chunk_id,
        source_span=span,
        original_text="Original text.",
        rewritten_text="Rewritten text.",
        summary="Summary.",
        parent_block_id=None,
        forced_split=False,
        metadata={},
    )


class TestProcessingResult:
    def test_from_state_counts_chunks(self):
        state = PipelineState.create("doc-1", "some text")
        state.chunks["chunk-001"] = _chunk("chunk-001")
        state.chunks["chunk-002"] = _chunk("chunk-002")

        result = ProcessingResult.from_state(state)

        assert result.total_chunks == 2

    def test_from_state_counts_blocks(self):
        state = PipelineState.create("doc-1", "some text")
        state.blocks["block-L1-001"] = SummaryBlock(
            id="block-L1-001",
            level=1,
            summary="Summary",
            child_ids=["chunk-001"],
            parent_block_id=None,
            metadata={},
        )

        result = ProcessingResult.from_state(state)

        assert result.total_blocks == 1

    def test_from_state_finds_root_blocks(self):
        state = PipelineState.create("doc-1", "some text")
        state.blocks["block-L1-001"] = SummaryBlock(
            id="block-L1-001",
            level=1,
            summary="S1",
            child_ids=["chunk-001"],
            parent_block_id="block-L2-001",
            metadata={},
        )
        state.blocks["block-L2-001"] = SummaryBlock(
            id="block-L2-001",
            level=2,
            summary="S2",
            child_ids=["block-L1-001"],
            parent_block_id=None,
            metadata={},
        )

        result = ProcessingResult.from_state(state)

        assert result.root_block_ids == ["block-L2-001"]

    def test_from_state_empty(self):
        state = PipelineState.create("doc-1", "some text")

        result = ProcessingResult.from_state(state)

        assert result.total_chunks == 0
        assert result.total_blocks == 0
        assert result.root_block_ids == []


class TestPipelineInit:
    @patch("chunker.pipeline.ChatOllama")
    def test_init_creates_all_components(self, mock_ollama_cls):
        config = _config()
        pipeline = Pipeline(config)

        mock_ollama_cls.assert_called_once_with(
            model=config.model, base_url=config.ollama_base_url
        )
        assert pipeline._extractor is not None
        assert pipeline._rewriter is not None
        assert pipeline._sweeper is not None
        assert pipeline._checkpointer is not None


class TestPipelineRun:
    def _make_pipeline_with_mocks(
        self, config: ChunkerConfig | None = None
    ) -> tuple[Pipeline, MagicMock, MagicMock, MagicMock, MagicMock]:
        config = config or _config()
        with patch("chunker.pipeline.ChatOllama"):
            pipeline = Pipeline(config)

        extractor = MagicMock()
        rewriter = MagicMock()
        sweeper = MagicMock()
        checkpointer = MagicMock()

        pipeline._extractor = extractor
        pipeline._rewriter = rewriter
        pipeline._sweeper = sweeper
        pipeline._checkpointer = checkpointer

        return pipeline, extractor, rewriter, sweeper, checkpointer

    def test_run_processes_all_text(self):
        pipeline, extractor, rewriter, sweeper, checkpointer = (
            self._make_pipeline_with_mocks()
        )
        text = "Hello world. This is a test."
        chunk1 = _chunk("chunk-001", (0, 12))
        chunk2 = _chunk("chunk-002", (12, 28))

        call_count = 0

        def extract_side_effect(state):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                state.cursor_position = 12
                state.chunk_counter = 1
                return chunk1
            else:
                state.cursor_position = len(text)
                state.chunk_counter = 2
                return chunk2

        extractor.extract_next.side_effect = extract_side_effect
        rewriter.rewrite.side_effect = lambda chunk, state: chunk

        result = pipeline.run(text, "doc-1")

        assert extractor.extract_next.call_count == 2
        assert rewriter.rewrite.call_count == 2
        assert sweeper.sweep.call_count == 2
        assert checkpointer.save.call_count == 2
        assert result.total_chunks == 2

    def test_run_adds_chunk_to_state_and_pending(self):
        pipeline, extractor, rewriter, sweeper, checkpointer = (
            self._make_pipeline_with_mocks()
        )
        text = "Hello."
        chunk = _chunk("chunk-001", (0, 6))

        def extract_side_effect(state):
            state.cursor_position = len(text)
            state.chunk_counter = 1
            return chunk

        extractor.extract_next.side_effect = extract_side_effect
        rewriter.rewrite.side_effect = lambda c, s: c

        saved_states = []
        checkpointer.save.side_effect = lambda s: saved_states.append(
            (dict(s.chunks), dict(s.pending_summaries))
        )

        pipeline.run(text, "doc-1")

        chunks_snapshot, pending_snapshot = saved_states[0]
        assert "chunk-001" in chunks_snapshot
        assert pending_snapshot[0] == ["chunk-001"]

    def test_run_calls_sweep_after_adding_chunk(self):
        pipeline, extractor, rewriter, sweeper, checkpointer = (
            self._make_pipeline_with_mocks()
        )
        text = "Hello."
        chunk = _chunk("chunk-001", (0, 6))

        def extract_side_effect(state):
            state.cursor_position = len(text)
            state.chunk_counter = 1
            return chunk

        extractor.extract_next.side_effect = extract_side_effect
        rewriter.rewrite.side_effect = lambda c, s: c

        call_order = []
        rewriter.rewrite.side_effect = lambda c, s: (
            call_order.append("rewrite"),
            c,
        )[1]
        sweeper.sweep.side_effect = lambda s: call_order.append("sweep")
        checkpointer.save.side_effect = lambda s: call_order.append("save")

        pipeline.run(text, "doc-1")

        assert call_order == ["rewrite", "sweep", "save"]

    def test_run_returns_processing_result(self):
        pipeline, extractor, rewriter, sweeper, checkpointer = (
            self._make_pipeline_with_mocks()
        )
        text = "Hello."
        chunk = _chunk("chunk-001", (0, 6))

        def extract_side_effect(state):
            state.cursor_position = len(text)
            state.chunk_counter = 1
            return chunk

        extractor.extract_next.side_effect = extract_side_effect
        rewriter.rewrite.side_effect = lambda c, s: c

        result = pipeline.run(text, "doc-1")

        assert isinstance(result, ProcessingResult)
        assert result.state.document_id == "doc-1"
        assert result.total_chunks == 1


class TestPipelineResume:
    def test_resume_loads_checkpoint_and_continues(self):
        config = _config()
        with patch("chunker.pipeline.ChatOllama"):
            pipeline = Pipeline(config)

        extractor = MagicMock()
        rewriter = MagicMock()
        sweeper = MagicMock()
        checkpointer = MagicMock()

        pipeline._extractor = extractor
        pipeline._rewriter = rewriter
        pipeline._sweeper = sweeper
        pipeline._checkpointer = checkpointer

        # Simulate resumed state: 12 chars already processed, 16 remaining
        restored_state = PipelineState.create("doc-1", "Hello world. More text here.")
        restored_state.cursor_position = 13
        restored_state.chunk_counter = 1
        restored_state.chunks["chunk-001"] = _chunk("chunk-001", (0, 13))
        restored_state.pending_summaries[0] = ["chunk-001"]

        checkpointer.load.return_value = restored_state

        chunk2 = _chunk("chunk-002", (13, 27))

        def extract_side_effect(state):
            state.cursor_position = len(state.source_text)
            state.chunk_counter = 2
            return chunk2

        extractor.extract_next.side_effect = extract_side_effect
        rewriter.rewrite.side_effect = lambda c, s: c

        result = pipeline.resume()

        checkpointer.load.assert_called_once()
        assert extractor.extract_next.call_count == 1
        assert result.total_chunks == 2

    def test_resume_with_fully_processed_checkpoint(self):
        config = _config()
        with patch("chunker.pipeline.ChatOllama"):
            pipeline = Pipeline(config)

        checkpointer = MagicMock()
        pipeline._checkpointer = checkpointer

        restored_state = PipelineState.create("doc-1", "Hello.")
        restored_state.cursor_position = 6
        restored_state.chunk_counter = 1
        restored_state.chunks["chunk-001"] = _chunk("chunk-001", (0, 6))

        checkpointer.load.return_value = restored_state

        result = pipeline.resume()

        assert result.total_chunks == 1


class TestBuildParser:
    def test_run_subcommand(self):
        parser = build_parser()
        args = parser.parse_args(["run", "input.txt"])
        assert args.command == "run"
        assert args.input_file == "input.txt"

    def test_run_with_model(self):
        parser = build_parser()
        args = parser.parse_args(["run", "input.txt", "--model", "gemma4:12b"])
        assert args.model == "gemma4:12b"

    def test_run_with_output_dir(self):
        parser = build_parser()
        args = parser.parse_args(["run", "input.txt", "--output-dir", "/tmp/out"])
        assert args.output_dir == "/tmp/out"

    def test_resume_subcommand(self):
        parser = build_parser()
        args = parser.parse_args(["resume", "checkpoint.json"])
        assert args.command == "resume"
        assert args.checkpoint_file == "checkpoint.json"

    def test_resume_with_output_dir(self):
        parser = build_parser()
        args = parser.parse_args(
            ["resume", "checkpoint.json", "--output-dir", "/tmp/out"]
        )
        assert args.output_dir == "/tmp/out"


class TestRunCommand:
    @patch("chunker.cli.Pipeline")
    def test_run_creates_pipeline_and_calls_run(self, mock_pipeline_cls, tmp_path):
        input_file = tmp_path / "doc.txt"
        input_file.write_text("Hello world.")

        mock_pipeline = MagicMock()
        mock_result = MagicMock()
        mock_result.total_chunks = 1
        mock_result.total_blocks = 0
        mock_result.root_block_ids = []
        mock_pipeline.run.return_value = mock_result
        mock_pipeline_cls.return_value = mock_pipeline

        parser = build_parser()
        args = parser.parse_args(["run", str(input_file)])

        run_command(args)

        mock_pipeline_cls.assert_called_once()
        config = mock_pipeline_cls.call_args[0][0]
        assert isinstance(config, ChunkerConfig)
        mock_pipeline.run.assert_called_once_with("Hello world.", input_file.stem)

    @patch("chunker.cli.Pipeline")
    def test_run_applies_model_profile(self, mock_pipeline_cls, tmp_path):
        input_file = tmp_path / "doc.txt"
        input_file.write_text("text")

        mock_pipeline = MagicMock()
        mock_result = MagicMock()
        mock_result.total_chunks = 0
        mock_result.total_blocks = 0
        mock_result.root_block_ids = []
        mock_pipeline.run.return_value = mock_result
        mock_pipeline_cls.return_value = mock_pipeline

        parser = build_parser()
        args = parser.parse_args(
            ["run", str(input_file), "--model", "gemma4:12b"]
        )

        run_command(args)

        config = mock_pipeline_cls.call_args[0][0]
        assert config.model == "gemma4:12b"
        assert config.max_chunk_tokens == 400  # gemma4:12b profile value


class TestResumeCommand:
    @patch("chunker.cli.Pipeline")
    def test_resume_creates_pipeline_and_calls_resume(self, mock_pipeline_cls, tmp_path):
        checkpoint_file = tmp_path / "checkpoint.json"
        checkpoint_file.write_text("{}")

        mock_pipeline = MagicMock()
        mock_result = MagicMock()
        mock_result.total_chunks = 1
        mock_result.total_blocks = 0
        mock_result.root_block_ids = []
        mock_pipeline.resume.return_value = mock_result
        mock_pipeline_cls.return_value = mock_pipeline

        parser = build_parser()
        args = parser.parse_args(["resume", str(checkpoint_file)])

        resume_command(args)

        mock_pipeline_cls.assert_called_once()
        config = mock_pipeline_cls.call_args[0][0]
        assert config.checkpoint_path == str(checkpoint_file)
        mock_pipeline.resume.assert_called_once()
