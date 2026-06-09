"""End-to-end pipeline test with mock LLM.

Uses real components (ChunkExtractor, ChunkRewriter, AggregationSweeper,
Checkpointer, ContextBuilder) but mocks LLMService responses to avoid
needing a running Ollama instance.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pymupdf
import pytest

from chunker.checkpoint import Checkpointer
from chunker.config import ChunkerConfig
from chunker.context import ContextBuilder
from chunker.llm.schemas import (
    BlockContextResult,
    CompletenessResult,
    GroupingResult,
    PageCompletenessResult,
    RewriteResult,
)
from chunker.llm.service import LLMService
from chunker.loaders import load_document
from chunker.models import Chunk
from chunker.nodes.aggregation import AggregationSweeper
from chunker.nodes.chunking import ChunkExtractor
from chunker.nodes.page_chunking import PageChunkExtractor
from chunker.nodes.rewriting import ChunkRewriter
from chunker.pipeline import Pipeline
from chunker.state import PipelineState


def _make_pdf(path: Path, texts: list[str]) -> None:
    """Build a small multi-page PDF, one text block per page."""
    doc = pymupdf.open()
    for text in texts:
        page = doc.new_page()
        page.insert_text((72, 100), text)
    doc.save(str(path))
    doc.close()


DOCUMENT = (
    "Machine learning models require large datasets for training. "
    "Data preprocessing is essential to ensure quality. "
    "Feature engineering transforms raw data into useful signals. "
    "Model evaluation uses metrics like accuracy and F1 score. "
    "Hyperparameter tuning optimizes model performance. "
    "Deployment requires monitoring for data drift."
)


def _config(checkpoint_path: str, **overrides) -> ChunkerConfig:
    defaults = dict(
        min_chunk_tokens=3,
        max_chunk_tokens=500,
        max_expansion_attempts=5,
        summary_aggregation_threshold=50,
        summary_count_threshold=3,
        min_group_size=2,
        max_group_size=4,
        model="qwen3:32b",
        checkpoint_path=checkpoint_path,
    )
    defaults.update(overrides)
    return ChunkerConfig(**defaults)


def _build_pipeline_with_mock_llm(
    config: ChunkerConfig,
) -> tuple[Pipeline, MagicMock]:
    """Create a Pipeline with real components but a mock LLMService."""
    mock_llm = MagicMock(spec=LLMService)

    with patch("chunker.pipeline.ChatOllama"):
        pipeline = Pipeline(config)

    # Replace LLMService in each component with the shared mock
    pipeline._extractor = ChunkExtractor(mock_llm, config)
    pipeline._page_extractor = PageChunkExtractor(mock_llm, config)
    context_builder = ContextBuilder(config)
    pipeline._rewriter = ChunkRewriter(mock_llm, context_builder)
    pipeline._sweeper = AggregationSweeper(mock_llm, config)

    return pipeline, mock_llm


class TestPipelineEndToEnd:
    @pytest.fixture()
    def checkpoint_path(self, tmp_path: Path) -> str:
        return str(tmp_path / "checkpoint.json")

    def _setup_llm_mock(self, mock_llm: MagicMock) -> None:
        """Configure mock to produce 4 chunks then trigger aggregation.

        Document has 6 sentences. With min_chunk_tokens=3 the CursorWindow
        grabs one sentence per initial expansion, then completeness checks
        determine boundaries. Two boundary phrases split after sentences 2
        and 4, producing 4 chunks total.
        """
        boundaries = [
            "Feature engineering transforms",
            "Hyperparameter tuning optimizes",
        ]
        completeness_idx = {"count": 0}

        def completeness_side_effect(window_text, context_text, *, chunk_id=None):
            idx = completeness_idx["count"]
            completeness_idx["count"] += 1
            phrase = boundaries[idx] if idx < len(boundaries) else None
            return CompletenessResult(complete=True, boundary_phrase=phrase)

        mock_llm.check_completeness.side_effect = completeness_side_effect

        chunk_counter = {"n": 0}

        def rewrite_side_effect(
            chunk_text, context_text, *, image_paths=None, chunk_id=None
        ):
            chunk_counter["n"] += 1
            return RewriteResult(
                context=f"[Rewritten {chunk_counter['n']}] {chunk_text.strip()}",
                summary=f"Summary of section {chunk_counter['n']}.",
                filename=f"section-{chunk_counter['n']}",
            )

        mock_llm.rewrite_chunk.side_effect = rewrite_side_effect

        mock_llm.group_summaries.return_value = GroupingResult(groups=[[0, 1], [2, 3]])

        mock_llm.synthesize_block.return_value = BlockContextResult(
            context="Overview of ML pipeline: data, features, evaluation, tuning, deployment.",
            summary="ML pipeline overview covering data, features, evaluation, tuning, and deployment.",
            filename="ml-pipeline-overview",
        )

    def test_full_pipeline_produces_chunks_and_blocks(self, checkpoint_path):
        config = _config(checkpoint_path)
        pipeline, mock_llm = _build_pipeline_with_mock_llm(config)
        self._setup_llm_mock(mock_llm)

        result = pipeline.run(DOCUMENT, "ml-doc")

        assert result.total_chunks == 4
        assert result.total_blocks >= 1

    def test_chunks_cover_full_document(self, checkpoint_path):
        config = _config(checkpoint_path)
        pipeline, mock_llm = _build_pipeline_with_mock_llm(config)
        self._setup_llm_mock(mock_llm)

        result = pipeline.run(DOCUMENT, "ml-doc")

        state = result.state
        spans = sorted(
            (c.source_span for c in state.chunks.values()), key=lambda s: s[0]
        )
        assert spans[0][0] == 0
        assert spans[-1][1] == len(DOCUMENT)
        for i in range(1, len(spans)):
            assert spans[i][0] == spans[i - 1][1]

    def test_chunks_have_context_and_summaries(self, checkpoint_path):
        config = _config(checkpoint_path)
        pipeline, mock_llm = _build_pipeline_with_mock_llm(config)
        self._setup_llm_mock(mock_llm)

        result = pipeline.run(DOCUMENT, "ml-doc")

        for chunk in result.state.chunks.values():
            assert chunk.context.startswith("[Rewritten")
            assert chunk.summary.startswith("Summary of section")

    def test_blocks_have_parent_child_links(self, checkpoint_path):
        config = _config(checkpoint_path)
        pipeline, mock_llm = _build_pipeline_with_mock_llm(config)
        self._setup_llm_mock(mock_llm)

        result = pipeline.run(DOCUMENT, "ml-doc")
        state = result.state

        for block in state.blocks.values():
            for child_id in block.child_ids:
                if child_id in state.chunks:
                    assert state.chunks[child_id].parent_block_id == block.id
                elif child_id in state.blocks:
                    assert state.blocks[child_id].parent_block_id == block.id

    def test_root_block_ids_have_no_parent(self, checkpoint_path):
        config = _config(checkpoint_path)
        pipeline, mock_llm = _build_pipeline_with_mock_llm(config)
        self._setup_llm_mock(mock_llm)

        result = pipeline.run(DOCUMENT, "ml-doc")

        for root_id in result.root_block_ids:
            assert result.state.blocks[root_id].parent_block_id is None

    def test_checkpoint_saved_after_run(self, checkpoint_path):
        config = _config(checkpoint_path)
        pipeline, mock_llm = _build_pipeline_with_mock_llm(config)
        self._setup_llm_mock(mock_llm)

        pipeline.run(DOCUMENT, "ml-doc")

        assert Path(checkpoint_path).exists()


class TestPipelineOutput:
    @pytest.fixture()
    def checkpoint_path(self, tmp_path: Path) -> str:
        return str(tmp_path / "checkpoint.json")

    def _setup_llm_mock(self, mock_llm: MagicMock) -> None:
        """Same LLM mock setup as TestPipelineEndToEnd."""
        boundaries = [
            "Feature engineering transforms",
            "Hyperparameter tuning optimizes",
        ]
        completeness_idx = {"count": 0}

        def completeness_side_effect(window_text, context_text, *, chunk_id=None):
            idx = completeness_idx["count"]
            completeness_idx["count"] += 1
            phrase = boundaries[idx] if idx < len(boundaries) else None
            return CompletenessResult(complete=True, boundary_phrase=phrase)

        mock_llm.check_completeness.side_effect = completeness_side_effect

        chunk_counter = {"n": 0}

        def rewrite_side_effect(
            chunk_text, context_text, *, image_paths=None, chunk_id=None
        ):
            chunk_counter["n"] += 1
            return RewriteResult(
                context=f"[Rewritten {chunk_counter['n']}] {chunk_text.strip()}",
                summary=f"Summary of section {chunk_counter['n']}.",
                filename=f"section-{chunk_counter['n']}",
            )

        mock_llm.rewrite_chunk.side_effect = rewrite_side_effect

        mock_llm.group_summaries.return_value = GroupingResult(groups=[[0, 1], [2, 3]])
        mock_llm.synthesize_block.return_value = BlockContextResult(
            context="Overview of ML pipeline: data, features, evaluation, tuning, deployment.",
            summary="ML pipeline overview covering data, features, evaluation, tuning, and deployment.",
            filename="ml-pipeline-overview",
        )

    def test_full_pipeline_writes_json_output(self, checkpoint_path, tmp_path):
        output_dir = tmp_path / "output"
        config = _config(checkpoint_path, output_dir=str(output_dir))
        pipeline, mock_llm = _build_pipeline_with_mock_llm(config)
        self._setup_llm_mock(mock_llm)

        pipeline.run(DOCUMENT, "ml-doc")

        json_path = output_dir / "hierarchy.json"
        assert json_path.exists()

        data = json.loads(json_path.read_text())
        assert data["document_id"] == "ml-doc"
        assert "root_block_ids" in data
        assert "blocks" in data
        assert "chunks" in data
        assert len(data["chunks"]) == 4

    def test_full_pipeline_writes_markdown_files(self, checkpoint_path, tmp_path):
        output_dir = tmp_path / "output"
        config = _config(checkpoint_path, output_dir=str(output_dir))
        pipeline, mock_llm = _build_pipeline_with_mock_llm(config)
        self._setup_llm_mock(mock_llm)

        pipeline.run(DOCUMENT, "ml-doc")

        assert (output_dir / "index.md").exists()
        assert (output_dir / "content").is_dir()
        assert (output_dir / "content" / "L0").is_dir()

        chunk_files = list((output_dir / "content" / "L0").iterdir())
        assert len(chunk_files) == 4

        higher_level_files = [
            f
            for level_dir in (output_dir / "content").iterdir()
            if level_dir.name != "L0"
            for f in level_dir.iterdir()
        ]
        assert len(higher_level_files) >= 1


class TestPipelineResume:
    @pytest.fixture()
    def checkpoint_path(self, tmp_path: Path) -> str:
        return str(tmp_path / "checkpoint.json")

    def test_resume_continues_from_checkpoint(self, checkpoint_path):
        """Run pipeline, save checkpoint mid-way, resume and complete."""
        config = _config(checkpoint_path)

        # First: create a partial state and save it as a checkpoint
        state = PipelineState.create("ml-doc", DOCUMENT)
        boundary = DOCUMENT.find("Feature engineering transforms")
        state.cursor_position = boundary
        state.chunk_counter = 2

        from chunker.models import Chunk

        state.chunks["chunk-001"] = Chunk(
            id="chunk-001",
            source_span=(0, DOCUMENT.find("Feature engineering transforms") // 2),
            original_text=DOCUMENT[
                : DOCUMENT.find("Feature engineering transforms") // 2
            ],
            context="[Rewritten 1]",
            summary="Summary 1.",
            filename="",
            parent_block_id=None,
            forced_split=False,
            metadata={},
        )
        state.chunks["chunk-002"] = Chunk(
            id="chunk-002",
            source_span=(
                DOCUMENT.find("Feature engineering transforms") // 2,
                boundary,
            ),
            original_text=DOCUMENT[
                DOCUMENT.find("Feature engineering transforms") // 2 : boundary
            ],
            context="[Rewritten 2]",
            summary="Summary 2.",
            filename="",
            parent_block_id=None,
            forced_split=False,
            metadata={},
        )
        state.pending_summaries[0] = ["chunk-001", "chunk-002"]

        checkpointer = Checkpointer(Path(checkpoint_path))
        checkpointer.save(state)

        # Now resume
        pipeline, mock_llm = _build_pipeline_with_mock_llm(config)

        completeness_calls = {"n": 0}

        def completeness_side_effect(window_text, context_text, *, chunk_id=None):
            completeness_calls["n"] += 1
            if completeness_calls["n"] == 1:
                return CompletenessResult(
                    complete=True,
                    boundary_phrase="Hyperparameter tuning optimizes",
                )
            return CompletenessResult(complete=True, boundary_phrase=None)

        mock_llm.check_completeness.side_effect = completeness_side_effect

        rewrite_n = {"n": 2}

        def rewrite_side_effect(
            chunk_text, context_text, *, image_paths=None, chunk_id=None
        ):
            rewrite_n["n"] += 1
            return RewriteResult(
                context=f"[Rewritten {rewrite_n['n']}]",
                summary=f"Summary {rewrite_n['n']}.",
                filename=f"section-{rewrite_n['n']}",
            )

        mock_llm.rewrite_chunk.side_effect = rewrite_side_effect
        mock_llm.group_summaries.return_value = GroupingResult(groups=[[0, 1], [2, 3]])
        mock_llm.synthesize_block.return_value = BlockContextResult(
            context="Synthesized group context.",
            summary="Group summary.",
            filename="group-summary",
        )

        result = pipeline.resume()

        # Should have original 2 + newly extracted chunks
        assert result.total_chunks >= 3
        assert result.state.cursor_position == len(DOCUMENT)


class TestPipelinePdfEndToEnd:
    """PDF mode through the same orchestration and unchanged back half.

    A synthetic multi-page PDF is rendered by the real loader; the LLM is
    mocked, so the page-completeness check and the (vision) rewrite are
    deterministic and no Ollama/vision model is needed.
    """

    PAGES = [
        "Alpha page one introduces the dataset and its collection method.",
        "Beta page two describes preprocessing and feature engineering steps.",
        "Gamma page three reports evaluation metrics and a results table.",
        "Delta page four covers deployment, monitoring, and drift handling.",
    ]

    @pytest.fixture()
    def checkpoint_path(self, tmp_path: Path) -> str:
        return str(tmp_path / "checkpoint.json")

    def _config(self, checkpoint_path: str, output_dir: str) -> ChunkerConfig:
        # min_chunk_tokens small enough that each page satisfies it alone, so
        # one page == one window == one chunk (4 pages -> 4 chunks).
        return ChunkerConfig(
            min_chunk_tokens=3,
            max_chunk_tokens=500,
            max_expansion_attempts=5,
            max_pages_per_chunk=8,
            summary_aggregation_threshold=50,
            summary_count_threshold=3,
            min_group_size=2,
            max_group_size=4,
            model="qwen3:32b",
            checkpoint_path=checkpoint_path,
            output_dir=output_dir,
        )

    def _setup_pdf_llm_mock(
        self, mock_llm: MagicMock, seen_images: list[list[str]]
    ) -> None:
        def page_completeness_side_effect(window_text, *, chunk_id=None):
            # Accept each single-page window as a complete boundary.
            return PageCompletenessResult(complete=True, split_after_page=None)

        mock_llm.check_page_completeness.side_effect = page_completeness_side_effect

        counter = {"n": 0}

        def rewrite_side_effect(
            chunk_text, context_text, *, image_paths=None, chunk_id=None
        ):
            counter["n"] += 1
            seen_images.append(list(image_paths or []))
            return RewriteResult(
                context=f"[Rewritten {counter['n']}] {chunk_text.strip()[:40]}",
                summary=f"Summary of page section {counter['n']}.",
                filename=f"page-section-{counter['n']}",
            )

        mock_llm.rewrite_chunk.side_effect = rewrite_side_effect

        mock_llm.group_summaries.return_value = GroupingResult(groups=[[0, 1], [2, 3]])
        mock_llm.synthesize_block.return_value = BlockContextResult(
            context="Overview of the report's four pages.",
            summary="Report overview across data, features, results, and deployment.",
            filename="report-overview",
        )

    def test_pdf_run_produces_same_outputs_as_text(self, checkpoint_path, tmp_path):
        output_dir = tmp_path / "output"
        config = self._config(checkpoint_path, str(output_dir))
        pdf = tmp_path / "report.pdf"
        _make_pdf(pdf, self.PAGES)
        document = load_document(str(pdf), config)

        pipeline, mock_llm = _build_pipeline_with_mock_llm(config)
        seen_images: list[list[str]] = []
        self._setup_pdf_llm_mock(mock_llm, seen_images)

        result = pipeline.run_document(document)

        # One chunk per page, every chunk page-bounded with its image (FR-02/03/04)
        assert result.total_chunks == 4
        assert result.total_blocks >= 1
        for chunk in result.state.chunks.values():
            assert chunk.page_span is not None
            assert chunk.image_paths

        # Page images threaded into the rewrite step (FR-10/FR-11 wiring)
        assert all(paths for paths in seen_images)
        assert seen_images[0][0].endswith("page-0001.png")

        # Same outputs as a text document (FR-06)
        assert (output_dir / "hierarchy.json").exists()
        assert (output_dir / "index.md").exists()
        assert (output_dir / "content" / "L0").is_dir()
        assert len(list((output_dir / "content" / "L0").iterdir())) == 4
        higher = [
            f
            for level_dir in (output_dir / "content").iterdir()
            if level_dir.name != "L0"
            for f in level_dir.iterdir()
        ]
        assert len(higher) >= 1

    def test_pdf_resume_continues_from_checkpoint(self, checkpoint_path, tmp_path):
        output_dir = tmp_path / "output"
        config = self._config(checkpoint_path, str(output_dir))
        pdf = tmp_path / "report.pdf"
        _make_pdf(pdf, self.PAGES)
        document = load_document(str(pdf), config)
        pages = document.pages

        # Partial state: first 2 pages already processed, saved as a checkpoint.
        state = PipelineState.create_from_pages(document.document_id, pages)
        state.cursor_page = 2
        state.chunk_counter = 2
        for i in (1, 2):
            state.chunks[f"chunk-{i:03d}"] = Chunk(
                id=f"chunk-{i:03d}",
                source_span=(0, 0),
                original_text=f"page {i} body",
                context=f"[Rewritten {i}]",
                summary=f"Summary {i}.",
                filename="",
                parent_block_id=None,
                forced_split=False,
                metadata={},
                page_span=(i, i),
                image_paths=[pages[i - 1].image_path],
            )
        state.pending_summaries[0] = ["chunk-001", "chunk-002"]
        Checkpointer(Path(checkpoint_path)).save(state)

        pipeline, mock_llm = _build_pipeline_with_mock_llm(config)
        seen_images: list[list[str]] = []
        self._setup_pdf_llm_mock(mock_llm, seen_images)

        result = pipeline.resume()

        # Original 2 chunks retained + remaining pages processed to the end.
        assert result.total_chunks >= 3
        assert result.state.cursor_page == len(pages)
        # Only the newly processed (3rd/4th) pages were re-extracted, not 1-2.
        assert len(seen_images) == len(pages) - 2
