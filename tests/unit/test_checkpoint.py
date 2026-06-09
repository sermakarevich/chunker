import json
from pathlib import Path

import pytest

from chunker.checkpoint import Checkpointer
from chunker.models import Chunk, Page, SummaryBlock
from chunker.state import PipelineState


@pytest.fixture
def checkpoint_path(tmp_path: Path) -> Path:
    return tmp_path / "checkpoint.json"


@pytest.fixture
def sample_state() -> PipelineState:
    state = PipelineState.create(
        document_id="doc-001",
        source_text="Hello world. This is a test document.",
    )
    state.cursor_position = 12
    state.chunks["chunk-001"] = Chunk(
        id="chunk-001",
        source_span=(0, 12),
        original_text="Hello world.",
        context="Hello world.",
        summary="Greeting",
        filename="",
        parent_block_id=None,
        forced_split=False,
        metadata={"tokens": 3},
    )
    state.blocks["block-001"] = SummaryBlock(
        id="block-001",
        level=1,
        context="",
        summary="Block summary",
        filename="",
        child_ids=["chunk-001"],
        parent_block_id=None,
        metadata={},
    )
    state.pending_summaries[0] = ["chunk-001"]
    state.chunk_counter = 1
    state.block_counters[1] = 1
    return state


class TestCheckpointerSave:
    def test_save_creates_json_file(self, checkpoint_path, sample_state):
        cp = Checkpointer(checkpoint_path)
        cp.save(sample_state)

        assert checkpoint_path.exists()
        data = json.loads(checkpoint_path.read_text())
        assert data["document_id"] == "doc-001"

    def test_save_contains_full_state(self, checkpoint_path, sample_state):
        cp = Checkpointer(checkpoint_path)
        cp.save(sample_state)

        data = json.loads(checkpoint_path.read_text())
        assert data["cursor_position"] == 12
        assert "chunk-001" in data["chunks"]
        assert "block-001" in data["blocks"]
        assert data["chunk_counter"] == 1

    def test_save_overwrites_existing(self, checkpoint_path, sample_state):
        cp = Checkpointer(checkpoint_path)
        cp.save(sample_state)

        sample_state.cursor_position = 30
        cp.save(sample_state)

        data = json.loads(checkpoint_path.read_text())
        assert data["cursor_position"] == 30


class TestCheckpointerLoad:
    def test_load_restores_state(self, checkpoint_path, sample_state):
        cp = Checkpointer(checkpoint_path)
        cp.save(sample_state)

        restored = cp.load()
        assert restored.document_id == "doc-001"
        assert restored.cursor_position == 12
        assert restored.source_text == sample_state.source_text

    def test_load_restores_chunks(self, checkpoint_path, sample_state):
        cp = Checkpointer(checkpoint_path)
        cp.save(sample_state)

        restored = cp.load()
        assert "chunk-001" in restored.chunks
        chunk = restored.chunks["chunk-001"]
        assert chunk.original_text == "Hello world."
        assert chunk.metadata == {"tokens": 3}

    def test_load_restores_blocks(self, checkpoint_path, sample_state):
        cp = Checkpointer(checkpoint_path)
        cp.save(sample_state)

        restored = cp.load()
        assert "block-001" in restored.blocks
        block = restored.blocks["block-001"]
        assert block.child_ids == ["chunk-001"]
        assert block.level == 1

    def test_load_restores_pending_summaries(self, checkpoint_path, sample_state):
        cp = Checkpointer(checkpoint_path)
        cp.save(sample_state)

        restored = cp.load()
        assert restored.pending_summaries == {0: ["chunk-001"]}

    def test_load_restores_block_counters(self, checkpoint_path, sample_state):
        cp = Checkpointer(checkpoint_path)
        cp.save(sample_state)

        restored = cp.load()
        assert restored.block_counters == {1: 1}


class TestSourceSpanRoundtrip:
    def test_source_span_survives_roundtrip(self, checkpoint_path, sample_state):
        cp = Checkpointer(checkpoint_path)
        cp.save(sample_state)

        restored = cp.load()
        chunk = restored.chunks["chunk-001"]
        assert chunk.source_span == (0, 12)
        assert isinstance(chunk.source_span, tuple)


class TestDocumentIdValidation:
    def test_load_raises_on_document_id_mismatch(self, checkpoint_path, sample_state):
        cp = Checkpointer(checkpoint_path)
        cp.save(sample_state)

        with pytest.raises(ValueError, match="document_id"):
            cp.load(expected_document_id="doc-999")

    def test_load_accepts_matching_document_id(self, checkpoint_path, sample_state):
        cp = Checkpointer(checkpoint_path)
        cp.save(sample_state)

        restored = cp.load(expected_document_id="doc-001")
        assert restored.document_id == "doc-001"

    def test_load_skips_validation_when_no_expected_id(
        self, checkpoint_path, sample_state
    ):
        cp = Checkpointer(checkpoint_path)
        cp.save(sample_state)

        restored = cp.load()
        assert restored.document_id == "doc-001"


class TestCheckpointerExists:
    def test_exists_false_when_no_file(self, checkpoint_path):
        cp = Checkpointer(checkpoint_path)
        assert cp.exists() is False

    def test_exists_true_after_save(self, checkpoint_path, sample_state):
        cp = Checkpointer(checkpoint_path)
        cp.save(sample_state)
        assert cp.exists() is True


class TestAtomicWrite:
    def test_no_partial_file_on_disk(self, checkpoint_path, sample_state, tmp_path):
        """Verify save uses atomic write: no temp files left behind."""
        cp = Checkpointer(checkpoint_path)
        cp.save(sample_state)

        files = list(tmp_path.iterdir())
        assert files == [checkpoint_path]

    def test_save_creates_parent_directories(self, tmp_path, sample_state):
        nested_path = tmp_path / "sub" / "dir" / "checkpoint.json"
        cp = Checkpointer(nested_path)
        cp.save(sample_state)

        assert nested_path.exists()


class TestRoundtripEquality:
    def test_full_roundtrip_produces_equal_state(self, checkpoint_path, sample_state):
        cp = Checkpointer(checkpoint_path)
        cp.save(sample_state)
        restored = cp.load()

        assert restored.document_id == sample_state.document_id
        assert restored.source_text == sample_state.source_text
        assert restored.cursor_position == sample_state.cursor_position
        assert restored.chunk_counter == sample_state.chunk_counter
        assert restored.block_counters == sample_state.block_counters
        assert restored.pending_summaries == sample_state.pending_summaries
        assert list(restored.chunks.keys()) == list(sample_state.chunks.keys())
        assert list(restored.blocks.keys()) == list(sample_state.blocks.keys())

        for key in sample_state.chunks:
            orig = sample_state.chunks[key]
            rest = restored.chunks[key]
            assert rest.id == orig.id
            assert rest.source_span == orig.source_span
            assert rest.original_text == orig.original_text
            assert rest.context == orig.context
            assert rest.summary == orig.summary
            assert rest.parent_block_id == orig.parent_block_id
            assert rest.forced_split == orig.forced_split
            assert rest.metadata == orig.metadata


@pytest.fixture
def pdf_state() -> PipelineState:
    state = PipelineState.create_from_pages(
        document_id="doc-pdf",
        pages=[
            Page(number=1, text="page one", image_path="/abs/pages/page-0001.png"),
            Page(number=2, text="", image_path="/abs/pages/page-0002.png"),
        ],
    )
    state.cursor_page = 1
    state.chunks["chunk-001"] = Chunk(
        id="chunk-001",
        source_span=(0, 0),
        original_text="",
        context="page one context",
        summary="summary",
        filename="",
        parent_block_id=None,
        forced_split=False,
        metadata={},
        page_span=(1, 1),
        image_paths=["/abs/pages/page-0001.png"],
    )
    state.chunk_counter = 1
    return state


class TestPdfCheckpointRoundtrip:
    def test_pdf_state_roundtrips(self, checkpoint_path, pdf_state):
        cp = Checkpointer(checkpoint_path)
        cp.save(pdf_state)

        restored = cp.load()
        assert restored.cursor_page == 1
        assert restored.pages is not None
        assert [p.number for p in restored.pages] == [1, 2]
        assert restored.pages[1].text == ""
        chunk = restored.chunks["chunk-001"]
        assert chunk.page_span == (1, 1)
        assert chunk.image_paths == ["/abs/pages/page-0001.png"]

    def test_checkpoint_stores_paths_not_bytes(self, checkpoint_path, pdf_state):
        cp = Checkpointer(checkpoint_path)
        cp.save(pdf_state)

        raw = checkpoint_path.read_text()
        data = json.loads(raw)
        assert data["pages"][0]["image_path"] == "/abs/pages/page-0001.png"
        assert "image_bytes" not in raw
        assert "base64" not in raw


class TestOldCheckpointMigration:
    def test_pre_feature_checkpoint_loads(self, checkpoint_path):
        """A checkpoint written before the PDF feature (no page keys) loads."""
        old = {
            "document_id": "doc-legacy",
            "source_text": "legacy text",
            "cursor_position": 4,
            "chunks": {
                "chunk-001": {
                    "id": "chunk-001",
                    "source_span": [0, 4],
                    "original_text": "leg",
                    "context": "ctx",
                    "summary": "sum",
                    "filename": "",
                    "parent_block_id": None,
                    "forced_split": False,
                    "metadata": {},
                }
            },
            "blocks": {},
            "pending_summaries": {},
            "chunk_counter": 1,
            "block_counters": {},
        }
        checkpoint_path.write_text(json.dumps(old))

        restored = Checkpointer(checkpoint_path).load()
        assert restored.pages is None
        assert restored.cursor_page == 0
        chunk = restored.chunks["chunk-001"]
        assert chunk.page_span is None
        assert chunk.image_paths == []
