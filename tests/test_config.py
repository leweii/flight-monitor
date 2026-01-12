# tests/test_config.py
import pytest
from src.config import load_config, expand_env_vars

def test_expand_env_vars_with_default():
    result = expand_env_vars("${MISSING_VAR:-default_value}")
    assert result == "default_value"

def test_expand_env_vars_with_env(monkeypatch):
    monkeypatch.setenv("TEST_VAR", "actual_value")
    result = expand_env_vars("${TEST_VAR:-default}")
    assert result == "actual_value"

def test_load_config_returns_dict(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
database:
  host: localhost
  port: 5432
routes: []
""")
    config = load_config(str(config_file))
    assert config["database"]["host"] == "localhost"
    assert config["database"]["port"] == 5432
