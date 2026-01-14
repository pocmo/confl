"""Tests for config module."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
import tomli_w

from confl.config import Config, ConfigError, get_config


@pytest.fixture
def temp_credentials_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a temporary credentials file location."""
    config_dir = tmp_path / ".config" / "confl"
    config_dir.mkdir(parents=True)
    creds_file = config_dir / "credentials.toml"

    # Patch the credentials path to use temp location
    def mock_get_credentials_path() -> Path:
        return creds_file

    monkeypatch.setattr("confl.credentials.get_credentials_path", mock_get_credentials_path)
    return creds_file


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clean environment variables."""
    monkeypatch.delenv("CONFL_SITE", raising=False)
    monkeypatch.delenv("CONFL_EMAIL", raising=False)
    monkeypatch.delenv("CONFL_TOKEN", raising=False)


def test_get_config_from_env_vars(clean_env: None) -> None:
    """Test loading config from environment variables."""
    with patch.dict(
        os.environ,
        {
            "CONFL_SITE": "mycompany.atlassian.net",
            "CONFL_EMAIL": "user@example.com",
            "CONFL_TOKEN": "test-token-123",
        },
    ):
        config = get_config()
        assert config.site == "mycompany.atlassian.net"
        assert config.email == "user@example.com"
        assert config.token == "test-token-123"


def test_get_config_from_credentials_file(clean_env: None, temp_credentials_file: Path) -> None:
    """Test loading config from credentials file."""
    # Write credentials file
    creds = {
        "site": "company.atlassian.net",
        "email": "dev@company.com",
        "token": "file-token-456",
    }
    with open(temp_credentials_file, "wb") as f:
        tomli_w.dump(creds, f)

    config = get_config()
    assert config.site == "company.atlassian.net"
    assert config.email == "dev@company.com"
    assert config.token == "file-token-456"


def test_env_vars_override_credentials_file(clean_env: None, temp_credentials_file: Path) -> None:
    """Test that environment variables take precedence over credentials file."""
    # Write credentials file
    creds = {
        "site": "file-site.atlassian.net",
        "email": "file@example.com",
        "token": "file-token",
    }
    with open(temp_credentials_file, "wb") as f:
        tomli_w.dump(creds, f)

    # Set environment variables
    with patch.dict(
        os.environ,
        {
            "CONFL_SITE": "env-site.atlassian.net",
            "CONFL_EMAIL": "env@example.com",
            "CONFL_TOKEN": "env-token",
        },
    ):
        config = get_config()
        assert config.site == "env-site.atlassian.net"
        assert config.email == "env@example.com"
        assert config.token == "env-token"


def test_missing_all_config_raises_error(clean_env: None, tmp_path: Path) -> None:
    """Test that missing configuration raises clear error."""
    with pytest.raises(ConfigError) as exc_info:
        get_config()

    assert "No configuration found" in str(exc_info.value)
    assert "CONFL_SITE" in str(exc_info.value)
    assert "confl auth login" in str(exc_info.value)


def test_partial_env_vars_without_credentials_raises_error(clean_env: None) -> None:
    """Test that partial env vars without credentials file raises error."""
    with patch.dict(os.environ, {"CONFL_SITE": "mycompany.atlassian.net"}):
        with pytest.raises(ConfigError) as exc_info:
            get_config()

        assert "Partial environment configuration" in str(exc_info.value)
        assert "credentials file" in str(exc_info.value)


def test_invalid_site_with_protocol_raises_error(clean_env: None) -> None:
    """Test that site with protocol raises validation error."""
    with patch.dict(
        os.environ,
        {
            "CONFL_SITE": "https://mycompany.atlassian.net",
            "CONFL_EMAIL": "user@example.com",
            "CONFL_TOKEN": "token",
        },
    ):
        with pytest.raises(ConfigError) as exc_info:
            get_config()

        assert "Invalid site" in str(exc_info.value)
        assert "hostname" in str(exc_info.value)


def test_invalid_site_with_slash_raises_error(clean_env: None) -> None:
    """Test that site with slash raises validation error."""
    with patch.dict(
        os.environ,
        {
            "CONFL_SITE": "/mycompany",
            "CONFL_EMAIL": "user@example.com",
            "CONFL_TOKEN": "token",
        },
    ):
        with pytest.raises(ConfigError) as exc_info:
            get_config()

        assert "Invalid site" in str(exc_info.value)


def test_invalid_email_raises_error(clean_env: None) -> None:
    """Test that invalid email raises validation error."""
    with patch.dict(
        os.environ,
        {
            "CONFL_SITE": "mycompany.atlassian.net",
            "CONFL_EMAIL": "not-an-email",
            "CONFL_TOKEN": "token",
        },
    ):
        with pytest.raises(ConfigError) as exc_info:
            get_config()

        assert "Invalid email" in str(exc_info.value)
        assert "@" in str(exc_info.value)


def test_empty_token_raises_error(clean_env: None) -> None:
    """Test that empty token raises validation error."""
    with patch.dict(
        os.environ,
        {
            "CONFL_SITE": "mycompany.atlassian.net",
            "CONFL_EMAIL": "user@example.com",
            "CONFL_TOKEN": "",
        },
    ):
        with pytest.raises(ConfigError) as exc_info:
            get_config()

        assert "token cannot be empty" in str(exc_info.value)


def test_config_is_immutable() -> None:
    """Test that Config objects are immutable."""
    config = Config(site="mycompany.atlassian.net", email="user@example.com", token="token")

    # dataclass frozen=True raises FrozenInstanceError (subclass of AttributeError)
    with pytest.raises(AttributeError):
        config.site = "other-site.atlassian.net"  # type: ignore


def test_partial_override_site_only(clean_env: None, temp_credentials_file: Path) -> None:
    """Test overriding only site with env var."""
    # Write credentials file
    creds = {
        "site": "file-site.atlassian.net",
        "email": "file@example.com",
        "token": "file-token",
    }
    with open(temp_credentials_file, "wb") as f:
        tomli_w.dump(creds, f)

    # Override only site
    with patch.dict(os.environ, {"CONFL_SITE": "env-site.atlassian.net"}):
        config = get_config()
        assert config.site == "env-site.atlassian.net"
        assert config.email == "file@example.com"
        assert config.token == "file-token"


def test_partial_override_email_only(clean_env: None, temp_credentials_file: Path) -> None:
    """Test overriding only email with env var."""
    creds = {
        "site": "file-site.atlassian.net",
        "email": "file@example.com",
        "token": "file-token",
    }
    with open(temp_credentials_file, "wb") as f:
        tomli_w.dump(creds, f)

    # Override only email
    with patch.dict(os.environ, {"CONFL_EMAIL": "env@example.com"}):
        config = get_config()
        assert config.site == "file-site.atlassian.net"
        assert config.email == "env@example.com"
        assert config.token == "file-token"


def test_partial_override_token_only(clean_env: None, temp_credentials_file: Path) -> None:
    """Test overriding only token with env var."""
    creds = {
        "site": "file-site.atlassian.net",
        "email": "file@example.com",
        "token": "file-token",
    }
    with open(temp_credentials_file, "wb") as f:
        tomli_w.dump(creds, f)

    # Override only token
    with patch.dict(os.environ, {"CONFL_TOKEN": "env-token"}):
        config = get_config()
        assert config.site == "file-site.atlassian.net"
        assert config.email == "file@example.com"
        assert config.token == "env-token"


def test_partial_override_site_and_email(clean_env: None, temp_credentials_file: Path) -> None:
    """Test overriding site and email with env vars."""
    creds = {
        "site": "file-site.atlassian.net",
        "email": "file@example.com",
        "token": "file-token",
    }
    with open(temp_credentials_file, "wb") as f:
        tomli_w.dump(creds, f)

    # Override site and email
    with patch.dict(
        os.environ, {"CONFL_SITE": "env-site.atlassian.net", "CONFL_EMAIL": "env@example.com"}
    ):
        config = get_config()
        assert config.site == "env-site.atlassian.net"
        assert config.email == "env@example.com"
        assert config.token == "file-token"
