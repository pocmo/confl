"""Blog post commands."""

import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown

from confl.client import ApiError, ConfluenceClient, get_client
from confl.converter import markdown_to_storage, storage_to_markdown
from confl.formatters import format_relative_time, strip_markdown
from confl.formatters.blogpost_formatter import (
    format_blogpost_metadata,
    get_blogpost_content,
)
from confl.table_formatter import (
    add_column_with_ellipsis,
    create_table,
)
from confl.utils.blogpost_helpers import extract_blogpost_id

app = typer.Typer(help="Manage blog posts")
console = Console()
err_console = Console(stderr=True)


@app.command("get")
def get_blogpost(
    ref: str = typer.Argument(..., help="Blog post ID or URL"),
    body_only: bool = typer.Option(False, "--body-only", help="Suppress metadata header"),
    json_output: bool = typer.Option(False, "--json", help="Output full API response as JSON"),
    raw: bool = typer.Option(False, "--raw", help="Output Confluence storage format"),
    markdown: bool = typer.Option(
        False, "--markdown", help="Output raw markdown (converted from storage format)"
    ),
    plain: bool = typer.Option(False, "--plain", help="Output plain text (stripped of formatting)"),
) -> None:
    """Fetch and display a blog post.

    Examples:
        confl blogpost get 12345678
        confl blogpost get "https://company.atlassian.net/wiki/spaces/DEV/blogposts/12345678/Title"
        confl blogpost get 12345678 --json
        confl blogpost get 12345678 --raw
        confl blogpost get 12345678 --markdown
        confl blogpost get 12345678 --plain
        confl blogpost get 12345678 --body-only
    """
    try:
        blogpost_id = extract_blogpost_id(ref)
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

    # Get the blog post
    try:
        client = get_client()
        confluence = ConfluenceClient(client)
        blogpost = confluence.get_blogpost(blogpost_id)
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
        print(json.dumps(blogpost, indent=2))
    elif raw:
        content = get_blogpost_content(blogpost, "storage")
        if not body_only:
            console.print(format_blogpost_metadata(blogpost))
        print(content)
    elif markdown:
        # Output raw markdown (converted from storage)
        content = get_blogpost_content(blogpost, "storage")
        markdown_content = storage_to_markdown(content)
        if not body_only:
            console.print(format_blogpost_metadata(blogpost))
        print(markdown_content)
    elif plain:
        # Output plain text (converted from storage, stripped of markdown)
        content = get_blogpost_content(blogpost, "storage")
        markdown_content = storage_to_markdown(content)
        plain_content = strip_markdown(markdown_content)
        if not body_only:
            console.print(format_blogpost_metadata(blogpost))
        print(plain_content)
    else:
        # Default: Rich terminal output with Markdown rendering
        if not body_only:
            console.print(format_blogpost_metadata(blogpost))

        # Get storage content and convert to Markdown
        content = get_blogpost_content(blogpost, "storage")
        markdown_content = storage_to_markdown(content)

        # Render with Rich's Markdown renderer
        md = Markdown(markdown_content)
        console.print(md)


@app.command("list")
def list_blogposts(
    space: str = typer.Option(..., "--space", help="Space key to filter by"),
    limit: int = typer.Option(25, "--limit", help="Maximum number of results"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON array"),
) -> None:
    """List blog posts in a space.

    Examples:
        confl blogpost list --space DEV
        confl blogpost list --space DEV --limit 50
        confl blogpost list --space DEV --json
    """
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

    # List blog posts
    try:
        blogposts = confluence.list_blogposts(space_id=space_id, limit=limit)
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
        print(json.dumps(blogposts, indent=2))
    else:
        # Rich table output with enhanced formatting
        table = create_table()
        add_column_with_ellipsis(table, "ID", style="dim")
        add_column_with_ellipsis(table, "Title", max_width=60)
        add_column_with_ellipsis(table, "Space", style="dim")
        add_column_with_ellipsis(table, "Published")

        for blogpost in blogposts:
            blogpost_id = blogpost.get("id", "")
            title = blogpost.get("title", "Untitled")
            space_id = blogpost.get("spaceId", "")

            # Extract published date from version
            published = ""
            version = blogpost.get("version", {})
            if "createdAt" in version:
                timestamp = version["createdAt"]
                published = format_relative_time(timestamp)

            table.add_row(blogpost_id, title, space_id, published)

        console.print(table)

        if not blogposts:
            console.print("[yellow]No blog posts found in this space.[/yellow]")


@app.command("delete")
def delete_blogpost(
    ref: str = typer.Argument(..., help="Blog post ID or URL"),
    json_output: bool = typer.Option(False, "--json", help="Output result as JSON"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
) -> None:
    """Delete a blog post.

    Examples:
        confl blogpost delete 12345678
        confl blogpost delete "https://company.atlassian.net/wiki/spaces/DEV/blogposts/12345678/Title"
        confl blogpost delete 12345678 --json
        confl blogpost delete 12345678 --dry-run
    """
    try:
        blogpost_id = extract_blogpost_id(ref)
    except ValueError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        sys.exit(2)

    # Dry-run mode
    if dry_run:
        if json_output:
            result = {"dry_run": True, "action": "delete_blogpost", "blogpost_id": blogpost_id}
            print(json.dumps(result, indent=2))
        else:
            console.print(f"[yellow]DRY RUN:[/yellow] Would delete blog post {blogpost_id}")
        return

    # Confirmation prompt (skip if --yes or not a TTY)
    if (
        not yes
        and sys.stdin.isatty()
        and not json_output
        and not typer.confirm(f"Are you sure you want to delete blog post {blogpost_id}?")
    ):
        console.print("[yellow]Cancelled[/yellow]")
        return

    # Delete the blog post
    try:
        client = get_client()
        confluence = ConfluenceClient(client)
        confluence.delete_blogpost(blogpost_id)
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
        result = {
            "success": True,
            "blogpost_id": blogpost_id,
            "message": "Blog post deleted successfully",
        }
        print(json.dumps(result, indent=2))
    else:
        console.print(f"[green]✓[/green] Blog post {blogpost_id} deleted successfully")


@app.command("create")
def create_blogpost(
    space: str = typer.Option(..., "--space", help="Space key (e.g., DEV)"),
    title: str = typer.Option(..., "--title", help="Blog post title"),
    body: str = typer.Option(None, "--body", help="Blog post content (Markdown by default)"),
    body_file: str = typer.Option(None, "--body-file", help="Read content from file"),
    raw: bool = typer.Option(False, "--raw", help="Provide content in storage format directly"),
    json_output: bool = typer.Option(False, "--json", help="Output result as JSON"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
) -> None:
    """Create a new blog post.

    Examples:
        confl blogpost create --space DEV --title "Release Notes" --body "# v1.0"
        confl blogpost create --space DEV --title "Update" --body-file content.md
        cat content.md | confl blogpost create --space DEV --title "Announcement"
        confl blogpost create --space DEV --title "Post" --body "<p>HTML</p>" --raw
        confl blogpost create --space DEV --title "Post" --body "# Content" --dry-run
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
                "action": "create_blogpost",
                "space": space,
                "title": title,
                "content_length": len(storage_content),
            }
            print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]DRY RUN:[/yellow] Would create blog post:")
            console.print(f"  Title: {title}")
            console.print(f"  Space: {space}")
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

    # Create the blog post
    try:
        created_blogpost = confluence.create_blogpost(
            space_id=space_id,
            title=title,
            body=storage_content,
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
        print(json.dumps(created_blogpost, indent=2))
    else:
        blogpost_id = created_blogpost.get("id", "")
        blogpost_links = created_blogpost.get("_links", {})
        web_ui = blogpost_links.get("webui", "")

        # Construct full URL if we have the base URL
        blogpost_url = ""
        if web_ui and hasattr(client, "base_url"):
            blogpost_url = f"{client.base_url}{web_ui}"

        console.print("[green]✓[/green] Blog post created successfully")
        console.print(f"ID: {blogpost_id}")
        if blogpost_url:
            console.print(f"URL: {blogpost_url}")


@app.command("update")
def update_blogpost(
    ref: str = typer.Argument(..., help="Blog post ID or URL"),
    body: str = typer.Option(None, "--body", help="Blog post content (Markdown by default)"),
    body_file: str = typer.Option(None, "--body-file", help="Read content from file"),
    title: str = typer.Option(
        None, "--title", help="New blog post title (keep existing if not provided)"
    ),
    raw: bool = typer.Option(False, "--raw", help="Provide content in storage format directly"),
    json_output: bool = typer.Option(False, "--json", help="Output result as JSON"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
) -> None:
    """Update an existing blog post's content and/or title.

    Examples:
        confl blogpost update 12345678 --body "# Updated content"
        confl blogpost update 12345678 --body-file content.md
        cat content.md | confl blogpost update 12345678
        confl blogpost update 12345678 --title "New Title"
        confl blogpost update 12345678 --body "Content" --title "New Title"
        confl blogpost update 12345678 --body "<p>HTML</p>" --raw
        confl blogpost update 12345678 --title "New Title" --dry-run
    """
    # Extract blog post ID
    try:
        blogpost_id = extract_blogpost_id(ref)
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
                "action": "update_blogpost",
                "blogpost_id": blogpost_id,
                "title": title,
                "content_length": len(content) if content else None,
            }
            print(json.dumps(result, indent=2))
        else:
            console.print(f"[yellow]DRY RUN:[/yellow] Would update blog post {blogpost_id}:")
            for update in updates:
                console.print(f"  - Set {update}")
        return

    # Get current blog post to fetch version and existing title/content
    try:
        client = get_client()
        confluence = ConfluenceClient(client)
        current_blogpost = confluence.get_blogpost(blogpost_id)
    except ApiError as e:
        if json_output and e.response_data:
            # Output raw error JSON to stderr
            print(json.dumps(e.response_data, indent=2), file=sys.stderr)
        else:
            # Human-readable error message
            err_console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)

    # Get current version number for optimistic locking
    version_number = current_blogpost.get("version", {}).get("number", 1)

    # Use provided title or keep existing
    new_title = title if title is not None else current_blogpost.get("title", "Untitled")

    # Process content
    if content is not None:
        # Convert markdown to storage format unless --raw
        storage_content = content if raw else markdown_to_storage(content)
    else:
        # No new content provided, keep existing
        storage_content = get_blogpost_content(current_blogpost, "storage")

    # Update the blog post
    try:
        updated_blogpost = confluence.update_blogpost(
            blogpost_id=blogpost_id,
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
        print(json.dumps(updated_blogpost, indent=2))
    else:
        blogpost_id = updated_blogpost.get("id", "")
        new_version = updated_blogpost.get("version", {}).get("number", "")

        console.print("[green]✓[/green] Blog post updated successfully")
        console.print(f"ID: {blogpost_id}")
        if new_version:
            console.print(f"Version: {new_version}")
