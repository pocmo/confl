"""CLI entry point."""

import typer

from confl.commands import auth

app = typer.Typer(
    name="confl",
    help="An unofficial CLI for Atlassian Confluence Cloud.",
    no_args_is_help=True,
)

# Register command groups
app.add_typer(auth.app, name="auth")


@app.callback()
def main() -> None:
    """An unofficial CLI for Atlassian Confluence Cloud."""
    pass


if __name__ == "__main__":
    app()
