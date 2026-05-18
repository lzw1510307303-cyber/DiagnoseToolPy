"""tests/integration/conftest.py — Shared fixtures for integration tests."""

from __future__ import annotations

import gzip
from pathlib import Path

import pytest


@pytest.fixture
def tmp_data_dir(tmp_path: Path) -> dict[str, Path]:
    """Create a complete data/ directory structure under tmp_path.

    Returns:
        dict with keys: data_dir, cases_dir, output_dir, input_dir
    """
    data = tmp_path / "data"
    data.mkdir()
    (data / "cases").mkdir()
    (data / "output").mkdir()
    (data / "input").mkdir()
    return {
        "data_dir": data,
        "cases_dir": data / "cases",
        "output_dir": data / "output",
        "input_dir": data / "input",
    }


@pytest.fixture
def sample_log_dir(tmp_path: Path) -> Path:
    """Create a temp directory with various log file types.

    Directory structure:
        app-20260516.log      # Standard log with ERROR/WARN
        worker-01.out         # Standard output
        error.log.gz          # gzip compressed log
        readme.md             # Unsupported extension (should be ignored)
    """
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    # Standard application log
    (log_dir / "app-20260516.log").write_text(
        "2026-05-16 10:00:01 INFO [[app]main] [com.demo.App] started\n"
        "2026-05-16 10:01:01 ERROR [[app]worker] [com.demo.Service] connection refused\n"
        "2026-05-16 10:01:02 WARN [[app]worker] [com.demo.Service] retry attempt 1\n"
        "2026-05-16 10:01:03 ERROR [[app]worker] [com.demo.Service] connection refused\n"
        "2026-05-16 10:02:00 INFO [[app]main] [com.demo.App] shutdown\n",
        encoding="utf-8",
    )

    # Standard output
    (log_dir / "worker-01.out").write_text(
        "2026-05-16 10:00:05 INFO [worker-01] task started\n"
        "2026-05-16 10:01:10 ERROR [worker-01] null pointer exception\n",
        encoding="utf-8",
    )

    # gzip compressed log
    gz_path = log_dir / "error.log.gz"
    with gzip.open(gz_path, mode="wt", encoding="utf-8") as f:
        f.write(
            "2026-05-16 09:55:00 ERROR [[sys]collector] timeout after 30s\n"
            "2026-05-16 09:55:01 WARN [[sys]collector] retrying...\n"
        )

    # Unsupported extension
    (log_dir / "readme.md").write_text("# Readme", encoding="utf-8")

    return log_dir


@pytest.fixture
def rules_dir(tmp_path: Path) -> Path:
    """Create a temp directory with test classification rules.

    rules/error-database.yaml
    rules/warn-retry.yaml
    """
    rules = tmp_path / "rules"
    rules.mkdir()

    (rules / "error-database.yaml").write_text(
        "category: database_error\n"
        "display_name: 数据库错误\n"
        "severity: ERROR\n"
        "keywords:\n"
        "  - connection refused\n"
        "  - null pointer\n"
        "  - timeout after\n",
        encoding="utf-8",
    )

    (rules / "warn-retry.yaml").write_text(
        "category: retry_warning\n"
        "display_name: 重试警告\n"
        "severity: WARN\n"
        "keywords:\n"
        "  - retry\n"
        "  - retrying\n",
        encoding="utf-8",
    )

    return rules


@pytest.fixture
def sample_task_output(tmp_data_dir: dict[str, Path]) -> dict[str, Path]:
    """Create a task output directory with evidence-pack.md and retrieval-query.json.

    This is used for diagnosis pipeline tests.
    """
    task_id = "DIAG-001"
    output_dir = tmp_data_dir["output_dir"] / task_id
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "artifacts").mkdir()

    # evidence-pack.md
    (output_dir / "evidence-pack.md").write_text(
        "# 日志诊断证据包\n\n"
        "## 1. 基本信息\n\n"
        "- 任务ID：DIAG-001\n"
        "- ERROR数量：3\n"
        "- WARN数量：1\n\n"
        "## 2. 异常分类统计\n\n"
        "| 分类 | 数量 |\n"
        "| database_error | 2 |\n"
        "| retry_warning | 1 |\n",
        encoding="utf-8",
    )

    # retrieval-query.json
    import json
    (output_dir / "retrieval-query.json").write_text(
        json.dumps({
            "query_text": "database connection refused error",
            "extracted_keywords": ["connection refused", "database"],
            "error_signatures": ["ConnectionRefusedError"],
            "keywords": ["connection refused", "database"],
            "components": [],
            "fault_modes": [],
            "exception_classes": ["ConnectionRefusedError"],
            "stack_symbols": [],
            "log_templates": [],
            "task_id": task_id,
            "summary": None,
        }),
        encoding="utf-8",
    )

    return {
        "task_id": task_id,
        "output_dir": output_dir,
        "data_dir": tmp_data_dir["data_dir"],
        "cases_dir": tmp_data_dir["cases_dir"],
    }
