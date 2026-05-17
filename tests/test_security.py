from pathlib import Path

import pytest

from diagnose_tool.core.security import PathValidationError, validate_server_directory


def test_validate_server_directory_accepts_allowed_directory(tmp_path: Path) -> None:
    allowed_root = tmp_path / "input"
    requested = allowed_root / "logs"
    requested.mkdir(parents=True)

    assert validate_server_directory(requested, (allowed_root,)) == requested.resolve()


def test_validate_server_directory_rejects_outside_directory(tmp_path: Path) -> None:
    allowed_root = tmp_path / "input"
    outside = tmp_path / "outside"
    allowed_root.mkdir()
    outside.mkdir()

    with pytest.raises(PathValidationError, match="outside allowed input roots"):
        validate_server_directory(outside, (allowed_root,))


def test_validate_server_directory_rejects_traversal_attempt(tmp_path: Path) -> None:
    allowed_root = tmp_path / "input"
    outside = tmp_path / "outside"
    allowed_root.mkdir()
    outside.mkdir()

    traversal = allowed_root / ".." / "outside"

    with pytest.raises(PathValidationError, match="outside allowed input roots"):
        validate_server_directory(traversal, (allowed_root,))


def test_validate_server_directory_rejects_sibling_prefix_path(tmp_path: Path) -> None:
    allowed_root = tmp_path / "input"
    sibling = tmp_path / "input-other"
    allowed_root.mkdir()
    sibling.mkdir()

    with pytest.raises(PathValidationError, match="outside allowed input roots"):
        validate_server_directory(sibling, (allowed_root,))


def test_validate_server_directory_rejects_file(tmp_path: Path) -> None:
    allowed_root = tmp_path / "input"
    allowed_root.mkdir()
    file_path = allowed_root / "app.log"
    file_path.write_text("log", encoding="utf-8")

    with pytest.raises(PathValidationError, match="not a directory"):
        validate_server_directory(file_path, (allowed_root,))
