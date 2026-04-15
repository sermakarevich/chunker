import json

from chunker.models import Chunk, SummaryBlock


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
