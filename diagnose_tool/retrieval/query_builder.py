"""Build retrieval query from analyzer output or JSON file."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field


class RetrievalQuery(BaseModel):
    task_id: str | None = None
    summary: str | None = None
    components: list[str] = Field(default_factory=list)
    fault_modes: list[str] = Field(default_factory=list)
    exception_classes: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    stack_symbols: list[str] = Field(default_factory=list)
    log_templates: list[str] = Field(default_factory=list)


def build_retrieval_query(source: str | Path) -> RetrievalQuery:
    """Build retrieval query from file path or analyzer output directory.

    Args:
        source: Path to retrieval-query.json or to a directory containing it.

    Returns:
        RetrievalQuery object with all fields populated.

    Raises:
        FileNotFoundError: If retrieval-query.json not found.
        ValueError: If JSON is malformed.
    """
    path = Path(source)
    if path.is_file():
        query_path = path
    else:
        query_path = path / "retrieval-query.json"

    if not query_path.exists():
        raise FileNotFoundError(f"retrieval-query.json not found at {query_path}")

    try:
        data = json.loads(query_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Malformed JSON in {query_path}: {e}") from e

    return RetrievalQuery(**data)
