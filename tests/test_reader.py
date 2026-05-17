from pathlib import Path

from diagnose_tool.analyzer.reader import LogLine, read_log_lines


FIXTURES = Path(__file__).parent / "fixtures"


def test_read_text_log_streams_line_records() -> None:
    path = FIXTURES / "reader-sample.log"

    records = list(read_log_lines(path))

    assert records == [
        LogLine(
            file_path=str(path.resolve()),
            line_no=1,
            raw="2026-05-16 10:01:01 INFO [[demo]main] [com.demo.App] started",
        ),
        LogLine(
            file_path=str(path.resolve()),
            line_no=2,
            raw="2026-05-16 10:01:02 ERROR [[demo]main] [com.demo.App] failed",
        ),
    ]


def test_read_empty_text_log_yields_no_records() -> None:
    assert list(read_log_lines(FIXTURES / "empty.log")) == []


def test_read_gzip_log_streams_line_records() -> None:
    path = FIXTURES / "reader-sample.log.gz"

    records = list(read_log_lines(path))

    assert [record.raw for record in records] == [
        "2026-05-16 10:01:01 INFO [[demo]main] [com.demo.App] started",
        "2026-05-16 10:01:02 ERROR [[demo]main] [com.demo.App] failed",
    ]
    assert [record.line_no for record in records] == [1, 2]
    assert all(record.file_path == str(path.resolve()) for record in records)


def test_read_log_replaces_invalid_bytes_and_continues() -> None:
    records = list(read_log_lines(FIXTURES / "reader-invalid-utf8.log"))

    assert len(records) == 2
    assert "\ufffd" in records[0].raw
    assert records[1].raw == "next line"
