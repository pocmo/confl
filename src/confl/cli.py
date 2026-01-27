"""CLI entry point."""

import logging

import typer

from confl import __version__
from confl.commands import attachment, auth, blogpost, comment, label, page, search, space, task
from confl.context import ExecutionContext

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
app.add_typer(task.app, name="task")

# Register direct commands
app.command(name="search")(search.search_command)

# Global execution context
_context = ExecutionContext()


def get_context() -> ExecutionContext:
    """Get the current execution context."""
    return _context


# Deprecated: Use get_context() instead
def get_profile() -> str | None:
    """Get the current profile name."""
    return _context.profile


def is_verbose() -> bool:
    """Check if verbose mode is enabled."""
    return _context.verbose


def is_debug() -> bool:
    """Check if debug mode is enabled."""
    return _context.debug


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"confl version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
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
    global _context
    _context = ExecutionContext(
        profile=profile,
        verbose=verbose,
        debug=debug,
    )

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
