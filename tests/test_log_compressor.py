"""Unit tests for the log compression algorithm."""

from __future__ import annotations

import unittest

from diagnose_tool.retrieval.log_compressor import (
    _compute_message_hash,
    compress_logs,
)
from diagnose_tool.retrieval.log_compressor import LogEntry as LE


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def make_log(
    log_id: str,
    message: str | None = None,
    thread: str | None = None,
    timestamp: str | None = None,
    level: str | None = None,
    raw: str | None = None,
) -> LE:
    """Create a LogEntry for testing."""
    msg = message or raw or ""
    return LE(
        id=log_id,
        timestamp=timestamp,
        level=level,
        module="test",
        thread=thread,
        logger="test",
        message=message,
        raw=raw or msg,
        file_path="/test/app.log",
        line_no=1,
    )


# ---------------------------------------------------------------------------
# _compute_message_hash tests
# ---------------------------------------------------------------------------


class TestComputeMessageHash(unittest.TestCase):
    def test_basic_hash(self) -> None:
        h = _compute_message_hash("hello world", "")
        self.assertEqual(len(h), 16)
        self.assertEqual(h, "5eb63bbbe01eeed0")  # MD5 of "hello world"

    def test_none_message_uses_raw(self) -> None:
        h = _compute_message_hash(None, "fallback text")
        fallback_h = _compute_message_hash("fallback text", "")
        self.assertEqual(h, fallback_h)

    def test_truncation_at_200_chars(self) -> None:
        # 200 chars and 500 chars should produce same hash (truncated to 200)
        short = "a" * 200
        long_msg = "a" * 500
        self.assertEqual(_compute_message_hash(short, ""), _compute_message_hash(long_msg, ""))

    def test_different_content_different_hash(self) -> None:
        h1 = _compute_message_hash("error occurred", "")
        h2 = _compute_message_hash("error resolved", "")
        self.assertNotEqual(h1, h2)


# ---------------------------------------------------------------------------
# compress_logs with compress='none'
# ---------------------------------------------------------------------------


class TestCompressNone(unittest.TestCase):
    def test_empty_list(self) -> None:
        result = compress_logs([], "none")
        self.assertEqual(result, [])

    def test_single_log(self) -> None:
        log = make_log("log-1", "test message", timestamp="2026-05-20 10:00:00")
        result = compress_logs([log], "none")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "log-1")

    def test_sorts_by_timestamp(self) -> None:
        log1 = make_log("log-1", timestamp="2026-05-20 12:00:00")
        log2 = make_log("log-2", timestamp="2026-05-20 10:00:00")
        log3 = make_log("log-3", timestamp="2026-05-20 11:00:00")
        result = compress_logs([log1, log2, log3], "none")
        self.assertEqual([r.id for r in result], ["log-2", "log-3", "log-1"])


# ---------------------------------------------------------------------------
# compress_logs with compress='message'
# ---------------------------------------------------------------------------


class TestCompressMessage(unittest.TestCase):
    def test_empty_list(self) -> None:
        result = compress_logs([], "message")
        self.assertEqual(result, [])

    def test_single_log_no_compression(self) -> None:
        """Single log with count=1 still returns a CompressedLogGroup."""
        log = make_log("log-1", "test message", timestamp="2026-05-20 10:00:00")
        result = compress_logs([log], "message")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].count, 1)
        self.assertEqual(result[0].group_type, "message")

    def test_identical_messages_compress(self) -> None:
        """Same message should compress to 1 group."""
        log1 = make_log("log-1", "Database error", timestamp="2026-05-20 10:00:00")
        log2 = make_log("log-2", "Database error", timestamp="2026-05-20 10:00:01")
        log3 = make_log("log-3", "Database error", timestamp="2026-05-20 10:00:02")
        result = compress_logs([log1, log2, log3], "message")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].count, 3)
        self.assertEqual(result[0].first_log.id, "log-1")
        self.assertEqual(result[0].last_log.id, "log-3")

    def test_different_messages_no_compression(self) -> None:
        """Each different message forms its own group."""
        log1 = make_log("log-1", "Error A", timestamp="2026-05-20 10:00:00")
        log2 = make_log("log-2", "Error B", timestamp="2026-05-20 10:00:01")
        log3 = make_log("log-3", "Error C", timestamp="2026-05-20 10:00:02")
        result = compress_logs([log1, log2, log3], "message")
        self.assertEqual(len(result), 3)
        self.assertEqual([r.count for r in result], [1, 1, 1])

    def test_message_none_uses_raw(self) -> None:
        """When message is None, raw line is used for hashing."""
        log1 = make_log("log-1", message=None, raw="2026-05-20 ERROR raw line 1")
        log2 = make_log("log-2", message=None, raw="2026-05-20 ERROR raw line 1")
        result = compress_logs([log1, log2], "message")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].count, 2)

    def test_sorted_by_timestamp(self) -> None:
        log1 = make_log("log-1", "same msg", timestamp="2026-05-20 12:00:00")
        log2 = make_log("log-2", "same msg", timestamp="2026-05-20 10:00:00")
        log3 = make_log("log-3", "same msg", timestamp="2026-05-20 11:00:00")
        result = compress_logs([log1, log2, log3], "message")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].first_log.id, "log-2")
        self.assertEqual(result[0].last_log.id, "log-1")


# ---------------------------------------------------------------------------
# compress_logs with compress='thread_id'
# ---------------------------------------------------------------------------


class TestCompressThreadId(unittest.TestCase):
    def test_empty_list(self) -> None:
        result = compress_logs([], "thread_id")
        self.assertEqual(result, [])

    def test_single_log(self) -> None:
        log = make_log("log-1", thread="thread-001", timestamp="2026-05-20 10:00:00")
        result = compress_logs([log], "thread_id")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].count, 1)
        self.assertEqual(result[0].group_type, "thread_id")

    def test_same_thread_compress(self) -> None:
        log1 = make_log("log-1", "msg1", thread="thread-001", timestamp="2026-05-20 10:00:00")
        log2 = make_log("log-2", "msg2", thread="thread-001", timestamp="2026-05-20 10:00:01")
        result = compress_logs([log1, log2], "thread_id")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].count, 2)
        self.assertEqual(result[0].key_value, "thread-001")

    def test_different_threads_no_compress(self) -> None:
        log1 = make_log("log-1", "msg", thread="thread-001", timestamp="2026-05-20 10:00:00")
        log2 = make_log("log-2", "msg", thread="thread-002", timestamp="2026-05-20 10:00:01")
        result = compress_logs([log1, log2], "thread_id")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].key_value, "thread-001")
        self.assertEqual(result[1].key_value, "thread-002")

    def test_null_thread_uses_sentinel(self) -> None:
        log1 = make_log("log-1", "msg", thread=None, timestamp="2026-05-20 10:00:00")
        log2 = make_log("log-2", "msg", thread=None, timestamp="2026-05-20 10:00:01")
        result = compress_logs([log1, log2], "thread_id")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].key_value, "__null_thread__")

    def test_null_and_non_null_threads_separate(self) -> None:
        log1 = make_log("log-1", "msg", thread=None, timestamp="2026-05-20 10:00:00")
        log2 = make_log("log-2", "msg", thread="thread-001", timestamp="2026-05-20 10:00:01")
        result = compress_logs([log1, log2], "thread_id")
        self.assertEqual(len(result), 2)
        keys = {r.key_value for r in result}
        self.assertIn("__null_thread__", keys)
        self.assertIn("thread-001", keys)


# ---------------------------------------------------------------------------
# compress_logs with compress='both'
# ---------------------------------------------------------------------------


class TestCompressBoth(unittest.TestCase):
    def test_empty_list(self) -> None:
        result = compress_logs([], "both")
        self.assertEqual(result, [])

    def test_single_log(self) -> None:
        log = make_log(
            "log-1", "message", thread="thread-001", timestamp="2026-05-20 10:00:00"
        )
        result = compress_logs([log], "both")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].count, 1)
        self.assertEqual(result[0].group_type, "both")
        self.assertTrue(result[0].key_value.startswith("thread-001:"))

    def test_nested_grouping(self) -> None:
        # thread-001 with 2 different messages -> 2 groups
        # thread-002 with 1 message -> 1 group
        log1 = make_log("log-1", "msgA", thread="thread-001", timestamp="2026-05-20 10:00:00")
        log2 = make_log("log-2", "msgB", thread="thread-001", timestamp="2026-05-20 10:00:01")
        log3 = make_log("log-3", "msgA", thread="thread-002", timestamp="2026-05-20 10:00:02")
        result = compress_logs([log1, log2, log3], "both")
        self.assertEqual(len(result), 3)  # 2 in thread-001 (different msgs) + 1 in thread-002
        for group in result:
            self.assertEqual(group.count, 1)
            self.assertEqual(group.group_type, "both")

    def test_same_thread_same_message_compress(self) -> None:
        log1 = make_log("log-1", "same msg", thread="thread-001", timestamp="2026-05-20 10:00:00")
        log2 = make_log("log-2", "same msg", thread="thread-001", timestamp="2026-05-20 10:00:01")
        result = compress_logs([log1, log2], "both")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].count, 2)

    def test_null_thread_sentinel_in_both(self) -> None:
        log1 = make_log("log-1", "msg", thread=None, timestamp="2026-05-20 10:00:00")
        log2 = make_log("log-2", "msg", thread=None, timestamp="2026-05-20 10:00:01")
        result = compress_logs([log1, log2], "both")
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].key_value.startswith("__null_thread__:"))


# ---------------------------------------------------------------------------
# group_id uniqueness
# ---------------------------------------------------------------------------


class TestGroupIdUniqueness(unittest.TestCase):
    def test_each_group_gets_unique_id(self) -> None:
        log1 = make_log("log-1", "msgA", timestamp="2026-05-20 10:00:00")
        log2 = make_log("log-2", "msgB", timestamp="2026-05-20 10:00:01")
        result = compress_logs([log1, log2], "message")
        self.assertEqual(len(result), 2)
        self.assertNotEqual(result[0].group_id, result[1].group_id)
        self.assertEqual(len(result[0].group_id), 12)
        self.assertEqual(len(result[1].group_id), 12)


# ---------------------------------------------------------------------------
# log_ids preservation
# ---------------------------------------------------------------------------


class TestLogIdsPreservation(unittest.TestCase):
    def test_log_ids_collected_correctly(self) -> None:
        log1 = make_log("log-1", "same", timestamp="2026-05-20 10:00:00")
        log2 = make_log("log-2", "same", timestamp="2026-05-20 10:00:01")
        log3 = make_log("log-3", "same", timestamp="2026-05-20 10:00:02")
        result = compress_logs([log1, log2, log3], "message")
        self.assertEqual(result[0].log_ids, ["log-1", "log-2", "log-3"])


# ---------------------------------------------------------------------------
# level and timestamps fields
# ---------------------------------------------------------------------------


class TestGroupMetadata(unittest.TestCase):
    def test_level_from_first_log(self) -> None:
        log1 = make_log("log-1", "msg", level="ERROR", timestamp="2026-05-20 10:00:00")
        log2 = make_log("log-2", "msg", level="DEBUG", timestamp="2026-05-20 10:00:01")
        result = compress_logs([log1, log2], "message")
        self.assertEqual(result[0].level, "ERROR")

    def test_timestamps_first_and_last(self) -> None:
        log1 = make_log("log-1", "msg", timestamp="2026-05-20 10:00:00")
        log2 = make_log("log-2", "msg", timestamp="2026-05-20 10:05:00")
        log3 = make_log("log-3", "msg", timestamp="2026-05-20 10:03:00")
        result = compress_logs([log1, log2, log3], "message")
        self.assertEqual(result[0].timestamps["first"], "2026-05-20 10:00:00")
        self.assertEqual(result[0].timestamps["last"], "2026-05-20 10:05:00")


# ---------------------------------------------------------------------------
# First 200 chars hash collision detection
# ---------------------------------------------------------------------------


class TestHashCollisionBoundary(unittest.TestCase):
    def test_same_first_200_chars_same_hash(self) -> None:
        """If first 200 chars are identical, hashes should be identical."""
        short1 = "x" * 200 + " different tail 1"
        short2 = "x" * 200 + " different tail 2"
        h1 = _compute_message_hash(short1, "")
        h2 = _compute_message_hash(short2, "")
        self.assertEqual(h1, h2)

    def test_different_within_first_200_chars_different_hash(self) -> None:
        """Different content within first 200 chars should produce different hashes."""
        msg1 = "a" * 199 + "b" + "x" * 300
        msg2 = "a" * 199 + "c" + "x" * 300
        h1 = _compute_message_hash(msg1, "")
        h2 = _compute_message_hash(msg2, "")
        self.assertNotEqual(h1, h2)


if __name__ == "__main__":
    unittest.main()
