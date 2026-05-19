"""Multi-keyword log search API routes."""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, HTTPException, Query
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


class LogRecord(BaseModel):
    """Single log record."""

    id: str
    timestamp: str
    level: str
    source: str
    message: str
    highlights: dict[str, list[str]] | None = None


class LogSearchResponse(BaseModel):
    """Log search response."""

    total: int
    page: int
    page_size: int
    results: list[LogRecord]


class ErrorResponse(BaseModel):
    """Error response."""

    error_code: str
    message: str


# Simulated log storage (replace with real storage in production)
_SIMULATED_LOGS: list[dict[str, Any]] = [
    {
        "id": "log-001",
        "timestamp": "2026-05-19T10:00:00+08:00",
        "level": "ERROR",
        "source": "app.service",
        "message": "Database connection timeout occurred",
    },
    {
        "id": "log-002",
        "timestamp": "2026-05-19T10:01:00+08:00",
        "level": "WARNING",
        "source": "app.service",
        "message": "Slow query detected: SELECT * FROM users",
    },
    {
        "id": "log-003",
        "timestamp": "2026-05-19T10:02:00+08:00",
        "level": "INFO",
        "source": "app.controller",
        "message": "User login successful: user123",
    },
    {
        "id": "log-004",
        "timestamp": "2026-05-19T10:03:00+08:00",
        "level": "ERROR",
        "source": "app.database",
        "message": "Database error: deadlock detected",
    },
    {
        "id": "log-005",
        "timestamp": "2026-05-19T10:04:00+08:00",
        "level": "ERROR",
        "source": "app.service",
        "message": "API timeout when calling external service",
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


def _match_log(log: dict[str, Any], request: LogSearchRequest) -> bool:
    """Check if a log entry matches the search criteria."""
    message = log.get("message", "").lower()
    level = log.get("level", "")

    # Check log level filter
    if request.log_levels and level not in [l.upper() for l in request.log_levels]:
        return False

    # Check exclude keywords
    for exclude_kw in request.exclude_keywords:
        if exclude_kw.lower() in message:
            return False

    # Check keywords based on match mode
    keywords_lower = [kw.lower() for kw in request.keywords]
    if request.match_mode == "AND":
        # All keywords must be present
        for keyword in keywords_lower:
            if keyword not in message:
                return False
    else:  # OR mode
        # At least one keyword must be present
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
    """Search logs with multi-keyword support."""
    # Validate keywords
    if not request.keywords:
        raise HTTPException(status_code=400, detail="At least one keyword is required")

    if len(request.keywords) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 keywords allowed")

    if len(request.exclude_keywords) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 exclude keywords allowed")

    # Validate time range
    start_dt = _parse_datetime(request.start_time)
    end_dt = _parse_datetime(request.end_time)

    if start_dt and end_dt:
        if end_dt < start_dt:
            raise HTTPException(status_code=400, detail="end_time must be after start_time")

        if (end_dt - start_dt).days > 30:
            raise HTTPException(status_code=400, detail="Time range cannot exceed 30 days")

    # Filter logs
    matched_logs: list[dict[str, Any]] = []
    for log in _SIMULATED_LOGS:
        # Time range filter
        if start_dt or end_dt:
            log_dt = _parse_datetime(log["timestamp"])
            if log_dt:
                if start_dt and log_dt < start_dt:
                    continue
                if end_dt and log_dt > end_dt:
                    continue

        # Match criteria
        if _match_log(log, request):
            matched_logs.append(log)

    # Generate highlights
    results: list[LogRecord] = []
    for log in matched_logs:
        highlights = _highlight_text(log["message"], request.keywords)
        results.append(
            LogRecord(
                id=log["id"],
                timestamp=log["timestamp"],
                level=log["level"],
                source=log["source"],
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
    )


@router.get("/history")
def get_keyword_history() -> dict[str, Any]:
    """Get keyword search history."""
    # Placeholder - implement with real storage if needed
    return {"history": []}


@router.get("/export")
def export_logs(
    format: str = Query(default="json", pattern="^(json|csv|txt)$"),
    keywords: str = Query(default=""),
    match_mode: str = Query(default="AND", pattern="^(AND|OR)$"),
) -> dict[str, Any]:
    """Export logs in specified format."""
    # Placeholder implementation
    return {
        "format": format,
        "message": "Export functionality - implement with real storage",
        "data": [],
    }
