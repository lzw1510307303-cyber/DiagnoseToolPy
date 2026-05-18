"""tests/integration/test_diagnosis_pipeline.py

Integration test: AI diagnosis orchestration from task output to LLM-based diagnosis.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from diagnose_tool.analyzer.diagnosis import (
    DiagnosisOrchestrator,
    EvidenceNotFoundError,
    TaskNotFoundError,
)
from diagnose_tool.casebase.case_indexer import add_case_to_index
from diagnose_tool.casebase.case_models import (
    CaseConfidence,
    CaseSourceType,
    CaseStatus,
    FaultCaseMetadata,
)
from diagnose_tool.core.llm_config import AppLLMConfig


class TestDiagnosisPipeline:
    """test_diagnosis_pipeline — diagnosis orchestration → retrieval → LLM call."""

    def test_orchestrator_produces_ai_diagnosis_md(
        self,
        sample_task_output: dict[str, Path],
        tmp_data_dir: dict[str, Path],
        monkeypatch,
    ) -> None:
        # === GIVEN ===
        task_id = sample_task_output["task_id"]
        data_dir = tmp_data_dir["data_dir"]
        cases_dir = tmp_data_dir["cases_dir"]

        # Create a historical case for similarity retrieval
        cases_dir.mkdir(parents=True, exist_ok=True)
        case_dir = cases_dir / "CASE-HISTORY001_connection-refused"
        case_dir.mkdir()
        (case_dir / "metadata.yaml").write_text(
            "case_id: CASE-HISTORY001\n"
            "title: MySQL Connection Refused\n"
            "slug: connection-refused\n"
            "source_type: manual\n"
            "status: archived\n"
            "confidence: confirmed\n"
            "tags: []\n"
            "components: []\n"
            "fault_modes: []\n"
            "exception_classes: []\n"
            "key_phrases: []\n"
            "created_at: 2026-05-10 10:00:00\n",
            encoding="utf-8",
        )
        (case_dir / "case.md").write_text(
            "# MySQL Connection Refused\n\n"
            "Root cause: max_connections exceeded.\n",
            encoding="utf-8",
        )
        (case_dir / "evidence-pack.md").write_text(
            "## 异常分类统计\n\n"
            "| database_error | 10 |\n",
            encoding="utf-8",
        )

        # Index the historical case
        metadata = FaultCaseMetadata(
            case_id="CASE-HISTORY001",
            title="MySQL Connection Refused",
            slug="connection-refused",
            source_type=CaseSourceType.MANUAL,
            status=CaseStatus.ARCHIVED,
            confidence=CaseConfidence.CONFIRMED,
        )
        add_case_to_index(metadata, cases_dir=cases_dir)

        # LLM config (mocked)
        llm_config = AppLLMConfig(
            enabled=True,
            model="mock-model",
            base_url="https://mock.example.com/v1",
            api_key="mock-key",
            timeout=30,
            data_dir=data_dir,
        )

        # Mock diagnosis response
        mock_diagnosis_response = (
            "Based on the evidence pack analysis, this appears to be a "
            "database connection error. The 'connection refused' keyword "
            "appears 2 times, suggesting the database service may be down "
            "or the connection pool is exhausted."
        )

        # === WHEN ===
        with patch(
            "diagnose_tool.analyzer.diagnosis.LLMClient"
        ) as MockLLMClient:
            mock_client_instance = MagicMock()
            MockLLMClient.return_value = mock_client_instance
            mock_client_instance.chat.return_value = mock_diagnosis_response

            orchestrator = DiagnosisOrchestrator(
                llm_config=llm_config,
                data_dir=data_dir,
            )
            case_id, diagnosis_text = orchestrator.run(task_id)

        # === THEN ===
        # Verify case_id
        assert case_id == task_id

        # Verify diagnosis text from mock
        assert "database connection error" in diagnosis_text

        # Verify ai-diagnosis.md was generated
        ai_diagnosis_path = cases_dir / task_id / "ai-diagnosis.md"
        assert ai_diagnosis_path.exists(), (
            f"Expected ai-diagnosis.md at {ai_diagnosis_path}"
        )

        diagnosis_md_content = ai_diagnosis_path.read_text(encoding="utf-8")
        assert "PRELIMINARY AI DIAGNOSIS" in diagnosis_md_content
        assert "DISCLAIMER" in diagnosis_md_content or "Disclaimer" in diagnosis_md_content
        assert task_id in diagnosis_md_content

    def test_orchestrator_raises_when_task_not_found(
        self,
        tmp_data_dir: dict[str, Path],
    ) -> None:
        """Verify TaskNotFoundError is raised when task output directory doesn't exist."""
        llm_config = AppLLMConfig(
            enabled=False,
            model="mock",
            base_url="",
            api_key="",
            timeout=10,
            data_dir=tmp_data_dir["data_dir"],
        )
        orchestrator = DiagnosisOrchestrator(
            llm_config=llm_config,
            data_dir=tmp_data_dir["data_dir"],
        )

        with pytest.raises(TaskNotFoundError):
            orchestrator.run("NONEXISTENT-TASK")

    def test_orchestrator_raises_when_evidence_pack_missing(
        self,
        tmp_data_dir: dict[str, Path],
    ) -> None:
        """Verify EvidenceNotFoundError is raised when evidence-pack.md is missing."""
        task_id = "DIAG-002"
        output_dir = tmp_data_dir["output_dir"] / task_id
        output_dir.mkdir(parents=True, exist_ok=True)
        # Note: we intentionally do NOT create evidence-pack.md

        llm_config = AppLLMConfig(
            enabled=False,
            model="mock",
            base_url="",
            api_key="",
            timeout=10,
            data_dir=tmp_data_dir["data_dir"],
        )
        orchestrator = DiagnosisOrchestrator(
            llm_config=llm_config,
            data_dir=tmp_data_dir["data_dir"],
        )

        with pytest.raises(EvidenceNotFoundError):
            orchestrator.run(task_id)

    def test_orchestrator_with_no_retrieval_query(
        self,
        sample_task_output: dict[str, Path],
        tmp_data_dir: dict[str, Path],
    ) -> None:
        """Verify orchestrator handles missing retrieval-query.json gracefully."""
        task_id = sample_task_output["task_id"]
        output_dir = sample_task_output["output_dir"]
        data_dir = tmp_data_dir["data_dir"]

        # Remove retrieval-query.json to test graceful handling
        retrieval_query_path = output_dir / "retrieval-query.json"
        if retrieval_query_path.exists():
            retrieval_query_path.unlink()

        llm_config = AppLLMConfig(
            enabled=True,
            model="mock-model",
            base_url="https://mock.example.com/v1",
            api_key="mock-key",
            timeout=30,
            data_dir=data_dir,
        )

        mock_diagnosis_response = "Diagnosis without retrieval context."

        with patch(
            "diagnose_tool.analyzer.diagnosis.LLMClient"
        ) as MockLLMClient:
            mock_client_instance = MagicMock()
            MockLLMClient.return_value = mock_client_instance
            mock_client_instance.chat.return_value = mock_diagnosis_response

            orchestrator = DiagnosisOrchestrator(
                llm_config=llm_config,
                data_dir=data_dir,
            )
            # Should not raise, even without retrieval-query.json
            case_id, diagnosis_text = orchestrator.run(task_id)

        assert case_id == task_id
        assert diagnosis_text == mock_diagnosis_response
