"""Tests for case writer."""

from __future__ import annotations

import yaml
from pathlib import Path

import pytest

from diagnose_tool.casebase.case_models import (
    CaseConfidence,
    CaseSourceType,
    CaseStatus,
    FaultCaseMetadata,
)
from diagnose_tool.casebase.case_writer import (
    CaseExistsError,
    MissingTaskArtifactError,
    archive_case_from_task,
)


class TestArchiveCaseFromTask:
    def test_archive_creates_directory(self, tmp_path: Path):
        task_output = tmp_path / "task_output"
        task_output.mkdir()

        (task_output / "evidence-pack.md").write_text("# Evidence\n", encoding="utf-8")
        (task_output / "key-logs.txt").write_text("ERROR sample\n", encoding="utf-8")
        (task_output / "case-draft.md").write_text("# Case Draft\n", encoding="utf-8")

        metadata = FaultCaseMetadata(
            case_id="CASE-001",
            title="Test Case",
            slug="test-case",
            source_type=CaseSourceType.AUTO,
            status=CaseStatus.ARCHIVED,
            confidence=CaseConfidence.CONFIRMED,
        )

        cases_dir = tmp_path / "cases"
        result = archive_case_from_task(task_output, metadata, cases_dir=cases_dir)

        assert result.exists()
        assert result.is_dir()
        assert result.name == "CASE-001_test-case"

    def test_metadata_written(self, tmp_path: Path):
        task_output = tmp_path / "task_output"
        task_output.mkdir()

        (task_output / "evidence-pack.md").write_text("# Evidence\n", encoding="utf-8")
        (task_output / "key-logs.txt").write_text("ERROR sample\n", encoding="utf-8")

        metadata = FaultCaseMetadata(
            case_id="CASE-002",
            title="Redis故障",
            slug="redis-fault",
            source_type=CaseSourceType.AUTO,
            status=CaseStatus.ARCHIVED,
            confidence=CaseConfidence.CONFIRMED,
            tags=["redis"],
            components=["order-core"],
            fault_modes=["connection-error"],
        )

        cases_dir = tmp_path / "cases"
        case_dir = archive_case_from_task(task_output, metadata, cases_dir=cases_dir)

        metadata_path = case_dir / "metadata.yaml"
        assert metadata_path.exists()

        with metadata_path.open("r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f)

        assert loaded["case_id"] == "CASE-002"
        assert loaded["title"] == "Redis故障"
        assert loaded["slug"] == "redis-fault"
        assert loaded["source_type"] == "auto"
        assert loaded["status"] == "archived"
        assert loaded["confidence"] == "confirmed"
        assert loaded["tags"] == ["redis"]
        assert loaded["components"] == ["order-core"]

    def test_evidence_copied(self, tmp_path: Path):
        task_output = tmp_path / "task_output"
        task_output.mkdir()

        evidence_content = "# Evidence Pack\nERROR: Redis connection failed"
        key_logs_content = "ERROR: Redis connection timeout\nWARN: Retrying"

        (task_output / "evidence-pack.md").write_text(evidence_content, encoding="utf-8")
        (task_output / "key-logs.txt").write_text(key_logs_content, encoding="utf-8")

        metadata = FaultCaseMetadata(
            case_id="CASE-003",
            title="Test",
            slug="test",
            source_type=CaseSourceType.AUTO,
            status=CaseStatus.ARCHIVED,
            confidence=CaseConfidence.CONFIRMED,
        )

        cases_dir = tmp_path / "cases"
        case_dir = archive_case_from_task(task_output, metadata, cases_dir=cases_dir)

        evidence_dst = case_dir / "evidence-pack.md"
        key_logs_dst = case_dir / "key-logs.txt"

        assert evidence_dst.exists()
        assert key_logs_dst.exists()
        assert evidence_dst.read_text(encoding="utf-8") == evidence_content
        assert key_logs_dst.read_text(encoding="utf-8") == key_logs_content

    def test_case_draft_copied_as_case_md(self, tmp_path: Path):
        task_output = tmp_path / "task_output"
        task_output.mkdir()

        (task_output / "evidence-pack.md").write_text("# Evidence\n", encoding="utf-8")
        (task_output / "key-logs.txt").write_text("ERROR\n", encoding="utf-8")
        (task_output / "case-draft.md").write_text("# Case Draft Content\n", encoding="utf-8")

        metadata = FaultCaseMetadata(
            case_id="CASE-004",
            title="Test",
            slug="test",
            source_type=CaseSourceType.AUTO,
            status=CaseStatus.ARCHIVED,
            confidence=CaseConfidence.CONFIRMED,
        )

        cases_dir = tmp_path / "cases"
        case_dir = archive_case_from_task(task_output, metadata, cases_dir=cases_dir)

        case_md = case_dir / "case.md"
        assert case_md.exists()
        assert case_md.read_text(encoding="utf-8") == "# Case Draft Content\n"

    def test_case_draft_missing_creates_empty_case_md(self, tmp_path: Path):
        task_output = tmp_path / "task_output"
        task_output.mkdir()

        (task_output / "evidence-pack.md").write_text("# Evidence\n", encoding="utf-8")
        (task_output / "key-logs.txt").write_text("ERROR\n", encoding="utf-8")

        metadata = FaultCaseMetadata(
            case_id="CASE-005",
            title="No Draft Case",
            slug="no-draft",
            source_type=CaseSourceType.AUTO,
            status=CaseStatus.ARCHIVED,
            confidence=CaseConfidence.CONFIRMED,
        )

        cases_dir = tmp_path / "cases"
        case_dir = archive_case_from_task(task_output, metadata, cases_dir=cases_dir)

        case_md = case_dir / "case.md"
        assert case_md.exists()
        assert "# No Draft Case" in case_md.read_text(encoding="utf-8")

    def test_raises_on_missing_task_output(self, tmp_path: Path):
        nonexistent = tmp_path / "nonexistent"

        metadata = FaultCaseMetadata(
            case_id="CASE-006",
            title="Test",
            slug="test",
            source_type=CaseSourceType.AUTO,
            status=CaseStatus.ARCHIVED,
            confidence=CaseConfidence.CONFIRMED,
        )

        cases_dir = tmp_path / "cases"
        with pytest.raises(MissingTaskArtifactError):
            archive_case_from_task(nonexistent, metadata, cases_dir=cases_dir)

    def test_raises_on_missing_evidence_pack(self, tmp_path: Path):
        task_output = tmp_path / "task_output"
        task_output.mkdir()
        (task_output / "key-logs.txt").write_text("ERROR\n", encoding="utf-8")

        metadata = FaultCaseMetadata(
            case_id="CASE-007",
            title="Test",
            slug="test",
            source_type=CaseSourceType.AUTO,
            status=CaseStatus.ARCHIVED,
            confidence=CaseConfidence.CONFIRMED,
        )

        cases_dir = tmp_path / "cases"
        with pytest.raises(MissingTaskArtifactError):
            archive_case_from_task(task_output, metadata, cases_dir=cases_dir)

    def test_raises_on_missing_key_logs(self, tmp_path: Path):
        task_output = tmp_path / "task_output"
        task_output.mkdir()
        (task_output / "evidence-pack.md").write_text("# Evidence\n", encoding="utf-8")

        metadata = FaultCaseMetadata(
            case_id="CASE-008",
            title="Test",
            slug="test",
            source_type=CaseSourceType.AUTO,
            status=CaseStatus.ARCHIVED,
            confidence=CaseConfidence.CONFIRMED,
        )

        cases_dir = tmp_path / "cases"
        with pytest.raises(MissingTaskArtifactError):
            archive_case_from_task(task_output, metadata, cases_dir=cases_dir)

    def test_raises_on_existing_case_dir(self, tmp_path: Path):
        task_output = tmp_path / "task_output"
        task_output.mkdir()

        (task_output / "evidence-pack.md").write_text("# Evidence\n", encoding="utf-8")
        (task_output / "key-logs.txt").write_text("ERROR\n", encoding="utf-8")

        metadata = FaultCaseMetadata(
            case_id="CASE-009",
            title="Test",
            slug="test",
            source_type=CaseSourceType.AUTO,
            status=CaseStatus.ARCHIVED,
            confidence=CaseConfidence.CONFIRMED,
        )

        cases_dir = tmp_path / "cases"
        cases_dir.mkdir()
        (cases_dir / "CASE-009_test").mkdir()

        with pytest.raises(CaseExistsError):
            archive_case_from_task(task_output, metadata, cases_dir=cases_dir)
