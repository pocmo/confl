"""Label commands."""

import json
import sys

import typer
from rich.console import Console

from confl.client import ApiError, ConfluenceClient, get_client
from confl.table_formatter import add_column_with_ellipsis, create_table

app = typer.Typer(help="Manage labels")
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


@app.command("list")
def list_labels(
    page: str = typer.Option(..., "--page", help="Page ID or URL"),
    limit: int = typer.Option(25, "--limit", help="Maximum number of results"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON array"),
) -> None:
    """List labels on a page.

    Examples:
        confl label list --page 123456
        confl label list --page https://site.atlassian.net/wiki/spaces/DEV/pages/123456
        confl label list --page 123456 --json
    """
    try:
        page_id = _extract_page_id(page)
        client = get_client()
        confluence = ConfluenceClient(client)
        labels = confluence.list_page_labels(page_id, limit=limit)
    except ApiError as e:
        if json_output and e.response_data:
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output based on flags
    if json_output:
        print(json.dumps(labels, indent=2))
    else:
        # Rich table output with enhanced formatting
        table = create_table()
        add_column_with_ellipsis(table, "ID", style="dim")
        add_column_with_ellipsis(table, "Name", max_width=40)
        add_column_with_ellipsis(table, "Prefix", max_width=20)

        for label in labels:
            label_id = label.get("id", "")
            name = label.get("name", "")
            prefix = label.get("prefix", "")
            table.add_row(label_id, name, prefix)

        console.print(table)

        if not labels:
            console.print("[yellow]No labels found on this page.[/yellow]")


@app.command("add")
def add_labels(
    labels: list[str],
    page: str = typer.Option(..., "--page", help="Page ID or URL"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON array"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
) -> None:
    """Add one or more labels to a page.

    Examples:
        confl label add --page 123456 architecture design
        confl label add --page 123456 "my-label" "another-label"
        confl label add --page 123456 release-notes --json
        confl label add --page 123456 architecture design --dry-run

    Args:
        labels: Label names to add
    """
    page_id = _extract_page_id(page)

    # Dry-run mode
    if dry_run:
        if json_output:
            result = {
                "dry_run": True,
                "action": "add_labels",
                "page_id": page_id,
                "labels": labels,
            }
            print(json.dumps(result, indent=2))
        else:
            console.print(
                f"[yellow]DRY RUN:[/yellow] Would add {len(labels)} label(s) to page {page_id}:"
            )
            for label_name in labels:
                console.print(f"  • {label_name}")
        return

    try:
        client = get_client()
        confluence = ConfluenceClient(client)
        added_labels = confluence.add_labels_to_page(page_id, labels)
    except ApiError as e:
        if json_output and e.response_data:
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output based on flags
    if json_output:
        print(json.dumps(added_labels, indent=2))
    else:
        console.print(f"[green]✓[/green] Added {len(labels)} label(s) to page {page_id}")
        for label_name in labels:
            console.print(f"  • {label_name}")


@app.command("remove")
def remove_label(
    label: str,
    page: str = typer.Option(..., "--page", help="Page ID or URL"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
) -> None:
    """Remove a label from a page.

    Examples:
        confl label remove --page 123456 old-label
        confl label remove --page 123456 "label-to-remove"
        confl label remove --page 123456 old-label --dry-run

    Args:
        label: Label name to remove
    """
    page_id = _extract_page_id(page)

    # Dry-run mode
    if dry_run:
        if json_output:
            result = {"dry_run": True, "action": "remove_label", "page_id": page_id, "label": label}
            print(json.dumps(result, indent=2))
        else:
            console.print(
                f"[yellow]DRY RUN:[/yellow] Would remove label '{label}' from page {page_id}"
            )
        return

    try:
        client = get_client()
        confluence = ConfluenceClient(client)
        confluence.remove_label_from_page(page_id, label)
    except ApiError as e:
        if json_output and e.response_data:
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output based on flags
    if json_output:
        print(json.dumps({"status": "success", "label": label, "page": page_id}, indent=2))
    else:
        console.print(f"[green]✓[/green] Removed label '{label}' from page {page_id}")


@app.command("search")
def search_by_label(
    label: str,
    limit: int = typer.Option(25, "--limit", help="Maximum number of results"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON array"),
) -> None:
    """Find all content (pages, blogposts, attachments) with a given label.

    Examples:
        confl label search architecture
        confl label search "release-notes" --limit 50
        confl label search design --json

    Args:
        label: Label name to search for
    """
    try:
        client = get_client()
        confluence = ConfluenceClient(client)

        # First, find the label ID by name
        label_obj = confluence.find_label_by_name(label)
        if not label_obj:
            err_console.print(f"[yellow]Label '{label}' not found.[/yellow]")
            sys.exit(0)

        label_id = label_obj["id"]

        # Fetch all content types with this label
        pages = confluence.list_pages_by_label(label_id, limit=limit)
        blogposts = confluence.list_blogposts_by_label(label_id, limit=limit)
        attachments = confluence.list_attachments_by_label(label_id, limit=limit)

    except ApiError as e:
        if json_output and e.response_data:
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output based on flags
    if json_output:
        result = {
            "label": label_obj,
            "pages": pages,
            "blogposts": blogposts,
            "attachments": attachments,
        }
        print(json.dumps(result, indent=2))
    else:
        console.print(f"[bold]Content with label '{label}':[/bold]\n")

        # Pages
        if pages:
            console.print(f"[cyan]Pages ({len(pages)}):[/cyan]")
            for page in pages:
                page_id = page.get("id", "")
                title = page.get("title", "Untitled")
                console.print(f"  • [{page_id}] {title}")
            console.print()

        # Blog posts
        if blogposts:
            console.print(f"[cyan]Blog Posts ({len(blogposts)}):[/cyan]")
            for post in blogposts:
                post_id = post.get("id", "")
                title = post.get("title", "Untitled")
                console.print(f"  • [{post_id}] {title}")
            console.print()

        # Attachments
        if attachments:
            console.print(f"[cyan]Attachments ({len(attachments)}):[/cyan]")
            for att in attachments:
                att_id = att.get("id", "")
                title = att.get("title", "Untitled")
                console.print(f"  • [{att_id}] {title}")
            console.print()

        if not pages and not blogposts and not attachments:
            console.print("[yellow]No content found with this label.[/yellow]")
