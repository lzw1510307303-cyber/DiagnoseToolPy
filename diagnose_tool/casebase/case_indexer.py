"""Case indexer for maintaining case index."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from diagnose_tool.casebase.case_models import CaseIndexEntry, FaultCaseMetadata


logger = logging.getLogger(__name__)

CASES_DIR = Path("data/cases")
INDEX_FILE = CASES_DIR / "index.yaml"


class CaseIndexError(Exception):
    pass


def rebuild_index(cases_dir: Path | None = None) -> list[CaseIndexEntry]:
    if cases_dir is None:
        cases_dir = CASES_DIR

    if not cases_dir.exists():
        return []

    entries: list[CaseIndexEntry] = []

    for case_subdir in cases_dir.iterdir():
        if not case_subdir.is_dir():
            continue

        if case_subdir.name == "index.yaml":
            continue

        metadata_path = case_subdir / "metadata.yaml"
        if not metadata_path.exists():
            logger.warning("Skipping case directory without metadata: %s", case_subdir.name)
            continue

        try:
            with metadata_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            metadata = FaultCaseMetadata.from_dict(data)
            entry = CaseIndexEntry.from_metadata(metadata)
            entries.append(entry)
        except Exception as e:
            logger.warning("Skipping malformed metadata in %s: %s", case_subdir.name, e)
            continue

    entries.sort(key=lambda e: e.created_at, reverse=True)
    return entries


def add_case_to_index(
    metadata: FaultCaseMetadata,
    cases_dir: Path | None = None,
    index_file: Path | None = None,
) -> None:
    if cases_dir is None:
        cases_dir = CASES_DIR

    cases_dir.mkdir(parents=True, exist_ok=True)

    entry = CaseIndexEntry.from_metadata(metadata)
    entries = get_index(cases_dir=cases_dir, index_file=index_file)

    existing = [i for i, e in enumerate(entries) if e.case_id == entry.case_id]
    if existing:
        entries[existing[0]] = entry
    else:
        entries.insert(0, entry)

    effective_index_file = index_file if index_file is not None else cases_dir / "index.yaml"
    write_index(entries, effective_index_file)


def get_index(
    cases_dir: Path | None = None,
    index_file: Path | None = None,
) -> list[CaseIndexEntry]:
    if cases_dir is None:
        cases_dir = CASES_DIR
    if index_file is None:
        index_file = cases_dir / "index.yaml"

    if not index_file.exists():
        return []

    with index_file.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data:
        return []

    return [CaseIndexEntry.from_dict(entry) for entry in data]


def write_index(entries: list[CaseIndexEntry], index_file: Path) -> None:
    index_file.parent.mkdir(parents=True, exist_ok=True)
    data = [entry.to_dict() for entry in entries]
    with index_file.open("w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
