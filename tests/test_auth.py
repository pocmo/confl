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


def test_auth_login_success(clean_env, temp_credentials_file):
    """Test auth login command with valid input."""
    result = runner.invoke(
        app,
        [
            "auth",
            "login",
            "--token",
            "--site",
            "mycompany.atlassian.net",
            "--email",
            "user@example.com",
        ],
        input="my-secret-token\n",
    )
    assert result.exit_code == 0
    assert "Credentials saved" in result.stdout
    assert "user@example.com" in result.stdout
    assert "mycompany.atlassian.net" in result.stdout

    # Verify credentials were written
    assert temp_credentials_file.exists()
    content = temp_credentials_file.read_text()
    assert "mycompany.atlassian.net" in content
    assert "user@example.com" in content
    assert "my-secret-token" in content


def test_auth_login_missing_token_flag(clean_env, temp_credentials_file):
    """Test auth login without --token flag."""
    result = runner.invoke(
        app,
        ["auth", "login", "--site", "mycompany.atlassian.net", "--email", "user@example.com"],
        input="my-secret-token\n",
    )
    assert result.exit_code == 2
    assert "The --token flag is required" in result.stdout


def test_auth_login_no_stdin(clean_env, temp_credentials_file):
    """Test auth login with no token on stdin."""
    result = runner.invoke(
        app,
        [
            "auth",
            "login",
            "--token",
            "--site",
            "mycompany.atlassian.net",
            "--email",
            "user@example.com",
        ],
        input="",
    )
    assert result.exit_code == 2
    assert "No token provided on stdin" in result.stdout


def test_auth_login_invalid_site_with_protocol(clean_env, temp_credentials_file):
    """Test auth login with site containing protocol."""
    result = runner.invoke(
        app,
        [
            "auth",
            "login",
            "--token",
            "--site",
            "https://mycompany.atlassian.net",
            "--email",
            "user@example.com",
        ],
        input="my-secret-token\n",
    )
    assert result.exit_code == 2
    assert "Invalid site format" in result.stdout


def test_auth_login_invalid_site_with_path(clean_env, temp_credentials_file):
    """Test auth login with site containing path."""
    result = runner.invoke(
        app,
        [
            "auth",
            "login",
            "--token",
            "--site",
            "mycompany.atlassian.net/wiki",
            "--email",
            "user@example.com",
        ],
        input="my-secret-token\n",
    )
    assert result.exit_code == 2
    assert "Invalid site format" in result.stdout


def test_auth_login_whitespace_in_token(clean_env, temp_credentials_file):
    """Test auth login strips whitespace from token."""
    result = runner.invoke(
        app,
        [
            "auth",
            "login",
            "--token",
            "--site",
            "mycompany.atlassian.net",
            "--email",
            "user@example.com",
        ],
        input="  my-secret-token  \n",
    )
    assert result.exit_code == 0

    # Verify token was stripped
    content = temp_credentials_file.read_text()
    assert 'token = "my-secret-token"' in content


def test_auth_logout_with_credentials(clean_env, temp_credentials_file):
    """Test auth logout when credentials exist."""
    temp_credentials_file.write_text(
        'site = "mycompany.atlassian.net"\nemail = "test@example.com"\ntoken = "test-token"\n'
    )

    result = runner.invoke(app, ["auth", "logout"])
    assert result.exit_code == 0
    assert "Logged out" in result.stdout
    assert not temp_credentials_file.exists()


def test_auth_logout_without_credentials(clean_env, temp_credentials_file):
    """Test auth logout when no credentials exist."""
    result = runner.invoke(app, ["auth", "logout"])
    assert result.exit_code == 0
    assert "Logged out" in result.stdout


def test_auth_login_logout_roundtrip(clean_env, temp_credentials_file):
    """Test full login/logout workflow."""
    # Login
    result = runner.invoke(
        app,
        ["auth", "login", "--token", "--site", "test.atlassian.net", "--email", "test@example.com"],
        input="test-token\n",
    )
    assert result.exit_code == 0

    # Verify authenticated
    result = runner.invoke(app, ["auth", "status"])
    assert result.exit_code == 0
    assert "Authenticated" in result.stdout

    # Logout
    result = runner.invoke(app, ["auth", "logout"])
    assert result.exit_code == 0

    # Verify not authenticated
    result = runner.invoke(app, ["auth", "status"])
    assert result.exit_code == 1
    assert "Not authenticated" in result.stdout
