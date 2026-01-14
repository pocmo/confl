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

    Individual env vars can override specific fields from credentials file.
    For example: CONFL_SITE set + credentials file has email/token
    → uses CONFL_SITE from env + email/token from file

    Returns:
        Config object with site, email, and token

    Raises:
        ConfigError: If required configuration is missing or invalid
    """
    # Check which env vars are set
    site_set = "CONFL_SITE" in os.environ
    email_set = "CONFL_EMAIL" in os.environ
    token_set = "CONFL_TOKEN" in os.environ

    # Get env var values (may be empty string)
    site_env = os.environ.get("CONFL_SITE")
    email_env = os.environ.get("CONFL_EMAIL")
    token_env = os.environ.get("CONFL_TOKEN")

    # If all env vars are set, use them directly
    if site_set and email_set and token_set:
        return _validate_and_create_config(site_env or "", email_env or "", token_env or "")

    # If some env vars are set, merge with credentials file
    if site_set or email_set or token_set:
        creds = load_credentials()
        if creds is None:
            raise ConfigError(
                "Partial environment configuration requires credentials file.\n"
                "Missing credentials file. Run 'confl auth login' to store credentials."
            )

        # Use env vars where set, fall back to credentials file
        # Use 'or ""' to handle case where env var is set but empty
        site = (site_env or "") if site_set else creds["site"]
        email = (email_env or "") if email_set else creds["email"]
        token = (token_env or "") if token_set else creds["token"]

        return _validate_and_create_config(site, email, token)

    # No env vars set, fall back to credentials file only
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
