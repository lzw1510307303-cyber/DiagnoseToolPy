"""Tests for case draft generation."""

from __future__ import annotations

import yaml
from pathlib import Path


from diagnose_tool.analyzer.case_draft import (
    _derive_title,
    generate_case_draft,
)
from diagnose_tool.analyzer.classifier import ClassificationResult, ClassificationRule
from diagnose_tool.analyzer.header_parser import ParsedLogRecord, ParseStatus
from diagnose_tool.analyzer.output_context import OutputContext


class TestCaseDraft:
    def test_case_draft_contains_required_sections(self, tmp_path: Path):
        ctx = OutputContext(
            task_id="task-20260517-001",
            source_path="/data/logs",
            created_at="2026-05-17 10:00:00",
            error_count=5,
            warn_count=10,
        )
        rule = ClassificationRule(
            category="null-pointer",
            display_name="NullPointer",
            severity="ERROR",
            keywords=["NullPointer"],
        )
        top_category = ClassificationResult(
            category="null-pointer",
            display_name="NullPointer",
            severity="ERROR",
            matched_keyword="NullPointer",
            rule=rule,
        )
        records = [
            ParsedLogRecord(
                timestamp="2026-05-17 10:01:01",
                level="ERROR",
                module="order-core",
                thread="worker-1",
                logger="com.demo.OrderService",
                message="NullPointer",
                raw="ERROR NullPointer",
                file_path="/data/logs/app.log",
                line_no=1,
                parse_status=ParseStatus.FULL,
            )
        ]
        generate_case_draft(ctx, top_category, records)
        content = (ctx.output_dir() / "case-draft.md").read_text(encoding="utf-8")
        assert "## 基本信息" in content
        assert "## 故障描述" in content
        assert "## 可能根因" in content
        assert "task-20260517-001" in content

    def test_title_derived_from_top_category(self):
        rule = ClassificationRule(
            category="null-pointer",
            display_name="NullPointer",
            severity="ERROR",
            keywords=["NullPointer"],
        )
        top_category = ClassificationResult(
            category="null-pointer",
            display_name="NullPointer",
            severity="ERROR",
            matched_keyword="NullPointer",
            rule=rule,
        )
        title = _derive_title(top_category)
        assert "NullPointer" in title

    def test_title_unknown_when_no_category(self):
        title = _derive_title(None)
        assert "未知" in title or "unknown" in title.lower()


class TestCaseMetadata:
    def test_metadata_yaml_has_required_fields(self, tmp_path: Path):
        ctx = OutputContext(
            task_id="task-20260517-001",
            source_path="/data/logs",
            created_at="2026-05-17 10:00:00",
            error_count=5,
            warn_count=10,
        )
        rule = ClassificationRule(
            category="null-pointer",
            display_name="NullPointer",
            severity="ERROR",
            keywords=["NullPointer"],
        )
        top_category = ClassificationResult(
            category="null-pointer",
            display_name="NullPointer",
            severity="ERROR",
            matched_keyword="NullPointer",
            rule=rule,
        )
        records = [
            ParsedLogRecord(
                timestamp="2026-05-17 10:01:01",
                level="ERROR",
                module="order-core",
                thread="worker-1",
                logger="com.demo.OrderService",
                message="NullPointer",
                raw="ERROR NullPointer",
                file_path="/data/logs/app.log",
                line_no=1,
                parse_status=ParseStatus.FULL,
            )
        ]
        generate_case_draft(ctx, top_category, records)
        content = (ctx.output_dir() / "case-metadata-draft.yaml").read_text(encoding="utf-8")
        metadata = yaml.safe_load(content)
        assert "CASE" in metadata["case_id"]
        assert metadata["source_type"] == "auto"
        assert metadata["status"] == "draft"
        assert metadata["confidence"] == "unconfirmed"
        assert "slug" in metadata
        assert isinstance(metadata["tags"], list)
        assert isinstance(metadata["components"], list)
        assert isinstance(metadata["fault_modes"], list)
        assert isinstance(metadata["exception_classes"], list)
        assert isinstance(metadata["key_phrases"], list)
