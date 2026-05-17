"""Evidence pack, key logs, and raw samples generation."""

from __future__ import annotations

import json
from typing import Any

from diagnose_tool.analyzer.classifier import ClassificationResult
from diagnose_tool.analyzer.header_parser import ParsedLogRecord
from diagnose_tool.analyzer.output_context import OutputContext
from diagnose_tool.analyzer.sampling import BoundedSamples


MAX_SAMPLES_PER_CATEGORY = 20


def generate_evidence_pack(
    output_context: OutputContext,
    records: list[ParsedLogRecord],
    classifications: list[ClassificationResult],
    error_count: int,
    warn_count: int,
    timeline_buckets: list[dict],
) -> None:
    output_context.ensure_directories()

    stats = _build_classification_stats(classifications)
    top_exceptions = _get_top_exceptions(classifications)
    key_features = _extract_key_features(classifications)

    content = _build_evidence_pack_markdown(
        output_context, stats, error_count, warn_count, timeline_buckets, key_features, top_exceptions
    )

    (output_context.output_dir() / "evidence-pack.md").write_text(content, encoding="utf-8")


def generate_key_logs(
    output_context: OutputContext,
    records: list[ParsedLogRecord],
    classifications: list[ClassificationResult],
) -> None:
    output_context.ensure_directories()
    samples = BoundedSamples(max_per_category=MAX_SAMPLES_PER_CATEGORY)

    _collect_key_log_samples(records, classifications, samples)

    lines = []
    for category in sorted(samples.get_all().keys()):
        for item in samples.get(category):
            lines.append(f"[{category}] {item}")
    if not lines:
        lines.append("(no key logs found)")

    (output_context.output_dir() / "key-logs.txt").write_text("\n".join(lines), encoding="utf-8")


def generate_raw_samples(
    output_context: OutputContext,
    records: list[ParsedLogRecord],
    classifications: list[ClassificationResult],
) -> None:
    output_context.ensure_directories()
    samples = BoundedSamples(max_per_category=MAX_SAMPLES_PER_CATEGORY)

    _collect_raw_samples(records, classifications, samples)

    output_path = output_context.artifacts_dir() / "raw-samples.jsonl"
    with output_path.open("w", encoding="utf-8") as f:
        for category, items in samples.get_all().items():
            for item in items:
                f.write(json.dumps({
                    "category": category,
                    "raw": item,
                    "timestamp": "",
                    "level": "",
                }, ensure_ascii=False) + "\n")


def _build_classification_stats(classifications: list[ClassificationResult]) -> dict[str, int]:
    stats: dict[str, int] = {}
    for c in classifications:
        if c.category != "unknown":
            stats[c.category] = stats.get(c.category, 0) + 1
    return stats


def _get_top_exceptions(classifications: list[ClassificationResult], top_n: int = 5) -> list[tuple[str, str, int]]:
    counts: dict[str, tuple[str, int]] = {}
    for c in classifications:
        if c.category != "unknown":
            if c.category not in counts:
                counts[c.category] = (c.display_name, 0)
            counts[c.category] = (c.display_name, counts[c.category][1] + 1)
    sorted_counts = sorted(counts.items(), key=lambda x: x[1][1], reverse=True)
    return [(cat, name, count) for cat, (name, count) in sorted_counts[:top_n]]


def _extract_key_features(classifications: list[ClassificationResult]) -> dict[str, Any]:
    exception_classes = set()
    keywords: set[str] = set()

    for c in classifications:
        if c.category != "unknown" and c.rule:
            for kw in c.rule.keywords:
                keywords.add(kw)

    return {
        "exception_classes": sorted(exception_classes),
        "keywords": sorted(keywords),
    }


def _build_evidence_pack_markdown(
    output_context: OutputContext,
    stats: dict[str, int],
    error_count: int,
    warn_count: int,
    timeline_buckets: list[dict],
    key_features: dict[str, Any],
    top_exceptions: list[tuple[str, str, int]],
) -> str:
    lines = [
        "# 日志诊断证据包",
        "",
        "## 1. 基本信息",
        "",
        f"- 任务ID：{output_context.task_id}",
        f"- 日志目录：{output_context.source_path}",
        f"- 文件数量：{output_context.total_files}",
        f"- 日志总大小：{output_context.total_bytes}",
        "- 分析模式：STANDARD",
        f"- ERROR数量：{error_count}",
        f"- WARN数量：{warn_count}",
        "",
        "## 2. 异常分类统计",
        "",
        "| 分类 | 数量 | 严重级别 |",
        "|---|---:|---|",
    ]

    for cat, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"| {cat} | {count} | ERROR |")

    if not stats:
        lines.append("| (无) | 0 | ERROR |")

    lines.extend([
        "",
        "## 3. 异常时间线",
        "",
        "| 时间窗口 | ERROR | WARN | 主要异常 |",
        "|---|---:|---:|---|",
    ])

    for bucket in timeline_buckets[-10:]:
        lines.append(f"| {bucket.get('timestamp', '')} | {bucket.get('error_count', 0)} | {bucket.get('warn_count', 0)} | |")

    lines.extend([
        "",
        "## 4. 关键日志特征",
        "",
        "### 异常类名",
    ])

    if key_features.get("exception_classes"):
        for ec in key_features["exception_classes"]:
            lines.append(f"- {ec}")
    else:
        lines.append("- (无)")

    lines.extend([
        "",
        "### 错误短语",
    ])

    if key_features.get("keywords"):
        for kw in list(key_features["keywords"])[:10]:
            lines.append(f"- {kw}")
    else:
        lines.append("- (无)")

    lines.extend([
        "",
        "## 5. Top 关键异常样例",
        "",
        "```text",
    ])

    if top_exceptions:
        for cat, name, count in top_exceptions:
            lines.append(f"{name} ({count}次)")
    else:
        lines.append("(无)")

    lines.extend([
        "```",
        "",
        "## 6. 相似案例召回",
        "",
        "以下案例仅作为参考，不代表当前故障一定相同。",
        "",
        "## 7. 诊断要求",
        "",
        "请判断：",
        "",
        "1. 最可能的根因是什么？",
        "2. 是否存在级联故障？",
        "3. 影响范围是什么？",
        "4. 建议优先排查哪些模块？",
        "5. 有哪些临时规避和长期优化建议？",
    ])

    return "\n".join(lines)


def _collect_key_log_samples(
    records: list[ParsedLogRecord],
    classifications: list[ClassificationResult],
    samples: BoundedSamples,
) -> None:
    class_map: dict[int, ClassificationResult] = {}
    for i, c in enumerate(classifications):
        class_map[i] = c

    for i, record in enumerate(records):
        c = class_map.get(i)
        if c and c.category != "unknown":
            if not samples.is_full(c.category):
                samples.add(c.category, record.raw[:200])


def _collect_raw_samples(
    records: list[ParsedLogRecord],
    classifications: list[ClassificationResult],
    samples: BoundedSamples,
) -> None:
    class_map: dict[int, ClassificationResult] = {}
    for i, c in enumerate(classifications):
        class_map[i] = c

    for i, record in enumerate(records):
        c = class_map.get(i)
        if c and c.category != "unknown":
            if not samples.is_full(c.category):
                samples.add(c.category, record.raw)
