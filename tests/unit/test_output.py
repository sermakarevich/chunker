from __future__ import annotations

import json
from pathlib import Path

import pytest

from chunker.models import Chunk, SummaryBlock
from chunker.nodes.output import JsonExporter, MarkdownRenderer
from chunker.state import PipelineState


# --- Fixtures ---


def _chunk(
    chunk_id: str,
    span: tuple[int, int] = (0, 100),
    parent: str | None = None,
    forced: bool = False,
) -> Chunk:
    return Chunk(
        id=chunk_id,
        source_span=span,
        original_text=f"Original text of {chunk_id}",
        rewritten_text=f"Rewritten text of {chunk_id}",
        summary=f"Summary of {chunk_id}",
        parent_block_id=parent,
        forced_split=forced,
        metadata={},
    )


def _block(
    block_id: str,
    level: int,
    children: list[str],
    parent: str | None = None,
) -> SummaryBlock:
    return SummaryBlock(
        id=block_id,
        level=level,
        summary=f"Summary of {block_id}",
        child_ids=children,
        parent_block_id=parent,
        metadata={},
    )


@pytest.fixture
def hierarchy_state() -> PipelineState:
    """3 chunks -> 1 L1 block -> 1 L2 root block."""
    state = PipelineState.create(document_id="doc-hier", source_text="x" * 300)
    state.chunks = {
        "chunk-001": _chunk("chunk-001", span=(0, 100), parent="block-L1-001"),
        "chunk-002": _chunk("chunk-002", span=(100, 200), parent="block-L1-001"),
        "chunk-003": _chunk("chunk-003", span=(200, 300), parent="block-L1-001"),
    }
    state.blocks = {
        "block-L1-001": _block(
            "block-L1-001",
            level=1,
            children=["chunk-001", "chunk-002", "chunk-003"],
            parent="block-L2-001",
        ),
        "block-L2-001": _block(
            "block-L2-001",
            level=2,
            children=["block-L1-001"],
            parent=None,
        ),
    }
    return state


@pytest.fixture
def flat_state() -> PipelineState:
    """2 chunks, no blocks — flat output."""
    state = PipelineState.create(document_id="doc-flat", source_text="y" * 200)
    state.chunks = {
        "chunk-001": _chunk("chunk-001", span=(0, 100)),
        "chunk-002": _chunk("chunk-002", span=(100, 200)),
    }
    return state


@pytest.fixture
def mixed_state() -> PipelineState:
    """3 chunks in a block + 1 orphan chunk with no parent."""
    state = PipelineState.create(document_id="doc-mixed", source_text="m" * 400)
    state.chunks = {
        "chunk-001": _chunk("chunk-001", span=(0, 100), parent="block-L1-001"),
        "chunk-002": _chunk("chunk-002", span=(100, 200), parent="block-L1-001"),
        "chunk-003": _chunk("chunk-003", span=(200, 300), parent="block-L1-001"),
        "chunk-004": _chunk("chunk-004", span=(300, 400)),  # orphan
    }
    state.blocks = {
        "block-L1-001": _block(
            "block-L1-001",
            level=1,
            children=["chunk-001", "chunk-002", "chunk-003"],
        ),
    }
    return state


@pytest.fixture
def multi_root_state() -> PipelineState:
    """4 chunks, 2 L1 blocks (both roots)."""
    state = PipelineState.create(document_id="doc-multi", source_text="z" * 400)
    state.chunks = {
        "chunk-001": _chunk("chunk-001", span=(0, 100), parent="block-L1-001"),
        "chunk-002": _chunk("chunk-002", span=(100, 200), parent="block-L1-001"),
        "chunk-003": _chunk("chunk-003", span=(200, 300), parent="block-L1-002"),
        "chunk-004": _chunk("chunk-004", span=(300, 400), parent="block-L1-002"),
    }
    state.blocks = {
        "block-L1-001": _block(
            "block-L1-001",
            level=1,
            children=["chunk-001", "chunk-002"],
        ),
        "block-L1-002": _block(
            "block-L1-002",
            level=1,
            children=["chunk-003", "chunk-004"],
        ),
    }
    return state


# --- JsonExporter.export() ---


class TestJsonExporterExport:
    def test_top_level_keys(self, hierarchy_state: PipelineState) -> None:
        result = JsonExporter().export(hierarchy_state)
        assert set(result.keys()) == {
            "document_id",
            "root_block_ids",
            "blocks",
            "chunks",
        }

    def test_document_id(self, hierarchy_state: PipelineState) -> None:
        result = JsonExporter().export(hierarchy_state)
        assert result["document_id"] == "doc-hier"

    def test_root_block_ids(self, hierarchy_state: PipelineState) -> None:
        result = JsonExporter().export(hierarchy_state)
        assert result["root_block_ids"] == ["block-L2-001"]

    def test_chunk_fields(self, hierarchy_state: PipelineState) -> None:
        result = JsonExporter().export(hierarchy_state)
        chunk = result["chunks"]["chunk-001"]
        assert chunk["id"] == "chunk-001"
        assert chunk["source_span"] == [0, 100]
        assert chunk["original_text"] == "Original text of chunk-001"
        assert chunk["rewritten_text"] == "Rewritten text of chunk-001"
        assert chunk["summary"] == "Summary of chunk-001"
        assert chunk["parent_block_id"] == "block-L1-001"
        assert chunk["forced_split"] is False

    def test_block_fields(self, hierarchy_state: PipelineState) -> None:
        result = JsonExporter().export(hierarchy_state)
        block = result["blocks"]["block-L1-001"]
        assert block["id"] == "block-L1-001"
        assert block["level"] == 1
        assert block["summary"] == "Summary of block-L1-001"
        assert block["child_ids"] == ["chunk-001", "chunk-002", "chunk-003"]
        assert block["parent_block_id"] == "block-L2-001"

    def test_all_chunks_present(self, hierarchy_state: PipelineState) -> None:
        result = JsonExporter().export(hierarchy_state)
        assert set(result["chunks"].keys()) == {
            "chunk-001",
            "chunk-002",
            "chunk-003",
        }

    def test_all_blocks_present(self, hierarchy_state: PipelineState) -> None:
        result = JsonExporter().export(hierarchy_state)
        assert set(result["blocks"].keys()) == {
            "block-L1-001",
            "block-L2-001",
        }

    def test_bidirectional_links(self, hierarchy_state: PipelineState) -> None:
        result = JsonExporter().export(hierarchy_state)
        for block_id, block in result["blocks"].items():
            for child_id in block["child_ids"]:
                if child_id in result["chunks"]:
                    assert result["chunks"][child_id]["parent_block_id"] == block_id
                elif child_id in result["blocks"]:
                    assert result["blocks"][child_id]["parent_block_id"] == block_id

    def test_flat_no_blocks(self, flat_state: PipelineState) -> None:
        result = JsonExporter().export(flat_state)
        assert result["blocks"] == {}
        assert result["root_block_ids"] == []
        assert len(result["chunks"]) == 2

    def test_flat_chunks_no_parent(self, flat_state: PipelineState) -> None:
        result = JsonExporter().export(flat_state)
        for chunk in result["chunks"].values():
            assert chunk["parent_block_id"] is None

    def test_multi_root(self, multi_root_state: PipelineState) -> None:
        result = JsonExporter().export(multi_root_state)
        assert sorted(result["root_block_ids"]) == [
            "block-L1-001",
            "block-L1-002",
        ]

    def test_export_is_json_serializable(
        self,
        hierarchy_state: PipelineState,
    ) -> None:
        result = JsonExporter().export(hierarchy_state)
        serialized = json.dumps(result)
        assert json.loads(serialized) == result


# --- JsonExporter.write() ---


class TestJsonExporterWrite:
    def test_writes_file(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        out = tmp_path / "hierarchy.json"
        JsonExporter().write(hierarchy_state, out)
        assert out.exists()

    def test_written_content_matches_export(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        out = tmp_path / "hierarchy.json"
        exporter = JsonExporter()
        exporter.write(hierarchy_state, out)
        written = json.loads(out.read_text())
        assert written == exporter.export(hierarchy_state)


# --- MarkdownRenderer directory structure ---


class TestMarkdownRendererStructure:
    def test_creates_chunks_dir(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        assert (tmp_path / "chunks").is_dir()

    def test_creates_blocks_dir(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        assert (tmp_path / "blocks").is_dir()

    def test_creates_index(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        assert (tmp_path / "index.md").is_file()

    def test_one_file_per_chunk(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        chunk_files = list((tmp_path / "chunks").glob("*.md"))
        assert len(chunk_files) == 3

    def test_one_file_per_block(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        block_files = list((tmp_path / "blocks").glob("*.md"))
        assert len(block_files) == 2

    def test_chunk_filename(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        assert (tmp_path / "chunks" / "chunk-001.md").is_file()

    def test_block_filename(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        assert (tmp_path / "blocks" / "block-L1-001.md").is_file()


# --- Chunk markdown content ---


class TestChunkMarkdown:
    def test_title(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "chunks" / "chunk-001.md").read_text()
        assert "# Chunk 001" in content

    def test_parent_link(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "chunks" / "chunk-001.md").read_text()
        assert "[[blocks/block-L1-001]]" in content

    def test_summary_section(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "chunks" / "chunk-001.md").read_text()
        assert "## Summary" in content
        assert "Summary of chunk-001" in content

    def test_content_section(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "chunks" / "chunk-001.md").read_text()
        assert "## Content" in content
        assert "Rewritten text of chunk-001" in content

    def test_original_section(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "chunks" / "chunk-001.md").read_text()
        assert "## Original" in content
        assert "Original text of chunk-001" in content


# --- Block markdown content ---


class TestBlockMarkdown:
    def test_title(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "blocks" / "block-L1-001.md").read_text()
        assert "# Summary Block L1-001" in content

    def test_parent_link(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "blocks" / "block-L1-001.md").read_text()
        assert "[[blocks/block-L2-001]]" in content

    def test_root_block_no_parent_link(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "blocks" / "block-L2-001.md").read_text()
        assert "**Parent:**" not in content

    def test_summary_section(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "blocks" / "block-L1-001.md").read_text()
        assert "## Summary" in content
        assert "Summary of block-L1-001" in content

    def test_children_links(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "blocks" / "block-L1-001.md").read_text()
        assert "[[chunks/chunk-001]]" in content
        assert "[[chunks/chunk-002]]" in content
        assert "[[chunks/chunk-003]]" in content

    def test_block_children_link_to_blocks(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "blocks" / "block-L2-001.md").read_text()
        assert "[[blocks/block-L1-001]]" in content


# --- Index file ---


class TestIndexMarkdown:
    def test_title(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "index.md").read_text()
        assert "# doc-hier" in content

    def test_links_to_root_blocks(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "index.md").read_text()
        assert "[[blocks/block-L2-001]]" in content

    def test_flat_index_links_to_chunks(
        self,
        flat_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(flat_state, tmp_path)
        content = (tmp_path / "index.md").read_text()
        assert "[[chunks/chunk-001]]" in content
        assert "[[chunks/chunk-002]]" in content

    def test_mixed_index_links_orphan_chunk(
        self,
        mixed_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(mixed_state, tmp_path)
        content = (tmp_path / "index.md").read_text()
        assert "[[chunks/chunk-004]]" in content

    def test_mixed_index_has_ungrouped_section(
        self,
        mixed_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(mixed_state, tmp_path)
        content = (tmp_path / "index.md").read_text()
        assert "## Ungrouped Chunks" in content

    def test_mixed_index_still_links_root_blocks(
        self,
        mixed_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(mixed_state, tmp_path)
        content = (tmp_path / "index.md").read_text()
        assert "[[blocks/block-L1-001]]" in content

    def test_multi_root_index(
        self,
        multi_root_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(multi_root_state, tmp_path)
        content = (tmp_path / "index.md").read_text()
        assert "[[blocks/block-L1-001]]" in content
        assert "[[blocks/block-L1-002]]" in content


# --- Wiki-link format ---


class TestWikiLinkFormat:
    def test_no_md_extension_in_links(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        for md_file in tmp_path.rglob("*.md"):
            content = md_file.read_text()
            assert ".md]]" not in content


# --- Flat output ---


class TestFlatOutput:
    def test_no_blocks_dir_content(
        self,
        flat_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(flat_state, tmp_path)
        blocks_dir = tmp_path / "blocks"
        if blocks_dir.exists():
            assert list(blocks_dir.glob("*.md")) == []

    def test_chunk_no_parent_link(
        self,
        flat_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(flat_state, tmp_path)
        content = (tmp_path / "chunks" / "chunk-001.md").read_text()
        assert "**Parent:**" not in content


# --- Full traversal ---


class TestFullTraversal:
    def _collect_links(self, content: str) -> list[str]:
        """Extract all [[path]] links from markdown content."""
        links = []
        start = 0
        while True:
            open_pos = content.find("[[", start)
            if open_pos == -1:
                break
            close_pos = content.find("]]", open_pos)
            if close_pos == -1:
                break
            links.append(content[open_pos + 2 : close_pos])
            start = close_pos + 2
        return links

    def _traverse(self, output_dir: Path) -> set[str]:
        """Start at index.md, follow all links, return visited file paths."""
        visited: set[str] = set()
        queue = ["index"]

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            file_path = output_dir / f"{current}.md"
            if not file_path.exists():
                continue

            content = file_path.read_text()
            for link in self._collect_links(content):
                if link not in visited:
                    queue.append(link)

        return visited

    def test_all_chunks_reachable_hierarchy(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        visited = self._traverse(tmp_path)
        for chunk_id in hierarchy_state.chunks:
            assert f"chunks/{chunk_id}" in visited

    def test_all_blocks_reachable_hierarchy(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        visited = self._traverse(tmp_path)
        for block_id in hierarchy_state.blocks:
            assert f"blocks/{block_id}" in visited

    def test_all_chunks_reachable_flat(
        self,
        flat_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(flat_state, tmp_path)
        visited = self._traverse(tmp_path)
        for chunk_id in flat_state.chunks:
            assert f"chunks/{chunk_id}" in visited

    def test_all_chunks_reachable_mixed(
        self,
        mixed_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(mixed_state, tmp_path)
        visited = self._traverse(tmp_path)
        for chunk_id in mixed_state.chunks:
            assert f"chunks/{chunk_id}" in visited

    def test_all_chunks_reachable_multi_root(
        self,
        multi_root_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(multi_root_state, tmp_path)
        visited = self._traverse(tmp_path)
        for chunk_id in multi_root_state.chunks:
            assert f"chunks/{chunk_id}" in visited
