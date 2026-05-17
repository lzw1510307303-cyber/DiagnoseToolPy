"""Tests for manual case creation."""

from __future__ import annotations

import yaml
from pathlib import Path


from diagnose_tool.casebase.case_models import (
    CaseConfidence,
    CaseSourceType,
    CaseStatus,
)
from diagnose_tool.casebase.case_service import (
    create_manual_case,
    _generate_slug,
)


class TestGenerateSlug:
    def test_slug_from_simple_title(self):
        slug = _generate_slug("Redis Connection Error")
        assert slug == "redis-connection-error"

    def test_slug_removes_special_chars(self):
        slug = _generate_slug("Order#1: Database@Failed!")
        assert slug == "order1-databasefailed"

    def test_slug_trims_whitespace(self):
        slug = _generate_slug("  Spaced Title  ")
        assert slug == "spaced-title"

    def test_slug_max_length(self):
        long_title = "A" * 100
        slug = _generate_slug(long_title)
        assert len(slug) == 50


class TestCreateManualCase:
    def test_create_manual_case_creates_directory(self, tmp_path: Path):
        case = create_manual_case(
            title="Test Case",
            content="# Test\n\nContent here",
            cases_dir=tmp_path,
        )

        assert case.metadata.case_id.startswith("CASE-")
        assert case.metadata.source_type == CaseSourceType.MANUAL
        assert case.metadata.status == CaseStatus.DRAFT

        case_dir = tmp_path / f"{case.metadata.case_id}_test-case"
        assert case_dir.exists()

    def test_create_manual_case_writes_metadata(self, tmp_path: Path):
        case = create_manual_case(
            title="Redis Fault",
            content="ERROR: connection failed",
            status=CaseStatus.ARCHIVED,
            confidence=CaseConfidence.CONFIRMED,
            tags=["redis", "connection"],
            cases_dir=tmp_path,
        )

        case_dir = tmp_path / f"{case.metadata.case_id}_redis-fault"
        metadata_path = case_dir / "metadata.yaml"

        with metadata_path.open("r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)

        assert metadata["case_id"] == case.metadata.case_id
        assert metadata["title"] == "Redis Fault"
        assert metadata["source_type"] == "manual"
        assert metadata["status"] == "archived"
        assert metadata["confidence"] == "confirmed"
        assert metadata["tags"] == ["redis", "connection"]

    def test_create_manual_case_writes_content(self, tmp_path: Path):
        content = "# Custom Title\n\nCustom content."
        case = create_manual_case(
            title="Custom Case",
            content=content,
            cases_dir=tmp_path,
        )

        case_dir = tmp_path / f"{case.metadata.case_id}_custom-case"
        case_md = case_dir / "case.md"

        assert case_md.read_text(encoding="utf-8") == content

    def test_create_manual_case_auto_generates_slug(self, tmp_path: Path):
        case = create_manual_case(
            title="Auto Generate Slug Test",
            cases_dir=tmp_path,
        )

        assert case.metadata.slug == "auto-generate-slug-test"

    def test_create_manual_case_uses_provided_slug(self, tmp_path: Path):
        case = create_manual_case(
            title="My Case",
            slug="custom-slug-123",
            cases_dir=tmp_path,
        )

        assert case.metadata.slug == "custom-slug-123"

    def test_create_manual_case_updates_index_on_archive(self, tmp_path: Path):
        case = create_manual_case(
            title="Indexed Case",
            status=CaseStatus.ARCHIVED,
            cases_dir=tmp_path,
        )

        index_file = tmp_path / "index.yaml"
        assert index_file.exists()

        with index_file.open("r", encoding="utf-8") as f:
            index_data = yaml.safe_load(f)

        assert len(index_data) == 1
        assert index_data[0]["case_id"] == case.metadata.case_id

    def test_create_manual_case_does_not_update_index_on_draft(self, tmp_path: Path):
        create_manual_case(
            title="Draft Case",
            status=CaseStatus.DRAFT,
            cases_dir=tmp_path,
        )

        index_file = tmp_path / "index.yaml"
        assert not index_file.exists()

    def test_create_manual_case_default_metadata(self, tmp_path: Path):
        case = create_manual_case(
            title="Default Test",
            cases_dir=tmp_path,
        )

        assert case.metadata.source_type == CaseSourceType.MANUAL
        assert case.metadata.status == CaseStatus.DRAFT
        assert case.metadata.confidence == CaseConfidence.UNCONFIRMED
        assert case.metadata.tags == []
        assert case.metadata.components == []
        assert case.metadata.fault_modes == []

    def test_create_manual_case_collision_handling(self, tmp_path: Path):
        case1 = create_manual_case(
            title="Collision Test",
            cases_dir=tmp_path,
        )

        case_dir = tmp_path / f"{case1.metadata.case_id}_collision-test"
        case_dir.mkdir(parents=True, exist_ok=True)

        case2 = create_manual_case(
            title="Collision Test",
            cases_dir=tmp_path,
        )

        assert case1.metadata.case_id != case2.metadata.case_id
