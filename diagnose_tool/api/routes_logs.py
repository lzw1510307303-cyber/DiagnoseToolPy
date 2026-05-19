"""Log search and compression API routes."""

from __future__ import annotations

import logging
import re
import time
from collections import OrderedDict
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from diagnose_tool.retrieval.log_compressor import (
    CompressedLogGroup,
    LogEntry,
    compress_logs,
)

router = APIRouter(prefix="/api/logs", tags=["logs"])

# ---------------------------------------------------------------------------
# Request/Response Models
# ---------------------------------------------------------------------------


class LogSearchRequest(BaseModel):
    """Request model for log search."""

    query: str = Field(min_length=1, description="Search keyword")
    compress: Literal["message", "thread_id", "both", "none"] = Field(
        default="none", description="Compression type"
    )
    file_paths: list[str] | None = Field(default=None, description="Limit to specific file paths")
    level_filter: list[str] | None = Field(default=None, description="Filter by log levels")
    time_range: dict[str, str] | None = Field(default=None, description="Time range filter")
    max_results: int = Field(default=1000, ge=1, le=10000, description="Max results to return")


class LogSearchResponse(BaseModel):
    """Response model for log search."""

    total_count: int
    compressed_count: int
    compress_type: str
    results: list
    search_time_ms: int


class LogExpandRequest(BaseModel):
    """Request model for expanding a compressed log group."""

    group_id: str = Field(min_length=1, description="Group ID to expand")


class LogExpandResponse(BaseModel):
    """Response model for expanding a compressed log group."""

    group_id: str
    logs: list[LogEntry]


# ---------------------------------------------------------------------------
# In-memory session cache for expand endpoint
# ---------------------------------------------------------------------------

_MAX_SESSION_GROUPS = 100


class SearchSession:
    """LRU cache storing group_id -> list[LogEntry] mappings."""

    def __init__(self) -> None:
        self._cache: OrderedDict[str, list[LogEntry]] = OrderedDict()

    def store(self, group_id: str, logs: list[LogEntry]) -> None:
        """Store logs for a group, evicting oldest if capacity exceeded."""
        if group_id in self._cache:
            self._cache.move_to_end(group_id)
        else:
            if len(self._cache) >= _MAX_SESSION_GROUPS:
                self._cache.popitem(last=False)
        self._cache[group_id] = logs

    def get(self, group_id: str) -> list[LogEntry] | None:
        """Retrieve logs for a group, or None if not found."""
        if group_id in self._cache:
            self._cache.move_to_end(group_id)
            return self._cache[group_id]
        return None

    def clear(self) -> None:
        """Clear all cached data."""
        self._cache.clear()


# Global session store
_search_session = SearchSession()


# ---------------------------------------------------------------------------
# File scanning helpers
# ---------------------------------------------------------------------------

_LOG_EXTENSIONS = (".log", ".txt")


def _is_path_safe(file_path: str, allowed_dir: str) -> bool:
    """Validate that a file path is within the allowed directory.

    Prevents path traversal attacks by ensuring the resolved path
    is under the allowed directory.

    Args:
        file_path: The path to validate.
        allowed_dir: The root directory that file_path must be within.

    Returns:
        True if the path is safe and within allowed_dir, False otherwise.
    """
    try:
        # Resolve both paths to their absolute, normalized form
        allowed = Path(allowed_dir).resolve()
        target = Path(file_path).resolve()

        # Check if the target path is under the allowed directory
        # This prevents both relative path traversal (../) and absolute paths pointing outside
        return str(target).startswith(str(allowed))
    except (OSError, ValueError):
        return False
_TIMESTAMP_RE = re.compile(
    r"(\d{4}-\d{2}-\d{2}[T ]?\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)"
)


def _is_log_file(path: str) -> bool:
    """Check if a file path has a log file extension."""
    return any(path.endswith(ext) for ext in _LOG_EXTENSIONS)


def _match_line(line: str, query: str, case_sensitive: bool = False) -> bool:
    """Check if a line matches the search query."""
    search_in = line if case_sensitive else line.lower()
    target = query if case_sensitive else query.lower()
    return target in search_in


def _parse_level(line: str) -> str | None:
    """Extract log level from a line if present."""
    upper = line.upper()
    for level in ("ERROR", "WARN", "WARNING", "INFO", "DEBUG", "TRACE"):
        if level in upper:
            if level == "WARNING":
                return "WARN"
            return level
    return None


def _extract_timestamp(line: str) -> str | None:
    """Extract first timestamp pattern from a line."""
    match = _TIMESTAMP_RE.search(line)
    return match.group(1) if match else None


def _scan_and_search(
    directory: str | None,
    file_paths: list[str] | None,
    query: str,
    level_filter: list[str] | None,
    max_results: int,
) -> list[LogEntry]:
    """Scan log files and search for matching lines.

    Args:
        directory: Base directory to scan (if file_paths not provided).
        file_paths: Explicit list of file paths to search.
        query: Keyword to search for.
        level_filter: Only include lines with these log levels.
        max_results: Maximum number of results to return.

    Returns:
        List of matching LogEntry objects.
    """
    import os

    results: list[LogEntry] = []
    visited_files: set[str] = set()

    # Determine which files to search
    files_to_search: list[str] = []
    if file_paths:
        # Use the log directory as the allowed base directory for path validation
        allowed_dir = _LOG_DIRECTORY if directory is None else directory
        for fp in file_paths:
            # Validate path is within allowed directory (prevent path traversal)
            if not _is_path_safe(fp, allowed_dir):
                logging.warning(f"file_paths contains path outside allowed directory (skipped): {fp}")
                continue
            if not os.path.isfile(fp):
                logging.warning(f"file_paths contains non-file path (skipped): {fp}")
                continue
            if _is_log_file(fp):
                files_to_search.append(fp)
    elif directory:
        for root, _, filenames in os.walk(directory):
            for fname in filenames:
                if _is_log_file(fname):
                    files_to_search.append(os.path.join(root, fname))

    for file_path in files_to_search:
        if file_path in visited_files:
            continue
        visited_files.add(file_path)

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                for line_no, raw_line in enumerate(f, start=1):
                    raw_line = raw_line.rstrip("\r\n")
                    if not raw_line.strip():
                        continue

                    # Match query
                    if not _match_line(raw_line, query):
                        continue

                    # Parse level
                    level = _parse_level(raw_line)
                    if level_filter and level and level not in level_filter:
                        continue

                    # Extract timestamp
                    timestamp = _extract_timestamp(raw_line)

                    # Build LogEntry
                    entry = LogEntry(
                        id=f"{os.path.basename(file_path)}:{line_no}",
                        timestamp=timestamp,
                        level=level,
                        module=None,
                        thread=None,
                        logger=None,
                        message=raw_line,  # Use raw as message for now
                        raw=raw_line,
                        file_path=file_path,
                        line_no=line_no,
                    )
                    results.append(entry)

                    if len(results) >= max_results:
                        return results

        except (OSError, IOError):
            # Skip files that can't be read
            continue

    return results


# Default log directory (configurable in production)
_DEFAULT_LOG_DIR = "."
_LOG_DIRECTORY = _DEFAULT_LOG_DIR


def set_log_directory(path: str) -> None:
    """Set the default log directory for searches."""
    global _LOG_DIRECTORY
    _LOG_DIRECTORY = path


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------


@router.post("/search", response_model=LogSearchResponse)
def search_logs(request: LogSearchRequest) -> LogSearchResponse:
    """Search logs and optionally compress results.

    Args:
        request: LogSearchRequest with query and compression options.

    Returns:
        LogSearchResponse with compressed results.
    """
    start_time = time.time()

    # Perform the search
    logs = _scan_and_search(
        directory=_LOG_DIRECTORY,
        file_paths=request.file_paths,
        query=request.query,
        level_filter=request.level_filter,
        max_results=request.max_results,
    )

    total_count = len(logs)

    # Apply compression
    compressed = compress_logs(logs, request.compress)

    # Count compressed groups
    if request.compress == "none":
        compressed_count = len(compressed)
    else:
        compressed_count = len(compressed)

    # Store groups in session for expand endpoint (only for compressed results)
    if request.compress != "none":
        _search_session.clear()  # Clear old session data
        # Build log dict once for O(1) lookups instead of O(n) per group
        log_dict: dict[str, LogEntry] = {log.id: log for log in logs}
        for item in compressed:
            if isinstance(item, CompressedLogGroup):
                # Use dict lookup O(1) per log_id instead of scanning all logs
                group_logs = [
                    log_dict[log_id]
                    for log_id in item.log_ids
                    if log_id in log_dict
                ]
                # Re-sort by timestamp
                group_logs = sorted(group_logs, key=lambda l: l.timestamp or "")
                _search_session.store(item.group_id, group_logs)

    elapsed_ms = int((time.time() - start_time) * 1000)

    return LogSearchResponse(
        total_count=total_count,
        compressed_count=compressed_count,
        compress_type=request.compress,
        results=compressed,  # type: ignore
        search_time_ms=elapsed_ms,
    )


@router.post("/expand", response_model=LogExpandResponse)
def expand_group(request: LogExpandRequest) -> LogExpandResponse:
    """Expand a compressed log group by ID.

    Args:
        request: LogExpandRequest with group_id.

    Returns:
        LogExpandResponse with all logs in the group.
    """
    logs = _search_session.get(request.group_id)
    if logs is None:
        raise HTTPException(
            status_code=404,
            detail=f"Group not found: {request.group_id}. The session may have expired.",
        )

    return LogExpandResponse(group_id=request.group_id, logs=logs)
