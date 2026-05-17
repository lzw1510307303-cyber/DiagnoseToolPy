"""Application configuration loading."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG_PATH = Path("config/app.yaml")


class ConfigError(RuntimeError):
    """Raised when application configuration cannot be loaded safely."""


@dataclass(frozen=True)
class AppConfig:
    """Runtime settings loaded from YAML."""

    name: str
    version: str
    host: str
    port: int
    allowed_input_roots: tuple[Path, ...]
    data_dir: Path


def load_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> AppConfig:
    """Load application settings from a YAML config file."""

    path = Path(config_path)
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as file:
            raw = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML config: {path}") from exc
    except OSError as exc:
        raise ConfigError(f"Unable to read config file: {path}") from exc

    if not isinstance(raw, dict):
        raise ConfigError("Config root must be a mapping")

    base_dir = path.resolve().parent.parent
    app = _mapping(raw, "app")
    server = _mapping(raw, "server")
    paths = _mapping(raw, "paths")

    name = _string(app, "name")
    version = str(app.get("version", ""))
    host = _string(server, "host")
    port = _int(server, "port")
    data_dir = _resolve_path(paths.get("data_dir", "data"), base_dir)
    allowed_input_roots = _path_list(paths, "allowed_input_roots", base_dir)

    if not allowed_input_roots:
        raise ConfigError("paths.allowed_input_roots must not be empty")

    return AppConfig(
        name=name,
        version=version,
        host=host,
        port=port,
        allowed_input_roots=tuple(allowed_input_roots),
        data_dir=data_dir,
    )


def _mapping(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ConfigError(f"{key} must be a mapping")
    return value


def _string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{key} must be a non-empty string")
    return value


def _int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(f"{key} must be an integer")
    return value


def _path_list(data: dict[str, Any], key: str, base_dir: Path) -> list[Path]:
    value = data.get(key)
    if not isinstance(value, list):
        raise ConfigError(f"{key} must be a list")
    return [_resolve_path(item, base_dir) for item in value]


def _resolve_path(value: Any, base_dir: Path) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError("Configured paths must be non-empty strings")
    path = Path(value)
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()
