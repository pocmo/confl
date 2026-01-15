"""Attachment commands."""

import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from confl.client import ApiError, ConfluenceClient, get_client
from confl.formatters import format_file_size

app = typer.Typer(help="Manage attachments")
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
def list_attachments(
    page: str = typer.Option(..., "--page", help="Page ID or URL"),
    limit: int = typer.Option(25, "--limit", help="Maximum number of results"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON array"),
) -> None:
    """List attachments on a page.

    Examples:
        confl attachment list --page 123456
        confl attachment list --page 123456 --limit 50
        confl attachment list --page 123456 --json
    """
    try:
        page_id = _extract_page_id(page)
        client = get_client()
        confluence = ConfluenceClient(client)
        attachments = confluence.list_attachments(page_id, limit=limit)
    except ApiError as e:
        if json_output and e.response_data:
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output based on flags
    if json_output:
        print(json.dumps(attachments, indent=2))
    else:
        # Rich table output
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("ID", style="dim")
        table.add_column("Title")
        table.add_column("Type")
        table.add_column("Size")

        for attachment in attachments:
            att_id = attachment.get("id", "")
            title = attachment.get("title", "Untitled")
            media_type = attachment.get("mediaType", "")
            file_size = attachment.get("fileSize", 0)
            size_str = format_file_size(file_size)

            table.add_row(att_id, title, media_type, size_str)

        console.print(table)

        if not attachments:
            console.print("[yellow]No attachments found.[/yellow]")


@app.command("get")
def get_attachment(
    attachment_id: str = typer.Argument(..., help="Attachment ID"),
    json_output: bool = typer.Option(False, "--json", help="Output full API response as JSON"),
) -> None:
    """Get attachment metadata.

    Examples:
        confl attachment get att123456
        confl attachment get att123456 --json
    """
    try:
        client = get_client()
        confluence = ConfluenceClient(client)
        attachment = confluence.get_attachment(attachment_id)
    except ApiError as e:
        if json_output and e.response_data:
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output based on flags
    if json_output:
        print(json.dumps(attachment, indent=2))
    else:
        # Rich formatted output
        console.print(f"[bold cyan]ID:[/bold cyan] {attachment.get('id', '')}")
        console.print(f"[bold cyan]Title:[/bold cyan] {attachment.get('title', '')}")
        console.print(f"[bold cyan]Media Type:[/bold cyan] {attachment.get('mediaType', '')}")

        file_size = attachment.get("fileSize", 0)
        size_str = format_file_size(file_size)
        console.print(f"[bold cyan]File Size:[/bold cyan] {size_str}")

        if "webuiLink" in attachment:
            console.print(f"[bold cyan]Web Link:[/bold cyan] {attachment['webuiLink']}")

        if "downloadLink" in attachment:
            console.print(f"[bold cyan]Download Link:[/bold cyan] {attachment['downloadLink']}")


@app.command("download")
def download_attachment(
    attachment_id: str = typer.Argument(..., help="Attachment ID"),
    output: str = typer.Option(
        None, "--output", "-o", help="Output file path (default: use original filename)"
    ),
) -> None:
    """Download attachment.

    Examples:
        confl attachment download att123456
        confl attachment download att123456 --output diagram.png
        confl attachment download att123456 -o /path/to/file.pdf
    """
    try:
        client = get_client()
        confluence = ConfluenceClient(client)

        # Get metadata first to get download link and filename
        attachment = confluence.get_attachment(attachment_id)
        download_link = attachment.get("downloadLink")

        if not download_link:
            err_console.print("[red]Error:[/red] No download link found in attachment metadata")
            sys.exit(1)

        # Download the file with progress indicator
        if sys.stdout.isatty():
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                progress.add_task("Downloading attachment...", total=None)
                content = confluence.download_attachment(download_link)
        else:
            content = confluence.download_attachment(download_link)

        # Determine output filename
        if output:
            output_path = Path(output)
        else:
            # Use original filename from attachment
            filename = attachment.get("title", f"attachment_{attachment_id}")
            output_path = Path(filename)

        # Write to file
        output_path.write_bytes(content)

        # Show success message
        file_size = len(content)
        size_str = format_file_size(file_size)
        console.print(f"[green]Downloaded {size_str} to {output_path}[/green]")

    except ApiError as e:
        err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)
    except Exception as e:
        err_console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command("upload")
def upload_attachment(
    page: str = typer.Option(..., "--page", help="Page ID or URL to attach to"),
    file: str = typer.Option(..., "--file", help="Path to file to upload"),
    comment: str = typer.Option(None, "--comment", help="Optional comment for attachment"),
    json_output: bool = typer.Option(False, "--json", help="Output full API response as JSON"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
) -> None:
    """Upload file attachment to a page.

    Examples:
        confl attachment upload --page 123456 --file diagram.png
        confl attachment upload --page 123456 --file doc.pdf --comment "Updated documentation"
        confl attachment upload --page 123456 --file image.jpg --json
        confl attachment upload --page 123456 --file doc.pdf --dry-run
    """
    try:
        page_id = _extract_page_id(page)

        # Check if file exists before dry-run output
        file_path = Path(file)
        if not file_path.exists():
            raise FileNotFoundError(
                f"File not found: {file}\n\n"
                "Please check:\n"
                "  • The file path is correct\n"
                "  • The file exists in the current directory\n"
                "  • You have permission to read the file\n\n"
                f"Current directory: {Path.cwd()}"
            )

        # Dry-run mode
        if dry_run:
            file_size = file_path.stat().st_size
            if json_output:
                result = {
                    "dry_run": True,
                    "action": "upload",
                    "page_id": page_id,
                    "file": file,
                    "file_size": file_size,
                    "comment": comment,
                }
                print(json.dumps(result, indent=2))
            else:
                console.print("[yellow]DRY RUN:[/yellow] Would upload attachment:")
                console.print(f"  Page: {page_id}")
                console.print(f"  File: {file}")
                console.print(f"  Size: {file_size} bytes")
                if comment:
                    console.print(f"  Comment: {comment}")
            return

        client = get_client()
        confluence = ConfluenceClient(client)

        # Upload the file with progress indicator
        if sys.stdout.isatty() and not json_output:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                progress.add_task("Uploading attachment...", total=None)
                result = confluence.upload_attachment(page_id, file, comment=comment)
        else:
            result = confluence.upload_attachment(page_id, file, comment=comment)

        if json_output:
            print(json.dumps(result, indent=2))
        else:
            # Show success message
            attachment_id = result.get("id", "")
            title = result.get("title", Path(file).name)
            console.print(f"[green]Uploaded '{title}' (ID: {attachment_id})[/green]")

    except FileNotFoundError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
    except ApiError as e:
        if json_output and e.response_data:
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)


@app.command("delete")
def delete_attachment(
    attachment_id: str = typer.Argument(..., help="Attachment ID"),
    json_output: bool = typer.Option(False, "--json", help="Output result as JSON"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
) -> None:
    """Delete an attachment.

    Examples:
        confl attachment delete att123456
        confl attachment delete att123456 --json
        confl attachment delete att123456 --dry-run
    """
    # Dry-run mode
    if dry_run:
        if json_output:
            result = {"dry_run": True, "action": "delete", "attachment_id": attachment_id}
            print(json.dumps(result, indent=2))
        else:
            console.print(f"[yellow]DRY RUN:[/yellow] Would delete attachment {attachment_id}")
        return

    # Confirmation prompt (skip if --yes or not a TTY)
    if not yes and sys.stdin.isatty() and not json_output:
        if not typer.confirm(f"Are you sure you want to delete attachment {attachment_id}?"):
            console.print("[yellow]Cancelled[/yellow]")
            return

    try:
        client = get_client()
        confluence = ConfluenceClient(client)
        confluence.delete_attachment(attachment_id)

        if json_output:
            print(json.dumps({"success": True, "id": attachment_id}, indent=2))
        else:
            console.print(f"[green]Deleted attachment {attachment_id}[/green]")

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
