"""Tests for auth commands."""

import json

import pytest
from typer.testing import CliRunner

from confl.cli import app

runner = CliRunner()


@pytest.fixture
def temp_credentials_file(tmp_path, monkeypatch):
    """Create a temporary credentials file."""
    config_dir = tmp_path / ".config" / "confl"
    config_dir.mkdir(parents=True)
    credentials_file = config_dir / "credentials.toml"

    # Patch the credentials path function
    monkeypatch.setattr("confl.credentials.get_credentials_path", lambda: credentials_file)

    return credentials_file


@pytest.fixture
def clean_env(monkeypatch):
    """Remove all CONFL_* environment variables."""
    for var in ["CONFL_SITE", "CONFL_EMAIL", "CONFL_TOKEN"]:
        monkeypatch.delenv(var, raising=False)


def test_auth_status_not_authenticated(clean_env):
    """Test auth status when not authenticated."""
    result = runner.invoke(app, ["auth", "status"])
    assert result.exit_code == 1
    assert "Not authenticated" in result.stdout
    assert "CONFL_SITE" in result.stdout


def test_auth_status_not_authenticated_json(clean_env):
    """Test auth status --json when not authenticated."""
    result = runner.invoke(app, ["auth", "status", "--json"])
    assert result.exit_code == 1
    output = json.loads(result.stdout)
    assert output["authenticated"] is False
    assert output["source"] is None


def test_auth_status_with_credentials_file(clean_env, temp_credentials_file):
    """Test auth status with credentials file."""
    temp_credentials_file.write_text(
        'site = "mycompany.atlassian.net"\n'
        'email = "test@example.com"\n'
        'token = "test-token-12345678"\n'
    )

    result = runner.invoke(app, ["auth", "status"])
    assert result.exit_code == 0
    assert "Authenticated via: credentials file" in result.stdout
    assert "mycompany.atlassian.net" in result.stdout
    assert "test@example.com" in result.stdout
    assert "****5678" in result.stdout
    assert "test-token-12345678" not in result.stdout  # Should be masked


def test_auth_status_with_credentials_file_json(clean_env, temp_credentials_file):
    """Test auth status --json with credentials file."""
    temp_credentials_file.write_text(
        'site = "mycompany.atlassian.net"\n'
        'email = "test@example.com"\n'
        'token = "test-token-12345678"\n'
    )

    result = runner.invoke(app, ["auth", "status", "--json"])
    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert output["authenticated"] is True
    assert output["source"] == "credentials"
    assert output["site"] == "mycompany.atlassian.net"
    assert output["email"] == "test@example.com"
    assert output["token"] == "****5678"


def test_auth_status_with_env_vars(clean_env, monkeypatch):
    """Test auth status with environment variables."""
    monkeypatch.setenv("CONFL_SITE", "envsite.atlassian.net")
    monkeypatch.setenv("CONFL_EMAIL", "env@test.com")
    monkeypatch.setenv("CONFL_TOKEN", "env-token-abcd")

    result = runner.invoke(app, ["auth", "status"])
    assert result.exit_code == 0
    assert "Authenticated via: environment variables" in result.stdout
    assert "envsite.atlassian.net" in result.stdout
    assert "env@test.com" in result.stdout
    assert "****abcd" in result.stdout


def test_auth_status_with_env_vars_json(clean_env, monkeypatch):
    """Test auth status --json with environment variables."""
    monkeypatch.setenv("CONFL_SITE", "envsite.atlassian.net")
    monkeypatch.setenv("CONFL_EMAIL", "env@test.com")
    monkeypatch.setenv("CONFL_TOKEN", "env-token-abcd")

    result = runner.invoke(app, ["auth", "status", "--json"])
    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert output["authenticated"] is True
    assert output["source"] == "environment"
    assert output["site"] == "envsite.atlassian.net"
    assert output["email"] == "env@test.com"
    assert output["token"] == "****abcd"


def test_auth_status_env_vars_override_credentials(clean_env, temp_credentials_file, monkeypatch):
    """Test that environment variables override credentials file."""
    temp_credentials_file.write_text(
        'site = "filesite.atlassian.net"\nemail = "file@example.com"\ntoken = "file-token"\n'
    )

    monkeypatch.setenv("CONFL_SITE", "override.atlassian.net")

    result = runner.invoke(app, ["auth", "status"])
    assert result.exit_code == 0
    assert "Authenticated via: environment variables" in result.stdout
    assert "override.atlassian.net" in result.stdout
    assert "file@example.com" in result.stdout  # From credentials file


def test_auth_status_invalid_config(clean_env, monkeypatch):
    """Test auth status with invalid configuration."""
    monkeypatch.setenv("CONFL_SITE", "https://invalid.com")
    monkeypatch.setenv("CONFL_EMAIL", "test@example.com")
    monkeypatch.setenv("CONFL_TOKEN", "token")

    result = runner.invoke(app, ["auth", "status"])
    assert result.exit_code == 1
    assert "Configuration error" in result.stdout
    assert "Invalid site" in result.stdout


def test_auth_status_invalid_config_json(clean_env, monkeypatch):
    """Test auth status --json with invalid configuration."""
    monkeypatch.setenv("CONFL_SITE", "https://invalid.com")
    monkeypatch.setenv("CONFL_EMAIL", "test@example.com")
    monkeypatch.setenv("CONFL_TOKEN", "token")

    result = runner.invoke(app, ["auth", "status", "--json"])
    assert result.exit_code == 1
    output = json.loads(result.stdout)
    assert output["authenticated"] is False
    assert "Invalid site" in output["error"]


def test_mask_token_short():
    """Test token masking for short tokens."""
    from confl.commands.auth import _mask_token

    assert _mask_token("abc") == "****"
    assert _mask_token("abcd") == "****"


def test_mask_token_long():
    """Test token masking for long tokens."""
    from confl.commands.auth import _mask_token

    assert _mask_token("abcde") == "****bcde"
    assert _mask_token("test-token-12345678") == "****5678"


def test_get_auth_source_none(clean_env):
    """Test _get_auth_source returns 'none' when not authenticated."""
    from confl.commands.auth import _get_auth_source

    assert _get_auth_source() == "none"


def test_get_auth_source_environment(clean_env, monkeypatch):
    """Test _get_auth_source returns 'environment' when env vars are set."""
    from confl.commands.auth import _get_auth_source

    monkeypatch.setenv("CONFL_SITE", "test.atlassian.net")

    assert _get_auth_source() == "environment"


def test_get_auth_source_credentials(clean_env, temp_credentials_file):
    """Test _get_auth_source returns 'credentials' when credentials file exists."""
    from confl.commands.auth import _get_auth_source

    temp_credentials_file.write_text(
        'site = "test.atlassian.net"\nemail = "test@example.com"\ntoken = "token"\n'
    )

    assert _get_auth_source() == "credentials"
