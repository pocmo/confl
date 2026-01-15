"""Page commands."""

import json
import re
import sys
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from confl.client import ApiError, ConfluenceClient, get_client
from confl.converter import markdown_to_storage, storage_to_markdown

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

    raise ValueError(
        f"Invalid page reference: {ref!r}\n\n"
        "Page references must be either:\n"
        "  • A numeric page ID (e.g., 12345678)\n"
        "  • A full Confluence page URL\n\n"
        "Examples:\n"
        "  confl page get 12345678\n"
        '  confl page get "https://company.atlassian.net/wiki/spaces/DEV/pages/12345678"\n\n'
        "Tip: Use 'confl search <query>' to find page IDs"
    )


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


def _strip_markdown(markdown_text: str) -> str:
    """Strip markdown formatting to produce plain text.

    Args:
        markdown_text: Markdown formatted text

    Returns:
        Plain text with markdown syntax removed
    """
    text = markdown_text

    # Remove code blocks (```...```)
    text = re.sub(r"```[\s\S]*?```", "", text)

    # Remove inline code (`...`)
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # Remove bold/italic (**text**, *text*, __text__, _text_)
    text = re.sub(r"\*\*([^\*]+)\*\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"\*([^\*]+)\*", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)

    # Remove links [text](url) -> text
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

    # Remove images ![alt](url)
    text = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", r"\1", text)

    # Remove headers (#, ##, ###, etc.)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    # Remove blockquotes (>)
    text = re.sub(r"^>\s+", "", text, flags=re.MULTILINE)

    # Remove horizontal rules (---, ***, ___)
    text = re.sub(r"^(\*{3,}|-{3,}|_{3,})$", "", text, flags=re.MULTILINE)

    # Remove list markers (-, *, +, 1.)
    text = re.sub(r"^[\s]*[-\*\+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[\s]*\d+\.\s+", "", text, flags=re.MULTILINE)

    # Clean up extra whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    return text


@app.command("get")
def get_page(
    ref: str = typer.Argument(..., help="Page ID or URL"),
    body_only: bool = typer.Option(False, "--body-only", help="Suppress metadata header"),
    json_output: bool = typer.Option(False, "--json", help="Output full API response as JSON"),
    raw: bool = typer.Option(False, "--raw", help="Output Confluence storage format"),
    markdown: bool = typer.Option(
        False, "--markdown", help="Output raw markdown (converted from storage format)"
    ),
    plain: bool = typer.Option(False, "--plain", help="Output plain text (stripped of formatting)"),
) -> None:
    """Fetch and display a page.

    Examples:
        confl page get 12345678
        confl page get "https://company.atlassian.net/wiki/spaces/DEV/pages/12345678/Title"
        confl page get 12345678 --json
        confl page get 12345678 --raw
        confl page get 12345678 --markdown
        confl page get 12345678 --plain
        confl page get 12345678 --body-only
    """
    try:
        page_id = _extract_page_id(ref)
    except ValueError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)

    # Validate mutually exclusive format flags
    format_flags = [json_output, raw, markdown, plain]
    if sum(format_flags) > 1:
        err_console.print(
            "[red]Error:[/red] Only one output format flag can be used at a time "
            "(--json, --raw, --markdown, --plain)"
        )
        sys.exit(2)

    # Get the page
    try:
        client = get_client()
        confluence = ConfluenceClient(client)
        page = confluence.get_page(page_id)
    except ApiError as e:
        if json_output and e.response_data:
            # Output raw error JSON to stderr
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            # Human-readable error message
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
        # Output raw markdown (converted from storage)
        content = _get_page_content(page, "storage")
        markdown_content = storage_to_markdown(content)
        if not body_only:
            console.print(_format_page_metadata(page))
        print(markdown_content)
    elif plain:
        # Output plain text (converted from storage, stripped of markdown)
        content = _get_page_content(page, "storage")
        markdown_content = storage_to_markdown(content)
        plain_content = _strip_markdown(markdown_content)
        if not body_only:
            console.print(_format_page_metadata(page))
        print(plain_content)
    else:
        # Default: Rich terminal output with Markdown rendering
        if not body_only:
            console.print(_format_page_metadata(page))

        # Get storage content and convert to Markdown
        content = _get_page_content(page, "storage")
        markdown_content = storage_to_markdown(content)

        # Render with Rich's Markdown renderer
        md = Markdown(markdown_content)
        console.print(md)


@app.command("list")
def list_pages(
    space: str = typer.Option(..., "--space", help="Space key to filter by"),
    limit: int = typer.Option(25, "--limit", help="Maximum number of results"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON array"),
) -> None:
    """List pages in a space.

    Examples:
        confl page list --space DEV
        confl page list --space DEV --limit 50
        confl page list --space DEV --json
    """
    try:
        client = get_client()
        confluence = ConfluenceClient(client)
        pages = confluence.list_pages(space_key=space, limit=limit)
    except ApiError as e:
        if json_output and e.response_data:
            # Output raw error JSON to stderr
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            # Human-readable error message
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output based on flags
    if json_output:
        print(json.dumps(pages, indent=2))
    else:
        # Rich table output
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("ID", style="dim")
        table.add_column("Title")
        table.add_column("Space")
        table.add_column("Updated")

        for page in pages:
            page_id = page.get("id", "")
            title = page.get("title", "Untitled")
            space_id = page.get("spaceId", "")

            # Extract updated date from version
            updated = ""
            version = page.get("version", {})
            if "createdAt" in version:
                timestamp = version["createdAt"]
                updated = timestamp.split("T")[0] if "T" in timestamp else timestamp

            table.add_row(page_id, title, space_id, updated)

        console.print(table)

        if not pages:
            console.print("[yellow]No pages found in this space.[/yellow]")


@app.command("delete")
def delete_page(
    ref: str = typer.Argument(..., help="Page ID or URL"),
    json_output: bool = typer.Option(False, "--json", help="Output result as JSON"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
) -> None:
    """Delete a page.

    Examples:
        confl page delete 12345678
        confl page delete "https://company.atlassian.net/wiki/spaces/DEV/pages/12345678/Title"
        confl page delete 12345678 --json
        confl page delete 12345678 --dry-run
    """
    try:
        page_id = _extract_page_id(ref)
    except ValueError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)

    # Dry-run mode
    if dry_run:
        if json_output:
            result = {"dry_run": True, "action": "delete", "page_id": page_id}
            print(json.dumps(result, indent=2))
        else:
            console.print(f"[yellow]DRY RUN:[/yellow] Would delete page {page_id}")
        return

    # Delete the page
    try:
        client = get_client()
        confluence = ConfluenceClient(client)
        confluence.delete_page(page_id)
    except ApiError as e:
        if json_output and e.response_data:
            # Output raw error JSON to stderr
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            # Human-readable error message
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output success
    if json_output:
        result = {"success": True, "page_id": page_id, "message": "Page deleted successfully"}
        print(json.dumps(result, indent=2))
    else:
        console.print(f"[green]✓[/green] Page {page_id} deleted successfully")


@app.command("create")
def create_page(
    space: str = typer.Option(..., "--space", help="Space key (e.g., DEV)"),
    title: str = typer.Option(..., "--title", help="Page title"),
    body: str = typer.Option(None, "--body", help="Page content (Markdown by default)"),
    body_file: str = typer.Option(None, "--body-file", help="Read content from file"),
    parent: str = typer.Option(None, "--parent", help="Parent page ID (optional)"),
    raw: bool = typer.Option(False, "--raw", help="Provide content in storage format directly"),
    json_output: bool = typer.Option(False, "--json", help="Output result as JSON"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
) -> None:
    """Create a new page.

    Examples:
        confl page create --space DEV --title "My Page" --body "# Content"
        confl page create --space DEV --title "My Page" --body-file content.md
        cat content.md | confl page create --space DEV --title "My Page"
        confl page create --space DEV --title "Child" --parent 12345678 --body "Content"
        confl page create --space DEV --title "Page" --body "<p>HTML</p>" --raw
        confl page create --space DEV --title "My Page" --body "# Content" --dry-run
    """
    # Get content from various sources
    content = None
    if body:
        content = body
    elif body_file:
        try:
            with open(body_file, encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            err_console.print(
                f"[red]Error:[/red] File not found: {body_file}\n\n"
                "Please check:\n"
                "  • The file path is correct\n"
                "  • The file exists in the current directory\n"
                "  • You have permission to read the file\n\n"
                f"Current directory: {Path.cwd()}"
            )
            sys.exit(2)
        except Exception as e:
            err_console.print(f"[red]Error:[/red] Failed to read file: {e}")
            sys.exit(2)
    elif not sys.stdin.isatty():
        # Read from stdin
        stdin_content = sys.stdin.read()
        # Only use stdin if it's not empty
        if stdin_content and stdin_content.strip():
            content = stdin_content

    # Must provide content
    if content is None:
        err_console.print(
            "[red]Error:[/red] Must provide content via --body, --body-file, or stdin"
        )
        sys.exit(2)

    # Convert markdown to storage format unless --raw
    storage_content = content if raw else markdown_to_storage(content)

    # Dry-run mode
    if dry_run:
        if json_output:
            result = {
                "dry_run": True,
                "action": "create",
                "space": space,
                "title": title,
                "parent": parent,
                "content_length": len(storage_content),
            }
            print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]DRY RUN:[/yellow] Would create page:")
            console.print(f"  Title: {title}")
            console.print(f"  Space: {space}")
            console.print(f"  Parent: {parent or 'none'}")
            console.print(f"  Content: {len(storage_content)} characters")
        return

    # Get space ID from space key
    try:
        client = get_client()
        confluence = ConfluenceClient(client)
        space_data = confluence.get_space_by_key(space)
        space_id = space_data.get("id")
        if not space_id:
            err_console.print(f"[red]Error:[/red] Could not get space ID for space: {space}")
            sys.exit(1)
    except ApiError as e:
        if json_output and e.response_data:
            # Output raw error JSON to stderr
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            # Human-readable error message
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Create the page
    try:
        created_page = confluence.create_page(
            space_id=space_id,
            title=title,
            body=storage_content,
            parent_id=parent,
        )
    except ApiError as e:
        if json_output and e.response_data:
            # Output raw error JSON to stderr
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            # Human-readable error message
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output success
    if json_output:
        print(json.dumps(created_page, indent=2))
    else:
        page_id = created_page.get("id", "")
        page_links = created_page.get("_links", {})
        web_ui = page_links.get("webui", "")

        # Construct full URL if we have the base URL
        page_url = ""
        if web_ui and hasattr(client, "base_url"):
            page_url = f"{client.base_url}{web_ui}"

        console.print("[green]✓[/green] Page created successfully")
        console.print(f"ID: {page_id}")
        if page_url:
            console.print(f"URL: {page_url}")


@app.command("update")
def update_page(
    ref: str = typer.Argument(..., help="Page ID or URL"),
    body: str = typer.Option(None, "--body", help="Page content (Markdown by default)"),
    body_file: str = typer.Option(None, "--body-file", help="Read content from file"),
    title: str = typer.Option(
        None, "--title", help="New page title (keep existing if not provided)"
    ),
    raw: bool = typer.Option(False, "--raw", help="Provide content in storage format directly"),
    json_output: bool = typer.Option(False, "--json", help="Output result as JSON"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
) -> None:
    """Update an existing page's content and/or title.

    Examples:
        confl page update 12345678 --body "# Updated content"
        confl page update 12345678 --body-file content.md
        cat content.md | confl page update 12345678
        confl page update 12345678 --title "New Title"
        confl page update 12345678 --body "Content" --title "New Title"
        confl page update 12345678 --body "<p>HTML</p>" --raw
        confl page update 12345678 --body "# Content" --dry-run
    """
    # Extract page ID
    try:
        page_id = _extract_page_id(ref)
    except ValueError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)

    # Get content from various sources
    content = None
    if body:
        content = body
    elif body_file:
        try:
            with open(body_file, encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            err_console.print(
                f"[red]Error:[/red] File not found: {body_file}\n\n"
                "Please check:\n"
                "  • The file path is correct\n"
                "  • The file exists in the current directory\n"
                "  • You have permission to read the file\n\n"
                f"Current directory: {Path.cwd()}"
            )
            sys.exit(2)
        except Exception as e:
            err_console.print(f"[red]Error:[/red] Failed to read file: {e}")
            sys.exit(2)
    elif not sys.stdin.isatty():
        # Read from stdin
        stdin_content = sys.stdin.read()
        # Only use stdin if it's not empty
        if stdin_content and stdin_content.strip():
            content = stdin_content

    # Must provide either content or title
    if content is None and title is None:
        err_console.print(
            "[red]Error:[/red] Must provide content via --body, --body-file, stdin, or --title"
        )
        sys.exit(2)

    # Dry-run mode (early exit, no API calls needed)
    if dry_run:
        updates = []
        if title:
            updates.append(f"title to '{title}'")
        if content:
            updates.append(f"content ({len(content)} characters)")

        if json_output:
            result = {
                "dry_run": True,
                "action": "update",
                "page_id": page_id,
                "title": title,
                "content_length": len(content) if content else None,
            }
            print(json.dumps(result, indent=2))
        else:
            console.print(f"[yellow]DRY RUN:[/yellow] Would update page {page_id}:")
            for update in updates:
                console.print(f"  - Set {update}")
        return

    # Get current page to fetch version and existing title/content
    try:
        client = get_client()
        confluence = ConfluenceClient(client)
        current_page = confluence.get_page(page_id)
    except ApiError as e:
        if json_output and e.response_data:
            # Output raw error JSON to stderr
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            # Human-readable error message
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Get current version number for optimistic locking
    version_number = current_page.get("version", {}).get("number", 1)

    # Use provided title or keep existing
    new_title = title if title is not None else current_page.get("title", "Untitled")

    # Process content
    if content is not None:
        # Convert markdown to storage format unless --raw
        storage_content = content if raw else markdown_to_storage(content)
    else:
        # No new content provided, keep existing
        storage_content = _get_page_content(current_page, "storage")

    # Update the page
    try:
        updated_page = confluence.update_page(
            page_id=page_id,
            title=new_title,
            body=storage_content,
            version_number=version_number + 1,
        )
    except ApiError as e:
        if json_output and e.response_data:
            # Output raw error JSON to stderr
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            # Human-readable error message
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output success
    if json_output:
        print(json.dumps(updated_page, indent=2))
    else:
        new_version = updated_page.get("version", {}).get("number", "")
        console.print(
            f"[green]✓[/green] Page {page_id} updated successfully (version {new_version})"
        )
