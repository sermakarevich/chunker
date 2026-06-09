import json

from chunker.models import Chunk, Page, SummaryBlock


class TestPage:
    def test_has_required_fields(self):
        page = Page(number=3, text="page text", image_path="/abs/pages/page-0003.png")
        assert page.number == 3
        assert page.text == "page text"
        assert page.image_path == "/abs/pages/page-0003.png"

    def test_json_roundtrip_by_path(self):
        page = Page(number=1, text="", image_path="/abs/pages/page-0001.png")
        restored = Page.from_json(page.to_json())
        assert restored.number == 1
        assert restored.text == ""
        assert restored.image_path == "/abs/pages/page-0001.png"

    def test_serializes_path_not_bytes(self):
        page = Page(number=2, text="t", image_path="/abs/pages/page-0002.png")
        data = page.to_dict()
        assert data == {
            "number": 2,
            "text": "t",
            "image_path": "/abs/pages/page-0002.png",
        }


class TestChunk:
    def test_has_required_fields(self):
        chunk = Chunk(
            id="chunk-001",
            source_span=(0, 100),
            original_text="original",
            context="context",
            summary="summary",
            filename="original-content",
            parent_block_id=None,
            forced_split=False,
            metadata={},
        )
        assert chunk.id == "chunk-001"
        assert chunk.source_span == (0, 100)
        assert chunk.original_text == "original"
        assert chunk.context == "context"
        assert chunk.summary == "summary"
        assert chunk.filename == "original-content"
        assert chunk.parent_block_id is None
        assert chunk.forced_split is False
        assert chunk.metadata == {}

    def test_json_serializable(self):
        chunk = Chunk(
            id="chunk-001",
            source_span=(0, 100),
            original_text="original",
            context="context",
            summary="summary",
            filename="original-content",
            parent_block_id=None,
            forced_split=False,
            metadata={"key": "value"},
        )
        data = json.loads(chunk.to_json())
        assert data["id"] == "chunk-001"
        assert data["source_span"] == [0, 100]
        assert data["context"] == "context"
        assert data["filename"] == "original-content"
        assert data["metadata"] == {"key": "value"}

    def test_from_json_roundtrip(self):
        chunk = Chunk(
            id="chunk-001",
            source_span=(0, 100),
            original_text="original",
            context="context",
            summary="summary",
            filename="original-content",
            parent_block_id="block-001",
            forced_split=True,
            metadata={"key": "value"},
        )
        restored = Chunk.from_json(chunk.to_json())
        assert restored.id == chunk.id
        assert restored.source_span == chunk.source_span
        assert restored.context == chunk.context
        assert restored.summary == chunk.summary
        assert restored.filename == chunk.filename
        assert restored.parent_block_id == chunk.parent_block_id
        assert restored.forced_split is True
        assert restored.metadata == chunk.metadata

    def test_page_fields_default_to_text_mode(self):
        chunk = Chunk(
            id="chunk-001",
            source_span=(0, 100),
            original_text="original",
            context="context",
            summary="summary",
            filename="original-content",
            parent_block_id=None,
            forced_split=False,
            metadata={},
        )
        assert chunk.page_span is None
        assert chunk.image_paths == []

    def test_pdf_fields_roundtrip(self):
        chunk = Chunk(
            id="chunk-007",
            source_span=(0, 0),
            original_text="",
            context="context",
            summary="summary",
            filename="f",
            parent_block_id=None,
            forced_split=False,
            metadata={},
            page_span=(3, 5),
            image_paths=["/abs/pages/page-0003.png", "/abs/pages/page-0004.png"],
        )
        data = json.loads(chunk.to_json())
        assert data["page_span"] == [3, 5]
        assert data["image_paths"] == [
            "/abs/pages/page-0003.png",
            "/abs/pages/page-0004.png",
        ]

        restored = Chunk.from_json(chunk.to_json())
        assert restored.page_span == (3, 5)
        assert isinstance(restored.page_span, tuple)
        assert restored.image_paths == chunk.image_paths

    def test_from_dict_migrates_old_checkpoint_without_pdf_keys(self):
        """A chunk dict written before the PDF feature has no page keys."""
        old = {
            "id": "chunk-001",
            "source_span": [0, 100],
            "original_text": "original",
            "context": "context",
            "summary": "summary",
            "filename": "f",
            "parent_block_id": None,
            "forced_split": False,
            "metadata": {},
        }
        chunk = Chunk.from_dict(old)
        assert chunk.page_span is None
        assert chunk.image_paths == []


class TestSummaryBlock:
    def test_has_required_fields(self):
        block = SummaryBlock(
            id="block-001",
            level=1,
            context="block context",
            summary="block summary",
            filename="block-overview",
            child_ids=["chunk-001", "chunk-002"],
            parent_block_id=None,
            metadata={},
        )
        assert block.id == "block-001"
        assert block.level == 1
        assert block.context == "block context"
        assert block.summary == "block summary"
        assert block.filename == "block-overview"
        assert block.child_ids == ["chunk-001", "chunk-002"]
        assert block.parent_block_id is None
        assert block.metadata == {}

    def test_json_serializable(self):
        block = SummaryBlock(
            id="block-001",
            level=1,
            context="block context",
            summary="block summary",
            filename="block-overview",
            child_ids=["chunk-001", "chunk-002"],
            parent_block_id=None,
            metadata={},
        )
        data = json.loads(block.to_json())
        assert data["id"] == "block-001"
        assert data["context"] == "block context"
        assert data["filename"] == "block-overview"
        assert data["child_ids"] == ["chunk-001", "chunk-002"]

    def test_from_json_roundtrip(self):
        block = SummaryBlock(
            id="block-001",
            level=2,
            context="block context",
            summary="summary",
            filename="block-overview",
            child_ids=["block-sub-1"],
            parent_block_id="block-root",
            metadata={"level_name": "section"},
        )
        restored = SummaryBlock.from_json(block.to_json())
        assert restored.id == block.id
        assert restored.level == block.level
        assert restored.context == block.context
        assert restored.summary == block.summary
        assert restored.filename == block.filename
        assert restored.parent_block_id == block.parent_block_id
        assert restored.metadata == block.metadata
