"""Tests for HTML report generation."""

from __future__ import annotations

from pathlib import Path


from diagnose_tool.analyzer.classifier import ClassificationResult, ClassificationRule
from diagnose_tool.analyzer.output_context import OutputContext
from diagnose_tool.analyzer.report import (
    generate_summary_html,
    _build_stats,
    _build_top_exceptions,
)


class TestGenerateSummaryHtml:
    def test_html_contains_required_sections(self, tmp_path: Path):
        ctx = OutputContext(
            task_id="test-task",
            source_path="/data/logs",
            created_at="2026-05-17 10:00:00",
            error_count=5,
            warn_count=10,
        )
        rule = ClassificationRule(
            category="null-pointer",
            display_name="NullPointer",
            severity="ERROR",
            keywords=["NPE"],
        )
        classifications = [
            ClassificationResult(
                category="null-pointer",
                display_name="NullPointer",
                severity="ERROR",
                matched_keyword="NPE",
                rule=rule,
            )
        ]
        generate_summary_html(ctx, classifications, 5, 10, [])
        content = (ctx.output_dir() / "summary.html").read_text(encoding="utf-8")
        assert "日志诊断报告" in content
        assert "test-task" in content
        assert "ERROR数量" in content
        assert "WARN数量" in content

    def test_html_contains_classification_stats(self, tmp_path: Path):
        ctx = OutputContext(
            task_id="test-task",
            source_path="/data/logs",
            created_at="2026-05-17 10:00:00",
            error_count=3,
            warn_count=10,
        )
        rule = ClassificationRule(
            category="null-pointer",
            display_name="NullPointer",
            severity="ERROR",
            keywords=["NPE"],
        )
        classifications = [
            ClassificationResult(
                category="null-pointer",
                display_name="NullPointer",
                severity="ERROR",
                matched_keyword="NPE",
                rule=rule,
            )
        ]
        generate_summary_html(ctx, classifications, 3, 10, [])
        content = (ctx.output_dir() / "summary.html").read_text(encoding="utf-8")
        assert "null-pointer" in content


class TestBuildStats:
    def test_counts_by_category(self):
        rule = ClassificationRule(
            category="error",
            display_name="Error",
            severity="ERROR",
            keywords=["ERR"],
        )
        classifications = [
            ClassificationResult(
                category="error",
                display_name="Error",
                severity="ERROR",
                matched_keyword="ERR",
                rule=rule,
            )
            for _ in range(3)
        ]
        stats = _build_stats(classifications)
        assert stats["error"] == 3

    def test_ignores_unknown(self):
        from diagnose_tool.analyzer.classifier import UNKNOWN_RESULT
        stats = _build_stats([UNKNOWN_RESULT])
        assert stats == {}


class TestBuildTopExceptions:
    def test_returns_top_n(self):
        rule = ClassificationRule(
            category="error",
            display_name="Error",
            severity="ERROR",
            keywords=["ERR"],
        )
        classifications = [
            ClassificationResult(
                category="error",
                display_name="Error",
                severity="ERROR",
                matched_keyword="ERR",
                rule=rule,
            )
            for _ in range(3)
        ]
        top = _build_top_exceptions(classifications)
        assert len(top) <= 5
        assert top[0] == ("Error", 3)
