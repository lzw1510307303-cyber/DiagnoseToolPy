"""Streaming log readers."""

from __future__ import annotations

import gzip
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, TextIO


@dataclass(frozen=True)
class LogLine:
    """One physical log line with source location."""

    file_path: str
    line_no: int
    raw: str


def read_log_lines(path: str | Path, encoding: str = "utf-8") -> Iterator[LogLine]:
    """Stream a normal text or gzip log file line by line."""

    file_path = Path(path)
    if file_path.suffix.lower() == ".gz":
        with gzip.open(file_path, mode="rt", encoding=encoding, errors="replace") as file:
            yield from _iter_lines(file_path, file)
        return

    with file_path.open("r", encoding=encoding, errors="replace") as file:
        yield from _iter_lines(file_path, file)


def _iter_lines(path: Path, file: TextIO) -> Iterator[LogLine]:
    resolved = str(path.resolve())
    for line_no, line in enumerate(file, start=1):
        yield LogLine(file_path=resolved, line_no=line_no, raw=line.rstrip("\n"))
