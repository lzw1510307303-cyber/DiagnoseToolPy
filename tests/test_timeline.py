"""Tests for timeline generation."""

from __future__ import annotations

import json
from pathlib import Path


from diagnose_tool.analyzer.output_context import OutputContext
from diagnose_tool.analyzer.timeline import (
    TimelineBucket,
    aggregate_timeline,
    generate_timeline,
    write_timeline_json,
)


class TestAggregateTimeline:
    def test_empty_input_returns_empty_list(self):
        assert aggregate_timeline([]) == []

    def test_error_and_warn_counts(self):
        records = [
            {"timestamp": "2026-05-17 10:01:01", "level": "ERROR"},
            {"timestamp": "2026-05-17 10:01:02", "level": "WARN"},
            {"timestamp": "2026-05-17 10:01:03", "level": "ERROR"},
        ]
        buckets = aggregate_timeline(records)
        assert len(buckets) == 1
        assert buckets[0].error_count == 2
        assert buckets[0].warn_count == 1

    def test_multiple_buckets(self):
        records = [
            {"timestamp": "2026-05-17 10:01:01", "level": "ERROR"},
            {"timestamp": "2026-05-17 10:02:01", "level": "ERROR"},
        ]
        buckets = aggregate_timeline(records)
        assert len(buckets) == 2

    def test_unknown_level_not_counted(self):
        records = [
            {"timestamp": "2026-05-17 10:01:01", "level": "DEBUG"},
            {"timestamp": "2026-05-17 10:01:02", "level": "INFO"},
        ]
        buckets = aggregate_timeline(records)
        assert buckets[0].error_count == 0
        assert buckets[0].warn_count == 0

    def test_missing_timestamp_skipped(self):
        records = [
            {"timestamp": "2026-05-17 10:01:01", "level": "ERROR"},
            {"level": "ERROR"},
        ]
        buckets = aggregate_timeline(records)
        assert len(buckets) == 1


class TestWriteTimelineJson:
    def test_writes_valid_json(self, tmp_path: Path):
        buckets = [
            TimelineBucket(timestamp="2026-05-17T10:01:00", error_count=3, warn_count=5),
        ]
        path = tmp_path / "timeline.json"
        write_timeline_json(buckets, path)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data) == 1
        assert data[0]["timestamp"] == "2026-05-17T10:01:00"
        assert data[0]["error_count"] == 3
        assert data[0]["warn_count"] == 5


class TestGenerateTimeline:
    def test_generates_and_writes(self, tmp_path: Path):
        ctx = OutputContext(
            task_id="test-task",
            source_path="/data",
            created_at="2026-05-17 10:00:00",
        )
        records = [
            {"timestamp": "2026-05-17 10:01:01", "level": "ERROR"},
            {"timestamp": "2026-05-17 10:01:02", "level": "WARN"},
        ]
        buckets = generate_timeline(records, ctx)
        assert len(buckets) == 1
        timeline_path = ctx.artifacts_dir() / "timeline.json"
        assert timeline_path.exists()
        data = json.loads(timeline_path.read_text(encoding="utf-8"))
        assert len(data) == 1
