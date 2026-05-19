"""Log compression algorithm for deduplication and grouping."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from typing import Literal

# Null thread sentinel value for grouping
_NULL_THREAD_KEY = "__null_thread__"


@dataclass
class LogEntry:
    """A single log entry with parsed fields."""

    id: str
    timestamp: str | None
    level: str | None
    module: str | None
    thread: str | None
    logger: str | None
    message: str | None
    raw: str
    file_path: str | None
    line_no: int | None


@dataclass
class CompressedLogGroup:
    """A compressed group of log entries."""

    group_id: str
    group_type: Literal["message", "thread_id", "both"]
    key_value: str
    count: int
    first_log: LogEntry
    last_log: LogEntry
    timestamps: dict[str, str]
    log_ids: list[str]
    level: str


def _compute_message_hash(message: str | None, raw: str) -> str:
    """Compute a 16-character MD5 hash from the first 200 characters of message or raw.

    Args:
        message: The log message content (may be None).
        raw: The raw log line (fallback when message is None).

    Returns:
        The first 16 characters of the MD5 hex digest.
    """
    content = (message or raw)[:200]
    return hashlib.md5(content.encode("utf-8")).hexdigest()[:16]


def _sort_by_timestamp(logs: list[LogEntry]) -> list[LogEntry]:
    """Sort logs by timestamp, treating None as empty string."""
    return sorted(logs, key=lambda log: log.timestamp or "")


def _build_group(
    logs: list[LogEntry],
    group_type: Literal["message", "thread_id", "both"],
    key_value: str,
) -> CompressedLogGroup:
    """Build a CompressedLogGroup from a list of logs in the same group.

    Args:
        logs: List of log entries in this group (should already be sorted by time).
        group_type: The type of compression used.
        key_value: The grouping key (thread value or message hash).

    Returns:
        A CompressedLogGroup instance.
    """
    sorted_logs = _sort_by_timestamp(logs)
    first = sorted_logs[0]
    last = sorted_logs[-1]
    return CompressedLogGroup(
        group_id=uuid.uuid4().hex[:12],
        group_type=group_type,
        key_value=key_value,
        count=len(sorted_logs),
        first_log=first,
        last_log=last,
        timestamps={"first": first.timestamp or "", "last": last.timestamp or ""},
        log_ids=[log.id for log in sorted_logs],
        level=first.level or "",
    )


def _group_by_message(logs: list[LogEntry]) -> list[CompressedLogGroup]:
    """Group logs by message hash (first 200 chars).

    Args:
        logs: List of log entries to group.

    Returns:
        List of compressed log groups sorted by first_log.timestamp.
    """
    hash_map: dict[str, list[LogEntry]] = {}
    for log in logs:
        h = _compute_message_hash(log.message, log.raw)
        if h not in hash_map:
            hash_map[h] = []
        hash_map[h].append(log)

    groups = []
    for h, group_logs in hash_map.items():
        groups.append(_build_group(group_logs, "message", h))

    return sorted(groups, key=lambda g: g.timestamps["first"])


def _group_by_thread(logs: list[LogEntry]) -> list[CompressedLogGroup]:
    """Group logs by thread field.

    Args:
        logs: List of log entries to group.

    Returns:
        List of compressed log groups sorted by first_log.timestamp.
    """
    thread_map: dict[str, list[LogEntry]] = {}
    for log in logs:
        key = log.thread if log.thread is not None else _NULL_THREAD_KEY
        if key not in thread_map:
            thread_map[key] = []
        thread_map[key].append(log)

    groups = []
    for thread_key, group_logs in thread_map.items():
        groups.append(_build_group(group_logs, "thread_id", thread_key))

    return sorted(groups, key=lambda g: g.timestamps["first"])


def _group_by_both(logs: list[LogEntry]) -> list[CompressedLogGroup]:
    """Nested grouping: thread_id outer, message hash inner.

    Args:
        logs: List of log entries to group.

    Returns:
        List of compressed log groups sorted by first_log.timestamp.
    """
    # First group by thread
    thread_map: dict[str, list[LogEntry]] = {}
    for log in logs:
        key = log.thread if log.thread is not None else _NULL_THREAD_KEY
        if key not in thread_map:
            thread_map[key] = []
        thread_map[key].append(log)

    # Then within each thread group, group by message hash
    groups: list[CompressedLogGroup] = []
    for thread_key, thread_logs in thread_map.items():
        msg_hash_map: dict[str, list[LogEntry]] = {}
        for log in thread_logs:
            h = _compute_message_hash(log.message, log.raw)
            if h not in msg_hash_map:
                msg_hash_map[h] = []
            msg_hash_map[h].append(log)

        for msg_hash, msg_logs in msg_hash_map.items():
            key_value = f"{thread_key}:{msg_hash}"
            groups.append(_build_group(msg_logs, "both", key_value))

    return sorted(groups, key=lambda g: g.timestamps["first"])


def compress_logs(
    logs: list[LogEntry],
    compress_type: Literal["message", "thread_id", "both", "none"] = "none",
) -> list[LogEntry | CompressedLogGroup]:
    """Compress a list of log entries according to compress_type.

    Args:
        logs: List of log entries to compress.
        compress_type: One of 'message', 'thread_id', 'both', 'none'.

    Returns:
        If compress_type is 'none', returns the original logs sorted by timestamp.
        Otherwise returns a list of CompressedLogGroup sorted by first_log.timestamp.
    """
    if compress_type == "none":
        return _sort_by_timestamp(logs)

    if compress_type == "message":
        return _group_by_message(logs)
    elif compress_type == "thread_id":
        return _group_by_thread(logs)
    elif compress_type == "both":
        return _group_by_both(logs)

    # Should not reach here due to Pydantic validation, but treat as none
    return _sort_by_timestamp(logs)
