"""Tests for case loader."""

from __future__ import annotations

import yaml
from pathlib import Path

import pytest

from diagnose_tool.casebase.case_loader import load_case, load_metadata


class TestLoadMetadata:
    def test_load_metadata_returns_metadata(self, tmp_path: Path):
        case_dir = tmp_path / "CASE-001_test"
        case_dir.mkdir()

        metadata = {
            "case_id": "CASE-001",
            "title": "Test Case",
            "slug": "test",
            "source_type": "auto",
            "status": "archived",
            "confidence": "confirmed",
            "tags": ["redis"],
            "components": ["order-core"],
            "fault_modes": ["connection-error"],
            "exception_classes": ["JedisException"],
            "key_phrases": ["connection pool"],
            "created_at": "2026-05-17 10:00:00",
        }
        metadata_path = case_dir / "metadata.yaml"
        with metadata_path.open("w", encoding="utf-8") as f:
            yaml.dump(metadata, f)

        loaded = load_metadata(case_dir)

        assert loaded.case_id == "CASE-001"
        assert loaded.title == "Test Case"
        assert loaded.slug == "test"
        assert loaded.tags == ["redis"]
        assert loaded.components == ["order-core"]

    def test_load_metadata_raises_on_missing_dir(self, tmp_path: Path):
        nonexistent = tmp_path / "nonexistent"
        with pytest.raises(FileNotFoundError):
            load_metadata(nonexistent)

    def test_load_metadata_raises_on_missing_yaml(self, tmp_path: Path):
        case_dir = tmp_path / "CASE-002_test"
        case_dir.mkdir()

        with pytest.raises(FileNotFoundError):
            load_metadata(case_dir)


class TestLoadCase:
    def test_load_case_returns_content_and_metadata(self, tmp_path: Path):
        case_dir = tmp_path / "CASE-003_case"
        case_dir.mkdir()

        metadata = {
            "case_id": "CASE-003",
            "title": "Case Content",
            "slug": "case",
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
        metadata_path = case_dir / "metadata.yaml"
        with metadata_path.open("w", encoding="utf-8") as f:
            yaml.dump(metadata, f)

        case_md_content = "# Case Title\n\nContent here."
        (case_dir / "case.md").write_text(case_md_content, encoding="utf-8")

        case = load_case(case_dir)

        assert case.metadata.case_id == "CASE-003"
        assert case.case_md_content == case_md_content
        assert case.case_path == str(case_dir)

    def test_load_case_raises_on_missing_dir(self, tmp_path: Path):
        nonexistent = tmp_path / "nonexistent"
        with pytest.raises(FileNotFoundError):
            load_case(nonexistent)

    def test_load_case_works_without_case_md(self, tmp_path: Path):
        case_dir = tmp_path / "CASE-004_no_md"
        case_dir.mkdir()

        metadata = {
            "case_id": "CASE-004",
            "title": "No MD",
            "slug": "no-md",
            "source_type": "auto",
            "status": "draft",
            "confidence": "unconfirmed",
            "tags": [],
            "components": [],
            "fault_modes": [],
            "exception_classes": [],
            "key_phrases": [],
            "created_at": "2026-05-17 10:00:00",
        }
        metadata_path = case_dir / "metadata.yaml"
        with metadata_path.open("w", encoding="utf-8") as f:
            yaml.dump(metadata, f)

        case = load_case(case_dir)

        assert case.metadata.case_id == "CASE-004"
        assert case.case_md_content is None
