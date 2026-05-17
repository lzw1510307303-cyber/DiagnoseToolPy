"""Generate prompt context for AI diagnosis with reference markers."""

from __future__ import annotations

from diagnose_tool.retrieval.query_builder import RetrievalQuery

MAX_DEFAULT = 3


def generate_prompt_context(
    query: RetrievalQuery,
    cases: list[tuple[str, float, dict]],
    max_cases: int = MAX_DEFAULT,
) -> str:
    """Generate markdown prompt context with reference-only markers.

    Args:
        query: The retrieval query.
        cases: List of (case_id, score, metadata_dict) tuples.
        max_cases: Maximum number of cases to include.

    Returns:
        Markdown string with reference markers.
    """
    if not cases:
        return _empty_context()

    selected = cases[:max_cases]

    lines = [
        "## Historical Case References (References Only)",
        "",
        "The following cases are provided as **references only**. "
        "They are **NOT assumed to have the same root cause** as the current issue.",
        "",
    ]

    for case_id, score, metadata in selected:
        title = metadata.get("title", case_id)
        summary = metadata.get("summary", "No summary available.")
        fault_modes = metadata.get("fault_modes", [])
        components = metadata.get("components", [])
        tags = metadata.get("tags", [])

        lines.append(f"### Case: {title}")
        lines.append(f"- **Case ID**: {case_id}")
        lines.append(f"- **Relevance Score**: {score:.2f}")
        lines.append(f"- **Summary**: {summary}")

        if fault_modes:
            lines.append(f"- **Fault Modes**: {', '.join(fault_modes)}")
        if components:
            lines.append(f"- **Components**: {', '.join(components)}")
        if tags:
            lines.append(f"- **Tags**: {', '.join(tags)}")

        lines.append("")

    lines.append("*Note: Historical cases are references only. "
                 "Analyze the current issue independently.*")

    return "\n".join(lines)


def _empty_context() -> str:
    return (
        "## Historical Case References\n\n"
        "No similar historical cases found.\n\n"
        "*Note: Historical cases are references only. "
        "Analyze the current issue independently.*\n"
    )
