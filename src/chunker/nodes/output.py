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
        chunks_dir = output_dir / "chunks"
        blocks_dir = output_dir / "blocks"
        chunks_dir.mkdir(parents=True, exist_ok=True)
        blocks_dir.mkdir(parents=True, exist_ok=True)

        self._used_filenames: dict[str, int] = {}
        self._id_to_filename: dict[str, str] = {}

        for chunk in state.chunks.values():
            resolved = self._resolve_filename(chunk.filename)
            self._id_to_filename[chunk.id] = resolved

        for block in state.blocks.values():
            resolved = self._resolve_filename(block.filename)
            self._id_to_filename[block.id] = resolved

        for chunk in state.chunks.values():
            self._write_chunk(chunk, state, chunks_dir)

        for block in state.blocks.values():
            self._write_block(block, state, blocks_dir)

        self._write_index(state, output_dir)

    def _resolve_filename(self, slug: str) -> str:
        if slug not in self._used_filenames:
            self._used_filenames[slug] = 1
            return slug
        self._used_filenames[slug] += 1
        return f"{slug}-{self._used_filenames[slug]}"

    def _wiki_link(self, node_id: str, state: PipelineState) -> str:
        filename = self._id_to_filename[node_id]
        if node_id in state.blocks:
            path = f"blocks/{filename}"
            summary = state.blocks[node_id].summary
        else:
            path = f"chunks/{filename}"
            summary = state.chunks[node_id].summary
        return f"[[{path}|{summary}]]"

    def _write_chunk(
        self, chunk: Chunk, state: PipelineState, chunks_dir: Path
    ) -> None:
        filename = self._id_to_filename[chunk.id]
        lines = [f"# {filename}"]

        if chunk.parent_block_id:
            lines.append("")
            lines.append(f"**Parent:** {self._wiki_link(chunk.parent_block_id, state)}")

        lines.extend(["", chunk.context, ""])

        (chunks_dir / f"{filename}.md").write_text("\n".join(lines))

    def _write_block(
        self,
        block: SummaryBlock,
        state: PipelineState,
        blocks_dir: Path,
    ) -> None:
        filename = self._id_to_filename[block.id]
        lines = [f"# {filename}"]

        if block.parent_block_id:
            lines.append("")
            lines.append(f"**Parent:** {self._wiki_link(block.parent_block_id, state)}")

        lines.extend(["", block.context, ""])

        if block.child_ids:
            lines.append("## Children")
            for child_id in block.child_ids:
                lines.append(f"- {self._wiki_link(child_id, state)}")
            lines.append("")

        (blocks_dir / f"{filename}.md").write_text("\n".join(lines))

    def _write_index(self, state: PipelineState, output_dir: Path) -> None:
        root_block_ids = [
            bid for bid, block in state.blocks.items() if block.parent_block_id is None
        ]
        orphan_chunk_ids = [
            cid for cid, chunk in state.chunks.items() if chunk.parent_block_id is None
        ]

        lines = [f"# {state.document_id}", "", "## Top-Level Summaries"]

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
