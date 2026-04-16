from __future__ import annotations

import json
from pathlib import Path

from chunker.models import Chunk, SummaryBlock
from chunker.state import PipelineState


class JsonExporter:
    def export(self, state: PipelineState) -> dict:
        root_block_ids = [
            bid for bid, block in state.blocks.items() if block.parent_block_id is None
        ]

        chunks = {}
        for chunk_id, chunk in state.chunks.items():
            chunks[chunk_id] = {
                "id": chunk.id,
                "source_span": list(chunk.source_span),
                "original_text": chunk.original_text,
                "context": chunk.context,
                "summary": chunk.summary,
                "filename": chunk.filename,
                "parent_block_id": chunk.parent_block_id,
                "forced_split": chunk.forced_split,
            }

        blocks = {}
        for block_id, block in state.blocks.items():
            blocks[block_id] = {
                "id": block.id,
                "level": block.level,
                "context": block.context,
                "summary": block.summary,
                "filename": block.filename,
                "child_ids": block.child_ids,
                "parent_block_id": block.parent_block_id,
            }

        return {
            "document_id": state.document_id,
            "root_block_ids": root_block_ids,
            "blocks": blocks,
            "chunks": chunks,
        }

    def write(self, state: PipelineState, path: Path) -> None:
        data = self.export(state)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))


class MarkdownRenderer:
    def render(self, state: PipelineState, output_dir: Path) -> None:
        self._used_filenames: dict[str, int] = {}
        self._id_to_filename: dict[str, str] = {}
        self._id_to_level: dict[str, int] = {}

        for chunk in state.chunks.values():
            resolved = self._resolve_filename(chunk.filename)
            self._id_to_filename[chunk.id] = resolved
            self._id_to_level[chunk.id] = 0

        for block in state.blocks.values():
            resolved = self._resolve_filename(block.filename)
            self._id_to_filename[block.id] = resolved
            self._id_to_level[block.id] = block.level + 1

        levels_used: set[int] = set(self._id_to_level.values())
        content_dir = output_dir / "content"
        for level in levels_used:
            (content_dir / f"L{level}").mkdir(parents=True, exist_ok=True)

        for chunk in state.chunks.values():
            self._write_chunk(chunk, state, content_dir)

        for block in state.blocks.values():
            self._write_block(block, state, content_dir)

        self._write_index(state, output_dir)

    @staticmethod
    def _sanitize_slug(slug: str) -> str:
        sanitized = slug.replace("/", "-").replace("\\", "-").replace("\x00", "")
        sanitized = sanitized.strip(". ")
        return sanitized or "untitled"

    def _resolve_filename(self, slug: str) -> str:
        slug = self._sanitize_slug(slug)
        if slug not in self._used_filenames:
            self._used_filenames[slug] = 1
            return slug
        self._used_filenames[slug] += 1
        return f"{slug}-{self._used_filenames[slug]}"

    def _node_path(self, node_id: str) -> str:
        level = self._id_to_level[node_id]
        filename = self._id_to_filename[node_id]
        return f"content/L{level}/{filename}"

    def _wiki_link(self, node_id: str, state: PipelineState) -> str:
        path = self._node_path(node_id)
        filename = self._id_to_filename[node_id]
        if node_id in state.blocks:
            summary = state.blocks[node_id].summary
        else:
            summary = state.chunks[node_id].summary
        return f"[[{path}|{filename}]] — {summary}"

    def _write_chunk(
        self, chunk: Chunk, state: PipelineState, content_dir: Path
    ) -> None:
        filename = self._id_to_filename[chunk.id]
        level = self._id_to_level[chunk.id]
        lines = [f"# {filename}"]

        if chunk.parent_block_id:
            lines.append("")
            lines.append(f"**Parent:** {self._wiki_link(chunk.parent_block_id, state)}")
        else:
            lines.append("")
            lines.append("**Parent:** [[index]]")

        lines.extend(["", chunk.context, ""])

        (content_dir / f"L{level}" / f"{filename}.md").write_text("\n".join(lines))

    def _write_block(
        self,
        block: SummaryBlock,
        state: PipelineState,
        content_dir: Path,
    ) -> None:
        filename = self._id_to_filename[block.id]
        level = self._id_to_level[block.id]
        lines = [f"# {filename}"]

        if block.parent_block_id:
            lines.append("")
            lines.append(f"**Parent:** {self._wiki_link(block.parent_block_id, state)}")
        else:
            lines.append("")
            lines.append("**Parent:** [[index]]")

        lines.extend(["", block.context, ""])

        if block.child_ids:
            lines.append("## Children")
            for child_id in block.child_ids:
                lines.append(f"- {self._wiki_link(child_id, state)}")
            lines.append("")

        (content_dir / f"L{level}" / f"{filename}.md").write_text("\n".join(lines))

    def _write_index(self, state: PipelineState, output_dir: Path) -> None:
        root_block_ids = [
            bid for bid, block in state.blocks.items() if block.parent_block_id is None
        ]
        orphan_chunk_ids = [
            cid for cid, chunk in state.chunks.items() if chunk.parent_block_id is None
        ]

        lines = [f"# {state.document_id}", ""]
        lines.append(f"**Source:** `{state.document_id}`")
        lines.extend(["", "## Top-Level Summaries"])

        if root_block_ids:
            for bid in root_block_ids:
                lines.append(f"- {self._wiki_link(bid, state)}")
        else:
            for cid in orphan_chunk_ids:
                lines.append(f"- {self._wiki_link(cid, state)}")

        if root_block_ids and orphan_chunk_ids:
            lines.extend(["", "## Ungrouped Chunks"])
            for cid in orphan_chunk_ids:
                lines.append(f"- {self._wiki_link(cid, state)}")

        lines.append("")
        (output_dir / "index.md").write_text("\n".join(lines))
