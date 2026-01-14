"""Tests for credentials storage."""

from pathlib import Path

import pytest

from confl.credentials import (
    delete_credentials,
    get_credentials_path,
    load_credentials,
    save_credentials,
)


@pytest.fixture
def temp_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a temporary home directory for testing."""
    monkeypatch.setenv("HOME", str(tmp_path))
    return tmp_path


def test_get_credentials_path(temp_home: Path) -> None:
    """Test that credentials path is correct."""
    expected = temp_home / ".config" / "confl" / "credentials.toml"
    assert get_credentials_path() == expected


def test_load_credentials_missing_file(temp_home: Path) -> None:
    """Test loading credentials when file doesn't exist."""
    assert load_credentials() is None


def test_save_and_load_credentials(temp_home: Path) -> None:
    """Test saving and loading credentials round-trip."""
    site = "mycompany.atlassian.net"
    email = "user@example.com"
    token = "test-token-12345"

    # Save credentials
    save_credentials(site, email, token)

    # Verify file was created
    creds_path = get_credentials_path()
    assert creds_path.exists()

    # Verify file permissions are restrictive (owner read/write only)
    assert creds_path.stat().st_mode & 0o777 == 0o600

    # Load credentials
    creds = load_credentials()
    assert creds is not None
    assert creds["site"] == site
    assert creds["email"] == email
    assert creds["token"] == token


def test_save_credentials_creates_directory(temp_home: Path) -> None:
    """Test that save_credentials creates config directory if missing."""
    config_dir = temp_home / ".config" / "confl"
    assert not config_dir.exists()

    save_credentials("site.atlassian.net", "user@example.com", "token")

    assert config_dir.exists()
    assert config_dir.is_dir()


def test_delete_credentials(temp_home: Path) -> None:
    """Test deleting credentials file."""
    # Create credentials file
    save_credentials("site.atlassian.net", "user@example.com", "token")
    creds_path = get_credentials_path()
    assert creds_path.exists()

    # Delete credentials
    delete_credentials()
    assert not creds_path.exists()


def test_delete_credentials_when_missing(temp_home: Path) -> None:
    """Test that delete_credentials handles missing file gracefully."""
    creds_path = get_credentials_path()
    assert not creds_path.exists()

    # Should not raise an error
    delete_credentials()
    assert not creds_path.exists()


def test_load_credentials_invalid_toml(temp_home: Path) -> None:
    """Test loading credentials with invalid TOML format."""
    creds_path = get_credentials_path()
    creds_path.parent.mkdir(parents=True, exist_ok=True)

    # Write invalid TOML
    creds_path.write_text("this is not valid toml { ]")

    assert load_credentials() is None


def test_load_credentials_missing_required_fields(temp_home: Path) -> None:
    """Test loading credentials with missing required fields."""
    creds_path = get_credentials_path()
    creds_path.parent.mkdir(parents=True, exist_ok=True)

    # Write TOML with missing fields
    creds_path.write_text('[credentials]\nsite = "example.com"\n')

    assert load_credentials() is None


def test_save_credentials_overwrites_existing(temp_home: Path) -> None:
    """Test that saving credentials overwrites existing file."""
    # Save initial credentials
    save_credentials("old-site.atlassian.net", "old@example.com", "old-token")

    # Save new credentials
    new_site = "new-site.atlassian.net"
    new_email = "new@example.com"
    new_token = "new-token"
    save_credentials(new_site, new_email, new_token)

    # Load and verify new credentials
    creds = load_credentials()
    assert creds is not None
    assert creds["site"] == new_site
    assert creds["email"] == new_email
    assert creds["token"] == new_token
