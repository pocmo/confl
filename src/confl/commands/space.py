"""Space commands."""

import json
import sys

import typer
from rich.console import Console
from rich.table import Table

from confl.client import ApiError, ConfluenceClient, get_client

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
        # Rich table output
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Key", style="dim")
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Status")

        for space in spaces:
            key = space.get("key", "")
            name = space.get("name", "Unnamed")
            space_type = space.get("type", "")
            status = space.get("status", "")

            table.add_row(key, name, space_type, status)

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
) -> None:
    """Update space details.

    Examples:
        confl space update DEV --name "New Name"
        confl space update DEV --description "New description"
        confl space update DEV --name "New Name" --description "New description"
        confl space update 123456 --name "New Name" --json
    """
    if not name and not description:
        err_console.print("[red]Error:[/red] At least one of --name or --description is required")
        sys.exit(2)

    try:
        space_ref = _extract_space_id_or_key(ref)
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
) -> None:
    """Delete a space.

    Warning: This permanently deletes the space and all its content.

    Examples:
        confl space delete DEV
        confl space delete 123456
        confl space delete DEV --json
    """
    try:
        space_ref = _extract_space_id_or_key(ref)
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
