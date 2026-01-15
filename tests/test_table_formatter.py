"""Tests for table formatting utilities."""

from io import StringIO

from rich.console import Console
from rich.table import Table

from confl.table_formatter import (
    add_column_with_ellipsis,
    colorize_status,
    create_table,
    print_table_with_pagination,
    sort_items,
    truncate_text,
)


class TestCreateTable:
    """Tests for create_table function."""

    def test_basic_table_creation(self) -> None:
        """Test creating a basic table with default settings."""
        table = create_table()
        assert isinstance(table, Table)
        assert table.show_header is True
        assert table.header_style == "bold cyan"

    def test_table_with_title(self) -> None:
        """Test creating a table with title."""
        table = create_table(title="Test Results")
        assert table.title == "Test Results"

    def test_table_with_lines(self) -> None:
        """Test creating a table with row lines."""
        table = create_table(show_lines=True)
        assert table.show_lines is True

    def test_table_with_expand(self) -> None:
        """Test creating an expanded table."""
        table = create_table(expand=True)
        assert table.expand is True


class TestAddColumnWithEllipsis:
    """Tests for add_column_with_ellipsis function."""

    def test_add_simple_column(self) -> None:
        """Test adding a simple column."""
        table = create_table()
        add_column_with_ellipsis(table, "Name")
        assert len(table.columns) == 1
        assert table.columns[0].header == "Name"

    def test_add_column_with_style(self) -> None:
        """Test adding a column with style."""
        table = create_table()
        add_column_with_ellipsis(table, "ID", style="dim")
        column = table.columns[0]
        assert column.header == "ID"
        assert column.style == "dim"

    def test_add_column_with_max_width(self) -> None:
        """Test adding a column with max width."""
        table = create_table()
        add_column_with_ellipsis(table, "Title", max_width=50)
        column = table.columns[0]
        assert column.max_width == 50
        assert column.overflow == "ellipsis"
        assert column.no_wrap is True

    def test_add_column_with_no_wrap(self) -> None:
        """Test adding a column with no_wrap."""
        table = create_table()
        add_column_with_ellipsis(table, "Status", no_wrap=True)
        column = table.columns[0]
        assert column.no_wrap is True

    def test_multiple_columns(self) -> None:
        """Test adding multiple columns."""
        table = create_table()
        add_column_with_ellipsis(table, "ID", style="dim")
        add_column_with_ellipsis(table, "Title", max_width=60)
        add_column_with_ellipsis(table, "Status")
        assert len(table.columns) == 3


class TestColorizeStatus:
    """Tests for colorize_status function."""

    def test_active_statuses_green(self) -> None:
        """Test that active statuses are colored green."""
        assert colorize_status("current") == "[green]current[/green]"
        assert colorize_status("active") == "[green]active[/green]"
        assert colorize_status("published") == "[green]published[/green]"
        # Case insensitive
        assert colorize_status("CURRENT") == "[green]CURRENT[/green]"

    def test_draft_statuses_yellow(self) -> None:
        """Test that draft/trashed statuses are colored yellow."""
        assert colorize_status("draft") == "[yellow]draft[/yellow]"
        assert colorize_status("trashed") == "[yellow]trashed[/yellow]"
        assert colorize_status("DRAFT") == "[yellow]DRAFT[/yellow]"

    def test_archived_statuses_dim(self) -> None:
        """Test that archived statuses are dimmed."""
        assert colorize_status("archived") == "[dim]archived[/dim]"
        assert colorize_status("deleted") == "[dim]deleted[/dim]"
        assert colorize_status("historical") == "[dim]historical[/dim]"

    def test_unknown_status_unchanged(self) -> None:
        """Test that unknown statuses are not modified."""
        assert colorize_status("unknown") == "unknown"
        assert colorize_status("pending") == "pending"


class TestTruncateText:
    """Tests for truncate_text function."""

    def test_short_text_unchanged(self) -> None:
        """Test that short text is not truncated."""
        text = "Short text"
        assert truncate_text(text, 20) == text

    def test_long_text_truncated(self) -> None:
        """Test that long text is truncated with ellipsis."""
        text = "This is a very long title that needs truncation"
        result = truncate_text(text, 20)
        assert len(result) == 20
        assert result.endswith("...")
        assert result == "This is a very lo..."

    def test_exact_length_text(self) -> None:
        """Test text at exact max length."""
        text = "Exactly20Characters!"
        assert truncate_text(text, 20) == text

    def test_custom_suffix(self) -> None:
        """Test truncation with custom suffix."""
        text = "Long text here"
        result = truncate_text(text, 10, suffix="…")
        assert len(result) == 10
        assert result.endswith("…")

    def test_empty_text(self) -> None:
        """Test truncation with empty text."""
        assert truncate_text("", 10) == ""


class TestSortItems:
    """Tests for sort_items function."""

    def test_sort_by_string_field(self) -> None:
        """Test sorting by string field."""
        items = [
            {"title": "Zebra", "id": "1"},
            {"title": "Apple", "id": "2"},
            {"title": "Mango", "id": "3"},
        ]
        sorted_items = sort_items(items, sort_by="title")
        assert sorted_items[0]["title"] == "Apple"
        assert sorted_items[1]["title"] == "Mango"
        assert sorted_items[2]["title"] == "Zebra"

    def test_sort_by_numeric_field(self) -> None:
        """Test sorting by numeric field."""
        items = [
            {"id": "3", "count": 30},
            {"id": "1", "count": 10},
            {"id": "2", "count": 20},
        ]
        sorted_items = sort_items(items, sort_by="count")
        assert sorted_items[0]["count"] == 10
        assert sorted_items[1]["count"] == 20
        assert sorted_items[2]["count"] == 30

    def test_sort_reverse(self) -> None:
        """Test reverse sorting."""
        items = [
            {"title": "A"},
            {"title": "B"},
            {"title": "C"},
        ]
        sorted_items = sort_items(items, sort_by="title", reverse=True)
        assert sorted_items[0]["title"] == "C"
        assert sorted_items[2]["title"] == "A"

    def test_sort_nested_field(self) -> None:
        """Test sorting by nested field."""
        items = [
            {"version": {"createdAt": "2024-01-03"}},
            {"version": {"createdAt": "2024-01-01"}},
            {"version": {"createdAt": "2024-01-02"}},
        ]
        sorted_items = sort_items(items, sort_by="version.createdAt")
        assert sorted_items[0]["version"]["createdAt"] == "2024-01-01"
        assert sorted_items[2]["version"]["createdAt"] == "2024-01-03"

    def test_sort_with_missing_keys(self) -> None:
        """Test sorting when some items lack the sort key."""
        items = [
            {"title": "B", "id": "2"},
            {"id": "1"},  # Missing title
            {"title": "A", "id": "3"},
        ]
        sorted_items = sort_items(items, sort_by="title")
        # Items without key should sort to beginning (empty string)
        assert sorted_items[0].get("title", "") == ""
        assert sorted_items[1]["title"] == "A"
        assert sorted_items[2]["title"] == "B"

    def test_sort_no_sort_by(self) -> None:
        """Test that items are unchanged when sort_by is None."""
        items = [{"id": "3"}, {"id": "1"}, {"id": "2"}]
        sorted_items = sort_items(items, sort_by=None)
        assert sorted_items == items

    def test_sort_empty_list(self) -> None:
        """Test sorting empty list."""
        assert sort_items([], sort_by="title") == []

    def test_sort_with_type_error(self) -> None:
        """Test sorting with incompatible types (should handle gracefully)."""
        items = [
            {"value": 10},
            {"value": "string"},
            {"value": 5},
        ]
        # Should return original order when sorting fails due to type mismatch
        sorted_items = sort_items(items, sort_by="value")
        assert len(sorted_items) == 3

    def test_sort_nested_field_with_non_dict_value(self) -> None:
        """Test sorting by nested field when intermediate value is not a dict."""
        items = [
            {"version": "string_not_dict", "id": "1"},
            {"version": {"createdAt": "2024-01-01"}, "id": "2"},
            {"version": {"createdAt": "2024-01-02"}, "id": "3"},
        ]
        sorted_items = sort_items(items, sort_by="version.createdAt")
        # Item with string version should sort to beginning (returns empty string)
        assert sorted_items[0]["id"] == "1"
        assert sorted_items[1]["id"] == "2"
        assert sorted_items[2]["id"] == "3"


class TestPrintTableWithPagination:
    """Tests for print_table_with_pagination function."""

    def test_print_table_without_pagination(self) -> None:
        """Test printing table without pagination notice."""
        console = Console(file=StringIO(), width=80)
        table = create_table()
        add_column_with_ellipsis(table, "Name")
        table.add_row("Test")

        print_table_with_pagination(console, table)
        output = console.file.getvalue()  # type: ignore
        assert "Test" in output
        assert "Showing" not in output

    def test_print_table_with_pagination_notice(self) -> None:
        """Test printing table with pagination notice."""
        console = Console(file=StringIO(), width=80)
        table = create_table()
        add_column_with_ellipsis(table, "Name")
        for i in range(10):
            table.add_row(f"Item {i}")

        print_table_with_pagination(console, table, max_rows=10, total_count=50)
        output = console.file.getvalue()  # type: ignore
        assert "Showing 10 of 50 results" in output
        assert "40 more available" in output

    def test_pagination_no_notice_when_all_shown(self) -> None:
        """Test no pagination notice when all items are shown."""
        console = Console(file=StringIO(), width=80)
        table = create_table()
        add_column_with_ellipsis(table, "Name")
        table.add_row("Item 1")

        print_table_with_pagination(console, table, max_rows=10, total_count=1)
        output = console.file.getvalue()  # type: ignore
        assert "Showing" not in output


class TestTableFormattingIntegration:
    """Integration tests for table formatting."""

    def test_complete_table_workflow(self) -> None:
        """Test complete workflow of creating and formatting a table."""
        # Create sample data
        items = [
            {"id": "1", "title": "Very long title that should be truncated", "status": "current"},
            {"id": "2", "title": "Short", "status": "draft"},
            {"id": "3", "title": "Medium length title", "status": "archived"},
        ]

        # Sort items
        sorted_items = sort_items(items, sort_by="title")

        # Create table
        table = create_table(title="Test Pages")
        add_column_with_ellipsis(table, "ID", style="dim")
        add_column_with_ellipsis(table, "Title", max_width=30)
        add_column_with_ellipsis(table, "Status")

        # Add rows with colorized status
        for item in sorted_items:
            table.add_row(
                item["id"],
                item["title"],
                colorize_status(item["status"]),
            )

        # Print to console
        console = Console(file=StringIO(), width=80)
        print_table_with_pagination(console, table, max_rows=2, total_count=3)

        output = console.file.getvalue()  # type: ignore
        assert "Test Pages" in output
        assert "Showing 2 of 3 results" in output
