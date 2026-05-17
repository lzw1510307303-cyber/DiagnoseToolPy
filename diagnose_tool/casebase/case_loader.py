"""Case loader for reading fault case directories."""

from __future__ import annotations

from pathlib import Path

import yaml

from diagnose_tool.casebase.case_models import FaultCase, FaultCaseMetadata


def load_case(case_path: Path) -> FaultCase:
    if not case_path.exists():
        raise FileNotFoundError(f"Case directory does not exist: {case_path}")

    metadata = load_metadata(case_path)

    case_md_path = case_path / "case.md"
    if case_md_path.exists():
        case_md_content = case_md_path.read_text(encoding="utf-8")
    else:
        case_md_content = None

    return FaultCase(
        metadata=metadata,
        case_path=str(case_path),
        evidence_path=str(case_path),
        case_md_content=case_md_content,
    )


def load_metadata(case_path: Path) -> FaultCaseMetadata:
    if not case_path.exists():
        raise FileNotFoundError(f"Case directory does not exist: {case_path}")

    metadata_path = case_path / "metadata.yaml"
    if not metadata_path.exists():
        raise FileNotFoundError(f"metadata.yaml not found in case directory: {case_path}")

    with metadata_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return FaultCaseMetadata.from_dict(data)
