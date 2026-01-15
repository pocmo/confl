"""Tests for profile-based configuration."""

from pathlib import Path

import pytest

from confl.config import ConfigError, get_config
from confl.credentials import (
    delete_credentials,
    get_default_profile,
    list_profiles,
    load_credentials,
    save_credentials,
)


@pytest.fixture
def temp_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a temporary home directory for testing."""
    monkeypatch.setenv("HOME", str(tmp_path))
    return tmp_path


def test_save_default_profile(temp_home: Path) -> None:
    """Test saving credentials to default profile."""
    save_credentials("site1.atlassian.net", "user1@example.com", "token1")

    creds = load_credentials()
    assert creds is not None
    assert creds["site"] == "site1.atlassian.net"
    assert creds["email"] == "user1@example.com"
    assert creds["token"] == "token1"


def test_save_named_profile(temp_home: Path) -> None:
    """Test saving credentials to a named profile."""
    save_credentials("dev.atlassian.net", "dev@example.com", "dev-token", profile="dev")

    creds = load_credentials("dev")
    assert creds is not None
    assert creds["site"] == "dev.atlassian.net"
    assert creds["email"] == "dev@example.com"
    assert creds["token"] == "dev-token"


def test_save_multiple_profiles(temp_home: Path) -> None:
    """Test saving multiple profiles."""
    save_credentials("prod.atlassian.net", "prod@example.com", "prod-token", profile="prod")
    save_credentials("dev.atlassian.net", "dev@example.com", "dev-token", profile="dev")
    save_credentials("staging.atlassian.net", "stage@example.com", "stage-token", profile="staging")

    # Verify all profiles are accessible
    prod_creds = load_credentials("prod")
    assert prod_creds is not None
    assert prod_creds["site"] == "prod.atlassian.net"

    dev_creds = load_credentials("dev")
    assert dev_creds is not None
    assert dev_creds["site"] == "dev.atlassian.net"

    staging_creds = load_credentials("staging")
    assert staging_creds is not None
    assert staging_creds["site"] == "staging.atlassian.net"


def test_load_nonexistent_profile(temp_home: Path) -> None:
    """Test loading a profile that doesn't exist."""
    save_credentials("site.atlassian.net", "user@example.com", "token", profile="default")

    # Try to load a profile that doesn't exist
    creds = load_credentials("nonexistent")
    assert creds is None


def test_list_profiles_empty(temp_home: Path) -> None:
    """Test listing profiles when none exist."""
    profiles = list_profiles()
    assert profiles == []


def test_list_profiles_multiple(temp_home: Path) -> None:
    """Test listing multiple profiles."""
    save_credentials("site1.atlassian.net", "user1@example.com", "token1", profile="prod")
    save_credentials("site2.atlassian.net", "user2@example.com", "token2", profile="dev")
    save_credentials("site3.atlassian.net", "user3@example.com", "token3", profile="staging")

    profiles = list_profiles()
    assert set(profiles) == {"prod", "dev", "staging"}


def test_get_default_profile(temp_home: Path) -> None:
    """Test getting the default profile name."""
    save_credentials("site.atlassian.net", "user@example.com", "token", profile="prod")

    default = get_default_profile()
    assert default == "default"  # First profile becomes default


def test_delete_specific_profile(temp_home: Path) -> None:
    """Test deleting a specific profile."""
    save_credentials("prod.atlassian.net", "prod@example.com", "prod-token", profile="prod")
    save_credentials("dev.atlassian.net", "dev@example.com", "dev-token", profile="dev")

    # Delete one profile
    delete_credentials("dev")

    # Verify prod still exists but dev doesn't
    assert load_credentials("prod") is not None
    assert load_credentials("dev") is None
    assert "prod" in list_profiles()
    assert "dev" not in list_profiles()


def test_delete_all_profiles(temp_home: Path) -> None:
    """Test deleting all profiles."""
    save_credentials("prod.atlassian.net", "prod@example.com", "prod-token", profile="prod")
    save_credentials("dev.atlassian.net", "dev@example.com", "dev-token", profile="dev")

    # Delete all profiles
    delete_credentials()

    # Verify all profiles are gone
    assert load_credentials("prod") is None
    assert load_credentials("dev") is None
    assert list_profiles() == []


def test_legacy_format_compatibility(temp_home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that legacy credentials format still works."""
    # Create a legacy format credentials file
    import tomli_w

    from confl.credentials import get_credentials_path

    creds_path = get_credentials_path()
    creds_path.parent.mkdir(parents=True, exist_ok=True)

    legacy_data = {
        "site": "legacy.atlassian.net",
        "email": "legacy@example.com",
        "token": "legacy-token",
    }

    with open(creds_path, "wb") as f:
        tomli_w.dump(legacy_data, f)

    # Verify it can be loaded
    creds = load_credentials()
    assert creds is not None
    assert creds["site"] == "legacy.atlassian.net"
    assert creds["email"] == "legacy@example.com"
    assert creds["token"] == "legacy-token"

    # Verify it's listed as default profile
    profiles = list_profiles()
    assert profiles == ["default"]


def test_legacy_format_migration(temp_home: Path) -> None:
    """Test that saving a new profile migrates legacy format to new format."""
    # Create legacy format
    import tomli_w

    from confl.credentials import get_credentials_path

    creds_path = get_credentials_path()
    creds_path.parent.mkdir(parents=True, exist_ok=True)

    legacy_data = {
        "site": "legacy.atlassian.net",
        "email": "legacy@example.com",
        "token": "legacy-token",
    }

    with open(creds_path, "wb") as f:
        tomli_w.dump(legacy_data, f)

    # Save a new profile (should trigger migration)
    save_credentials("dev.atlassian.net", "dev@example.com", "dev-token", profile="dev")

    # Verify both profiles exist
    default_creds = load_credentials("default")
    assert default_creds is not None
    assert default_creds["site"] == "legacy.atlassian.net"

    dev_creds = load_credentials("dev")
    assert dev_creds is not None
    assert dev_creds["site"] == "dev.atlassian.net"

    # Verify profiles are listed
    profiles = list_profiles()
    assert "default" in profiles
    assert "dev" in profiles


def test_config_with_profile(temp_home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test loading config with specific profile."""
    # Clear env vars
    for var in ["CONFL_SITE", "CONFL_EMAIL", "CONFL_TOKEN", "CONFL_PROFILE"]:
        monkeypatch.delenv(var, raising=False)

    save_credentials("prod.atlassian.net", "prod@example.com", "prod-token", profile="prod")
    save_credentials("dev.atlassian.net", "dev@example.com", "dev-token", profile="dev")

    # Load prod profile
    config = get_config(profile="prod")
    assert config.site == "prod.atlassian.net"
    assert config.email == "prod@example.com"
    assert config.token == "prod-token"

    # Load dev profile
    config = get_config(profile="dev")
    assert config.site == "dev.atlassian.net"
    assert config.email == "dev@example.com"
    assert config.token == "dev-token"


def test_config_with_profile_env_var(temp_home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test loading config with CONFL_PROFILE environment variable."""
    # Clear other env vars
    for var in ["CONFL_SITE", "CONFL_EMAIL", "CONFL_TOKEN"]:
        monkeypatch.delenv(var, raising=False)

    save_credentials("prod.atlassian.net", "prod@example.com", "prod-token", profile="prod")
    save_credentials("dev.atlassian.net", "dev@example.com", "dev-token", profile="dev")

    # Set CONFL_PROFILE env var
    monkeypatch.setenv("CONFL_PROFILE", "dev")

    # Load config (should use dev profile from env var)
    config = get_config()
    assert config.site == "dev.atlassian.net"
    assert config.email == "dev@example.com"
    assert config.token == "dev-token"


def test_config_profile_precedence(temp_home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that explicit profile parameter takes precedence over env var."""
    # Clear other env vars
    for var in ["CONFL_SITE", "CONFL_EMAIL", "CONFL_TOKEN"]:
        monkeypatch.delenv(var, raising=False)

    save_credentials("prod.atlassian.net", "prod@example.com", "prod-token", profile="prod")
    save_credentials("dev.atlassian.net", "dev@example.com", "dev-token", profile="dev")

    # Set CONFL_PROFILE env var to dev
    monkeypatch.setenv("CONFL_PROFILE", "dev")

    # But explicitly request prod profile
    config = get_config(profile="prod")
    assert config.site == "prod.atlassian.net"
    assert config.email == "prod@example.com"
    assert config.token == "prod-token"


def test_config_nonexistent_profile_error(temp_home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that requesting nonexistent profile raises helpful error."""
    # Clear env vars
    for var in ["CONFL_SITE", "CONFL_EMAIL", "CONFL_TOKEN", "CONFL_PROFILE"]:
        monkeypatch.delenv(var, raising=False)

    save_credentials("prod.atlassian.net", "prod@example.com", "prod-token", profile="prod")

    # Try to load nonexistent profile
    with pytest.raises(ConfigError) as exc_info:
        get_config(profile="nonexistent")

    assert "nonexistent" in str(exc_info.value)
