"""Tests for retrieval query generation."""

from __future__ import annotations

import json
from pathlib import Path


from diagnose_tool.analyzer.classifier import ClassificationResult, ClassificationRule
from diagnose_tool.analyzer.header_parser import ParsedLogRecord, ParseStatus
from diagnose_tool.analyzer.output_context import OutputContext
from diagnose_tool.analyzer.retrieval_query import (
    generate_retrieval_query,
    _build_retrieval_query,
)


class TestRetrievalQuery:
    def test_query_contains_required_fields(self, tmp_path: Path):
        ctx = OutputContext(
            task_id="task-20260517-001",
            source_path="/data/logs",
            created_at="2026-05-17 10:00:00",
        )
        rule = ClassificationRule(
            category="null-pointer",
            display_name="NullPointer",
            severity="ERROR",
            keywords=["NullPointer"],
        )
        classifications = [
            ClassificationResult(
                category="null-pointer",
                display_name="NullPointer",
                severity="ERROR",
                matched_keyword="NullPointer",
                rule=rule,
            )
        ]
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
        generate_retrieval_query(ctx, classifications, records)
        content = (ctx.output_dir() / "retrieval-query.json").read_text(encoding="utf-8")
        query = json.loads(content)
        assert "task_id" in query
        assert "summary" in query
        assert "components" in query
        assert "fault_modes" in query
        assert "exception_classes" in query
        assert "keywords" in query
        assert "stack_symbols" in query
        assert "log_templates" in query

    def test_query_excludes_raw_logs(self, tmp_path: Path):
        ctx = OutputContext(
            task_id="task-20260517-001",
            source_path="/data/logs",
            created_at="2026-05-17 10:00:00",
        )
        rule = ClassificationRule(
            category="null-pointer",
            display_name="NullPointer",
            severity="ERROR",
            keywords=["NullPointer"],
        )
        classifications = [
            ClassificationResult(
                category="null-pointer",
                display_name="NullPointer",
                severity="ERROR",
                matched_keyword="NullPointer",
                rule=rule,
            )
        ]
        records = [
            ParsedLogRecord(
                timestamp="2026-05-17 10:01:01",
                level="ERROR",
                module="order-core",
                thread="worker-1",
                logger="com.demo.OrderService",
                message="NullPointer",
                raw="ERROR NullPointer at com.demo.Service.method(Service.java:123)",
                file_path="/data/logs/app.log",
                line_no=1,
                parse_status=ParseStatus.FULL,
            )
        ]
        generate_retrieval_query(ctx, classifications, records)
        content = (ctx.output_dir() / "retrieval-query.json").read_text(encoding="utf-8")
        query = json.loads(content)
        for val in query.values():
            if isinstance(val, str):
                assert "at com.demo.Service.method" not in val or val == query.get("summary", "")


class TestBuildRetrievalQuery:
    def test_keywords_from_rules(self):
        ctx = OutputContext(
            task_id="task-001",
            source_path="/data",
            created_at="2026-05-17 10:00:00",
        )
        rule = ClassificationRule(
            category="null-pointer",
            display_name="NullPointer",
            severity="ERROR",
            keywords=["NullPointer", "NPE"],
        )
        classifications = [
            ClassificationResult(
                category="null-pointer",
                display_name="NullPointer",
                severity="ERROR",
                matched_keyword="NullPointer",
                rule=rule,
            )
        ]
        query = _build_retrieval_query(ctx, classifications, [])
        assert "NullPointer" in query["keywords"]
        assert "NPE" in query["keywords"]
