"""Tests for the complex header parser."""

from __future__ import annotations

from __future__ import annotations

from diagnose_tool.analyzer.header_parser import (
    ParseStatus,
    _parse_module_thread,
    _strip_brackets,
    parse_log_record,
    scan_balanced_bracket_groups,
)


class TestScanBalancedBracketGroups:
    def test_single_bracket_group(self):
        result = list(scan_balanced_bracket_groups("[com.demo.OrderService] query"))
        assert result == ["[com.demo.OrderService]"]

    def test_nested_double_bracket(self):
        result = list(scan_balanced_bracket_groups("[[order-core]worker-1] rest"))
        assert result == ["[[order-core]worker-1]"]

    def test_multiple_bracket_groups(self):
        result = list(scan_balanced_bracket_groups("[[order-core]worker-1] [com.demo.OrderService] query"))
        assert result == ["[[order-core]worker-1]", "[com.demo.OrderService]"]

    def test_no_bracket_groups(self):
        result = list(scan_balanced_bracket_groups("plain text message"))
        assert result == []

    def test_text_between_bracket_groups(self):
        result = list(scan_balanced_bracket_groups("[a] [b] between text"))
        assert result == ["[a]", "[b]"]


class TestStripBrackets:
    def test_double_bracket(self):
        assert _strip_brackets("[[order-core]]") == "[order-core]"

    def test_single_bracket(self):
        assert _strip_brackets("[order-core]") == "order-core"

    def test_no_brackets(self):
        assert _strip_brackets("order-core") == "order-core"


class TestParseModuleThread:
    def test_nested_bracket_parses_module_and_thread(self):
        module, thread = _parse_module_thread("[[order-core]worker-1]")
        assert module == "order-core"
        assert thread == "worker-1"

    def test_single_bracket_becomes_module(self):
        module, thread = _parse_module_thread("[order-core]")
        assert module == "order-core"
        assert thread is None

    def test_none_returns_none_none(self):
        module, thread = _parse_module_thread(None)
        assert (module, thread) == (None, None)


class TestParseLogRecord:
    def test_full_nested_header_parses_all_fields(self):
        record = parse_log_record(
            "2026-05-16 10:01:01.123 ERROR [[order-core]worker-1] [com.demo.OrderService] query failed"
        )
        assert record.timestamp == "2026-05-16 10:01:01.123"
        assert record.level == "ERROR"
        assert record.module == "order-core"
        assert record.thread == "worker-1"
        assert record.logger == "com.demo.OrderService"
        assert record.message == "query failed"
        assert record.raw == "2026-05-16 10:01:01.123 ERROR [[order-core]worker-1] [com.demo.OrderService] query failed"
        assert record.parse_status == ParseStatus.FULL

    def test_missing_logger_returns_partial(self):
        record = parse_log_record("2026-05-16 10:01:01.123 ERROR [[order-core]worker-1] query failed")
        assert record.parse_status == ParseStatus.PARTIAL
        assert record.module == "order-core"
        assert record.thread == "worker-1"
        assert record.logger is None
        assert record.message == "query failed"

    def test_no_brackets_returns_partial(self):
        record = parse_log_record("2026-05-16 10:01:01.123 ERROR some message")
        assert record.parse_status == ParseStatus.PARTIAL
        assert record.timestamp == "2026-05-16 10:01:01.123"
        assert record.level == "ERROR"
        assert record.module is None
        assert record.logger is None
        assert record.message == "some message"

    def test_malformed_line_returns_raw(self):
        record = parse_log_record("not a log line at all")
        assert record.parse_status == ParseStatus.RAW
        assert record.timestamp is None
        assert record.level is None
        assert record.raw == "not a log line at all"

    def test_missing_timestamp_level_returns_raw(self):
        record = parse_log_record("[com.demo.OrderService] query failed")
        assert record.parse_status == ParseStatus.RAW
        assert record.raw == "[com.demo.OrderService] query failed"

    def test_raw_preserved_on_partial_parse(self):
        record = parse_log_record("2026-05-16 10:01:01.123 ERROR [[order-core]worker-1] query failed")
        assert record.raw == "2026-05-16 10:01:01.123 ERROR [[order-core]worker-1] query failed"

    def test_source_location_passed_through(self):
        record = parse_log_record(
            "2026-05-16 10:01:01.123 ERROR [[order-core]worker-1] [com.demo.OrderService] query failed",
            file_path="/var/log/app.log",
            line_no=42,
        )
        assert record.file_path == "/var/log/app.log"
        assert record.line_no == 42

    def test_warn_level_parses(self):
        record = parse_log_record("2026-05-16 10:01:01.123 WARN [[order-core]worker-1] [com.demo.OrderService] warn message")
        assert record.level == "WARN"
        assert record.parse_status == ParseStatus.FULL

    def test_info_level_parses(self):
        record = parse_log_record("2026-05-16 10:01:01.123 INFO [svc] [c.l.Service] info message")
        assert record.level == "INFO"
        assert record.module == "svc"
        assert record.parse_status == ParseStatus.FULL

    def test_logger_without_message(self):
        record = parse_log_record("2026-05-16 10:01:01.123 ERROR [[core]t1] [com.demo.Service]")
        assert record.logger == "com.demo.Service"
        assert record.message is None
        assert record.parse_status == ParseStatus.PARTIAL