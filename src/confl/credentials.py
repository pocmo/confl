"""Credentials storage for Confluence authentication."""

import tomllib
from pathlib import Path
from typing import TypedDict

import tomli_w


class Credentials(TypedDict):
    """Credentials for Confluence authentication."""

    site: str
    email: str
    token: str


def get_credentials_path() -> Path:
    """Return the path to the credentials file.

    Returns:
        Path to ~/.config/confl/credentials.toml
    """
    config_dir = Path.home() / ".config" / "confl"
    return config_dir / "credentials.toml"


def load_credentials() -> Credentials | None:
    """Load credentials from the credentials file.

    Returns:
        Credentials if file exists and is valid, None otherwise
    """
    creds_path = get_credentials_path()
    if not creds_path.exists():
        return None

    try:
        with open(creds_path, "rb") as f:
            data = tomllib.load(f)

        # Validate required fields
        if not all(key in data for key in ("site", "email", "token")):
            return None

        return Credentials(site=data["site"], email=data["email"], token=data["token"])
    except (OSError, tomllib.TOMLDecodeError):
        return None


def save_credentials(site: str, email: str, token: str) -> None:
    """Save credentials to the credentials file.

    Creates the config directory if it doesn't exist.
    Sets file permissions to 0o600 (read/write for owner only).

    Args:
        site: Confluence site (e.g., "mycompany.atlassian.net")
        email: Email address associated with the API token
        token: API token for authentication
    """
    creds_path = get_credentials_path()
    config_dir = creds_path.parent

    # Create config directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)

    # Write credentials
    data = {"site": site, "email": email, "token": token}
    with open(creds_path, "wb") as f:
        tomli_w.dump(data, f)

    # Set restrictive permissions (owner read/write only)
    creds_path.chmod(0o600)


def delete_credentials() -> None:
    """Delete the credentials file if it exists."""
    creds_path = get_credentials_path()
    if creds_path.exists():
        creds_path.unlink()
