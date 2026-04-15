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
    filename: str = "",
    summary: str = "",
) -> Chunk:
    return Chunk(
        id=chunk_id,
        source_span=span,
        original_text=f"Original text of {chunk_id}",
        context=f"Context of {chunk_id}",
        summary=summary or f"Summary of {chunk_id}.",
        filename=filename or chunk_id.replace("chunk-", "chunk-slug-"),
        parent_block_id=parent,
        forced_split=forced,
        metadata={},
    )


def _block(
    block_id: str,
    level: int,
    children: list[str],
    parent: str | None = None,
    filename: str = "",
    context: str = "",
    summary: str = "",
) -> SummaryBlock:
    return SummaryBlock(
        id=block_id,
        level=level,
        context=context or f"Context of {block_id}",
        summary=summary or f"Summary of {block_id}.",
        filename=filename or block_id.replace("block-", "block-slug-"),
        child_ids=children,
        parent_block_id=parent,
        metadata={},
    )


@pytest.fixture
def hierarchy_state() -> PipelineState:
    """3 chunks -> 1 L1 block -> 1 L2 root block."""
    state = PipelineState.create(document_id="doc-hier", source_text="x" * 300)
    state.chunks = {
        "chunk-001": _chunk(
            "chunk-001",
            span=(0, 100),
            parent="block-L1-001",
            filename="first-topic-overview",
            summary="Covers the first topic in detail.",
        ),
        "chunk-002": _chunk(
            "chunk-002",
            span=(100, 200),
            parent="block-L1-001",
            filename="second-topic-analysis",
            summary="Analyzes the second topic thoroughly.",
        ),
        "chunk-003": _chunk(
            "chunk-003",
            span=(200, 300),
            parent="block-L1-001",
            filename="third-topic-summary",
            summary="Summarizes the third topic findings.",
        ),
    }
    state.blocks = {
        "block-L1-001": _block(
            "block-L1-001",
            level=1,
            children=["chunk-001", "chunk-002", "chunk-003"],
            parent="block-L2-001",
            filename="level-one-group",
            context="Context of block-L1-001",
            summary="Groups first three topics together.",
        ),
        "block-L2-001": _block(
            "block-L2-001",
            level=2,
            children=["block-L1-001"],
            parent=None,
            filename="top-level-overview",
            context="Context of block-L2-001",
            summary="Top-level overview of all topics.",
        ),
    }
    return state


@pytest.fixture
def flat_state() -> PipelineState:
    """2 chunks, no blocks -- flat output."""
    state = PipelineState.create(document_id="doc-flat", source_text="y" * 200)
    state.chunks = {
        "chunk-001": _chunk(
            "chunk-001",
            span=(0, 100),
            filename="flat-topic-one",
            summary="First flat topic details.",
        ),
        "chunk-002": _chunk(
            "chunk-002",
            span=(100, 200),
            filename="flat-topic-two",
            summary="Second flat topic details.",
        ),
    }
    return state


@pytest.fixture
def mixed_state() -> PipelineState:
    """3 chunks in a block + 1 orphan chunk with no parent."""
    state = PipelineState.create(document_id="doc-mixed", source_text="m" * 400)
    state.chunks = {
        "chunk-001": _chunk(
            "chunk-001",
            span=(0, 100),
            parent="block-L1-001",
            filename="grouped-topic-one",
            summary="First grouped topic.",
        ),
        "chunk-002": _chunk(
            "chunk-002",
            span=(100, 200),
            parent="block-L1-001",
            filename="grouped-topic-two",
            summary="Second grouped topic.",
        ),
        "chunk-003": _chunk(
            "chunk-003",
            span=(200, 300),
            parent="block-L1-001",
            filename="grouped-topic-three",
            summary="Third grouped topic.",
        ),
        "chunk-004": _chunk(
            "chunk-004",
            span=(300, 400),
            filename="orphan-topic",
            summary="Ungrouped orphan topic.",
        ),
    }
    state.blocks = {
        "block-L1-001": _block(
            "block-L1-001",
            level=1,
            children=["chunk-001", "chunk-002", "chunk-003"],
            filename="mixed-group",
            context="Context of block-L1-001",
            summary="Groups three related topics.",
        ),
    }
    return state


@pytest.fixture
def multi_root_state() -> PipelineState:
    """4 chunks, 2 L1 blocks (both roots)."""
    state = PipelineState.create(document_id="doc-multi", source_text="z" * 400)
    state.chunks = {
        "chunk-001": _chunk(
            "chunk-001",
            span=(0, 100),
            parent="block-L1-001",
            filename="multi-topic-one",
            summary="First multi-root topic.",
        ),
        "chunk-002": _chunk(
            "chunk-002",
            span=(100, 200),
            parent="block-L1-001",
            filename="multi-topic-two",
            summary="Second multi-root topic.",
        ),
        "chunk-003": _chunk(
            "chunk-003",
            span=(200, 300),
            parent="block-L1-002",
            filename="multi-topic-three",
            summary="Third multi-root topic.",
        ),
        "chunk-004": _chunk(
            "chunk-004",
            span=(300, 400),
            parent="block-L1-002",
            filename="multi-topic-four",
            summary="Fourth multi-root topic.",
        ),
    }
    state.blocks = {
        "block-L1-001": _block(
            "block-L1-001",
            level=1,
            children=["chunk-001", "chunk-002"],
            filename="multi-group-alpha",
            context="Context of block-L1-001",
            summary="Alpha group of topics.",
        ),
        "block-L1-002": _block(
            "block-L1-002",
            level=1,
            children=["chunk-003", "chunk-004"],
            filename="multi-group-beta",
            context="Context of block-L1-002",
            summary="Beta group of topics.",
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
        assert chunk["context"] == "Context of chunk-001"
        assert chunk["summary"] == "Covers the first topic in detail."
        assert chunk["filename"] == "first-topic-overview"
        assert chunk["parent_block_id"] == "block-L1-001"
        assert chunk["forced_split"] is False

    def test_chunk_has_no_rewritten_text(self, hierarchy_state: PipelineState) -> None:
        result = JsonExporter().export(hierarchy_state)
        chunk = result["chunks"]["chunk-001"]
        assert "rewritten_text" not in chunk

    def test_block_fields(self, hierarchy_state: PipelineState) -> None:
        result = JsonExporter().export(hierarchy_state)
        block = result["blocks"]["block-L1-001"]
        assert block["id"] == "block-L1-001"
        assert block["level"] == 1
        assert block["context"] == "Context of block-L1-001"
        assert block["summary"] == "Groups first three topics together."
        assert block["filename"] == "level-one-group"
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
    def test_creates_content_dir(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        assert (tmp_path / "content").is_dir()

    def test_creates_level_dirs(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        assert (tmp_path / "content" / "L0").is_dir()
        assert (tmp_path / "content" / "L2").is_dir()
        assert (tmp_path / "content" / "L3").is_dir()

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
        chunk_files = list((tmp_path / "content" / "L0").glob("*.md"))
        assert len(chunk_files) == 3

    def test_one_file_per_block(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        l2_files = list((tmp_path / "content" / "L2").glob("*.md"))
        l3_files = list((tmp_path / "content" / "L3").glob("*.md"))
        assert len(l2_files) + len(l3_files) == 2

    def test_chunk_filename_uses_slug(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        assert (tmp_path / "content" / "L0" / "first-topic-overview.md").is_file()
        assert (tmp_path / "content" / "L0" / "second-topic-analysis.md").is_file()
        assert (tmp_path / "content" / "L0" / "third-topic-summary.md").is_file()

    def test_block_filename_uses_slug(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        assert (tmp_path / "content" / "L2" / "level-one-group.md").is_file()
        assert (tmp_path / "content" / "L3" / "top-level-overview.md").is_file()

    def test_no_id_based_filenames(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        for md_file in tmp_path.rglob("*.md"):
            name = md_file.name
            assert not name.startswith("chunk-0"), f"ID-based filename found: {name}"
            assert not name.startswith("block-L"), f"ID-based filename found: {name}"


# --- Filename deduplication ---


class TestFilenameDedup:
    def test_duplicate_filenames_get_suffix(self, tmp_path: Path) -> None:
        """Two chunks with same filename get deduplicated."""
        state = PipelineState.create(document_id="doc-dup", source_text="d" * 200)
        state.chunks = {
            "chunk-001": _chunk(
                "chunk-001",
                span=(0, 100),
                filename="same-topic",
                summary="First same-topic chunk.",
            ),
            "chunk-002": _chunk(
                "chunk-002",
                span=(100, 200),
                filename="same-topic",
                summary="Second same-topic chunk.",
            ),
        }
        MarkdownRenderer().render(state, tmp_path)
        chunk_files = sorted(f.name for f in (tmp_path / "content" / "L0").glob("*.md"))
        assert "same-topic.md" in chunk_files
        assert "same-topic-2.md" in chunk_files

    def test_triple_duplicate_filenames(self, tmp_path: Path) -> None:
        """Three nodes with same filename get -2 and -3 suffixes."""
        state = PipelineState.create(document_id="doc-dup3", source_text="t" * 300)
        state.chunks = {
            "chunk-001": _chunk(
                "chunk-001",
                span=(0, 100),
                filename="repeated",
                summary="First repeated.",
            ),
            "chunk-002": _chunk(
                "chunk-002",
                span=(100, 200),
                filename="repeated",
                summary="Second repeated.",
            ),
            "chunk-003": _chunk(
                "chunk-003",
                span=(200, 300),
                filename="repeated",
                summary="Third repeated.",
            ),
        }
        MarkdownRenderer().render(state, tmp_path)
        chunk_files = sorted(f.name for f in (tmp_path / "content" / "L0").glob("*.md"))
        assert "repeated.md" in chunk_files
        assert "repeated-2.md" in chunk_files
        assert "repeated-3.md" in chunk_files


# --- Chunk markdown content ---


class TestChunkMarkdown:
    def test_title(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "content" / "L0" / "first-topic-overview.md").read_text()
        assert content.startswith("# ")

    def test_parent_link_uses_filename(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "content" / "L0" / "first-topic-overview.md").read_text()
        assert (
            "[[content/L2/level-one-group|Groups first three topics together.]]"
            in content
        )

    def test_context_body(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "content" / "L0" / "first-topic-overview.md").read_text()
        assert "Context of chunk-001" in content

    def test_no_summary_section(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "content" / "L0" / "first-topic-overview.md").read_text()
        assert "## Summary" not in content

    def test_no_original_section(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "content" / "L0" / "first-topic-overview.md").read_text()
        assert "## Original" not in content

    def test_no_content_header(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "content" / "L0" / "first-topic-overview.md").read_text()
        assert "## Content" not in content


# --- Block markdown content ---


class TestBlockMarkdown:
    def test_title(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "content" / "L2" / "level-one-group.md").read_text()
        assert content.startswith("# ")

    def test_parent_link_uses_filename(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "content" / "L2" / "level-one-group.md").read_text()
        assert (
            "[[content/L3/top-level-overview|Top-level overview of all topics.]]"
            in content
        )

    def test_root_block_links_to_index(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "content" / "L3" / "top-level-overview.md").read_text()
        assert "**Parent:** [[index]]" in content

    def test_context_body(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "content" / "L2" / "level-one-group.md").read_text()
        assert "Context of block-L1-001" in content

    def test_no_summary_section(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "content" / "L2" / "level-one-group.md").read_text()
        assert "## Summary" not in content

    def test_children_links_use_filename_and_summary(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "content" / "L2" / "level-one-group.md").read_text()
        assert (
            "[[content/L0/first-topic-overview|Covers the first topic in detail.]]"
            in content
        )
        assert (
            "[[content/L0/second-topic-analysis|Analyzes the second topic thoroughly.]]"
            in content
        )
        assert (
            "[[content/L0/third-topic-summary|Summarizes the third topic findings.]]"
            in content
        )

    def test_block_children_link_to_blocks_with_summary(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "content" / "L3" / "top-level-overview.md").read_text()
        assert (
            "[[content/L2/level-one-group|Groups first three topics together.]]"
            in content
        )


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

    def test_source_reference(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "index.md").read_text()
        assert "**Source:** `doc-hier`" in content

    def test_links_to_root_blocks_with_summary(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        content = (tmp_path / "index.md").read_text()
        assert (
            "[[content/L3/top-level-overview|Top-level overview of all topics.]]"
            in content
        )

    def test_flat_index_links_to_chunks_with_summary(
        self,
        flat_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(flat_state, tmp_path)
        content = (tmp_path / "index.md").read_text()
        assert "[[content/L0/flat-topic-one|First flat topic details.]]" in content
        assert "[[content/L0/flat-topic-two|Second flat topic details.]]" in content

    def test_mixed_index_links_orphan_chunk_with_summary(
        self,
        mixed_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(mixed_state, tmp_path)
        content = (tmp_path / "index.md").read_text()
        assert "[[content/L0/orphan-topic|Ungrouped orphan topic.]]" in content

    def test_mixed_index_has_ungrouped_section(
        self,
        mixed_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(mixed_state, tmp_path)
        content = (tmp_path / "index.md").read_text()
        assert "## Ungrouped Chunks" in content

    def test_mixed_index_still_links_root_blocks_with_summary(
        self,
        mixed_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(mixed_state, tmp_path)
        content = (tmp_path / "index.md").read_text()
        assert "[[content/L2/mixed-group|Groups three related topics.]]" in content

    def test_multi_root_index_with_summary(
        self,
        multi_root_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(multi_root_state, tmp_path)
        content = (tmp_path / "index.md").read_text()
        assert "[[content/L2/multi-group-alpha|Alpha group of topics.]]" in content
        assert "[[content/L2/multi-group-beta|Beta group of topics.]]" in content


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

    def test_all_wiki_links_have_summary_labels(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        for md_file in tmp_path.rglob("*.md"):
            content = md_file.read_text()
            start = 0
            while True:
                open_pos = content.find("[[", start)
                if open_pos == -1:
                    break
                close_pos = content.find("]]", open_pos)
                assert close_pos != -1
                link_content = content[open_pos + 2 : close_pos]
                if link_content == "index":
                    start = close_pos + 2
                    continue
                assert "|" in link_content, (
                    f"Wiki-link without summary label: [[{link_content}]] in {md_file.name}"
                )
                start = close_pos + 2

    def test_no_id_based_link_paths(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        for md_file in tmp_path.rglob("*.md"):
            content = md_file.read_text()
            assert "chunks/chunk-0" not in content
            assert "blocks/block-L" not in content


# --- Flat output ---


class TestFlatOutput:
    def test_no_higher_level_content(
        self,
        flat_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(flat_state, tmp_path)
        l0 = tmp_path / "content" / "L0"
        assert l0.is_dir()
        assert len(list(l0.glob("*.md"))) == 2
        content_dirs = list((tmp_path / "content").iterdir())
        assert len(content_dirs) == 1

    def test_orphan_chunk_links_to_index(
        self,
        flat_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(flat_state, tmp_path)
        content = (tmp_path / "content" / "L0" / "flat-topic-one.md").read_text()
        assert "**Parent:** [[index]]" in content


# --- Full traversal ---


class TestFullTraversal:
    def _collect_links(self, content: str) -> list[str]:
        """Extract all [[path|label]] or [[path]] links, return paths."""
        links = []
        start = 0
        while True:
            open_pos = content.find("[[", start)
            if open_pos == -1:
                break
            close_pos = content.find("]]", open_pos)
            if close_pos == -1:
                break
            link_content = content[open_pos + 2 : close_pos]
            path = link_content.split("|")[0]
            links.append(path)
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

    def _node_path(self, node_id: str, state: PipelineState) -> str:
        if node_id in state.chunks:
            return f"content/L0/{state.chunks[node_id].filename}"
        block = state.blocks[node_id]
        return f"content/L{block.level + 1}/{block.filename}"

    def test_all_chunks_reachable_hierarchy(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        visited = self._traverse(tmp_path)
        for chunk in hierarchy_state.chunks.values():
            assert f"content/L0/{chunk.filename}" in visited

    def test_all_blocks_reachable_hierarchy(
        self,
        hierarchy_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(hierarchy_state, tmp_path)
        visited = self._traverse(tmp_path)
        for block in hierarchy_state.blocks.values():
            expected = f"content/L{block.level + 1}/{block.filename}"
            assert expected in visited

    def test_all_chunks_reachable_flat(
        self,
        flat_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(flat_state, tmp_path)
        visited = self._traverse(tmp_path)
        for chunk in flat_state.chunks.values():
            assert f"content/L0/{chunk.filename}" in visited

    def test_all_chunks_reachable_mixed(
        self,
        mixed_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(mixed_state, tmp_path)
        visited = self._traverse(tmp_path)
        for chunk in mixed_state.chunks.values():
            assert f"content/L0/{chunk.filename}" in visited

    def test_all_chunks_reachable_multi_root(
        self,
        multi_root_state: PipelineState,
        tmp_path: Path,
    ) -> None:
        MarkdownRenderer().render(multi_root_state, tmp_path)
        visited = self._traverse(tmp_path)
        for chunk in multi_root_state.chunks.values():
            assert f"content/L0/{chunk.filename}" in visited
