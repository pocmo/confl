"""Space commands."""

import json
import sys

import typer
from rich.console import Console

from confl.client import ApiError, ConfluenceClient, get_client
from confl.table_formatter import (
    add_column_with_ellipsis,
    colorize_status,
    create_table,
)

app = typer.Typer(help="Manage spaces")
console = Console()
err_console = Console(stderr=True)


def _extract_space_id_or_key(ref: str) -> str:
    """Extract space identifier from reference.

    Args:
        ref: Space reference - either space key or numeric ID

    Returns:
        Space identifier (key or ID) as string
    """
    # Return as-is - API accepts both keys and IDs
    return ref


@app.command("list")
def list_spaces(
    limit: int = typer.Option(25, "--limit", help="Maximum number of results"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON array"),
    type_filter: str = typer.Option(None, "--type", help="Filter by space type (global, personal)"),
    status_filter: str = typer.Option(
        None, "--status", help="Filter by space status (current, archived)"
    ),
) -> None:
    """List spaces.

    Examples:
        confl space list
        confl space list --limit 50
        confl space list --type global
        confl space list --status current
        confl space list --json
    """
    try:
        client = get_client()
        confluence = ConfluenceClient(client)
        spaces = confluence.list_spaces(
            limit=limit, type_filter=type_filter, status_filter=status_filter
        )
    except ApiError as e:
        if json_output and e.response_data:
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output based on flags
    if json_output:
        print(json.dumps(spaces, indent=2))
    else:
        # Rich table output with enhanced formatting
        table = create_table()
        add_column_with_ellipsis(table, "Key", style="dim")
        add_column_with_ellipsis(table, "Name", max_width=50)
        add_column_with_ellipsis(table, "Type")
        add_column_with_ellipsis(table, "Status")

        for space in spaces:
            key = space.get("key", "")
            name = space.get("name", "Unnamed")
            space_type = space.get("type", "")
            status = space.get("status", "")

            # Apply color coding to status
            status_formatted = colorize_status(status)

            table.add_row(key, name, space_type, status_formatted)

        console.print(table)

        if not spaces:
            console.print("[yellow]No spaces found.[/yellow]")


@app.command("get")
def get_space(
    ref: str = typer.Argument(..., help="Space key or ID"),
    json_output: bool = typer.Option(False, "--json", help="Output full API response as JSON"),
) -> None:
    """Get space details.

    Examples:
        confl space get DEV
        confl space get 123456
        confl space get DEV --json
    """
    try:
        space_ref = _extract_space_id_or_key(ref)
        client = get_client()
        confluence = ConfluenceClient(client)
        space = confluence.get_space(space_ref)
    except ApiError as e:
        if json_output and e.response_data:
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output based on flags
    if json_output:
        print(json.dumps(space, indent=2))
    else:
        # Rich formatted output
        console.print(f"[bold]Key:[/bold] {space.get('key', '')}")
        console.print(f"[bold]Name:[/bold] {space.get('name', 'Unnamed')}")
        console.print(f"[bold]Type:[/bold] {space.get('type', '')}")
        console.print(f"[bold]Status:[/bold] {space.get('status', '')}")

        if "description" in space and space["description"]:
            desc = space["description"]
            if isinstance(desc, dict):
                # Description might be in structured format
                desc_value = desc.get("plain", {}).get("value", "") or desc.get("value", "")
            else:
                desc_value = str(desc)
            if desc_value:
                console.print(f"[bold]Description:[/bold] {desc_value}")

        if "homepageId" in space:
            console.print(f"[bold]Homepage ID:[/bold] {space['homepageId']}")

        if "authorId" in space:
            console.print(f"[bold]Author ID:[/bold] {space['authorId']}")

        if "createdAt" in space:
            created = space["createdAt"]
            date = created.split("T")[0] if "T" in created else created
            console.print(f"[bold]Created:[/bold] {date}")


@app.command("create")
def create_space(
    key: str = typer.Option(..., "--key", help="Space key (short unique identifier)"),
    name: str = typer.Option(..., "--name", help="Space name"),
    description: str = typer.Option(None, "--description", help="Space description"),
    json_output: bool = typer.Option(False, "--json", help="Output created space as JSON"),
) -> None:
    """Create a new space.

    Examples:
        confl space create --key DEV --name "Development"
        confl space create --key DEV --name "Development" --description "Dev team space"
        confl space create --key DEV --name "Development" --json
    """
    try:
        client = get_client()
        confluence = ConfluenceClient(client)
        space = confluence.create_space(key=key, name=name, description=description)
    except ApiError as e:
        if json_output and e.response_data:
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output based on flags
    if json_output:
        print(json.dumps(space, indent=2))
    else:
        console.print(
            f"[green]✓[/green] Space created: {space.get('key', '')} - {space.get('name', '')}"
        )
        console.print(f"Space ID: {space.get('id', '')}")


@app.command("update")
def update_space(
    ref: str = typer.Argument(..., help="Space key or ID"),
    name: str = typer.Option(None, "--name", help="New space name"),
    description: str = typer.Option(None, "--description", help="New space description"),
    json_output: bool = typer.Option(False, "--json", help="Output updated space as JSON"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
) -> None:
    """Update space details.

    Examples:
        confl space update DEV --name "New Name"
        confl space update DEV --description "New description"
        confl space update DEV --name "New Name" --description "New description"
        confl space update 123456 --name "New Name" --json
        confl space update DEV --name "New Name" --dry-run
    """
    if not name and not description:
        err_console.print("[red]Error:[/red] At least one of --name or --description is required")
        sys.exit(2)

    space_ref = _extract_space_id_or_key(ref)

    # Dry-run mode
    if dry_run:
        updates = []
        if name:
            updates.append(f"name to '{name}'")
        if description:
            updates.append(f"description to '{description}'")

        if json_output:
            result = {
                "dry_run": True,
                "action": "update_space",
                "space": space_ref,
                "name": name,
                "description": description,
            }
            print(json.dumps(result, indent=2))
        else:
            console.print(f"[yellow]DRY RUN:[/yellow] Would update space {space_ref}:")
            for update in updates:
                console.print(f"  - Set {update}")
        return

    try:
        client = get_client()
        confluence = ConfluenceClient(client)
        space = confluence.update_space(space_ref, name=name, description=description)
    except ApiError as e:
        if json_output and e.response_data:
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output based on flags
    if json_output:
        print(json.dumps(space, indent=2))
    else:
        console.print(
            f"[green]✓[/green] Space updated: {space.get('key', '')} - {space.get('name', '')}"
        )


@app.command("delete")
def delete_space(
    ref: str = typer.Argument(..., help="Space key or ID"),
    json_output: bool = typer.Option(False, "--json", help="Output result as JSON"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
) -> None:
    """Delete a space.

    Warning: This permanently deletes the space and all its content.

    Examples:
        confl space delete DEV
        confl space delete 123456
        confl space delete DEV --json
        confl space delete DEV --dry-run
    """
    space_ref = _extract_space_id_or_key(ref)

    # Dry-run mode
    if dry_run:
        if json_output:
            result = {"dry_run": True, "action": "delete_space", "space": space_ref}
            print(json.dumps(result, indent=2))
        else:
            console.print(f"[yellow]DRY RUN:[/yellow] Would delete space {space_ref}")
            console.print(
                "[yellow]Warning:[/yellow] This would permanently delete the space "
                "and all its content"
            )
        return

    # Confirmation prompt (skip if --yes or not a TTY)
    if not yes and sys.stdin.isatty() and not json_output:
        if not typer.confirm(
            f"Are you sure you want to delete space {space_ref}? "
            "This will permanently delete the space and all its content"
        ):
            console.print("[yellow]Cancelled[/yellow]")
            return

    try:
        client = get_client()
        confluence = ConfluenceClient(client)
        confluence.delete_space(space_ref)
    except ApiError as e:
        if json_output and e.response_data:
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Output based on flags
    if json_output:
        print(json.dumps({"status": "deleted", "space": ref}, indent=2))
    else:
        console.print(f"[green]✓[/green] Space deleted: {ref}")
