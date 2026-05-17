"""Tests for the rule-based classifier."""

from __future__ import annotations

import pytest
from pathlib import Path

from diagnose_tool.analyzer.classifier import (
    ClassificationRule,
    RuleLoadError,
    classify_event,
    load_rules_from_dir,
    UNKNOWN_RESULT,
)


class TestLoadRulesFromDir:
    def test_loads_yaml_files(self, tmp_path: Path):
        rule_file = tmp_path / "test-rule.yaml"
        rule_file.write_text(
            "category: test-cat\ndisplay_name: Test Category\nseverity: ERROR\nkeywords:\n  - test-keyword\n",
            encoding="utf-8",
        )
        rules = load_rules_from_dir(tmp_path)
        assert len(rules) == 1
        assert rules[0].category == "test-cat"
        assert rules[0].display_name == "Test Category"
        assert rules[0].severity == "ERROR"
        assert "test-keyword" in rules[0].keywords

    def test_ignores_non_yaml_files(self, tmp_path: Path):
        (tmp_path / "readme.txt").write_text("not a rule", encoding="utf-8")
        rule_file = tmp_path / "test-rule.yaml"
        rule_file.write_text(
            "category: test\ndisplay_name: Test\nseverity: ERROR\nkeywords:\n  - kw\n",
            encoding="utf-8",
        )
        rules = load_rules_from_dir(tmp_path)
        assert len(rules) == 1

    def test_missing_required_field_raises(self, tmp_path: Path):
        rule_file = tmp_path / "bad-rule.yaml"
        rule_file.write_text(
            "category: test\ndisplay_name: Test\nseverity: ERROR\n",
            encoding="utf-8",
        )
        with pytest.raises(RuleLoadError, match="Missing required field 'keywords'"):
            load_rules_from_dir(tmp_path)

    def test_malformed_yaml_raises(self, tmp_path: Path):
        rule_file = tmp_path / "bad-rule.yaml"
        rule_file.write_text("category: [", encoding="utf-8")
        with pytest.raises(RuleLoadError, match="Malformed YAML"):
            load_rules_from_dir(tmp_path)

    def test_keywords_not_list_raises(self, tmp_path: Path):
        rule_file = tmp_path / "bad-rule.yaml"
        rule_file.write_text(
            "category: test\ndisplay_name: Test\nseverity: ERROR\nkeywords: not-a-list\n",
            encoding="utf-8",
        )
        with pytest.raises(RuleLoadError, match="'keywords' must be a list"):
            load_rules_from_dir(tmp_path)

    def test_empty_dir_returns_empty_list(self, tmp_path: Path):
        rules = load_rules_from_dir(tmp_path)
        assert rules == []

    def test_nonexistent_dir_returns_empty_list(self):
        rules = load_rules_from_dir(Path("/nonexistent/path"))
        assert rules == []


class TestClassifyEvent:
    def test_keyword_match_returns_category(self):
        rule = ClassificationRule(
            category="null-pointer",
            display_name="Null Pointer",
            severity="ERROR",
            keywords=["NullPointerException", "null pointer"],
        )
        result = classify_event("Caused by: java.lang.NullPointerException", [rule])
        assert result.category == "null-pointer"
        assert result.display_name == "Null Pointer"
        assert result.severity == "ERROR"
        assert result.matched_keyword == "NullPointerException"

    def test_raw_text_match(self):
        rule = ClassificationRule(
            category="io-error",
            display_name="I/O Error",
            severity="ERROR",
            keywords=["IOException", "FileNotFound"],
        )
        result = classify_event("java.io.FileNotFoundException: /path/to/file", [rule])
        assert result.category == "io-error"
        assert result.matched_keyword == "FileNotFound"

    def test_no_match_returns_unknown(self):
        rule = ClassificationRule(
            category="test",
            display_name="Test",
            severity="INFO",
            keywords=["specific-keyword"],
        )
        result = classify_event("Some unrelated log message", [rule])
        assert result.category == "unknown"
        assert result.matched_keyword is None
        assert result.rule is None

    def test_first_matched_rule_returns(self):
        rule1 = ClassificationRule(
            category="first",
            display_name="First",
            severity="ERROR",
            keywords=["error"],
        )
        rule2 = ClassificationRule(
            category="second",
            display_name="Second",
            severity="WARN",
            keywords=["error"],
        )
        result = classify_event("An error occurred", [rule1, rule2])
        assert result.category == "first"
        assert result.matched_keyword == "error"

    def test_case_insensitive_match(self):
        rule = ClassificationRule(
            category="test",
            display_name="Test",
            severity="ERROR",
            keywords=["EXCEPTION"],
        )
        result = classify_event("java.lang exception occurred", [rule])
        assert result.category == "test"
        assert result.matched_keyword == "EXCEPTION"

    def test_empty_rules_returns_unknown(self):
        result = classify_event("Any message here", [])
        assert result == UNKNOWN_RESULT

    def test_unknown_result_fields(self):
        assert UNKNOWN_RESULT.category == "unknown"
        assert UNKNOWN_RESULT.display_name == "Unknown"
        assert UNKNOWN_RESULT.severity == "UNKNOWN"
        assert UNKNOWN_RESULT.matched_keyword is None
        assert UNKNOWN_RESULT.rule is None
