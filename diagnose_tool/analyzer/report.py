"""HTML report generation using Jinja2."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from diagnose_tool.analyzer.classifier import ClassificationResult
from diagnose_tool.analyzer.output_context import OutputContext


def generate_summary_html(
    output_context: OutputContext,
    classifications: list[ClassificationResult],
    error_count: int,
    warn_count: int,
    timeline_data: list[dict[str, Any]],
    template_path: Path | None = None,
) -> None:
    output_context.ensure_directories()

    if template_path is None:
        template_path = Path(__file__).parent.parent / "templates" / "report.html"

    env = Environment(loader=FileSystemLoader(template_path.parent))
    template = env.get_template(template_path.name)

    stats = _build_stats(classifications)
    top_exceptions = _build_top_exceptions(classifications)

    html_content = template.render(
        task_id=output_context.task_id,
        source_path=output_context.source_path,
        error_count=error_count,
        warn_count=warn_count,
        classification_stats=stats,
        timeline_data=timeline_data,
        top_exceptions=top_exceptions,
    )

    (output_context.output_dir() / "summary.html").write_text(html_content, encoding="utf-8")


def _build_stats(classifications: list[ClassificationResult]) -> dict[str, int]:
    stats: dict[str, int] = {}
    for c in classifications:
        if c.category != "unknown":
            stats[c.category] = stats.get(c.category, 0) + 1
    return stats


def _build_top_exceptions(classifications: list[ClassificationResult], top_n: int = 5) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for c in classifications:
        if c.category != "unknown":
            counts[c.display_name] = counts.get(c.display_name, 0) + 1
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_counts[:top_n]
