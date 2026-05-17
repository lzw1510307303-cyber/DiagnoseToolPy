"""Server-side path validation helpers."""

from __future__ import annotations

from pathlib import Path


class PathValidationError(ValueError):
    """Raised when a requested server path is not allowed."""


def validate_server_directory(path: str | Path, allowed_roots: list[Path] | tuple[Path, ...]) -> Path:
    """Return a resolved directory path only when it is under an allowed root."""

    requested = Path(path).resolve()
    if not requested.exists():
        raise PathValidationError("Requested path does not exist")
    if not requested.is_dir():
        raise PathValidationError("Requested path is not a directory")

    resolved_roots = tuple(Path(root).resolve() for root in allowed_roots)
    if not resolved_roots:
        raise PathValidationError("No allowed input roots configured")

    if any(_is_relative_to(requested, root) for root in resolved_roots):
        return requested

    raise PathValidationError("Requested path is outside allowed input roots")


def is_server_directory_allowed(path: str | Path, allowed_roots: list[Path] | tuple[Path, ...]) -> bool:
    """Return whether a requested server directory is allowed."""

    try:
        validate_server_directory(path, allowed_roots)
    except PathValidationError:
        return False
    return True


def _is_relative_to(path: Path, root: Path) -> bool:
    return path == root or root in path.parents
