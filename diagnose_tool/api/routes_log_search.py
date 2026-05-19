"""Multi-keyword log search API routes with compression support."""

from __future__ import annotations

import re
import hashlib
from collections import defaultdict
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/logs", tags=["logs"])


class LogSearchRequest(BaseModel):
    """Log search request model."""

    keywords: list[str] = Field(default_factory=list, max_length=20)
    match_mode: str = Field(default="AND", pattern="^(AND|OR)$")
    exclude_keywords: list[str] = Field(default_factory=list, max_length=5)
    log_levels: list[str] = Field(default_factory=list)
    start_time: str | None = Field(default=None)
    end_time: str | None = Field(default=None)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    compress: bool = Field(default=False, description="Enable log compression/deduplication")
    compress_by: str = Field(default="message", pattern="^(message|thread_id|both)$")


class LogRecord(BaseModel):
    """Single log record."""

    id: str
    timestamp: str
    level: str
    source: str
    message: str
    thread_id: str | None = Field(default=None, description="Thread identifier for grouping")
    highlights: dict[str, list[str]] | None = None


class CompressedLogGroup(BaseModel):
    """A compressed group of similar logs."""

    count: int = Field(description="Number of logs in this group")
    first_log: LogRecord = Field(description="First log in the group (representative)")
    timestamps: list[str] = Field(description="All timestamps in this group")
    log_ids: list[str] = Field(description="All log IDs in this group")


class LogSearchResponse(BaseModel):
    """Log search response."""

    total: int
    total_after_compress: int | None = Field(default=None, description="Total after compression")
    page: int
    page_size: int
    results: list[LogRecord | CompressedLogGroup]
    compressed: bool = Field(default=False, description="Whether compression is applied")


class LogExportRequest(BaseModel):
    """Log export request with compression support."""

    keywords: list[str]
    match_mode: str = "AND"
    exclude_keywords: list[str] = Field(default_factory=list)
    log_levels: list[str] = Field(default_factory=list)
    start_time: str | None = None
    end_time: str | None = None
    compress: bool = False
    compress_by: str = "message"


# Simulated log storage (replace with real storage in production)
_SIMULATED_LOGS: list[dict[str, Any]] = [
    {
        "id": "log-001",
        "timestamp": "2026-05-19T10:00:00+08:00",
        "level": "ERROR",
        "source": "app.service",
        "thread_id": "thread-pool-1",
        "message": "Database connection timeout occurred",
    },
    {
        "id": "log-002",
        "timestamp": "2026-05-19T10:00:01+08:00",
        "level": "WARNING",
        "source": "app.service",
        "thread_id": "thread-pool-1",
        "message": "Slow query detected: SELECT * FROM users",
    },
    {
        "id": "log-003",
        "timestamp": "2026-05-19T10:00:02+08:00",
        "level": "INFO",
        "source": "app.controller",
        "thread_id": "thread-pool-2",
        "message": "User login successful: user123",
    },
    {
        "id": "log-004",
        "timestamp": "2026-05-19T10:00:03+08:00",
        "level": "ERROR",
        "source": "app.database",
        "thread_id": "thread-pool-1",
        "message": "Database connection timeout occurred",
    },
    {
        "id": "log-005",
        "timestamp": "2026-05-19T10:00:04+08:00",
        "level": "ERROR",
        "source": "app.service",
        "thread_id": "thread-pool-2",
        "message": "API timeout when calling external service",
    },
    {
        "id": "log-006",
        "timestamp": "2026-05-19T10:00:05+08:00",
        "level": "ERROR",
        "source": "app.database",
        "thread_id": "thread-pool-1",
        "message": "Database connection timeout occurred",
    },
    {
        "id": "log-007",
        "timestamp": "2026-05-19T10:00:06+08:00",
        "level": "INFO",
        "source": "app.controller",
        "thread_id": "thread-pool-3",
        "message": "User logout: user456",
    },
    {
        "id": "log-008",
        "timestamp": "2026-05-19T10:00:07+08:00",
        "level": "WARNING",
        "source": "app.service",
        "thread_id": "thread-pool-1",
        "message": "Slow query detected: SELECT * FROM orders",
    },
]


def _escape_special_chars(text: str) -> str:
    """Escape special regex characters in text."""
    special_chars = r".*+?^${}()|[\]\\"
    return "".join(f"\\{c}" if c in special_chars else c for c in text)


def _highlight_text(text: str, keywords: list[str]) -> dict[str, list[str]]:
    """Generate highlight markers for keywords in text."""
    highlights: dict[str, list[str]] = {}
    text_lower = text.lower()

    for keyword in keywords:
        if keyword.lower() in text_lower:
            escaped = _escape_special_chars(keyword)
            pattern = re.compile(escaped, re.IGNORECASE)
            matches = pattern.findall(text)
            if matches:
                highlights[keyword] = matches

    return highlights


def _normalize_message_for_compress(message: str) -> str:
    """Normalize message for compression by removing variable parts."""
    # Remove timestamps, UUIDs, numbers that might vary
    normalized = re.sub(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[^\s]*', '<TS>', message)
    normalized = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '<UUID>', normalized)
    normalized = re.sub(r'\d{3,}', '<NUM>', normalized)
    return normalized.strip()


def _compute_compression_key(log: dict[str, Any], compress_by: str) -> str:
    """Compute compression key for a log entry."""
    if compress_by == "thread_id":
        return f"thread:{log.get('thread_id', 'unknown')}"
    elif compress_by == "message":
        normalized_msg = _normalize_message_for_compress(log.get('message', ''))
        return f"msg:{normalized_msg}"
    else:  # "both"
        thread_id = log.get('thread_id', 'unknown')
        normalized_msg = _normalize_message_for_compress(log.get('message', ''))
        return f"thread:{thread_id}:msg:{normalized_msg}"


def _compress_logs(logs: list[dict[str, Any]], compress_by: str) -> list[CompressedLogGroup]:
    """Compress similar logs into groups."""
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for log in logs:
        key = _compute_compression_key(log, compress_by)
        groups[key].append(log)

    compressed_groups: list[CompressedLogGroup] = []
    for key, group_logs in groups.items():
        first = group_logs[0]
        compressed_groups.append(
            CompressedLogGroup(
                count=len(group_logs),
                first_log=LogRecord(
                    id=first["id"],
                    timestamp=first["timestamp"],
                    level=first["level"],
                    source=first["source"],
                    thread_id=first.get("thread_id"),
                    message=first["message"],
                    highlights=None,
                ),
                timestamps=[log["timestamp"] for log in group_logs],
                log_ids=[log["id"] for log in group_logs],
            )
        )

    # Sort by count descending (most frequent first)
    compressed_groups.sort(key=lambda x: x.count, reverse=True)
    return compressed_groups


def _match_log(log: dict[str, Any], request: LogSearchRequest) -> bool:
    """Check if a log entry matches the search criteria."""
    message = log.get("message", "").lower()
    level = log.get("level", "")

    if request.log_levels and level.upper() not in [l.upper() for l in request.log_levels]:
        return False

    for exclude_kw in request.exclude_keywords:
        if exclude_kw.lower() in message:
            return False

    keywords_lower = [kw.lower() for kw in request.keywords]
    if request.match_mode == "AND":
        for keyword in keywords_lower:
            if keyword not in message:
                return False
    else:
        if keywords_lower and not any(kw in message for kw in keywords_lower):
            return False

    return True


def _parse_datetime(dt_str: str | None) -> datetime | None:
    """Parse datetime string with timezone support."""
    if not dt_str:
        return None

    formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue

    raise HTTPException(
        status_code=400,
        detail=f"Invalid datetime format: {dt_str}. Use ISO 8601 format (e.g., 2026-05-19T00:00:00+08:00)",
    )


@router.post("/search", response_model=LogSearchResponse)
def search_logs(request: LogSearchRequest) -> LogSearchResponse:
    """Search logs with multi-keyword support and optional compression."""
    if not request.keywords:
        raise HTTPException(status_code=400, detail="At least one keyword is required")

    if len(request.keywords) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 keywords allowed")

    if len(request.exclude_keywords) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 exclude keywords allowed")

    start_dt = _parse_datetime(request.start_time)
    end_dt = _parse_datetime(request.end_time)

    if start_dt and end_dt:
        if end_dt < start_dt:
            raise HTTPException(status_code=400, detail="end_time must be after start_time")

        if (end_dt - start_dt).days > 30:
            raise HTTPException(status_code=400, detail="Time range cannot exceed 30 days")

    matched_logs: list[dict[str, Any]] = []
    for log in _SIMULATED_LOGS:
        if start_dt or end_dt:
            log_dt = _parse_datetime(log["timestamp"])
            if log_dt:
                if start_dt and log_dt < start_dt:
                    continue
                if end_dt and log_dt > end_dt:
                    continue

        if _match_log(log, request):
            matched_logs.append(log)

    total_before_compress = len(matched_logs)
    total_after_compress = None

    # Apply compression if requested
    if request.compress:
        compressed_groups = _compress_logs(matched_logs, request.compress_by)
        total_after_compress = len(compressed_groups)

        # Paginate compressed results
        start_idx = (request.page - 1) * request.page_size
        end_idx = start_idx + request.page_size
        paginated = compressed_groups[start_idx:end_idx]

        return LogSearchResponse(
            total=total_before_compress,
            total_after_compress=total_after_compress,
            page=request.page,
            page_size=request.page_size,
            results=paginated,
            compressed=True,
        )

    # Generate highlights for non-compressed results
    results: list[LogRecord] = []
    for log in matched_logs:
        highlights = _highlight_text(log["message"], request.keywords)
        results.append(
            LogRecord(
                id=log["id"],
                timestamp=log["timestamp"],
                level=log["level"],
                source=log["source"],
                thread_id=log.get("thread_id"),
                message=log["message"],
                highlights=highlights if highlights else None,
            )
        )

    # Paginate
    total = len(results)
    start_idx = (request.page - 1) * request.page_size
    end_idx = start_idx + request.page_size
    paginated = results[start_idx:end_idx]

    return LogSearchResponse(
        total=total,
        page=request.page,
        page_size=request.page_size,
        results=paginated,
        compressed=False,
    )


@router.get("/history")
def get_keyword_history() -> dict[str, Any]:
    """Get keyword search history."""
    return {"history": []}


@router.get("/export")
def export_logs(
    format: str = Query(default="json", pattern="^(json|csv|txt)$"),
    keywords: str = Query(default=""),
    match_mode: str = Query(default="AND", pattern="^(AND|OR)$"),
) -> dict[str, Any]:
    """Export logs in specified format."""
    return {
        "format": format,
        "message": "Export functionality - implement with real storage",
        "data": [],
    }
