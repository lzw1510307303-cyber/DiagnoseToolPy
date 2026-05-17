"""Multiline log event candidate merging."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Iterator

from diagnose_tool.analyzer.reader import LogLine


LOG_START_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")
STACK_CONTINUATION_RE = re.compile(
    r"^(\s+at\s+|\s*\.\.\.\s+\d+\s+more|Caused by:|Suppressed:|\s*java\.|\s*[a-zA-Z_$][\w.$]*Exception[:\s]|\s*[a-zA-Z_$][\w.$]*Error[:\s])"
)


@dataclass(frozen=True)
class LogEventCandidate:
    """Raw merged log event candidate."""

    file_path: str
    start_line_no: int
    end_line_no: int
    raw: str


def merge_multiline_events(lines: Iterable[LogLine]) -> Iterator[LogEventCandidate]:
    """Merge physical log lines into raw event candidates."""

    current: list[LogLine] = []

    for line in lines:
        if is_log_start(line.raw):
            if current:
                yield _build_event(current)
            current = [line]
            continue

        if not current:
            current = [line]
            continue

        if is_continuation_line(line.raw):
            current.append(line)
            continue

        current.append(line)

    if current:
        yield _build_event(current)


def is_log_start(raw: str) -> bool:
    """Return whether a raw line looks like a new log event start."""

    return bool(LOG_START_RE.match(raw))


def is_continuation_line(raw: str) -> bool:
    """Return whether a raw line looks like a Java stack trace continuation."""

    return bool(STACK_CONTINUATION_RE.match(raw)) or raw.startswith(("\t", " "))


def _build_event(lines: list[LogLine]) -> LogEventCandidate:
    first = lines[0]
    last = lines[-1]
    return LogEventCandidate(
        file_path=first.file_path,
        start_line_no=first.line_no,
        end_line_no=last.line_no,
        raw="\n".join(line.raw for line in lines),
    )
