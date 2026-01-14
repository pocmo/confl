"""Authentication commands."""

import json
import os
import sys
from typing import Any

import typer
from rich.console import Console

from confl.config import ConfigError, get_config
from confl.credentials import delete_credentials, load_credentials, save_credentials

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


@app.command()
def login(
    token: bool = typer.Option(False, "--token", help="Read token from stdin"),
    site: str = typer.Option(..., "--site", help="Confluence site (e.g., mycompany.atlassian.net)"),
    email: str = typer.Option(..., "--email", help="Email address for authentication"),
) -> None:
    """Store authentication credentials.

    Reads the API token from stdin (non-interactive, pipeable).

    Example:
        echo "$TOKEN" | confl auth login --token --site mycompany.atlassian.net \\
            --email user@example.com
    """
    if not token:
        console.print("[red]Error:[/red] The --token flag is required")
        console.print(
            'Read token from stdin by using: echo "$TOKEN" | confl auth login --token ...'
        )
        sys.exit(2)

    # Read token from stdin
    token_value = sys.stdin.read().strip()
    if not token_value:
        console.print("[red]Error:[/red] No token provided on stdin")
        sys.exit(2)

    # Validate site format (basic check)
    if not site or "/" in site or site.startswith("http"):
        console.print(
            "[red]Error:[/red] Invalid site format. "
            "Use just the domain (e.g., mycompany.atlassian.net)"
        )
        sys.exit(2)

    # Save credentials
    try:
        save_credentials(site=site, email=email, token=token_value)
        console.print(f"[green]✓[/green] Credentials saved for {email} at {site}")
    except OSError as e:
        console.print(f"[red]Error:[/red] Failed to save credentials: {e}")
        sys.exit(1)


@app.command()
def logout() -> None:
    """Delete stored authentication credentials.

    Succeeds silently if no credentials exist.
    """
    delete_credentials()
    console.print("[green]✓[/green] Logged out")
