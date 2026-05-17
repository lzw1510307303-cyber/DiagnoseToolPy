"""Casebase module for fault case management."""

from __future__ import annotations

from diagnose_tool.casebase.case_models import (
    CaseConfidence,
    CaseIndexEntry,
    CaseSourceType,
    CaseStatus,
    FaultCase,
    FaultCaseMetadata,
)
from diagnose_tool.casebase.case_writer import (
    CaseExistsError,
    MissingTaskArtifactError,
    archive_case_from_task,
)
from diagnose_tool.casebase.case_loader import (
    load_case,
    load_metadata,
)
from diagnose_tool.casebase.case_indexer import (
    CaseIndexError,
    add_case_to_index,
    get_index,
    rebuild_index,
)
from diagnose_tool.casebase.case_service import (
    create_case_from_analysis,
    create_manual_case,
    get_all_cases,
    get_case,
)

__all__ = [
    "CaseConfidence",
    "CaseIndexEntry",
    "CaseSourceType",
    "CaseStatus",
    "FaultCase",
    "FaultCaseMetadata",
    "CaseExistsError",
    "MissingTaskArtifactError",
    "archive_case_from_task",
    "load_case",
    "load_metadata",
    "CaseIndexError",
    "add_case_to_index",
    "get_index",
    "rebuild_index",
    "create_case_from_analysis",
    "create_manual_case",
    "get_all_cases",
    "get_case",
]
