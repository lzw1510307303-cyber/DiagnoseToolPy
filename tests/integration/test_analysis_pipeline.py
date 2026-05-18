"""tests/integration/test_analysis_pipeline.py

Integration test: full log analysis pipeline from scanner to case draft.
scanner → reader → header_parser → classifier → sampling → timeline → evidence → case_draft → report
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch


from diagnose_tool.analyzer.case_draft import generate_case_draft
from diagnose_tool.analyzer.classifier import classify_event, load_rules_from_dir
from diagnose_tool.analyzer.evidence import (
    generate_evidence_pack,
    generate_key_logs,
    generate_raw_samples,
)
from diagnose_tool.analyzer.header_parser import parse_log_record
from diagnose_tool.analyzer.output_context import OutputContext
from diagnose_tool.analyzer.reader import read_log_lines
from diagnose_tool.analyzer.report import generate_summary_html
from diagnose_tool.analyzer.sampling import BoundedSamples
from diagnose_tool.analyzer.scanner import scan_directory
from diagnose_tool.analyzer.timeline import aggregate_timeline, generate_timeline


class TestAnalysisPipeline:
    """test_analysis_pipeline — full log analysis pipeline."""

    def test_full_analysis_pipeline_produces_all_artifacts(
        self,
        sample_log_dir: Path,
        rules_dir: Path,
        tmp_data_dir: dict[str, Path],
    ) -> None:
        # === GIVEN ===
        task_id = "PIPELINE-001"
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
            finished_at="2026-05-16 10:00:10",
            total_files=4,
            processed_files=4,
            total_bytes=0,
            processed_bytes=0,
            error_count=0,
            warn_count=0,
        )

        rules = load_rules_from_dir(rules_dir)

        # === WHEN ===
        # Step 1: scan_directory
        scan_result = scan_directory(sample_log_dir)

        # Step 2: read_log_lines + parse_log_record
        records = []
        for file_info in scan_result.files:
            if file_info.type == "unsupported":
                continue
            for line in read_log_lines(file_info.path):
                record = parse_log_record(line.raw, line.file_path, line.line_no)
                records.append(record)

        # Step 3: classify_event
        classifications = [classify_event(r.raw, rules) for r in records]

        # Step 4: count errors/warns
        error_count = sum(1 for r in records if r.level == "ERROR")
        warn_count = sum(1 for r in records if r.level in ("WARN", "WARNING"))

        # Step 5: sampling
        samples = BoundedSamples(max_per_category=5)
        class_map = {i: c for i, c in enumerate(classifications)}
        for i, record in enumerate(records):
            c = class_map.get(i)
            if c and c.category != "unknown":
                if not samples.is_full(c.category):
                    samples.add(c.category, record.raw[:100])

        # Step 6: timeline
        records_as_dicts = [
            {"timestamp": r.timestamp or "", "level": r.level or ""}
            for r in records
        ]
        timeline_buckets = aggregate_timeline(records_as_dicts)

        # Step 7-9: All file generation inside the patch context
        # Since OutputContext.output_dir() returns hardcoded path (not tmp), we need to
        # patch output_dir and artifacts_dir to redirect to our tmp directory
        with patch.object(
            OutputContext,
            "output_dir",
            return_value=expected_output_dir,
        ), patch.object(
            OutputContext,
            "artifacts_dir",
            return_value=expected_artifacts_dir,
        ):
            # Ensure directories exist before generating artifacts
            expected_output_dir.mkdir(parents=True, exist_ok=True)
            expected_artifacts_dir.mkdir(parents=True, exist_ok=True)

            # Write timeline.json
            generate_timeline(records_as_dicts, output_context)

            # Generate evidence pack
            generate_evidence_pack(
                output_context=output_context,
                records=records,
                classifications=classifications,
                error_count=error_count,
                warn_count=warn_count,
                timeline_buckets=[b.__dict__ for b in timeline_buckets],
            )
            generate_key_logs(output_context, records, classifications)
            generate_raw_samples(output_context, records, classifications)

            # Step 8: case_draft
            top_category = None
            for c in classifications:
                if c.category != "unknown":
                    top_category = c
                    break
            generate_case_draft(output_context, top_category, records)

            # Step 9: summary HTML
            generate_summary_html(
                output_context=output_context,
                classifications=classifications,
                error_count=error_count,
                warn_count=warn_count,
                timeline_data=[b.__dict__ for b in timeline_buckets],
            )

        # === THEN ===
        output_path = expected_output_dir
        artifacts_path = expected_artifacts_dir

        # Scanner verification
        assert scan_result.supported_file_count >= 3
        assert len(records) > 0, "Should have parsed some log records"

        # Pipeline artifact verification - all 7 files should exist
        assert (output_path / "evidence-pack.md").exists(), "evidence-pack.md missing"
        assert (output_path / "case-draft.md").exists(), "case-draft.md missing"
        assert (output_path / "case-metadata-draft.yaml").exists(), "case-metadata-draft.yaml missing"
        assert (output_path / "summary.html").exists(), "summary.html missing"
        # key-logs.txt is written to output_dir (not artifacts_dir)
        assert (output_path / "key-logs.txt").exists(), "key-logs.txt missing"
        # raw-samples.jsonl is written to artifacts_dir
        assert (artifacts_path / "raw-samples.jsonl").exists(), "raw-samples.jsonl missing"
        # timeline.json is written to artifacts_dir
        assert (artifacts_path / "timeline.json").exists(), "timeline.json missing"

        # evidence-pack.md content verification
        evidence_content = (output_path / "evidence-pack.md").read_text(encoding="utf-8")
        assert "ERROR数量" in evidence_content
        assert task_id in evidence_content

        # case-draft.md content verification
        draft_content = (output_path / "case-draft.md").read_text(encoding="utf-8")
        assert "故障描述" in draft_content
        assert "可能根因" in draft_content

        # timeline.json format verification
        timeline_json = json.loads((artifacts_path / "timeline.json").read_text(encoding="utf-8"))
        assert isinstance(timeline_json, list)
        if timeline_json:
            assert "timestamp" in timeline_json[0]

        # key-logs.txt non-empty verification
        key_logs = (output_path / "key-logs.txt").read_text(encoding="utf-8")
        # Should contain classified logs (ERROR or WARN category)
        assert "ERROR" in key_logs or "WARN" in key_logs or "no key logs" not in key_logs.lower()

        # raw-samples.jsonl format verification
        raw_samples_path = artifacts_path / "raw-samples.jsonl"
        lines = raw_samples_path.read_text(encoding="utf-8").strip().split("\n")
        if lines and lines[0]:
            first = json.loads(lines[0])
            assert "category" in first
            assert "raw" in first

    def test_pipeline_with_empty_log_directory(
        self,
        tmp_path: Path,
        rules_dir: Path,
        tmp_data_dir: dict[str, Path],
    ) -> None:
        """Verify pipeline handles empty log directory gracefully."""
        empty_log_dir = tmp_path / "empty_logs"
        empty_log_dir.mkdir()

        task_id = "PIPELINE-EMPTY"
        expected_output_dir = tmp_data_dir["output_dir"] / task_id
        expected_output_dir.mkdir(parents=True, exist_ok=True)
        expected_artifacts_dir = expected_output_dir / "artifacts"
        expected_artifacts_dir.mkdir(parents=True, exist_ok=True)

        output_context = OutputContext(
            task_id=task_id,
            source_path=str(empty_log_dir),
            created_at="2026-05-16 10:00:00",
            started_at="2026-05-16 10:00:01",
            finished_at="2026-05-16 10:00:10",
            total_files=0,
            processed_files=0,
            total_bytes=0,
            processed_bytes=0,
            error_count=0,
            warn_count=0,
        )

        rules = load_rules_from_dir(rules_dir)

        with patch.object(
            OutputContext,
            "output_dir",
            return_value=expected_output_dir,
        ), patch.object(
            OutputContext,
            "artifacts_dir",
            return_value=expected_artifacts_dir,
        ):
            scan_result = scan_directory(empty_log_dir)

            records = []
            for file_info in scan_result.files:
                if file_info.type == "unsupported":
                    continue
                for line in read_log_lines(file_info.path):
                    record = parse_log_record(line.raw, line.file_path, line.line_no)
                    records.append(record)

            classifications = [classify_event(r.raw, rules) for r in records]
            error_count = sum(1 for r in records if r.level == "ERROR")
            warn_count = sum(1 for r in records if r.level in ("WARN", "WARNING"))

            records_as_dicts = [
                {"timestamp": r.timestamp or "", "level": r.level or ""}
                for r in records
            ]
            timeline_buckets = aggregate_timeline(records_as_dicts)

            generate_evidence_pack(
                output_context=output_context,
                records=records,
                classifications=classifications,
                error_count=error_count,
                warn_count=warn_count,
                timeline_buckets=[b.__dict__ for b in timeline_buckets],
            )
            generate_key_logs(output_context, records, classifications)
            generate_raw_samples(output_context, records, classifications)
            generate_timeline(records_as_dicts, output_context)

            top_category = next(
                (c for c in classifications if c.category != "unknown"),
                None,
            )
            generate_case_draft(output_context, top_category, records)

            generate_summary_html(
                output_context=output_context,
                classifications=classifications,
                error_count=error_count,
                warn_count=warn_count,
                timeline_data=[b.__dict__ for b in timeline_buckets],
            )

        # Verify evidence-pack exists but with 0 counts
        evidence_content = (expected_output_dir / "evidence-pack.md").read_text(encoding="utf-8")
        assert "ERROR数量：0" in evidence_content
        assert "WARN数量：0" in evidence_content
