"""Table formatting utilities for consistent CLI output."""

from typing import Any

from rich.console import Console
from rich.table import Table


def create_table(
    title: str | None = None,
    show_lines: bool = False,
    expand: bool = False,
) -> Table:
    """Create a Rich table with consistent styling.

    Args:
        title: Optional table title
        show_lines: Whether to show lines between rows
        expand: Whether table should expand to full width

    Returns:
        Configured Rich Table instance
    """
    return Table(
        title=title,
        show_header=True,
        header_style="bold cyan",
        show_lines=show_lines,
        expand=expand,
    )


def add_column_with_ellipsis(
    table: Table,
    header: str,
    style: str | None = None,
    max_width: int | None = None,
    no_wrap: bool = False,
) -> None:
    """Add a column to table with ellipsis overflow for long content.

    Args:
        table: Rich Table instance
        header: Column header text
        style: Optional style string
        max_width: Maximum column width (content will be truncated with ...)
        no_wrap: Whether to prevent wrapping
    """
    table.add_column(
        header,
        style=style,
        max_width=max_width,
        overflow="ellipsis",
        no_wrap=no_wrap or max_width is not None,
    )


def colorize_status(status: str) -> str:
    """Apply color to status values for better visibility.

    Args:
        status: Status string (e.g., "current", "draft", "archived")

    Returns:
        Styled status string with Rich markup
    """
    status_lower = status.lower()

    # Status color mapping
    if status_lower in ("current", "active", "published"):
        return f"[green]{status}[/green]"
    elif status_lower in ("draft", "trashed"):
        return f"[yellow]{status}[/yellow]"
    elif status_lower in ("archived", "deleted", "historical"):
        return f"[dim]{status}[/dim]"
    else:
        return status


def print_table_with_pagination(
    console: Console,
    table: Table,
    max_rows: int | None = None,
    total_count: int | None = None,
) -> None:
    """Print table with optional pagination notice.

    Args:
        console: Rich Console instance
        table: Populated Rich Table
        max_rows: Maximum rows displayed (if limited)
        total_count: Total number of items available
    """
    console.print(table)

    # Show pagination notice if results were limited
    if max_rows and total_count and total_count > max_rows:
        remaining = total_count - max_rows
        console.print(
            f"[dim]Showing {max_rows} of {total_count} results ({remaining} more available)[/dim]"
        )


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to append when truncated (default: "...")

    Returns:
        Truncated text with suffix if over max_length, otherwise original text
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def sort_items(
    items: list[dict[str, Any]],
    sort_by: str | None = None,
    reverse: bool = False,
) -> list[dict[str, Any]]:
    """Sort list of dictionaries by a key.

    Args:
        items: List of dictionaries to sort
        sort_by: Key to sort by (e.g., "title", "id")
        reverse: Whether to sort in reverse order

    Returns:
        Sorted list of items
    """
    if not sort_by or not items:
        return items

    # Handle nested keys (e.g., "version.createdAt")
    def get_nested_value(item: dict[str, Any], key: str) -> Any:
        keys = key.split(".")
        value: Any = item
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, "")
            else:
                return ""
        return value

    try:
        return sorted(
            items,
            key=lambda x: get_nested_value(x, sort_by),
            reverse=reverse,
        )
    except (TypeError, KeyError):
        # If sorting fails, return original order
        return items
