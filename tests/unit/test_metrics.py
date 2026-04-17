from __future__ import annotations

import time

from chunker.metrics import Metrics, _fmt


class TestFmt:
    def test_seconds(self):
        assert _fmt(3.2) == "3.2s"

    def test_minutes(self):
        assert _fmt(125.5) == "2m05.5s"

    def test_hours(self):
        assert _fmt(3725.0) == "1h02m05.0s"


class TestMetrics:
    def test_track_records_duration(self):
        m = Metrics()
        with m.track("extraction", chunk_id="chunk-001"):
            time.sleep(0.01)
        assert len(m.extraction) == 1
        assert m.extraction[0].duration >= 0.01
        assert m.extraction[0].chunk_id == "chunk-001"

    def test_report_contains_sections(self):
        m = Metrics()
        with m.track("extraction", chunk_id="chunk-001"):
            pass
        with m.track("rewriting", chunk_id="chunk-001"):
            pass
        report = m.report(total_chunks=5, total_blocks=2)
        assert "Extraction" in report
        assert "Rewriting" in report
        assert "5 total" in report
        assert "2" in report  # blocks

    def test_report_with_resumed_chunks(self):
        m = Metrics()
        m.resumed_chunks = 3
        with m.track("extraction"):
            pass
        report = m.report(total_chunks=5, total_blocks=0)
        assert "3 resumed" in report
        assert "2 new" in report

    def test_report_no_steps_no_crash(self):
        m = Metrics()
        report = m.report(total_chunks=0, total_blocks=0)
        assert "Pipeline Metrics" in report
