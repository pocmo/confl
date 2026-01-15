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


def load_credentials(profile: str | None = None) -> Credentials | None:
    """Load credentials from the credentials file.

    Args:
        profile: Profile name to load. If None, loads the default profile.

    Returns:
        Credentials if file exists and is valid, None otherwise
    """
    creds_path = get_credentials_path()
    if not creds_path.exists():
        return None

    try:
        with open(creds_path, "rb") as f:
            data = tomllib.load(f)

        # Handle legacy format (flat structure without profiles)
        if "site" in data and "email" in data and "token" in data:
            # Legacy format - only return if no profile specified or profile is "default"
            if profile is None or profile == "default":
                return Credentials(site=data["site"], email=data["email"], token=data["token"])
            return None

        # New format with profiles
        profiles = data.get("profiles", {})

        # Determine which profile to use
        profile_name = profile or data.get("default_profile", "default")

        if profile_name not in profiles:
            return None

        profile_data = profiles[profile_name]

        # Validate required fields in profile
        if not all(key in profile_data for key in ("site", "email", "token")):
            return None

        return Credentials(
            site=profile_data["site"],
            email=profile_data["email"],
            token=profile_data["token"],
        )
    except (OSError, tomllib.TOMLDecodeError):
        return None


def save_credentials(site: str, email: str, token: str, profile: str = "default") -> None:
    """Save credentials to the credentials file.

    Creates the config directory if it doesn't exist.
    Sets file permissions to 0o600 (read/write for owner only).

    Args:
        site: Confluence site (e.g., "mycompany.atlassian.net")
        email: Email address associated with the API token
        token: API token for authentication
        profile: Profile name to save under (default: "default")
    """
    creds_path = get_credentials_path()
    config_dir = creds_path.parent

    # Create config directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)

    # Load existing data or start fresh
    existing_data: dict = {}
    if creds_path.exists():
        try:
            with open(creds_path, "rb") as f:
                existing_data = tomllib.load(f)
        except (OSError, tomllib.TOMLDecodeError):
            pass  # Start fresh if file is corrupted

    # Convert legacy format to new format if needed
    if "site" in existing_data and "email" in existing_data and "token" in existing_data:
        # Migrate legacy format to profiles
        legacy_profile = {
            "site": existing_data["site"],
            "email": existing_data["email"],
            "token": existing_data["token"],
        }
        existing_data = {
            "default_profile": "default",
            "profiles": {"default": legacy_profile},
        }

    # Ensure profiles structure exists
    if "profiles" not in existing_data:
        existing_data["profiles"] = {}
    if "default_profile" not in existing_data:
        existing_data["default_profile"] = "default"

    # Add or update the profile
    existing_data["profiles"][profile] = {
        "site": site,
        "email": email,
        "token": token,
    }

    # Write updated data
    with open(creds_path, "wb") as f:
        tomli_w.dump(existing_data, f)

    # Set restrictive permissions (owner read/write only)
    creds_path.chmod(0o600)


def delete_credentials(profile: str | None = None) -> None:
    """Delete stored credentials.

    Args:
        profile: Profile name to delete. If None, deletes the entire credentials file.
    """
    creds_path = get_credentials_path()
    if not creds_path.exists():
        return

    # If no profile specified, delete entire file
    if profile is None:
        creds_path.unlink()
        return

    # Delete specific profile
    try:
        with open(creds_path, "rb") as f:
            data = tomllib.load(f)

        # Handle legacy format - convert to new format first
        if "site" in data and "email" in data and "token" in data:
            if profile == "default":
                # Deleting the only profile in legacy format - delete entire file
                creds_path.unlink()
                return
            # Profile doesn't exist in legacy format
            return

        # Remove profile from profiles dict
        profiles = data.get("profiles", {})
        if profile in profiles:
            del profiles[profile]

            # If no profiles left, delete entire file
            if not profiles:
                creds_path.unlink()
            else:
                # Update default_profile if we deleted it
                if data.get("default_profile") == profile and profiles:
                    data["default_profile"] = next(iter(profiles))

                # Write updated data
                with open(creds_path, "wb") as f:
                    tomli_w.dump(data, f)
                creds_path.chmod(0o600)
    except (OSError, tomllib.TOMLDecodeError):
        pass  # Silently ignore errors


def list_profiles() -> list[str]:
    """List all available profiles.

    Returns:
        List of profile names, empty if no profiles exist
    """
    creds_path = get_credentials_path()
    if not creds_path.exists():
        return []

    try:
        with open(creds_path, "rb") as f:
            data = tomllib.load(f)

        # Handle legacy format
        if "site" in data and "email" in data and "token" in data:
            return ["default"]

        # New format with profiles
        return list(data.get("profiles", {}).keys())
    except (OSError, tomllib.TOMLDecodeError):
        return []


def get_default_profile() -> str | None:
    """Get the default profile name.

    Returns:
        Default profile name, or None if not set
    """
    creds_path = get_credentials_path()
    if not creds_path.exists():
        return None

    try:
        with open(creds_path, "rb") as f:
            data = tomllib.load(f)

        # Handle legacy format
        if "site" in data and "email" in data and "token" in data:
            return "default"

        # New format with profiles
        return data.get("default_profile")
    except (OSError, tomllib.TOMLDecodeError):
        return None
