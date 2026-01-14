"""Page commands."""

import json
import re
import sys
from typing import Any

import typer
from rich.console import Console

from confl.client import ApiError, ConfluenceClient, get_client

app = typer.Typer(help="Manage pages")
console = Console()
err_console = Console(stderr=True)


def _extract_page_id(ref: str) -> str:
    """Extract page ID from a reference (ID or URL).

    Args:
        ref: Page reference - either a numeric ID or Confluence URL

    Returns:
        Page ID as string

    Raises:
        ValueError: If the reference is invalid
    """
    # If it's just a number, return it
    if ref.isdigit():
        return ref

    # Try to extract from URL
    # URL patterns:
    # https://company.atlassian.net/wiki/spaces/KEY/pages/12345678/Title
    # https://company.atlassian.net/wiki/spaces/KEY/pages/12345678
    match = re.search(r"/pages/(\d+)", ref)
    if match:
        return match.group(1)

    raise ValueError(f"Invalid page reference: {ref}")


def _format_page_metadata(page: dict[str, Any]) -> str:
    """Format page metadata as a header.

    Args:
        page: Page data from API

    Returns:
        Formatted metadata string
    """
    lines = []
    lines.append(f"Title: {page.get('title', 'Untitled')}")

    # Space key
    if "spaceId" in page:
        # TODO: For now just show the space ID, later we can resolve to key
        lines.append(f"Space: {page['spaceId']}")

    # Author (from version history)
    version = page.get("version", {})
    if "authorId" in version:
        lines.append(f"Author: {version['authorId']}")

    # Updated timestamp
    if "createdAt" in version:
        # Extract just the date portion (YYYY-MM-DD)
        timestamp = version["createdAt"]
        date = timestamp.split("T")[0] if "T" in timestamp else timestamp
        lines.append(f"Updated: {date}")

    lines.append("---")
    return "\n".join(lines)


def _get_page_content(page: dict[str, Any], format_type: str = "storage") -> str:
    """Extract page content in the specified format.

    Args:
        page: Page data from API
        format_type: Content format ("storage" or "atlas_doc_format")

    Returns:
        Page content as string
    """
    body = page.get("body", {})
    format_data = body.get(format_type, {})
    value = format_data.get("value", "")
    return str(value)


@app.command("get")
def get_page(
    ref: str = typer.Argument(..., help="Page ID or URL"),
    body_only: bool = typer.Option(False, "--body-only", help="Suppress metadata header"),
    json_output: bool = typer.Option(False, "--json", help="Output full API response as JSON"),
    raw: bool = typer.Option(False, "--raw", help="Output Confluence storage format"),
    markdown: bool = typer.Option(
        False, "--markdown", help="Output raw markdown (when conversion ready)"
    ),
) -> None:
    """Fetch and display a page.

    Examples:
        confl page get 12345678
        confl page get "https://company.atlassian.net/wiki/spaces/DEV/pages/12345678/Title"
        confl page get 12345678 --json
        confl page get 12345678 --raw
        confl page get 12345678 --body-only
    """
    try:
        page_id = _extract_page_id(ref)
    except ValueError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)

    # Get the page
    try:
        client = get_client()
        confluence = ConfluenceClient(client)
        page = confluence.get_page(page_id)
    except ApiError as e:
        err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output based on flags
    if json_output:
        print(json.dumps(page, indent=2))
    elif raw:
        content = _get_page_content(page, "storage")
        if not body_only:
            console.print(_format_page_metadata(page))
        print(content)
    elif markdown:
        # TODO: Implement markdown conversion when ready
        err_console.print(
            "[yellow]Warning:[/yellow] Markdown conversion not yet implemented. "
            "Showing storage format instead."
        )
        content = _get_page_content(page, "storage")
        if not body_only:
            console.print(_format_page_metadata(page))
        print(content)
    else:
        # Default: Rich terminal output
        # For now, show storage format as it is
        # TODO: Convert to markdown first, then render with Rich
        if not body_only:
            console.print(_format_page_metadata(page))

        content = _get_page_content(page, "storage")
        # Try to render as markdown for now (will be improved with proper conversion)
        # For now just print the content
        console.print(content)
