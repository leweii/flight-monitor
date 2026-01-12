# tests/test_cli.py
import pytest
from click.testing import CliRunner
from src.cli import cli

def test_cli_list_routes(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
database:
  host: localhost
routes:
  - name: 厦门-新加坡
    origin: XMN
    destination: SIN
    check_interval: 1h
""")

    runner = CliRunner()
    result = runner.invoke(cli, ['list-routes', '--config', str(config_file)])

    assert result.exit_code == 0
    assert "厦门-新加坡" in result.output
    assert "XMN" in result.output

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])

    assert result.exit_code == 0
    assert "start" in result.output
    assert "list-routes" in result.output
