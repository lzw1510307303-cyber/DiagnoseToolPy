"""tests/integration/test_case_lifecycle.py

Integration test: POST /api/cases → file system → index.yaml lifecycle.
"""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from diagnose_tool.casebase.case_indexer import get_index
from diagnose_tool.casebase.case_models import CaseConfidence, CaseStatus
from diagnose_tool.casebase.case_service import create_manual_case
from diagnose_tool.main import create_app


class TestCaseLifecycle:
    """test_case_lifecycle — Case creation → file write → index → list query."""

    def test_case_created_via_api_produces_correct_files(
        self,
        tmp_data_dir: dict[str, Path],
        monkeypatch,
    ) -> None:
        # === GIVEN ===
        cases_dir = tmp_data_dir["cases_dir"]
        # Note: tmp_data_dir fixture already creates cases_dir, so no need to mkdir

        # Redirect module-level CASES_DIR globals to our tmp directory
        monkeypatch.setattr(
            "diagnose_tool.casebase.case_indexer.CASES_DIR",
            cases_dir,
        )
        monkeypatch.setattr(
            "diagnose_tool.casebase.case_service.CASES_DIR",
            cases_dir,
        )

        app = create_app()

        # === WHEN ===
        # Step 1: POST create Case
        response = TestClient(app).post(
            "/api/cases",
            json={
                "title": "Redis Connection Error",
                "content": "# Redis\n\nConnection refused after 3 retries.",
                "status": "draft",
                "confidence": "unconfirmed",
                "tags": ["redis", "network"],
                "components": ["redis-client"],
                "fault_modes": ["connection_error"],
                "exception_classes": ["ConnectionRefusedError"],
                "key_phrases": ["connection refused"],
            },
        )

        # === THEN (Step 1) ===
        assert response.status_code == 200, response.text
        payload = response.json()
        case_id = payload["case_id"]
        assert case_id.startswith("CASE-")
        assert payload["title"] == "Redis Connection Error"
        assert payload["status"] == "draft"

        # === THEN (Step 2): Verify file system write ===
        # Find the created case directory
        case_dirs = list(cases_dir.iterdir())
        assert len(case_dirs) == 1, f"Expected 1 case dir, got {case_dirs}"
        case_dir = case_dirs[0]

        metadata_path = case_dir / "metadata.yaml"
        assert metadata_path.exists(), f"metadata.yaml not found in {case_dir}"
        case_md_path = case_dir / "case.md"
        assert case_md_path.exists(), f"case.md not found in {case_dir}"

        import yaml
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        assert metadata["case_id"] == case_id
        assert metadata["title"] == "Redis Connection Error"
        assert metadata["source_type"] == "manual"
        assert metadata["status"] == "draft"
        assert "redis" in metadata["tags"]
        assert "redis-client" in metadata["components"]

        case_md_content = case_md_path.read_text(encoding="utf-8")
        assert "Redis" in case_md_content
        assert "Connection refused" in case_md_content

        # === THEN (Step 3): Verify index behavior for ARCHIVED cases ===
        # create_manual_case only adds to index when status is ARCHIVED
        # So a DRAFT case should NOT appear in index.yaml
        # DRAFT status does not write to index - this is current behavior

        # Create an ARCHIVED case to verify index works
        create_manual_case(
            title="Archived Error Case",
            content="# Archived\n\nAn archived case.",
            status=CaseStatus.ARCHIVED,
            confidence=CaseConfidence.LIKELY,
            cases_dir=cases_dir,
        )

        # Now index should have 1 entry (the archived case)
        index_entries_after = get_index(cases_dir=cases_dir)
        assert len(index_entries_after) == 1
        assert index_entries_after[0].title == "Archived Error Case"
        assert index_entries_after[0].status == CaseStatus.ARCHIVED

    def test_archived_case_appears_in_case_list(
        self,
        tmp_data_dir: dict[str, Path],
        monkeypatch,
    ) -> None:
        """Verify that ARCHIVED cases are properly indexed and listed."""
        cases_dir = tmp_data_dir["cases_dir"]
        # Note: tmp_data_dir fixture already creates cases_dir, so no need to mkdir

        monkeypatch.setattr(
            "diagnose_tool.casebase.case_indexer.CASES_DIR",
            cases_dir,
        )
        monkeypatch.setattr(
            "diagnose_tool.casebase.case_service.CASES_DIR",
            cases_dir,
        )

        app = create_app()

        # Create an archived case via API
        response = TestClient(app).post(
            "/api/cases",
            json={
                "title": "MySQL Timeout",
                "content": "# MySQL\n\nTimeout after 30 seconds.",
                "status": "archived",
                "confidence": "confirmed",
                "tags": ["mysql", "database"],
                "components": ["mysql-connector"],
                "fault_modes": ["timeout"],
                "exception_classes": ["OperationalError"],
                "key_phrases": ["timeout after"],
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "archived"

        # Verify index contains this case
        index_entries = get_index(cases_dir=cases_dir)
        assert len(index_entries) == 1
        assert index_entries[0].case_id == payload["case_id"]
        assert index_entries[0].title == "MySQL Timeout"
