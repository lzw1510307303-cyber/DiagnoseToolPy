"""Tests for case service."""

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
from diagnose_tool.casebase.case_service import (
    create_case_from_analysis,
    get_all_cases,
    get_case,
)


class TestCreateCaseFromAnalysis:
    def test_create_case_orchestrates(self, tmp_path: Path):
        task_output = tmp_path / "task_output"
        task_output.mkdir()

        (task_output / "evidence-pack.md").write_text("# Evidence\n", encoding="utf-8")
        (task_output / "key-logs.txt").write_text("ERROR sample\n", encoding="utf-8")
        (task_output / "case-draft.md").write_text("# Case Draft\n", encoding="utf-8")

        metadata = FaultCaseMetadata(
            case_id="CASE-001",
            title="Orchestrated Case",
            slug="orchestrated",
            source_type=CaseSourceType.AUTO,
            status=CaseStatus.ARCHIVED,
            confidence=CaseConfidence.CONFIRMED,
        )

        cases_dir = tmp_path / "cases"
        case_dir = create_case_from_analysis(task_output, metadata, cases_dir=cases_dir)

        assert case_dir.exists()
        assert (case_dir / "metadata.yaml").exists()
        assert (case_dir / "case.md").exists()
        assert (case_dir / "evidence-pack.md").exists()
        assert (case_dir / "key-logs.txt").exists()


class TestGetAllCases:
    def test_get_all_cases_returns_list(self, tmp_path: Path):
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir()

        case1_dir = cases_dir / "CASE-001_first"
        case1_dir.mkdir()
        metadata1 = {
            "case_id": "CASE-001",
            "title": "First Case",
            "slug": "first",
            "source_type": "auto",
            "status": "archived",
            "confidence": "confirmed",
            "tags": [],
            "components": [],
            "fault_modes": [],
            "exception_classes": [],
            "key_phrases": [],
            "created_at": "2026-05-17 10:00:00",
        }
        with (case1_dir / "metadata.yaml").open("w", encoding="utf-8") as f:
            yaml.dump(metadata1, f)
        (case1_dir / "case.md").write_text("# First\n", encoding="utf-8")

        index_file = cases_dir / "index.yaml"
        with index_file.open("w", encoding="utf-8") as f:
            yaml.dump([{"case_id": "CASE-001", "title": "First Case", "slug": "first",
                        "status": "archived", "source_type": "auto", "created_at": "2026-05-17 10:00:00"}], f)

        cases = get_all_cases(cases_dir=cases_dir)

        assert len(cases) == 1
        assert cases[0].metadata.case_id == "CASE-001"

    def test_get_all_cases_empty(self, tmp_path: Path):
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir()

        cases = get_all_cases(cases_dir=cases_dir)
        assert cases == []


class TestGetCase:
    def test_get_case_by_id(self, tmp_path: Path):
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir()

        case1_dir = cases_dir / "CASE-001_search"
        case1_dir.mkdir()
        metadata1 = {
            "case_id": "CASE-001",
            "title": "Searchable Case",
            "slug": "search",
            "source_type": "manual",
            "status": "reviewing",
            "confidence": "likely",
            "tags": [],
            "components": [],
            "fault_modes": [],
            "exception_classes": [],
            "key_phrases": [],
            "created_at": "2026-05-17 10:00:00",
        }
        with (case1_dir / "metadata.yaml").open("w", encoding="utf-8") as f:
            yaml.dump(metadata1, f)
        (case1_dir / "case.md").write_text("# Searchable\n", encoding="utf-8")

        index_file = cases_dir / "index.yaml"
        with index_file.open("w", encoding="utf-8") as f:
            yaml.dump([{"case_id": "CASE-001", "title": "Searchable Case", "slug": "search",
                        "status": "reviewing", "source_type": "manual", "created_at": "2026-05-17 10:00:00"}], f)

        case = get_case("CASE-001", cases_dir=cases_dir)

        assert case.metadata.case_id == "CASE-001"
        assert case.metadata.title == "Searchable Case"

    def test_get_case_not_found(self, tmp_path: Path):
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir()

        index_file = cases_dir / "index.yaml"
        index_file.write_text("[]", encoding="utf-8")

        with pytest.raises(FileNotFoundError):
            get_case("CASE-NOTFOUND", cases_dir=cases_dir)
