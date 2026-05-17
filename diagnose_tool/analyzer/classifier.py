"""YAML rule-based log event classifier."""

from __future__ import annotations

import yaml
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ClassificationRule:
    category: str
    display_name: str
    severity: str
    keywords: list[str]


@dataclass(frozen=True)
class ClassificationResult:
    category: str
    display_name: str
    severity: str
    matched_keyword: str | None
    rule: ClassificationRule | None


UNKNOWN_RESULT = ClassificationResult(
    category="unknown",
    display_name="Unknown",
    severity="UNKNOWN",
    matched_keyword=None,
    rule=None,
)


class RuleLoadError(Exception):
    pass


def load_rules_from_dir(rules_dir: Path) -> list[ClassificationRule]:
    rules = []
    if not rules_dir.exists():
        return rules
    for path in sorted(rules_dir.iterdir()):
        if path.suffix.lower() in (".yaml", ".yml"):
            rules.append(_load_rule_file(path))
    return rules


def _load_rule_file(path: Path) -> ClassificationRule:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise RuleLoadError(f"Malformed YAML in {path}: {e}") from e

    if not isinstance(data, dict):
        raise RuleLoadError(f"Expected dict in {path}, got {type(data).__name__}")

    for field in ("category", "display_name", "severity", "keywords"):
        if field not in data:
            raise RuleLoadError(f"Missing required field '{field}' in {path}")

    if not isinstance(data["keywords"], list):
        raise RuleLoadError(f"'keywords' must be a list in {path}")

    for kw in data["keywords"]:
        if not isinstance(kw, str):
            raise RuleLoadError(f"Each keyword must be a string in {path}")

    return ClassificationRule(
        category=str(data["category"]),
        display_name=str(data["display_name"]),
        severity=str(data["severity"]),
        keywords=data["keywords"],
    )


def classify_event(
    text: str,
    rules: list[ClassificationRule],
) -> ClassificationResult:
    for rule in rules:
        for keyword in rule.keywords:
            if keyword.lower() in text.lower():
                return ClassificationResult(
                    category=rule.category,
                    display_name=rule.display_name,
                    severity=rule.severity,
                    matched_keyword=keyword,
                    rule=rule,
                )
    return UNKNOWN_RESULT
