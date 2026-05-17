"""Output context for analysis task results."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class OutputContext:
    task_id: str
    source_path: str
    created_at: str
    started_at: str | None = None
    finished_at: str | None = None
    total_files: int = 0
    processed_files: int = 0
    total_bytes: int = 0
    processed_bytes: int = 0
    error_count: int = 0
    warn_count: int = 0

    def output_dir(self) -> Path:
        return Path("data/output") / self.task_id

    def artifacts_dir(self) -> Path:
        return self.output_dir() / "artifacts"

    def ensure_directories(self) -> None:
        self.output_dir().mkdir(parents=True, exist_ok=True)
        self.artifacts_dir().mkdir(parents=True, exist_ok=True)
