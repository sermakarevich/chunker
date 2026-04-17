from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class StepRecord:
    duration: float
    chunk_id: str | None = None
    block_id: str | None = None


@dataclass
class Metrics:
    wall_start: float = field(default_factory=time.monotonic)
    extraction: list[StepRecord] = field(default_factory=list)
    rewriting: list[StepRecord] = field(default_factory=list)
    aggregation: list[StepRecord] = field(default_factory=list)
    checkpointing: list[StepRecord] = field(default_factory=list)
    output: list[StepRecord] = field(default_factory=list)
    resumed_chunks: int = 0

    @contextmanager
    def track(self, step: str, *, chunk_id: str | None = None, block_id: str | None = None):
        t0 = time.monotonic()
        yield
        record = StepRecord(
            duration=time.monotonic() - t0,
            chunk_id=chunk_id,
            block_id=block_id,
        )
        getattr(self, step).append(record)

    def report(self, total_chunks: int, total_blocks: int) -> str:
        wall = time.monotonic() - self.wall_start

        lines = [
            "",
            "=" * 60,
            "  Pipeline Metrics",
            "=" * 60,
        ]

        new_chunks = total_chunks - self.resumed_chunks
        lines.append(f"  Chunks: {total_chunks} total ({self.resumed_chunks} resumed, {new_chunks} new)")
        lines.append(f"  Blocks: {total_blocks}")
        lines.append(f"  Wall time: {_fmt(wall)}")
        lines.append("-" * 60)

        for label, records in [
            ("Extraction", self.extraction),
            ("Rewriting", self.rewriting),
            ("Aggregation", self.aggregation),
            ("Checkpointing", self.checkpointing),
            ("Output", self.output),
        ]:
            if not records:
                continue
            total = sum(r.duration for r in records)
            avg = total / len(records)
            fastest = min(r.duration for r in records)
            slowest = max(r.duration for r in records)
            pct = (total / wall * 100) if wall > 0 else 0
            lines.append(
                f"  {label:<15s}  {_fmt(total):>9s} total  "
                f"({len(records):>3d} calls, "
                f"avg {_fmt(avg)}, "
                f"min {_fmt(fastest)}, "
                f"max {_fmt(slowest)})  "
                f"{pct:5.1f}%"
            )

        accounted = sum(
            sum(r.duration for r in records)
            for records in [
                self.extraction,
                self.rewriting,
                self.aggregation,
                self.checkpointing,
                self.output,
            ]
        )
        overhead = wall - accounted
        if wall > 0:
            lines.append(f"  {'Overhead':<15s}  {_fmt(overhead):>9s} total  {overhead / wall * 100:34.1f}%")

        if new_chunks > 0 and wall > 0:
            per_chunk = wall / new_chunks
            lines.append("-" * 60)
            lines.append(f"  Throughput: {per_chunk:.1f}s per chunk, {new_chunks / wall * 60:.1f} chunks/min")

        lines.append("=" * 60)
        return "\n".join(lines)


def _fmt(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    m, s = divmod(seconds, 60)
    if m < 60:
        return f"{int(m)}m{s:04.1f}s"
    h, m = divmod(m, 60)
    return f"{int(h)}h{int(m):02d}m{s:04.1f}s"
