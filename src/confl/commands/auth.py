"""Authentication commands."""

import json
import os
import sys
from typing import Any

import typer
from rich.console import Console

from confl.config import ConfigError, get_config
from confl.credentials import load_credentials

app = typer.Typer(help="Manage authentication")
console = Console()


def _get_auth_source() -> str:
    """Determine the authentication source.

    Returns:
        "environment" if any CONFL_* env vars are set,
        "credentials" if only credentials file is used,
        "none" if not authenticated
    """
    # Check if any env vars are set
    if any(var in os.environ for var in ["CONFL_SITE", "CONFL_EMAIL", "CONFL_TOKEN"]):
        return "environment"

    # Check if credentials file exists
    creds = load_credentials()
    if creds is not None:
        return "credentials"

    return "none"


def _mask_token(token: str) -> str:
    """Mask an API token for display.

    Args:
        token: API token to mask

    Returns:
        Masked token (e.g., "****abcd")
    """
    if len(token) <= 4:
        return "****"
    return f"****{token[-4:]}"


@app.command()
def status(
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
) -> None:
    """Show current authentication status.

    Displays the authentication source, site, email, and masked token.
    Exit code 0 if authenticated, 1 if not authenticated.
    """
    output: dict[str, Any]
    auth_source = _get_auth_source()

    if auth_source == "none":
        if json_output:
            output = {
                "authenticated": False,
                "source": None,
                "site": None,
                "email": None,
                "token": None,
            }
            print(json.dumps(output, indent=2))
        else:
            console.print("[red]Not authenticated[/red]")
            console.print("\nSet environment variables (CONFL_SITE, CONFL_EMAIL, CONFL_TOKEN)")
            console.print("or run 'confl auth login' to store credentials.")
        sys.exit(1)

    # Try to load config (will raise ConfigError if invalid)
    try:
        config = get_config()
    except ConfigError as e:
        if json_output:
            output = {
                "authenticated": False,
                "error": str(e),
            }
            print(json.dumps(output, indent=2))
        else:
            console.print(f"[red]Configuration error:[/red] {e}")
        sys.exit(1)

    # Successfully authenticated
    source_display = "environment variables" if auth_source == "environment" else "credentials file"

    if json_output:
        output = {
            "authenticated": True,
            "source": auth_source,
            "site": config.site,
            "email": config.email,
            "token": _mask_token(config.token),
        }
        print(json.dumps(output, indent=2))
    else:
        console.print(f"[green]Authenticated via:[/green] {source_display}")
        console.print(f"[cyan]Site:[/cyan] {config.site}")
        console.print(f"[cyan]Email:[/cyan] {config.email}")
        console.print(f"[cyan]Token:[/cyan] {_mask_token(config.token)}")

    sys.exit(0)
