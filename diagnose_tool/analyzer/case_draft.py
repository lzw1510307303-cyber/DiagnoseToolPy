"""Case draft and metadata generation."""

from __future__ import annotations

import re
import yaml

from diagnose_tool.analyzer.classifier import ClassificationResult
from diagnose_tool.analyzer.header_parser import ParsedLogRecord
from diagnose_tool.analyzer.output_context import OutputContext


def generate_case_draft(
    output_context: OutputContext,
    top_category: ClassificationResult | None,
    records: list[ParsedLogRecord],
) -> None:
    output_context.ensure_directories()

    title = _derive_title(top_category)

    content = _build_case_draft_markdown(output_context, title, top_category, records)
    (output_context.output_dir() / "case-draft.md").write_text(content, encoding="utf-8")

    metadata = _build_case_metadata(output_context, title, top_category, records)
    (output_context.output_dir() / "case-metadata-draft.yaml").write_text(
        yaml.dump(metadata, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def _derive_title(top_category: ClassificationResult | None) -> str:
    if top_category and top_category.category != "unknown":
        return f"{top_category.display_name}导致的故障"
    return "未知故障"


def _build_case_draft_markdown(
    output_context: OutputContext,
    title: str,
    top_category: ClassificationResult | None,
    records: list[ParsedLogRecord],
) -> str:
    lines = [
        f"# {title}",
        "",
        "## 基本信息",
        "",
        f"- 任务ID：{output_context.task_id}",
        f"- 日志目录：{output_context.source_path}",
        f"- 分析时间：{output_context.created_at}",
        "",
        "## 故障描述",
        "",
        "(待填写) 请描述观察到的故障现象",
        "",
        "## 可能根因",
        "",
        "(待填写) 请分析可能的根本原因",
        "",
        "## 影响范围",
        "",
        "(待填写) 请评估影响范围",
        "",
        "## 关键证据",
        "",
        "- 证据包：evidence-pack.md",
        "- 关键日志：key-logs.txt",
        "",
    ]

    return "\n".join(lines)


def _build_case_metadata(
    output_context: OutputContext,
    title: str,
    top_category: ClassificationResult | None,
    records: list[ParsedLogRecord],
) -> dict:
    slug = re.sub(r"[^\w\s-]", "", title.lower()).replace(" ", "-")
    slug = re.sub(r"-+", "-", slug).strip("-")

    tags = []
    components = []
    exception_classes = []
    key_phrases = []
    fault_modes = []

    if top_category and top_category.category != "unknown":
        fault_modes.append(top_category.category)
        if top_category.rule:
            key_phrases.extend(top_category.rule.keywords[:5])

    for record in records[:50]:
        if record.logger:
            components.append(record.logger)
        if record.module:
            components.append(record.module)

    exception_classes = list(set(exception_classes))[:10]
    components = list(set(components))[:10]

    return {
        "case_id": f"CASE-{output_context.task_id.replace('-', '').upper()}",
        "title": title,
        "slug": slug[:50],
        "source_type": "auto",
        "status": "draft",
        "confidence": "unconfirmed",
        "tags": sorted(set(tags)),
        "components": sorted(set(components)),
        "fault_modes": sorted(set(fault_modes)),
        "exception_classes": sorted(set(exception_classes)),
        "key_phrases": sorted(set(key_phrases)),
    }
