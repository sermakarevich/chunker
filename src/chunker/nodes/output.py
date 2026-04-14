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
                "rewritten_text": chunk.rewritten_text,
                "summary": chunk.summary,
                "parent_block_id": chunk.parent_block_id,
                "forced_split": chunk.forced_split,
            }

        blocks = {}
        for block_id, block in state.blocks.items():
            blocks[block_id] = {
                "id": block.id,
                "level": block.level,
                "summary": block.summary,
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


def _child_link(child_id: str, blocks: dict[str, SummaryBlock]) -> str:
    if child_id in blocks:
        return f"blocks/{child_id}"
    return f"chunks/{child_id}"


class MarkdownRenderer:
    def render(self, state: PipelineState, output_dir: Path) -> None:
        chunks_dir = output_dir / "chunks"
        blocks_dir = output_dir / "blocks"
        chunks_dir.mkdir(parents=True, exist_ok=True)
        blocks_dir.mkdir(parents=True, exist_ok=True)

        for chunk in state.chunks.values():
            self._write_chunk(chunk, chunks_dir)

        for block in state.blocks.values():
            self._write_block(block, state, blocks_dir)

        self._write_index(state, output_dir)

    def _write_chunk(self, chunk: Chunk, chunks_dir: Path) -> None:
        number = chunk.id.split("-")[-1]
        lines = [f"# Chunk {number}"]

        if chunk.parent_block_id:
            lines.append("")
            lines.append(f"**Parent:** [[blocks/{chunk.parent_block_id}]]")

        lines.extend(
            [
                "",
                "## Summary",
                chunk.summary,
                "",
                "## Content",
                chunk.rewritten_text,
                "",
                "## Original",
                chunk.original_text,
                "",
            ]
        )

        (chunks_dir / f"{chunk.id}.md").write_text("\n".join(lines))

    def _write_block(
        self,
        block: SummaryBlock,
        state: PipelineState,
        blocks_dir: Path,
    ) -> None:
        label = block.id.replace("block-", "")
        lines = [f"# Summary Block {label}"]

        if block.parent_block_id:
            lines.append("")
            lines.append(f"**Parent:** [[blocks/{block.parent_block_id}]]")

        lines.extend(
            [
                "",
                "## Summary",
                block.summary,
                "",
                "## Children",
            ]
        )

        for child_id in block.child_ids:
            link = _child_link(child_id, state.blocks)
            lines.append(f"- [[{link}]]")

        lines.append("")
        (blocks_dir / f"{block.id}.md").write_text("\n".join(lines))

    def _write_index(self, state: PipelineState, output_dir: Path) -> None:
        root_block_ids = [
            bid for bid, block in state.blocks.items() if block.parent_block_id is None
        ]

        lines = [f"# {state.document_id}", "", "## Top-Level Summaries"]

        if root_block_ids:
            for bid in root_block_ids:
                lines.append(f"- [[blocks/{bid}]]")
        else:
            for cid in state.chunks:
                lines.append(f"- [[chunks/{cid}]]")

        lines.append("")
        (output_dir / "index.md").write_text("\n".join(lines))
