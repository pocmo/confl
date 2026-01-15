"""Search commands."""

import html
import json
import sys

import typer
from rich.console import Console

from confl.client import ApiError, ConfluenceClient, get_client
from confl.cql import build_cql_query
from confl.table_formatter import add_column_with_ellipsis, create_table

console = Console()
err_console = Console(stderr=True)


def search_command(
    query: str | None = typer.Argument(None, help="Raw CQL query string"),
    text: str | None = typer.Option(None, "--text", help="Search for text in content"),
    space: str | None = typer.Option(None, "--space", help="Filter by space key"),
    content_type: str | None = typer.Option(
        None, "--type", help="Filter by content type (page, blogpost, etc.)"
    ),
    label: str | None = typer.Option(None, "--label", help="Filter by label"),
    limit: int = typer.Option(25, "--limit", help="Maximum number of results"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON array"),
) -> None:
    """Search for Confluence content using CQL or simple filters.

    Two modes of operation:

    1. Raw CQL query (power users):
       confl search "space = DEV AND type = page ORDER BY lastmodified DESC"

    2. Simple filters (common cases):
       confl search --text "API docs" --space DEV --type page --label draft

    Examples:
        # Search for text in a space
        confl search --text "database migration" --space ENG

        # Find all pages with a label
        confl search --type page --label architecture

        # Raw CQL for complex queries
        confl search "space = MARKETING AND created >= now('-7d')"

        # Combine filters
        confl search --text "meeting notes" --space TEAM --type page
    """
    # Determine which mode: raw CQL or flags
    has_flags = any([text, space, content_type, label])

    if query and has_flags:
        err_console.print(
            "[red]Error:[/red] Cannot use both raw CQL query and filter flags. "
            "Use either 'confl search \"CQL\"' or 'confl search --text/--space/--type/--label'."
        )
        sys.exit(1)

    if not query and not has_flags:
        err_console.print(
            "[red]Error:[/red] No search criteria provided. "
            "Specify either a raw CQL query or use filter flags (--text, --space, --type, --label)."
        )
        sys.exit(1)

    # Build CQL query from flags or use raw query
    if has_flags:
        cql = build_cql_query(text=text, space=space, content_type=content_type, label=label)
        if not cql:
            err_console.print("[red]Error:[/red] No valid search conditions provided.")
            sys.exit(1)
    else:
        cql = query  # type: ignore

    try:
        client = get_client()
        confluence = ConfluenceClient(client)
        results = confluence.search_content(cql, limit=limit)
    except ApiError as e:
        if json_output and e.response_data:
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output based on flags
    if json_output:
        print(json.dumps(results, indent=2))
    else:
        # Rich table output with enhanced formatting
        table = create_table()
        add_column_with_ellipsis(table, "Type", style="dim")
        add_column_with_ellipsis(table, "ID", style="dim")
        add_column_with_ellipsis(table, "Title", max_width=60)
        add_column_with_ellipsis(table, "Space")

        for result in results:
            # v1 API response structure
            content = result.get("content", {})
            content_type_val = content.get("type", "")
            content_id = content.get("id", "")
            title = html.unescape(result.get("title", "Untitled"))

            # Extract space key if available
            space_data = content.get("space", {})
            space_key = space_data.get("key", "")

            table.add_row(content_type_val, content_id, title, space_key)

        if not results:
            console.print("[yellow]No results found for your search.[/yellow]")
        else:
            console.print(table)
            console.print(f"\n[dim]Found {len(results)} result(s)[/dim]")
