"""CLI entry point."""

import logging

import typer

from confl.commands import attachment, auth, blogpost, comment, label, page, search, space

app = typer.Typer(
    name="confl",
    help="An unofficial CLI for Atlassian Confluence Cloud.",
    no_args_is_help=True,
)

# Register command groups
app.add_typer(auth.app, name="auth")
app.add_typer(page.app, name="page")
app.add_typer(space.app, name="space")
app.add_typer(attachment.app, name="attachment")
app.add_typer(label.app, name="label")
app.add_typer(comment.app, name="comment")
app.add_typer(blogpost.app, name="blogpost")

# Register direct commands
app.command(name="search")(search.search_command)

# Global context
_profile: str | None = None
_verbose: bool = False
_debug: bool = False


def get_profile() -> str | None:
    """Get the current profile name."""
    return _profile


def is_verbose() -> bool:
    """Check if verbose mode is enabled."""
    return _verbose


def is_debug() -> bool:
    """Check if debug mode is enabled."""
    return _debug


@app.callback()
def main(
    profile: str | None = typer.Option(
        None,
        "--profile",
        help="Configuration profile to use (can also set CONFL_PROFILE env var)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed operation information",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Show debug information including HTTP requests/responses",
    ),
) -> None:
    """An unofficial CLI for Atlassian Confluence Cloud."""
    global _profile, _verbose, _debug
    _profile = profile
    _verbose = verbose
    _debug = debug

    # Configure logging based on flags
    if debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(levelname)s] %(message)s",
        )
    elif verbose:
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
        )


if __name__ == "__main__":
    app()
