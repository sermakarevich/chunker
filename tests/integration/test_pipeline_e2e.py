"""End-to-end pipeline test with mock LLM.

Uses real components (ChunkExtractor, ChunkRewriter, AggregationSweeper,
Checkpointer, ContextBuilder) but mocks LLMService responses to avoid
needing a running Ollama instance.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from chunker.checkpoint import Checkpointer
from chunker.config import ChunkerConfig
from chunker.context import ContextBuilder
from chunker.llm.schemas import (
    CompletenessResult,
    GroupingResult,
    RewriteResult,
)
from chunker.llm.service import LLMService
from chunker.nodes.aggregation import AggregationSweeper
from chunker.nodes.chunking import ChunkExtractor
from chunker.nodes.rewriting import ChunkRewriter
from chunker.pipeline import Pipeline
from chunker.state import PipelineState


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

        def rewrite_side_effect(chunk_text, context_text, *, chunk_id=None):
            chunk_counter["n"] += 1
            return RewriteResult(
                rewritten_text=f"[Rewritten {chunk_counter['n']}] {chunk_text.strip()}",
                summary=f"Summary of section {chunk_counter['n']}.",
            )

        mock_llm.rewrite_chunk.side_effect = rewrite_side_effect

        mock_llm.group_summaries.return_value = GroupingResult(groups=[[0, 1], [2, 3]])

        mock_llm.summarize_group.return_value = (
            "Overview of ML pipeline: data, features, evaluation, tuning, deployment."
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

    def test_chunks_have_rewritten_text_and_summaries(self, checkpoint_path):
        config = _config(checkpoint_path)
        pipeline, mock_llm = _build_pipeline_with_mock_llm(config)
        self._setup_llm_mock(mock_llm)

        result = pipeline.run(DOCUMENT, "ml-doc")

        for chunk in result.state.chunks.values():
            assert chunk.rewritten_text.startswith("[Rewritten")
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

        def rewrite_side_effect(chunk_text, context_text, *, chunk_id=None):
            chunk_counter["n"] += 1
            return RewriteResult(
                rewritten_text=f"[Rewritten {chunk_counter['n']}] {chunk_text.strip()}",
                summary=f"Summary of section {chunk_counter['n']}.",
            )

        mock_llm.rewrite_chunk.side_effect = rewrite_side_effect

        mock_llm.group_summaries.return_value = GroupingResult(groups=[[0, 1], [2, 3]])
        mock_llm.summarize_group.return_value = (
            "Overview of ML pipeline: data, features, evaluation, tuning, deployment."
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
        assert (output_dir / "chunks").is_dir()
        assert (output_dir / "blocks").is_dir()

        chunk_files = list((output_dir / "chunks").iterdir())
        assert len(chunk_files) == 4

        block_files = list((output_dir / "blocks").iterdir())
        assert len(block_files) >= 1


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
            rewritten_text="[Rewritten 1]",
            summary="Summary 1.",
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
            rewritten_text="[Rewritten 2]",
            summary="Summary 2.",
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

        def rewrite_side_effect(chunk_text, context_text, *, chunk_id=None):
            rewrite_n["n"] += 1
            return RewriteResult(
                rewritten_text=f"[Rewritten {rewrite_n['n']}]",
                summary=f"Summary {rewrite_n['n']}.",
            )

        mock_llm.rewrite_chunk.side_effect = rewrite_side_effect
        mock_llm.group_summaries.return_value = GroupingResult(groups=[[0, 1], [2, 3]])
        mock_llm.summarize_group.return_value = "Group summary."

        result = pipeline.resume()

        # Should have original 2 + newly extracted chunks
        assert result.total_chunks >= 3
        assert result.state.cursor_position == len(DOCUMENT)
