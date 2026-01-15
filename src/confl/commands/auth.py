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


def _get_auth_source(profile: str | None = None) -> str:
    """Determine the authentication source.

    Args:
        profile: Profile name to check. If None, checks default profile.

    Returns:
        "environment" if any CONFL_* env vars are set,
        "credentials" if only credentials file is used,
        "none" if not authenticated
    """
    # Check if any env vars are set
    if any(var in os.environ for var in ["CONFL_SITE", "CONFL_EMAIL", "CONFL_TOKEN"]):
        return "environment"

    # Check if credentials file exists
    creds = load_credentials(profile)
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
    profile: str | None = typer.Option(None, "--profile", help="Profile to check status for"),
) -> None:
    """Show current authentication status.

    Displays the authentication source, site, email, and masked token.
    Exit code 0 if authenticated, 1 if not authenticated.
    """
    output: dict[str, Any]

    # Import here to use CLI context profile if not explicitly provided
    from confl.cli import get_context

    if profile is None:
        profile = get_context().profile

    auth_source = _get_auth_source(profile)

    if auth_source == "none":
        profile_msg = f" for profile '{profile}'" if profile else ""
        if json_output:
            output = {
                "authenticated": False,
                "profile": profile,
                "source": None,
                "site": None,
                "email": None,
                "token": None,
            }
            print(json.dumps(output, indent=2))
        else:
            console.print(f"[red]Not authenticated{profile_msg}[/red]")
            console.print("\nSet environment variables (CONFL_SITE, CONFL_EMAIL, CONFL_TOKEN)")
            console.print("or run 'confl auth login' to store credentials.")
        sys.exit(1)

    # Try to load config (will raise ConfigError if invalid)
    try:
        config = get_config(profile)
    except ConfigError as e:
        if json_output:
            output = {
                "authenticated": False,
                "profile": profile,
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
            "profile": profile,
            "source": auth_source,
            "site": config.site,
            "email": config.email,
            "token": _mask_token(config.token),
        }
        print(json.dumps(output, indent=2))
    else:
        profile_msg = f" (profile: {profile})" if profile else ""
        console.print(f"[green]Authenticated via:[/green] {source_display}{profile_msg}")
        console.print(f"[cyan]Site:[/cyan] {config.site}")
        console.print(f"[cyan]Email:[/cyan] {config.email}")
        console.print(f"[cyan]Token:[/cyan] {_mask_token(config.token)}")

    sys.exit(0)


@app.command()
def login(
    token: bool = typer.Option(False, "--token", help="Read token from stdin"),
    site: str = typer.Option(..., "--site", help="Confluence site (e.g., mycompany.atlassian.net)"),
    email: str = typer.Option(..., "--email", help="Email address for authentication"),
    profile: str = typer.Option(
        "default", "--profile", help="Profile name to save credentials under"
    ),
) -> None:
    """Store authentication credentials.

    Reads the API token from stdin (non-interactive, pipeable).

    Example:
        echo "$TOKEN" | confl auth login --token --site mycompany.atlassian.net \\
            --email user@example.com
        
        # Save to a named profile:
        echo "$TOKEN" | confl auth login --token --site dev.atlassian.net \\
            --email user@example.com --profile dev
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
        save_credentials(site=site, email=email, token=token_value, profile=profile)
        profile_msg = f" (profile: {profile})" if profile != "default" else ""
        console.print(f"[green]✓[/green] Credentials saved for {email} at {site}{profile_msg}")
    except OSError as e:
        console.print(f"[red]Error:[/red] Failed to save credentials: {e}")
        sys.exit(1)


@app.command()
def logout(
    profile: str | None = typer.Option(
        None, "--profile", help="Profile name to delete. If not specified, deletes all profiles."
    ),
) -> None:
    """Delete stored authentication credentials.

    By default, deletes all profiles. Use --profile to delete a specific profile.

    Examples:
        confl auth logout              # Delete all profiles
        confl auth logout --profile dev  # Delete only 'dev' profile
    """
    delete_credentials(profile)
    if profile:
        console.print(f"[green]✓[/green] Logged out from profile '{profile}'")
    else:
        console.print("[green]✓[/green] Logged out (all profiles deleted)")


@app.command(name="list")
def list_profiles_command() -> None:
    """List all available profiles.

    Shows all configured profiles and indicates the default profile.
    """
    from confl.credentials import get_default_profile, list_profiles

    profiles = list_profiles()

    if not profiles:
        console.print("[yellow]No profiles configured[/yellow]")
        console.print("\nRun 'confl auth login' to add a profile")
        return

    default_profile = get_default_profile()

    console.print("[cyan]Available profiles:[/cyan]")
    for profile_name in sorted(profiles):
        if profile_name == default_profile:
            console.print(f"  • {profile_name} [dim](default)[/dim]")
        else:
            console.print(f"  • {profile_name}")

    console.print(f"\n[dim]Total: {len(profiles)} profile(s)[/dim]")
