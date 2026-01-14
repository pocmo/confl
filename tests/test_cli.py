"""Smoke tests for CLI."""

from typer.testing import CliRunner

from confl.cli import app

runner = CliRunner()


def test_cli_app_exists():
    """Test that the CLI app is importable."""
    assert app is not None
    assert app.info.name == "confl"


def test_cli_help():
    """Test that --help works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "confl" in result.stdout.lower()
    assert "Confluence" in result.stdout
