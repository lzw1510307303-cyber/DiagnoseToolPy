from diagnose_tool.analyzer.multiline import LogEventCandidate, merge_multiline_events
from diagnose_tool.analyzer.reader import LogLine


def _line(line_no: int, raw: str) -> LogLine:
    return LogLine(file_path="app.log", line_no=line_no, raw=raw)


def test_merge_multiline_events_groups_java_stack_trace() -> None:
    events = list(
        merge_multiline_events(
            [
                _line(1, "2026-05-16 10:01:01 ERROR [[task]worker] [com.demo.Task] failed"),
                _line(2, "java.lang.RuntimeException: failed"),
                _line(3, "    at com.demo.A.method(A.java:10)"),
                _line(4, "Caused by: java.io.IOException: disk"),
                _line(5, "    at com.demo.B.method(B.java:20)"),
                _line(6, "2026-05-16 10:01:02 INFO [[task]worker] [com.demo.Task] done"),
            ]
        )
    )

    assert events == [
        LogEventCandidate(
            file_path="app.log",
            start_line_no=1,
            end_line_no=5,
            raw=(
                "2026-05-16 10:01:01 ERROR [[task]worker] [com.demo.Task] failed\n"
                "java.lang.RuntimeException: failed\n"
                "    at com.demo.A.method(A.java:10)\n"
                "Caused by: java.io.IOException: disk\n"
                "    at com.demo.B.method(B.java:20)"
            ),
        ),
        LogEventCandidate(
            file_path="app.log",
            start_line_no=6,
            end_line_no=6,
            raw="2026-05-16 10:01:02 INFO [[task]worker] [com.demo.Task] done",
        ),
    ]


def test_merge_multiline_events_preserves_leading_malformed_line() -> None:
    events = list(
        merge_multiline_events(
            [
                _line(1, "    at com.demo.Before.start(Before.java:1)"),
                _line(2, "2026-05-16 10:01:01 INFO [[task]worker] [com.demo.Task] start"),
            ]
        )
    )

    assert events[0] == LogEventCandidate(
        file_path="app.log",
        start_line_no=1,
        end_line_no=1,
        raw="    at com.demo.Before.start(Before.java:1)",
    )
    assert events[1].start_line_no == 2


def test_merge_multiline_events_yields_multiple_events_in_order() -> None:
    iterator = merge_multiline_events(
        iter(
            [
                _line(1, "2026-05-16 10:01:01 INFO [[task]worker] [com.demo.Task] one"),
                _line(2, "continued detail"),
                _line(3, "2026-05-16 10:01:02 INFO [[task]worker] [com.demo.Task] two"),
                _line(4, "2026-05-16 10:01:03 INFO [[task]worker] [com.demo.Task] three"),
            ]
        )
    )

    first = next(iterator)
    second = next(iterator)
    third = next(iterator)

    assert first.start_line_no == 1
    assert first.end_line_no == 2
    assert second.start_line_no == 3
    assert third.start_line_no == 4


def test_merge_multiline_events_empty_input_yields_no_events() -> None:
    assert list(merge_multiline_events([])) == []
