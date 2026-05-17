from pathlib import Path

import pytest

from diagnose_tool.core.config import ConfigError, load_config


def test_load_config_reads_valid_yaml(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_path = config_dir / "app.yaml"
    config_path.write_text(
        """
app:
  name: DiagnoseToolPy
  version: 0.1.0
server:
  host: 127.0.0.1
  port: 18080
paths:
  allowed_input_roots:
    - data/input
  data_dir: data
""".strip(),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.name == "DiagnoseToolPy"
    assert config.version == "0.1.0"
    assert config.host == "127.0.0.1"
    assert config.port == 18080
    assert config.allowed_input_roots == ((tmp_path / "data/input").resolve(),)
    assert config.data_dir == (tmp_path / "data").resolve()


def test_load_config_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="Config file not found"):
        load_config(tmp_path / "missing.yaml")


def test_load_config_rejects_malformed_yaml(tmp_path: Path) -> None:
    config_path = tmp_path / "app.yaml"
    config_path.write_text("app: [", encoding="utf-8")

    with pytest.raises(ConfigError, match="Invalid YAML config"):
        load_config(config_path)
