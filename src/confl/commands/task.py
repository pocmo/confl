"""Task commands."""

import json
import sys
from typing import Any

import typer
from rich.console import Console

from confl.client import ApiError, ConfluenceClient, get_client
from confl.formatters import format_relative_time
from confl.table_formatter import add_column_with_ellipsis, create_table

app = typer.Typer(help="Manage tasks")
console = Console()
err_console = Console(stderr=True)


def _format_task_body(task: dict[str, Any]) -> str:
    """Extract and format task body text.

    Args:
        task: Task object from API

    Returns:
        Task body as plain text
    """
    body = task.get("body", {})
    storage = body.get("storage", {})
    value = storage.get("value", "")

    # Strip HTML tags for display (simple approach)
    import re

    text = re.sub(r"<[^>]+>", "", value)
    return text.strip()


@app.command("list")
def list_tasks(
    status: str = typer.Option(None, "--status", help="Filter by status (complete, incomplete)"),
    assigned_to: str = typer.Option(
        None, "--assigned-to", help="Filter by assigned user Account ID"
    ),
    page: str = typer.Option(None, "--page", help="Filter by page ID"),
    space: str = typer.Option(None, "--space", help="Filter by space ID"),
    limit: int = typer.Option(25, "--limit", help="Maximum number of results"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON array"),
) -> None:
    """List tasks with optional filters.

    Examples:
        confl task list
        confl task list --status incomplete
        confl task list --assigned-to 123abc456def
        confl task list --page 123456
        confl task list --json
    """
    try:
        client = get_client()
        confluence = ConfluenceClient(client)

        # Validate status if provided
        if status and status not in ("complete", "incomplete"):
            err_console.print("[red]Error:[/red] Status must be 'complete' or 'incomplete'")
            sys.exit(1)

        tasks = confluence.list_tasks(
            status=status,
            assigned_to=assigned_to,
            page_id=page,
            space_id=space,
            limit=limit,
        )

    except ApiError as e:
        if json_output and e.response_data:
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output based on flags
    if json_output:
        print(json.dumps(tasks, indent=2))
    else:
        # Rich table output
        table = create_table()
        add_column_with_ellipsis(table, "ID", style="dim")
        add_column_with_ellipsis(table, "Status")
        add_column_with_ellipsis(table, "Body", max_width=40)
        add_column_with_ellipsis(table, "Page ID", style="dim")
        add_column_with_ellipsis(table, "Created")

        for task in tasks:
            task_id = task.get("id", "")
            task_status = task.get("status", "")

            # Get body preview
            body_text = _format_task_body(task)
            body_preview = body_text[:40]
            if len(body_text) > 40:
                body_preview += "..."

            # Get page ID
            page_id = task.get("pageId", "")

            # Get creation date
            created_at = task.get("createdAt", "")
            created_relative = format_relative_time(created_at) if created_at else ""

            # Status color
            status_display = task_status
            if task_status == "complete":
                status_display = f"[green]{task_status}[/green]"
            elif task_status == "incomplete":
                status_display = f"[yellow]{task_status}[/yellow]"

            table.add_row(task_id, status_display, body_preview, page_id, created_relative)

        console.print(table)

        if not tasks:
            console.print("[yellow]No tasks found.[/yellow]")


@app.command("get")
def get_task(
    task_id: str = typer.Argument(..., help="Task ID"),
    json_output: bool = typer.Option(False, "--json", help="Output full API response as JSON"),
) -> None:
    """Get task details.

    Examples:
        confl task get 123456
        confl task get 123456 --json
    """
    try:
        client = get_client()
        confluence = ConfluenceClient(client)
        task = confluence.get_task(task_id)

    except ApiError as e:
        if json_output and e.response_data:
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output based on flags
    if json_output:
        print(json.dumps(task, indent=2))
    else:
        # Rich formatted output
        console.print(f"[bold cyan]ID:[/bold cyan] {task.get('id', '')}")

        status = task.get("status", "")
        status_display = status
        if status == "complete":
            status_display = f"[green]{status}[/green]"
        elif status == "incomplete":
            status_display = f"[yellow]{status}[/yellow]"
        console.print(f"[bold cyan]Status:[/bold cyan] {status_display}")

        console.print(f"[bold cyan]Page ID:[/bold cyan] {task.get('pageId', '')}")
        console.print(f"[bold cyan]Space ID:[/bold cyan] {task.get('spaceId', '')}")

        if "createdBy" in task:
            console.print(f"[bold cyan]Created By:[/bold cyan] {task['createdBy']}")
        if "assignedTo" in task:
            console.print(f"[bold cyan]Assigned To:[/bold cyan] {task['assignedTo']}")
        if "completedBy" in task:
            console.print(f"[bold cyan]Completed By:[/bold cyan] {task['completedBy']}")

        created_at = task.get("createdAt", "")
        console.print(f"[bold cyan]Created:[/bold cyan] {created_at}")

        if "dueAt" in task:
            console.print(f"[bold cyan]Due:[/bold cyan] {task['dueAt']}")
        if "completedAt" in task:
            console.print(f"[bold cyan]Completed:[/bold cyan] {task['completedAt']}")

        console.print("\n[bold cyan]Body:[/bold cyan]")
        body_text = _format_task_body(task)
        console.print(body_text if body_text else "[dim](empty)[/dim]")


@app.command("update")
def update_task(
    task_id: str = typer.Argument(..., help="Task ID to update"),
    status: str = typer.Option(..., "--status", help="New status (complete or incomplete)"),
    json_output: bool = typer.Option(False, "--json", help="Output full API response as JSON"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
) -> None:
    """Update a task's status.

    Examples:
        confl task update 123456 --status complete
        confl task update 123456 --status incomplete
        confl task update 123456 --status complete --dry-run
    """
    try:
        # Validate status
        if status not in ("complete", "incomplete"):
            err_console.print("[red]Error:[/red] Status must be 'complete' or 'incomplete'")
            sys.exit(1)

        # Dry-run mode
        if dry_run:
            if json_output:
                result = {
                    "dry_run": True,
                    "action": "update_task",
                    "task_id": task_id,
                    "status": status,
                }
                print(json.dumps(result, indent=2))
            else:
                console.print(f"[yellow]DRY RUN:[/yellow] Would update task {task_id}:")
                console.print(f"  Status: {status}")
            return

        client = get_client()
        confluence = ConfluenceClient(client)
        result = confluence.update_task(task_id, status)

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
        console.print(f"[green]Updated task {task_id} to status: {status}[/green]")
