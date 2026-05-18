"""tests/integration/test_scan_pipeline.py

Integration test: scanner → evidence → report full pipeline.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch


from diagnose_tool.analyzer.classifier import classify_event, load_rules_from_dir
from diagnose_tool.analyzer.evidence import generate_evidence_pack
from diagnose_tool.analyzer.header_parser import parse_log_record
from diagnose_tool.analyzer.output_context import OutputContext
from diagnose_tool.analyzer.reader import read_log_lines
from diagnose_tool.analyzer.report import generate_summary_html
from diagnose_tool.analyzer.scanner import scan_directory
from diagnose_tool.analyzer.timeline import aggregate_timeline


class TestScanPipeline:
    """test_scan_pipeline — scan → evidence → HTML report pipeline."""

    def test_full_pipeline_produces_evidence_and_html(
        self,
        sample_log_dir: Path,
        rules_dir: Path,
        tmp_data_dir: dict[str, Path],
    ) -> None:
        # === GIVEN ===
        task_id = "SCAN-001"
        source_path = str(sample_log_dir)
        expected_output_dir = tmp_data_dir["output_dir"] / task_id
        expected_output_dir.mkdir(parents=True, exist_ok=True)
        expected_artifacts_dir = expected_output_dir / "artifacts"
        expected_artifacts_dir.mkdir(parents=True, exist_ok=True)

        output_context = OutputContext(
            task_id=task_id,
            source_path=source_path,
            created_at="2026-05-16 10:00:00",
            started_at="2026-05-16 10:00:01",
            finished_at="2026-05-16 10:00:05",
            total_files=4,
            processed_files=4,
            total_bytes=0,
            processed_bytes=0,
            error_count=0,
            warn_count=0,
        )

        rules = load_rules_from_dir(rules_dir)

        # === WHEN ===
        # Step 1: scan directory
        scan_result = scan_directory(sample_log_dir)

        # Step 2: collect records and classifications
        records = []
        classifications = []
        error_count = 0
        warn_count = 0

        for file_info in scan_result.files:
            if file_info.type == "unsupported":
                continue
            for line in read_log_lines(file_info.path):
                record = parse_log_record(line.raw, line.file_path, line.line_no)
                records.append(record)
                classification = classify_event(record.raw, rules)
                classifications.append(classification)
                if classification.category != "unknown":
                    if record.level == "ERROR":
                        error_count += 1
                    elif record.level in ("WARN", "WARNING"):
                        warn_count += 1

        # Step 3: generate timeline buckets
        records_as_dicts = [
            {"timestamp": r.timestamp or "", "level": r.level or ""}
            for r in records
        ]
        timeline_buckets = aggregate_timeline(records_as_dicts)

        # Step 4-5: generate evidence pack and HTML report with patched output_dir
        with patch.object(
            OutputContext,
            "output_dir",
            return_value=expected_output_dir,
        ), patch.object(
            OutputContext,
            "artifacts_dir",
            return_value=expected_artifacts_dir,
        ):
            generate_evidence_pack(
                output_context=output_context,
                records=records,
                classifications=classifications,
                error_count=error_count,
                warn_count=warn_count,
                timeline_buckets=[b.__dict__ for b in timeline_buckets],
            )

            generate_summary_html(
                output_context=output_context,
                classifications=classifications,
                error_count=error_count,
                warn_count=warn_count,
                timeline_data=[b.__dict__ for b in timeline_buckets],
            )

        # === THEN ===

        # Verify scanner output
        assert scan_result.supported_file_count == 3  # .log, .out, .gz (not .md)
        assert scan_result.unsupported_file_count == 1  # readme.md

        # Verify evidence-pack.md exists
        evidence_pack_path = expected_output_dir / "evidence-pack.md"
        assert evidence_pack_path.exists(), f"Expected {evidence_pack_path} to exist"
        content = evidence_pack_path.read_text(encoding="utf-8")
        assert "日志诊断证据包" in content
        assert "ERROR数量" in content

        # Verify summary.html exists
        html_path = expected_output_dir / "summary.html"
        assert html_path.exists(), f"Expected {html_path} to exist"
        html_content = html_path.read_text(encoding="utf-8")
        assert "html" in html_content.lower()

        # Verify artifacts/ subdirectory exists
        assert expected_artifacts_dir.exists()
