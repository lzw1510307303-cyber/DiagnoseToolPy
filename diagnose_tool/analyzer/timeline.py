"""Timeline generation for analysis results."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from diagnose_tool.analyzer.output_context import OutputContext


@dataclass
class TimelineBucket:
    timestamp: str
    error_count: int = 0
    warn_count: int = 0


def aggregate_timeline(
    records: list[dict],
    timestamp_field: str = "timestamp",
    level_field: str = "level",
    bucket_minutes: int = 1,
) -> list[TimelineBucket]:
    if not records:
        return []

    buckets: dict[str, TimelineBucket] = defaultdict(
        lambda: TimelineBucket(timestamp="", error_count=0, warn_count=0)
    )

    for record in records:
        ts = record.get(timestamp_field) or ""
        level = (record.get(level_field) or "").upper()

        if not ts:
            continue

        bucket_key = _get_bucket_key(ts, bucket_minutes)
        if bucket_key not in buckets:
            buckets[bucket_key] = TimelineBucket(timestamp=bucket_key)

        bucket = buckets[bucket_key]
        if level == "ERROR":
            bucket.error_count += 1
        elif level in ("WARN", "WARNING"):
            bucket.warn_count += 1

    return [buckets[key] for key in sorted(buckets.keys())]


def _get_bucket_key(timestamp: str, bucket_minutes: int) -> str:
    try:
        dt_str = timestamp[:19]
        dt_str = dt_str.replace(" ", "T")
        year = int(dt_str[0:4])
        month = int(dt_str[5:7])
        day = int(dt_str[8:10])
        hour = int(dt_str[11:13])
        minute = int(dt_str[14:16])
        second = int(dt_str[17:19])

        from datetime import datetime
        dt = datetime(year, month, day, hour, minute, second)
        bucket_dt = dt.replace(second=0, microsecond=0)
        total_minutes = bucket_dt.hour * 60 + bucket_dt.minute
        total_minutes = (total_minutes // bucket_minutes) * bucket_minutes
        bucket_dt = bucket_dt.replace(
            hour=total_minutes // 60, minute=total_minutes % 60
        )
        return bucket_dt.strftime("%Y-%m-%dT%H:%M:%S")
    except (ValueError, IndexError):
        return timestamp[:19]


def write_timeline_json(
    buckets: list[TimelineBucket],
    output_path: Path,
) -> None:
    data = [
        {
            "timestamp": b.timestamp,
            "error_count": b.error_count,
            "warn_count": b.warn_count,
        }
        for b in buckets
    ]
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def generate_timeline(
    records: list[dict],
    output_context: OutputContext,
    timestamp_field: str = "timestamp",
    level_field: str = "level",
    bucket_minutes: int = 1,
) -> list[TimelineBucket]:
    buckets = aggregate_timeline(records, timestamp_field, level_field, bucket_minutes)
    output_context.ensure_directories()
    write_timeline_json(buckets, output_context.artifacts_dir() / "timeline.json")
    return buckets
