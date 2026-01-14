"""Configuration management for confl.

Configuration is loaded from environment variables first, then falls back to
credentials file. The precedence order is:
1. Environment variables (CONFL_*)
2. Credentials file (~/.config/confl/credentials.toml)
"""

import os
from dataclasses import dataclass

from confl.credentials import load_credentials


@dataclass(frozen=True)
class Config:
    """Configuration for Confluence API access."""

    site: str
    email: str
    token: str


class ConfigError(Exception):
    """Raised when configuration is invalid or missing."""

    pass


def get_config() -> Config:
    """Load configuration from environment variables or credentials file.

    Environment variables take precedence over credentials file:
    - CONFL_SITE: Confluence site (e.g., mycompany.atlassian.net)
    - CONFL_EMAIL: Email associated with API token
    - CONFL_TOKEN: API token for authentication

    Returns:
        Config object with site, email, and token

    Raises:
        ConfigError: If required configuration is missing or invalid
    """
    # Try environment variables first
    # Use 'in' to distinguish between unset and empty string
    site = os.environ.get("CONFL_SITE")
    email = os.environ.get("CONFL_EMAIL")
    token = os.environ.get("CONFL_TOKEN")

    site_set = "CONFL_SITE" in os.environ
    email_set = "CONFL_EMAIL" in os.environ
    token_set = "CONFL_TOKEN" in os.environ

    # If all env vars are set (even if empty), try to use them and let validation handle errors
    if site_set and email_set and token_set:
        return _validate_and_create_config(site or "", email or "", token or "")

    # If some but not all env vars are set, that's an error
    if site_set or email_set or token_set:
        missing = []
        if not site_set:
            missing.append("CONFL_SITE")
        if not email_set:
            missing.append("CONFL_EMAIL")
        if not token_set:
            missing.append("CONFL_TOKEN")
        raise ConfigError(
            f"Incomplete environment configuration. Missing: {', '.join(missing)}\n"
            "Either set all three environment variables, "
            "or use 'confl auth login' to store credentials."
        )

    # Fall back to credentials file
    creds = load_credentials()
    if creds is None:
        raise ConfigError(
            "No configuration found.\n"
            "Set environment variables (CONFL_SITE, CONFL_EMAIL, CONFL_TOKEN) "
            "or run 'confl auth login' to store credentials."
        )

    return _validate_and_create_config(creds["site"], creds["email"], creds["token"])


def _validate_and_create_config(site: str, email: str, token: str) -> Config:
    """Validate configuration values and create Config object.

    Args:
        site: Confluence site hostname
        email: Email address
        token: API token

    Returns:
        Config object

    Raises:
        ConfigError: If validation fails
    """
    # Validate site looks like a hostname
    if not site or "://" in site or site.startswith("/"):
        raise ConfigError(
            f"Invalid site: {site!r}\n"
            "Site should be a hostname like 'mycompany.atlassian.net', not a URL."
        )

    # Validate email looks reasonable (basic check)
    if not email or "@" not in email:
        raise ConfigError(f"Invalid email: {email!r}\nEmail should contain '@'.")

    # Validate token is not empty
    if not token:
        raise ConfigError("API token cannot be empty.")

    return Config(site=site, email=email, token=token)
