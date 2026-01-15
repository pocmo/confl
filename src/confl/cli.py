"""CLI entry point."""


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

# Global profile context
_profile: str | None = None


def get_profile() -> str | None:
    """Get the current profile name."""
    return _profile


@app.callback()
def main(
    profile: str | None = typer.Option(
        None,
        "--profile",
        help="Configuration profile to use (can also set CONFL_PROFILE env var)",
    ),
) -> None:
    """An unofficial CLI for Atlassian Confluence Cloud."""
    global _profile
    _profile = profile


if __name__ == "__main__":
    app()
