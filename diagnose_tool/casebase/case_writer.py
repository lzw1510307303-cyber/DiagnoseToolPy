"""Case writer for creating fault case directories."""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from diagnose_tool.casebase.case_models import FaultCaseMetadata


class CaseExistsError(Exception):
    pass


class MissingTaskArtifactError(Exception):
    pass


CASES_DIR = Path("data/cases")


def archive_case_from_task(
    task_output_path: Path,
    case_metadata: FaultCaseMetadata,
    cases_dir: Path | None = None,
) -> Path:
    if cases_dir is None:
        cases_dir = CASES_DIR

    if not task_output_path.exists():
        raise MissingTaskArtifactError(f"Task output directory does not exist: {task_output_path}")

    evidence_pack_src = task_output_path / "evidence-pack.md"
    key_logs_src = task_output_path / "key-logs.txt"
    case_draft_src = task_output_path / "case-draft.md"

    if not evidence_pack_src.exists():
        raise MissingTaskArtifactError(f"evidence-pack.md not found in task output: {task_output_path}")
    if not key_logs_src.exists():
        raise MissingTaskArtifactError(f"key-logs.txt not found in task output: {task_output_path}")

    case_dir_name = f"{case_metadata.case_id}_{case_metadata.slug}"
    case_dir = cases_dir / case_dir_name

    if case_dir.exists():
        raise CaseExistsError(f"Case directory already exists: {case_dir}")

    case_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = case_dir / "metadata.yaml"
    with metadata_path.open("w", encoding="utf-8") as f:
        yaml.dump(case_metadata.to_dict(), f, allow_unicode=True, sort_keys=False)

    if case_draft_src.exists():
        case_md_dst = case_dir / "case.md"
        shutil.copy2(case_draft_src, case_md_dst)
    else:
        case_md_dst = case_dir / "case.md"
        case_md_dst.write_text(
            f"# {case_metadata.title}\n\n",
            encoding="utf-8",
        )

    evidence_pack_dst = case_dir / "evidence-pack.md"
    shutil.copy2(evidence_pack_src, evidence_pack_dst)

    key_logs_dst = case_dir / "key-logs.txt"
    shutil.copy2(key_logs_src, key_logs_dst)

    return case_dir
