"""Tests for case indexer."""

from __future__ import annotations

import yaml
from pathlib import Path


from diagnose_tool.casebase.case_indexer import (
    add_case_to_index,
    get_index,
    rebuild_index,
)
from diagnose_tool.casebase.case_models import (
    CaseConfidence,
    CaseSourceType,
    CaseStatus,
    FaultCaseMetadata,
)


class TestRebuildIndex:
    def test_rebuild_index_returns_entries(self, tmp_path: Path):
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir()

        case1_dir = cases_dir / "CASE-001_test"
        case1_dir.mkdir()
        metadata1 = {
            "case_id": "CASE-001",
            "title": "Case One",
            "slug": "test",
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

        case2_dir = cases_dir / "CASE-002_case"
        case2_dir.mkdir()
        metadata2 = {
            "case_id": "CASE-002",
            "title": "Case Two",
            "slug": "case",
            "source_type": "manual",
            "status": "reviewing",
            "confidence": "likely",
            "tags": [],
            "components": [],
            "fault_modes": [],
            "exception_classes": [],
            "key_phrases": [],
            "created_at": "2026-05-17 11:00:00",
        }
        with (case2_dir / "metadata.yaml").open("w", encoding="utf-8") as f:
            yaml.dump(metadata2, f)

        entries = rebuild_index(cases_dir=cases_dir)

        assert len(entries) == 2
        assert entries[0].case_id == "CASE-002"
        assert entries[1].case_id == "CASE-001"

    def test_rebuild_index_empty_dir(self, tmp_path: Path):
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir()

        entries = rebuild_index(cases_dir=cases_dir)
        assert entries == []

    def test_rebuild_index_nonexistent_dir(self, tmp_path: Path):
        nonexistent = tmp_path / "nonexistent"
        entries = rebuild_index(cases_dir=nonexistent)
        assert entries == []

    def test_malformed_metadata_skipped(self, tmp_path: Path, caplog):
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir()

        bad_case = cases_dir / "CASE-BAD_test"
        bad_case.mkdir()
        with (bad_case / "metadata.yaml").open("w", encoding="utf-8") as f:
            yaml.dump({"invalid": "data"}, f)

        good_case = cases_dir / "CASE-GOOD_test"
        good_case.mkdir()
        metadata = {
            "case_id": "CASE-GOOD",
            "title": "Good Case",
            "slug": "test",
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
        with (good_case / "metadata.yaml").open("w", encoding="utf-8") as f:
            yaml.dump(metadata, f)

        entries = rebuild_index(cases_dir=cases_dir)
        assert len(entries) == 1
        assert entries[0].case_id == "CASE-GOOD"

    def test_rebuild_index_skips_index_yaml(self, tmp_path: Path):
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir()

        (cases_dir / "index.yaml").write_text("[]", encoding="utf-8")

        case_dir = cases_dir / "CASE-001_test"
        case_dir.mkdir()
        metadata = {
            "case_id": "CASE-001",
            "title": "Test",
            "slug": "test",
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
        with (case_dir / "metadata.yaml").open("w", encoding="utf-8") as f:
            yaml.dump(metadata, f)

        entries = rebuild_index(cases_dir=cases_dir)
        assert len(entries) == 1


class TestAddCaseToIndex:
    def test_add_case_creates_index(self, tmp_path: Path):
        cases_dir = tmp_path / "cases"
        index_file = cases_dir / "index.yaml"

        metadata = FaultCaseMetadata(
            case_id="CASE-001",
            title="Added Case",
            slug="added",
            source_type=CaseSourceType.AUTO,
            status=CaseStatus.ARCHIVED,
            confidence=CaseConfidence.CONFIRMED,
        )

        add_case_to_index(metadata, cases_dir=cases_dir, index_file=index_file)

        assert index_file.exists()
        entries = get_index(cases_dir=cases_dir, index_file=index_file)
        assert len(entries) == 1
        assert entries[0].case_id == "CASE-001"

    def test_add_case_updates_existing(self, tmp_path: Path):
        cases_dir = tmp_path / "cases"
        index_file = cases_dir / "index.yaml"

        metadata1 = FaultCaseMetadata(
            case_id="CASE-001",
            title="Original",
            slug="original",
            source_type=CaseSourceType.AUTO,
            status=CaseStatus.DRAFT,
            confidence=CaseConfidence.UNCONFIRMED,
        )
        add_case_to_index(metadata1, cases_dir=cases_dir, index_file=index_file)

        metadata2 = FaultCaseMetadata(
            case_id="CASE-001",
            title="Updated",
            slug="updated",
            source_type=CaseSourceType.AUTO,
            status=CaseStatus.ARCHIVED,
            confidence=CaseConfidence.CONFIRMED,
        )
        add_case_to_index(metadata2, cases_dir=cases_dir, index_file=index_file)

        entries = get_index(cases_dir=cases_dir, index_file=index_file)
        assert len(entries) == 1
        assert entries[0].title == "Updated"
        assert entries[0].status == CaseStatus.ARCHIVED


class TestGetIndex:
    def test_get_index_returns_entries(self, tmp_path: Path):
        cases_dir = tmp_path / "cases"
        index_file = cases_dir / "index.yaml"
        cases_dir.mkdir()

        entries_data = [
            {
                "case_id": "CASE-001",
                "title": "Test",
                "slug": "test",
                "status": "archived",
                "source_type": "auto",
                "created_at": "2026-05-17 10:00:00",
            }
        ]
        with index_file.open("w", encoding="utf-8") as f:
            yaml.dump(entries_data, f)

        entries = get_index(cases_dir=cases_dir, index_file=index_file)
        assert len(entries) == 1
        assert entries[0].case_id == "CASE-001"

    def test_get_index_missing_file(self, tmp_path: Path):
        nonexistent = tmp_path / "nonexistent" / "index.yaml"
        entries = get_index(cases_dir=nonexistent.parent, index_file=nonexistent)
        assert entries == []

    def test_get_index_empty_file(self, tmp_path: Path):
        cases_dir = tmp_path / "cases"
        index_file = cases_dir / "index.yaml"
        cases_dir.mkdir()
        index_file.write_text("[]", encoding="utf-8")

        entries = get_index(cases_dir=cases_dir, index_file=index_file)
        assert entries == []
