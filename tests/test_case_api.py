"""Tests for case API routes."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from diagnose_tool.main import app


class TestCreateCaseAPI:
    def test_post_cases_creates_manual_case(self, tmp_path: Path, monkeypatch) -> None:
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir()

        def fake_create_manual_case(**kwargs):
            from diagnose_tool.casebase.case_models import (
                CaseConfidence,
                CaseSourceType,
                CaseStatus,
                FaultCase,
                FaultCaseMetadata,
            )

            provided_slug = kwargs.get("slug")
            slug = provided_slug if provided_slug else "redis-connection-error"

            metadata = FaultCaseMetadata(
                case_id="CASE-TEST001",
                title=kwargs.get("title", "Test"),
                slug=slug,
                source_type=CaseSourceType.MANUAL,
                status=kwargs.get("status", CaseStatus.DRAFT),
                confidence=kwargs.get("confidence", CaseConfidence.UNCONFIRMED),
            )
            return FaultCase(
                metadata=metadata,
                case_path=str(cases_dir / f"{metadata.case_id}_{metadata.slug}"),
                evidence_path=str(cases_dir / f"{metadata.case_id}_{metadata.slug}"),
                case_md_content=kwargs.get("content", ""),
            )

        from diagnose_tool.api import routes_case
        monkeypatch.setattr(routes_case, "create_manual_case", fake_create_manual_case)

        response = TestClient(app).post(
            "/api/cases",
            json={
                "title": "Redis Connection Error",
                "content": "# Error\n\nRedis connection failed",
                "status": "archived",
                "confidence": "confirmed",
                "tags": ["redis", "connection"],
            },
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["case_id"] == "CASE-TEST001"
        assert payload["title"] == "Redis Connection Error"
        assert payload["status"] == "archived"
        assert payload["source_type"] == "manual"

    def test_post_cases_with_minimal_input(self, tmp_path: Path, monkeypatch) -> None:
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir()

        def fake_create_manual_case(**kwargs):
            from diagnose_tool.casebase.case_models import (
                CaseConfidence,
                CaseSourceType,
                CaseStatus,
                FaultCase,
                FaultCaseMetadata,
            )

            metadata = FaultCaseMetadata(
                case_id="CASE-TEST002",
                title=kwargs.get("title", "Minimal"),
                slug="minimal",
                source_type=CaseSourceType.MANUAL,
                status=CaseStatus.DRAFT,
                confidence=CaseConfidence.UNCONFIRMED,
            )
            return FaultCase(
                metadata=metadata,
                case_path=str(cases_dir / f"{metadata.case_id}_{metadata.slug}"),
                evidence_path=str(cases_dir / f"{metadata.case_id}_{metadata.slug}"),
                case_md_content="",
            )

        from diagnose_tool.api import routes_case
        monkeypatch.setattr(routes_case, "create_manual_case", fake_create_manual_case)

        response = TestClient(app).post(
            "/api/cases",
            json={"title": "Minimal Case"},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["title"] == "Minimal Case"

    def test_post_cases_validation_error_missing_title(self) -> None:
        response = TestClient(app).post(
            "/api/cases",
            json={},
        )

        assert response.status_code == 422

    def test_post_cases_validation_error_invalid_status(self, tmp_path: Path, monkeypatch) -> None:
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir()

        def fake_create_manual_case(**kwargs):
            from diagnose_tool.casebase.case_models import (
                CaseConfidence,
                CaseSourceType,
                CaseStatus,
                FaultCase,
                FaultCaseMetadata,
            )

            metadata = FaultCaseMetadata(
                case_id="CASE-TEST003",
                title="Test",
                slug="test",
                source_type=CaseSourceType.MANUAL,
                status=CaseStatus.DRAFT,
                confidence=CaseConfidence.UNCONFIRMED,
            )
            return FaultCase(
                metadata=metadata,
                case_path=str(cases_dir / f"{metadata.case_id}_{metadata.slug}"),
                evidence_path=str(cases_dir / f"{metadata.case_id}_{metadata.slug}"),
                case_md_content="",
            )

        from diagnose_tool.api import routes_case
        monkeypatch.setattr(routes_case, "create_manual_case", fake_create_manual_case)

        response = TestClient(app).post(
            "/api/cases",
            json={
                "title": "Test Case",
                "status": "invalid-status",
            },
        )

        assert response.status_code == 422
        assert "Invalid status" in response.json()["detail"]

    def test_post_cases_validation_error_invalid_confidence(self, tmp_path: Path, monkeypatch) -> None:
        cases_dir = tmp_path / "cases"
        cases_dir.mkdir()

        def fake_create_manual_case(**kwargs):
            from diagnose_tool.casebase.case_models import (
                CaseConfidence,
                CaseSourceType,
                CaseStatus,
                FaultCase,
                FaultCaseMetadata,
            )

            metadata = FaultCaseMetadata(
                case_id="CASE-TEST004",
                title="Test",
                slug="test",
                source_type=CaseSourceType.MANUAL,
                status=CaseStatus.DRAFT,
                confidence=CaseConfidence.UNCONFIRMED,
            )
            return FaultCase(
                metadata=metadata,
                case_path=str(cases_dir / f"{metadata.case_id}_{metadata.slug}"),
                evidence_path=str(cases_dir / f"{metadata.case_id}_{metadata.slug}"),
                case_md_content="",
            )

        from diagnose_tool.api import routes_case
        monkeypatch.setattr(routes_case, "create_manual_case", fake_create_manual_case)

        response = TestClient(app).post(
            "/api/cases",
            json={
                "title": "Test Case",
                "confidence": "invalid-confidence",
            },
        )

        assert response.status_code == 422
        assert "Invalid confidence" in response.json()["detail"]
