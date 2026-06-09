from __future__ import annotations

from unittest.mock import MagicMock, patch

from chunker.cli import build_parser, run_command, resume_command
from chunker.config import ChunkerConfig
from chunker.loaders import LoadedDocument
from chunker.models import Chunk, Page, SummaryBlock
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
        context="Rewritten text.",
        summary="Summary.",
        filename="",
        parent_block_id=None,
        forced_split=False,
        metadata={},
    )


def _page(number: int) -> Page:
    return Page(
        number=number, text=f"page {number} text", image_path=f"/img/page-{number}.png"
    )


def _pdf_chunk(chunk_id: str, page_span: tuple[int, int]) -> Chunk:
    return Chunk(
        id=chunk_id,
        source_span=(0, 0),
        original_text="Page text.",
        context="Rewritten.",
        summary="Summary.",
        filename="",
        parent_block_id=None,
        forced_split=False,
        metadata={},
        page_span=page_span,
        image_paths=[f"/img/page-{page_span[0]}.png"],
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
            context="",
            summary="Summary",
            filename="",
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
            context="",
            summary="S1",
            filename="",
            child_ids=["chunk-001"],
            parent_block_id="block-L2-001",
            metadata={},
        )
        state.blocks["block-L2-001"] = SummaryBlock(
            id="block-L2-001",
            level=2,
            context="",
            summary="S2",
            filename="",
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
        assert pipeline._page_extractor is not None
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

    def test_run_processes_all_text(self, tmp_path):
        pipeline, extractor, rewriter, sweeper, checkpointer = (
            self._make_pipeline_with_mocks(_config(output_dir=str(tmp_path)))
        )
        checkpointer.exists.return_value = False
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

    def test_run_adds_chunk_to_state_and_pending(self, tmp_path):
        pipeline, extractor, rewriter, sweeper, checkpointer = (
            self._make_pipeline_with_mocks(_config(output_dir=str(tmp_path)))
        )
        checkpointer.exists.return_value = False
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

    def test_run_calls_sweep_after_adding_chunk(self, tmp_path):
        pipeline, extractor, rewriter, sweeper, checkpointer = (
            self._make_pipeline_with_mocks(_config(output_dir=str(tmp_path)))
        )
        checkpointer.exists.return_value = False
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

    def test_run_returns_processing_result(self, tmp_path):
        pipeline, extractor, rewriter, sweeper, checkpointer = (
            self._make_pipeline_with_mocks(_config(output_dir=str(tmp_path)))
        )
        checkpointer.exists.return_value = False
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

    def test_run_resumes_from_checkpoint_when_exists(self, tmp_path):
        pipeline, extractor, rewriter, sweeper, checkpointer = (
            self._make_pipeline_with_mocks(_config(output_dir=str(tmp_path)))
        )
        text = "Hello world. More text here."
        checkpointer.exists.return_value = True

        restored_state = PipelineState.create("doc-1", text)
        restored_state.cursor_position = 13
        restored_state.chunk_counter = 1
        restored_state.chunks["chunk-001"] = _chunk("chunk-001", (0, 13))
        restored_state.pending_summaries[0] = ["chunk-001"]
        checkpointer.load.return_value = restored_state

        chunk2 = _chunk("chunk-002", (13, 27))

        def extract_side_effect(state):
            state.cursor_position = len(text)
            state.chunk_counter = 2
            return chunk2

        extractor.extract_next.side_effect = extract_side_effect
        rewriter.rewrite.side_effect = lambda c, s: c

        result = pipeline.run(text, "doc-1")

        checkpointer.load.assert_called_once_with(expected_document_id="doc-1")
        assert extractor.extract_next.call_count == 1
        assert result.total_chunks == 2


class TestPipelineResume:
    def test_resume_loads_checkpoint_and_continues(self, tmp_path):
        config = _config(output_dir=str(tmp_path))
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

    def test_resume_with_fully_processed_checkpoint(self, tmp_path):
        config = _config(output_dir=str(tmp_path))
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
        args = parser.parse_args(["run", "input.txt", "--model", "gemma4:26b"])
        assert args.model == "gemma4:26b"

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

    def test_run_with_pdf_dpi(self):
        parser = build_parser()
        args = parser.parse_args(["run", "input.pdf", "--pdf-dpi", "200"])
        assert args.pdf_dpi == 200

    def test_run_with_vision_model(self):
        parser = build_parser()
        args = parser.parse_args(
            ["run", "input.pdf", "--vision-model", "gemma4:latest"]
        )
        assert args.vision_model == "gemma4:latest"

    def test_run_pdf_flags_default_to_none(self):
        parser = build_parser()
        args = parser.parse_args(["run", "input.txt"])
        assert args.pdf_dpi is None
        assert args.vision_model is None

    def test_resume_with_model_and_vision_model(self):
        parser = build_parser()
        args = parser.parse_args(
            [
                "resume",
                "checkpoint.json",
                "--model",
                "qwen3:32b",
                "--vision-model",
                "gemma4:latest",
            ]
        )
        assert args.model == "qwen3:32b"
        assert args.vision_model == "gemma4:latest"


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
        mock_pipeline.run_document.return_value = mock_result
        mock_pipeline_cls.return_value = mock_pipeline

        parser = build_parser()
        args = parser.parse_args(["run", str(input_file)])

        run_command(args)

        mock_pipeline_cls.assert_called_once()
        config = mock_pipeline_cls.call_args[0][0]
        assert isinstance(config, ChunkerConfig)
        mock_pipeline.run_document.assert_called_once()
        document = mock_pipeline.run_document.call_args.args[0]
        assert document.source_text == "Hello world."
        assert document.pages is None
        assert document.document_id == input_file.stem

    @patch("chunker.cli.Pipeline")
    def test_run_applies_model_profile(self, mock_pipeline_cls, tmp_path):
        input_file = tmp_path / "doc.txt"
        input_file.write_text("text")

        mock_pipeline = MagicMock()
        mock_result = MagicMock()
        mock_result.total_chunks = 0
        mock_result.total_blocks = 0
        mock_result.root_block_ids = []
        mock_pipeline.run_document.return_value = mock_result
        mock_pipeline_cls.return_value = mock_pipeline

        parser = build_parser()
        args = parser.parse_args(["run", str(input_file), "--model", "gemma4:26b"])

        run_command(args)

        config = mock_pipeline_cls.call_args[0][0]
        assert config.model == "gemma4:26b"
        assert config.max_chunk_tokens == 4000  # gemma4:26b profile value

    @patch("chunker.cli.Pipeline")
    def test_run_places_checkpoint_in_output_dir(self, mock_pipeline_cls, tmp_path):
        input_file = tmp_path / "doc.txt"
        input_file.write_text("text")
        output_dir = tmp_path / "my_output"

        mock_pipeline = MagicMock()
        mock_result = MagicMock()
        mock_result.total_chunks = 0
        mock_result.total_blocks = 0
        mock_result.root_block_ids = []
        mock_pipeline.run_document.return_value = mock_result
        mock_pipeline_cls.return_value = mock_pipeline

        parser = build_parser()
        args = parser.parse_args(
            ["run", str(input_file), "--output-dir", str(output_dir)]
        )

        run_command(args)

        config = mock_pipeline_cls.call_args[0][0]
        assert config.checkpoint_path == str(output_dir / "checkpoint.json")

    @patch("chunker.cli.Pipeline")
    def test_run_routes_pdf_and_resolves_vision_model(
        self, mock_pipeline_cls, tmp_path
    ):
        import pymupdf

        pdf = tmp_path / "doc.pdf"
        doc = pymupdf.open()
        doc.new_page().insert_text((72, 100), "Page one text.")
        doc.save(str(pdf))
        doc.close()

        mock_pipeline = MagicMock()
        mock_result = MagicMock()
        mock_result.total_chunks = 1
        mock_result.total_blocks = 0
        mock_result.root_block_ids = []
        mock_pipeline.run_document.return_value = mock_result
        mock_pipeline_cls.return_value = mock_pipeline

        parser = build_parser()
        args = parser.parse_args(
            [
                "run",
                str(pdf),
                "--output-dir",
                str(tmp_path / "out"),
                "--pdf-dpi",
                "72",
                "--vision-model",
                "gemma4:latest",
            ]
        )

        run_command(args)

        config = mock_pipeline_cls.call_args[0][0]
        assert config.pdf_dpi == 72
        assert config.vision_model == "gemma4:latest"
        # PDF + vision model => effective model promoted before Pipeline build.
        assert config.model == "gemma4:latest"
        document = mock_pipeline.run_document.call_args.args[0]
        assert document.pages is not None
        assert document.source_text is None


class TestPipelineOutput:
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

    def _setup_single_chunk(self, extractor, rewriter, text):
        chunk = _chunk("chunk-001", (0, len(text)))

        def extract_side_effect(state):
            state.cursor_position = len(text)
            state.chunk_counter = 1
            return chunk

        extractor.extract_next.side_effect = extract_side_effect
        rewriter.rewrite.side_effect = lambda c, s: c

    def test_run_creates_json_output(self, tmp_path):
        config = _config(output_dir=str(tmp_path))
        pipeline, extractor, rewriter, sweeper, checkpointer = (
            self._make_pipeline_with_mocks(config)
        )
        checkpointer.exists.return_value = False
        text = "Hello world."
        self._setup_single_chunk(extractor, rewriter, text)

        pipeline.run(text, "doc-1")

        assert (tmp_path / "hierarchy.json").exists()

    def test_run_creates_markdown_index(self, tmp_path):
        config = _config(output_dir=str(tmp_path))
        pipeline, extractor, rewriter, sweeper, checkpointer = (
            self._make_pipeline_with_mocks(config)
        )
        checkpointer.exists.return_value = False
        text = "Hello world."
        self._setup_single_chunk(extractor, rewriter, text)

        pipeline.run(text, "doc-1")

        assert (tmp_path / "index.md").exists()

    def test_run_creates_chunk_files(self, tmp_path):
        config = _config(output_dir=str(tmp_path))
        pipeline, extractor, rewriter, sweeper, checkpointer = (
            self._make_pipeline_with_mocks(config)
        )
        checkpointer.exists.return_value = False
        text = "Hello world."
        self._setup_single_chunk(extractor, rewriter, text)

        pipeline.run(text, "doc-1")

        assert (tmp_path / "content" / "L0").is_dir()
        chunk_files = list((tmp_path / "content" / "L0").iterdir())
        assert len(chunk_files) == 1

    def test_resume_creates_output(self, tmp_path):
        config = _config(output_dir=str(tmp_path))
        pipeline, extractor, rewriter, sweeper, checkpointer = (
            self._make_pipeline_with_mocks(config)
        )

        restored_state = PipelineState.create("doc-1", "Hello.")
        restored_state.cursor_position = 6
        restored_state.chunk_counter = 1
        restored_state.chunks["chunk-001"] = _chunk("chunk-001", (0, 6))

        checkpointer.load.return_value = restored_state

        pipeline.resume()

        assert (tmp_path / "hierarchy.json").exists()
        assert (tmp_path / "index.md").exists()


class TestResumeCommand:
    @patch("chunker.cli.Pipeline")
    def test_resume_creates_pipeline_and_calls_resume(
        self, mock_pipeline_cls, tmp_path
    ):
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

    @patch("chunker.cli.Pipeline")
    def test_resume_promotes_vision_model(self, mock_pipeline_cls, tmp_path):
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
        args = parser.parse_args(
            ["resume", str(checkpoint_file), "--vision-model", "gemma4:latest"]
        )

        resume_command(args)

        config = mock_pipeline_cls.call_args[0][0]
        assert config.vision_model == "gemma4:latest"
        # A PDF resume needs the vision model promoted to the effective model.
        assert config.model == "gemma4:latest"


class TestPipelinePdfMode:
    def _pipeline_with_mocks(self, config: ChunkerConfig) -> Pipeline:
        with patch("chunker.pipeline.ChatOllama"):
            pipeline = Pipeline(config)
        pipeline._extractor = MagicMock()
        pipeline._page_extractor = MagicMock()
        pipeline._rewriter = MagicMock()
        pipeline._sweeper = MagicMock()
        pipeline._checkpointer = MagicMock()
        return pipeline

    def test_process_uses_page_extractor_in_pdf_mode(self, tmp_path):
        config = _config(output_dir=str(tmp_path))
        pipeline = self._pipeline_with_mocks(config)
        pipeline._checkpointer.exists.return_value = False
        pages = [_page(1), _page(2)]

        def page_extract_side_effect(state):
            state.chunk_counter += 1
            n = state.chunk_counter
            state.cursor_page = n
            return _pdf_chunk(f"chunk-{n:03d}", (n, n))

        pipeline._page_extractor.extract_next.side_effect = page_extract_side_effect
        pipeline._rewriter.rewrite.side_effect = lambda c, s: c

        document = LoadedDocument(document_id="doc-pdf", source_text=None, pages=pages)
        result = pipeline.run_document(document)

        assert pipeline._page_extractor.extract_next.call_count == 2
        assert pipeline._extractor.extract_next.call_count == 0
        assert result.total_chunks == 2

    def test_run_document_resumes_existing_checkpoint(self, tmp_path):
        config = _config(output_dir=str(tmp_path))
        pipeline = self._pipeline_with_mocks(config)
        pages = [_page(1), _page(2)]
        pipeline._checkpointer.exists.return_value = True

        restored = PipelineState.create_from_pages("doc-pdf", pages)
        restored.cursor_page = 1
        restored.chunk_counter = 1
        restored.chunks["chunk-001"] = _pdf_chunk("chunk-001", (1, 1))
        pipeline._checkpointer.load.return_value = restored

        def page_extract_side_effect(state):
            state.chunk_counter += 1
            state.cursor_page = 2
            return _pdf_chunk("chunk-002", (2, 2))

        pipeline._page_extractor.extract_next.side_effect = page_extract_side_effect
        pipeline._rewriter.rewrite.side_effect = lambda c, s: c

        document = LoadedDocument(document_id="doc-pdf", source_text=None, pages=pages)
        result = pipeline.run_document(document)

        pipeline._checkpointer.load.assert_called_once_with(
            expected_document_id="doc-pdf"
        )
        assert pipeline._page_extractor.extract_next.call_count == 1
        assert result.total_chunks == 2

    def test_progress_pct_is_mode_aware_and_zero_guarded(self, tmp_path):
        config = _config(output_dir=str(tmp_path))
        pipeline = self._pipeline_with_mocks(config)

        text_state = PipelineState.create("d", "abcdefghij")  # len 10
        text_state.cursor_position = 5
        assert pipeline._progress_pct(text_state) == 50.0

        empty_text = PipelineState.create("d", "")
        assert pipeline._progress_pct(empty_text) == 100.0

        pdf_state = PipelineState.create_from_pages(
            "d", [_page(1), _page(2), _page(3), _page(4)]
        )
        pdf_state.cursor_page = 1
        assert pipeline._progress_pct(pdf_state) == 25.0
