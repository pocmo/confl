"""Comment commands."""

import json
import sys
from pathlib import Path
from typing import Any

import typer
from rich.console import Console

from confl.client import ApiError, ConfluenceClient, get_client
from confl.converter import markdown_to_storage, storage_to_markdown
from confl.formatters import format_relative_time
from confl.table_formatter import add_column_with_ellipsis, create_table

app = typer.Typer(help="Manage comments")
console = Console()
err_console = Console(stderr=True)


def _extract_page_id(ref: str) -> str:
    """Extract page ID from reference.

    Args:
        ref: Page reference - either page ID or URL

    Returns:
        Page ID as string
    """
    # If it looks like a URL, extract the page ID
    if "://" in ref or ref.startswith("/"):
        # URL format: https://<site>/wiki/spaces/<key>/pages/<id>/<title>
        # or: /wiki/spaces/<key>/pages/<id>/<title>
        parts = ref.split("/pages/")
        if len(parts) >= 2:
            # Get ID part (may have trailing /title)
            id_part = parts[1].split("/")[0]
            return id_part

    # Otherwise assume it's already an ID
    return ref


def _format_comment_body(comment: dict[str, Any]) -> str:
    """Extract and format comment body content.

    Args:
        comment: Comment object from API

    Returns:
        Comment body as plain text or markdown
    """
    body = comment.get("body", {})
    storage = body.get("storage", {})
    value = storage.get("value", "")

    # Try to convert storage format to markdown
    try:
        return storage_to_markdown(value)
    except Exception:
        # If conversion fails, return raw content
        return str(value)


@app.command("list")
def list_comments(
    page: str = typer.Option(None, "--page", help="Page ID or URL to filter by"),
    limit: int = typer.Option(25, "--limit", help="Maximum number of results"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON array"),
    include_inline: bool = typer.Option(False, "--include-inline", help="Include inline comments"),
) -> None:
    """List comments on a page or all comments.

    Examples:
        confl comment list --page 123456
        confl comment list --page 123456 --include-inline
        confl comment list --json
    """
    try:
        page_id = _extract_page_id(page) if page else None
        client = get_client()
        confluence = ConfluenceClient(client)

        # Get footer comments
        footer_comments = confluence.list_footer_comments(page_id, limit=limit)

        # Get inline comments if requested
        inline_comments = []
        if include_inline:
            inline_comments = confluence.list_inline_comments(page_id, limit=limit)

        # Combine results
        all_comments = footer_comments + inline_comments

    except ApiError as e:
        if json_output and e.response_data:
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output based on flags
    if json_output:
        print(json.dumps(all_comments, indent=2))
    else:
        # Rich table output with enhanced formatting
        table = create_table()
        add_column_with_ellipsis(table, "ID", style="dim")
        add_column_with_ellipsis(table, "Type")
        add_column_with_ellipsis(table, "Body Preview", max_width=50)
        add_column_with_ellipsis(table, "Author", max_width=20)
        add_column_with_ellipsis(table, "Created")

        for comment in all_comments:
            comment_id = comment.get("id", "")
            comment_type = "inline" if "inlineCommentProperties" in comment else "footer"

            # Get body preview (first 50 chars)
            body_text = _format_comment_body(comment)
            body_preview = body_text[:50].replace("\n", " ")
            if len(body_text) > 50:
                body_preview += "..."

            # Get author
            author_id = comment.get("authorId", "unknown")

            # Get creation date
            created_at = comment.get("createdAt", "")
            created_relative = format_relative_time(created_at) if created_at else ""

            table.add_row(comment_id, comment_type, body_preview, author_id, created_relative)

        if not all_comments:
            console.print("[yellow]No comments found.[/yellow]")
        else:
            console.print(table)


@app.command("get")
def get_comment(
    comment_id: str = typer.Argument(..., help="Comment ID"),
    json_output: bool = typer.Option(False, "--json", help="Output full API response as JSON"),
    markdown: bool = typer.Option(False, "--markdown", help="Output body as markdown"),
) -> None:
    """Get comment details.

    Note: Images and attachments are not displayed in terminal output.
    Use --json to see attachment references.

    Examples:
        confl comment get 123456
        confl comment get 123456 --markdown
        confl comment get 123456 --json
    """
    try:
        client = get_client()
        confluence = ConfluenceClient(client)

        # Try footer comment first
        try:
            comment = confluence.get_footer_comment(comment_id)
        except ApiError:
            # Try inline comment
            comment = confluence.get_inline_comment(comment_id)

    except ApiError as e:
        if json_output and e.response_data:
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output based on flags
    if json_output:
        print(json.dumps(comment, indent=2))
    elif markdown:
        body_text = _format_comment_body(comment)
        print(body_text)
    else:
        # Rich formatted output
        console.print(f"[bold cyan]ID:[/bold cyan] {comment.get('id', '')}")

        comment_type = "inline" if "inlineCommentProperties" in comment else "footer"
        console.print(f"[bold cyan]Type:[/bold cyan] {comment_type}")

        console.print(f"[bold cyan]Author:[/bold cyan] {comment.get('authorId', 'unknown')}")

        created_at = comment.get("createdAt", "")
        console.print(f"[bold cyan]Created:[/bold cyan] {created_at}")

        version = comment.get("version", {})
        if "createdAt" in version:
            console.print(f"[bold cyan]Modified:[/bold cyan] {version['createdAt']}")

        console.print("\n[bold cyan]Body:[/bold cyan]")
        body_text = _format_comment_body(comment)
        console.print(body_text)


@app.command("add")
def add_comment(
    page: str = typer.Option(None, "--page", help="Page ID or URL to comment on"),
    body: str = typer.Option(None, "--body", help="Comment body text (markdown)"),
    body_file: str = typer.Option(None, "--body-file", help="Read body from file"),
    parent: str = typer.Option(None, "--parent", help="Parent comment ID for replies"),
    json_output: bool = typer.Option(False, "--json", help="Output full API response as JSON"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
) -> None:
    """Add a comment to a page or reply to another comment.

    Examples:
        confl comment add --page 123456 --body "Great work!"
        confl comment add --page 123456 --body-file comment.md
        confl comment add --parent 789012 --body "I agree"
        confl comment add --page 123456 --body "Comment" --dry-run
    """
    try:
        # Validate inputs
        if not page and not parent:
            err_console.print("[red]Error:[/red] Must provide either --page or --parent")
            sys.exit(1)

        if not body and not body_file:
            err_console.print("[red]Error:[/red] Must provide either --body or --body-file")
            sys.exit(1)

        # Get body content
        body_text = Path(body_file).read_text() if body_file else body or ""

        # Convert markdown to storage format
        storage_body = markdown_to_storage(body_text)

        page_id = _extract_page_id(page) if page else None

        # Dry-run mode
        if dry_run:
            if json_output:
                result = {
                    "dry_run": True,
                    "action": "add_comment",
                    "page_id": page_id,
                    "parent_comment_id": parent,
                    "body_length": len(storage_body),
                }
                print(json.dumps(result, indent=2))
            else:
                console.print("[yellow]DRY RUN:[/yellow] Would add comment:")
                if page_id:
                    console.print(f"  Page: {page_id}")
                if parent:
                    console.print(f"  Parent comment: {parent}")
                console.print(f"  Body: {len(storage_body)} characters")
            return

        client = get_client()
        confluence = ConfluenceClient(client)

        # Create comment
        result = confluence.create_footer_comment(
            body=storage_body,
            page_id=page_id,
            parent_comment_id=parent,
        )

    except FileNotFoundError as e:
        err_console.print(
            f"[red]Error:[/red] {e}\n\n"
            "Please check:\n"
            "  • The file path is correct\n"
            "  • The file exists in the current directory\n"
            "  • You have permission to read the file\n\n"
            f"Current directory: {Path.cwd()}"
        )
        sys.exit(1)
    except ApiError as e:
        if json_output and e.response_data:
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output based on flags
    if json_output:
        print(json.dumps(result, indent=2))
    else:
        comment_id = result.get("id", "")
        console.print(f"[green]Created comment {comment_id}[/green]")


@app.command("update")
def update_comment(
    comment_id: str = typer.Argument(..., help="Comment ID to update"),
    body: str = typer.Option(None, "--body", help="New comment body text (markdown)"),
    body_file: str = typer.Option(None, "--body-file", help="Read body from file"),
    json_output: bool = typer.Option(False, "--json", help="Output full API response as JSON"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
) -> None:
    """Update a comment's body.

    Examples:
        confl comment update 123456 --body "Updated text"
        confl comment update 123456 --body-file comment.md
        confl comment update 123456 --body "Updated" --dry-run
    """
    try:
        if not body and not body_file:
            err_console.print("[red]Error:[/red] Must provide either --body or --body-file")
            sys.exit(1)

        # Get body content
        body_text = Path(body_file).read_text() if body_file else body or ""

        # Convert markdown to storage format
        storage_body = markdown_to_storage(body_text)

        # Dry-run mode
        if dry_run:
            if json_output:
                result = {
                    "dry_run": True,
                    "action": "update_comment",
                    "comment_id": comment_id,
                    "body_length": len(storage_body),
                }
                print(json.dumps(result, indent=2))
            else:
                console.print(f"[yellow]DRY RUN:[/yellow] Would update comment {comment_id}:")
                console.print(f"  Body: {len(storage_body)} characters")
            return

        client = get_client()
        confluence = ConfluenceClient(client)

        # Update comment
        result = confluence.update_footer_comment(comment_id, storage_body)

    except FileNotFoundError as e:
        err_console.print(
            f"[red]Error:[/red] {e}\n\n"
            "Please check:\n"
            "  • The file path is correct\n"
            "  • The file exists in the current directory\n"
            "  • You have permission to read the file\n\n"
            f"Current directory: {Path.cwd()}"
        )
        sys.exit(1)
    except ApiError as e:
        if json_output and e.response_data:
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output based on flags
    if json_output:
        print(json.dumps(result, indent=2))
    else:
        console.print(f"[green]Updated comment {comment_id}[/green]")


@app.command("delete")
def delete_comment(
    comment_id: str = typer.Argument(..., help="Comment ID to delete"),
    json_output: bool = typer.Option(False, "--json", help="Output result as JSON"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
) -> None:
    """Delete a comment.

    Examples:
        confl comment delete 123456
        confl comment delete 123456 --json
        confl comment delete 123456 --dry-run
    """
    # Dry-run mode
    if dry_run:
        if json_output:
            result = {"dry_run": True, "action": "delete_comment", "comment_id": comment_id}
            print(json.dumps(result, indent=2))
        else:
            console.print(f"[yellow]DRY RUN:[/yellow] Would delete comment {comment_id}")
        return

    # Confirmation prompt (skip if --yes or not a TTY)
    if (
        not yes
        and sys.stdin.isatty()
        and not json_output
        and not typer.confirm(f"Are you sure you want to delete comment {comment_id}?")
    ):
        console.print("[yellow]Cancelled[/yellow]")
        return

    try:
        client = get_client()
        confluence = ConfluenceClient(client)
        confluence.delete_footer_comment(comment_id)

        if json_output:
            print(json.dumps({"success": True, "id": comment_id}, indent=2))
        else:
            console.print(f"[green]Deleted comment {comment_id}[/green]")

    except ApiError as e:
        if json_output:
            if e.response_data:
                print(json.dumps(e.response_data, indent=2), file=sys.stderr)
            else:
                print(
                    json.dumps({"success": False, "error": e.message}, indent=2),
                    file=sys.stderr,
                )
        else:
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)
