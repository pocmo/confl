"""CLI entry point."""

import typer

from confl.commands import auth, page

app = typer.Typer(
    name="confl",
    help="An unofficial CLI for Atlassian Confluence Cloud.",
    no_args_is_help=True,
)

# Register command groups
app.add_typer(auth.app, name="auth")
app.add_typer(page.app, name="page")


@app.callback()
def main() -> None:
    """An unofficial CLI for Atlassian Confluence Cloud."""
    pass


if __name__ == "__main__":
    app()
