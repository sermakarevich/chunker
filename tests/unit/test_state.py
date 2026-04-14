import json

from chunker.state import PipelineState


class TestPipelineState:
    def test_create_initial(self):
        state = PipelineState.create(
            document_id="doc-001",
            source_text="Hello world. This is a test.",
        )
        assert state.document_id == "doc-001"
        assert state.source_text == "Hello world. This is a test."
        assert state.cursor_position == 0
        assert state.chunks == {}
        assert state.blocks == {}
        assert state.pending_summaries == {}
        assert state.chunk_counter == 0
        assert state.block_counters == {}

    def test_has_more_text_at_start(self):
        state = PipelineState.create(
            document_id="doc-001",
            source_text="Some text here.",
        )
        assert state.has_more_text is True

    def test_has_more_text_at_end(self):
        state = PipelineState.create(
            document_id="doc-001",
            source_text="Some text here.",
        )
        state.cursor_position = len(state.source_text)
        assert state.has_more_text is False

    def test_has_more_text_empty_document(self):
        state = PipelineState.create(
            document_id="doc-001",
            source_text="",
        )
        assert state.has_more_text is False

    def test_json_roundtrip(self, agentic_rag_text):
        state = PipelineState.create(
            document_id="doc-001",
            source_text=agentic_rag_text,
        )
        state.cursor_position = 412

        serialized = state.to_json()
        data = json.loads(serialized)
        assert data["document_id"] == "doc-001"
        assert data["cursor_position"] == 412

        restored = PipelineState.from_json(serialized)
        assert restored.document_id == state.document_id
        assert restored.cursor_position == 412
        assert restored.source_text == state.source_text
        assert restored.chunks == {}
        assert restored.blocks == {}

    def test_json_roundtrip_with_chunks_and_blocks(self):
        from chunker.models import Chunk, SummaryBlock

        state = PipelineState.create(
            document_id="doc-001",
            source_text="Test document text.",
        )
        state.chunks["chunk-001"] = Chunk(
            id="chunk-001",
            source_span=(0, 10),
            original_text="Test docum",
            rewritten_text="Test document",
            summary="A test",
            parent_block_id=None,
            forced_split=False,
            metadata={},
        )
        state.blocks["block-001"] = SummaryBlock(
            id="block-001",
            level=1,
            summary="Block summary",
            child_ids=["chunk-001"],
            parent_block_id=None,
            metadata={},
        )
        state.pending_summaries[0] = ["chunk-001"]
        state.chunk_counter = 1

        restored = PipelineState.from_json(state.to_json())
        assert "chunk-001" in restored.chunks
        assert restored.chunks["chunk-001"].original_text == "Test docum"
        assert "block-001" in restored.blocks
        assert restored.blocks["block-001"].child_ids == ["chunk-001"]
        assert restored.pending_summaries == {0: ["chunk-001"]}
        assert restored.chunk_counter == 1
