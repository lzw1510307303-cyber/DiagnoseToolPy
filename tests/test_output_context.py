"""Tests for output context."""

from __future__ import annotations

from pathlib import Path

from diagnose_tool.analyzer.output_context import OutputContext


class TestOutputContext:
    def test_context_fields_accessible(self):
        ctx = OutputContext(
            task_id="task-001",
            source_path="/data/logs",
            created_at="2026-05-17 10:00:00",
            started_at="2026-05-17 10:00:01",
            finished_at="2026-05-17 10:05:00",
            total_files=10,
            processed_files=10,
            total_bytes=1024,
            processed_bytes=1024,
            error_count=5,
            warn_count=20,
        )
        assert ctx.task_id == "task-001"
        assert ctx.source_path == "/data/logs"
        assert ctx.error_count == 5
        assert ctx.warn_count == 20
        assert ctx.total_files == 10

    def test_output_dir_path(self):
        ctx = OutputContext(
            task_id="task-20260517-001",
            source_path="/data/input",
            created_at="2026-05-17 10:00:00",
        )
        assert ctx.output_dir() == Path("data/output/task-20260517-001")

    def test_artifacts_dir_path(self):
        ctx = OutputContext(
            task_id="task-20260517-001",
            source_path="/data/input",
            created_at="2026-05-17 10:00:00",
        )
        assert ctx.artifacts_dir() == Path("data/output/task-20260517-001/artifacts")

    def test_ensure_directories_creates_dirs(self, tmp_path: Path):
        ctx = OutputContext(
            task_id="task-test-001",
            source_path="/data/input",
            created_at="2026-05-17 10:00:00",
        )
        ctx.ensure_directories()
        assert ctx.output_dir().exists()
        assert ctx.artifacts_dir().exists()
