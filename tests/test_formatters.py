"""Tests for formatting utilities."""

from datetime import UTC, datetime, timedelta

from confl.formatters import format_duration, format_file_size, format_relative_time


class TestFormatFileSize:
    """Tests for format_file_size function."""

    def test_bytes(self):
        """Test formatting bytes."""
        assert format_file_size(0) == "0 B"
        assert format_file_size(100) == "100 B"
        assert format_file_size(1023) == "1023 B"

    def test_kilobytes(self):
        """Test formatting kilobytes."""
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1536) == "1.5 KB"
        assert format_file_size(10240) == "10.0 KB"
        assert format_file_size(1024 * 100) == "100.0 KB"

    def test_megabytes(self):
        """Test formatting megabytes."""
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1536 * 1024) == "1.5 MB"
        assert format_file_size(10 * 1024 * 1024) == "10.0 MB"
        assert format_file_size(1024 * 1024 * 100) == "100.0 MB"

    def test_gigabytes(self):
        """Test formatting gigabytes."""
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"
        assert format_file_size(int(1.5 * 1024 * 1024 * 1024)) == "1.5 GB"
        assert format_file_size(10 * 1024 * 1024 * 1024) == "10.0 GB"


class TestFormatRelativeTime:
    """Tests for format_relative_time function."""

    def test_just_now(self):
        """Test formatting for very recent timestamps."""
        now = datetime.now(UTC)
        timestamp = now.isoformat()
        assert format_relative_time(timestamp) == "just now"

        # 30 seconds ago
        timestamp = (now - timedelta(seconds=30)).isoformat()
        assert format_relative_time(timestamp) == "just now"

    def test_minutes_ago(self):
        """Test formatting for timestamps within the last hour."""
        now = datetime.now(UTC)

        # 1 minute ago
        timestamp = (now - timedelta(minutes=1)).isoformat()
        assert format_relative_time(timestamp) == "1 minute ago"

        # 5 minutes ago
        timestamp = (now - timedelta(minutes=5)).isoformat()
        assert format_relative_time(timestamp) == "5 minutes ago"

        # 59 minutes ago
        timestamp = (now - timedelta(minutes=59)).isoformat()
        assert format_relative_time(timestamp) == "59 minutes ago"

    def test_hours_ago(self):
        """Test formatting for timestamps within the last day."""
        now = datetime.now(UTC)

        # 1 hour ago
        timestamp = (now - timedelta(hours=1)).isoformat()
        assert format_relative_time(timestamp) == "1 hour ago"

        # 2 hours ago
        timestamp = (now - timedelta(hours=2)).isoformat()
        assert format_relative_time(timestamp) == "2 hours ago"

        # 23 hours ago
        timestamp = (now - timedelta(hours=23)).isoformat()
        assert format_relative_time(timestamp) == "23 hours ago"

    def test_days_ago(self):
        """Test formatting for timestamps within the last week."""
        now = datetime.now(UTC)

        # 1 day ago
        timestamp = (now - timedelta(days=1)).isoformat()
        assert format_relative_time(timestamp) == "1 day ago"

        # 3 days ago
        timestamp = (now - timedelta(days=3)).isoformat()
        assert format_relative_time(timestamp) == "3 days ago"

        # 6 days ago
        timestamp = (now - timedelta(days=6)).isoformat()
        assert format_relative_time(timestamp) == "6 days ago"

    def test_weeks_ago(self):
        """Test formatting for timestamps within the last month."""
        now = datetime.now(UTC)

        # 1 week ago (7 days)
        timestamp = (now - timedelta(weeks=1)).isoformat()
        assert format_relative_time(timestamp) == "1 week ago"

        # 2 weeks ago
        timestamp = (now - timedelta(weeks=2)).isoformat()
        assert format_relative_time(timestamp) == "2 weeks ago"

        # 3 weeks ago
        timestamp = (now - timedelta(weeks=3)).isoformat()
        assert format_relative_time(timestamp) == "3 weeks ago"

    def test_months_ago(self):
        """Test formatting for timestamps within the last year."""
        now = datetime.now(UTC)

        # 1 month ago (30 days)
        timestamp = (now - timedelta(days=30)).isoformat()
        assert format_relative_time(timestamp) == "1 month ago"

        # 2 months ago (60 days)
        timestamp = (now - timedelta(days=60)).isoformat()
        assert format_relative_time(timestamp) == "2 months ago"

        # 6 months ago (180 days)
        timestamp = (now - timedelta(days=180)).isoformat()
        assert format_relative_time(timestamp) == "6 months ago"

    def test_years_ago(self):
        """Test formatting for timestamps over a year old."""
        now = datetime.now(UTC)

        # 1 year ago (365 days)
        timestamp = (now - timedelta(days=365)).isoformat()
        assert format_relative_time(timestamp) == "1 year ago"

        # 2 years ago
        timestamp = (now - timedelta(days=730)).isoformat()
        assert format_relative_time(timestamp) == "2 years ago"

    def test_iso_with_z_suffix(self):
        """Test parsing ISO timestamps with Z suffix."""
        now = datetime.now(UTC)
        timestamp = (now - timedelta(hours=2)).isoformat().replace("+00:00", "Z")
        assert format_relative_time(timestamp) == "2 hours ago"

    def test_iso_with_milliseconds(self):
        """Test parsing ISO timestamps with milliseconds."""
        now = datetime.now(UTC)
        # Confluence API format
        timestamp = (now - timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        assert format_relative_time(timestamp) == "5 hours ago"

    def test_invalid_timestamp(self):
        """Test handling of invalid timestamps."""
        # Should return the original string or just the date part
        result = format_relative_time("invalid")
        assert result == "invalid"

        result = format_relative_time("2024-01-15T12:00:00.000Z-invalid")
        # Should return the date part if parsing fails
        assert "2024-01-15" in result or result == "2024-01-15T12:00:00.000Z-invalid"


class TestFormatDuration:
    """Tests for format_duration function."""

    def test_seconds(self):
        """Test formatting durations under a minute."""
        assert format_duration(0) == "0s"
        assert format_duration(1) == "1s"
        assert format_duration(30) == "30s"
        assert format_duration(59) == "59s"

    def test_minutes(self):
        """Test formatting durations under an hour."""
        assert format_duration(60) == "1m"
        assert format_duration(90) == "1m 30s"
        assert format_duration(120) == "2m"
        assert format_duration(150) == "2m 30s"
        assert format_duration(3599) == "59m 59s"

    def test_hours(self):
        """Test formatting durations over an hour."""
        assert format_duration(3600) == "1h"
        assert format_duration(3660) == "1h 1m"
        assert format_duration(7200) == "2h"
        assert format_duration(7380) == "2h 3m"
        assert format_duration(36000) == "10h"

    def test_decimal_seconds(self):
        """Test formatting with decimal seconds."""
        assert format_duration(45.7) == "45s"
        assert format_duration(90.9) == "1m 30s"


class TestFormatRelativeTimeEdgeCases:
    """Additional edge case tests for format_relative_time to improve coverage."""

    def test_naive_timestamp(self):
        """Test handling of timezone-naive timestamps."""
        from datetime import datetime, timedelta

        # Create a naive timestamp (no timezone info)
        now = datetime.now()
        naive_timestamp = (now - timedelta(hours=2)).isoformat()

        # Should handle naive timestamps by adding UTC timezone
        result = format_relative_time(naive_timestamp)
        assert "ago" in result or result == "just now"


class TestStripMarkdown:
    """Test Markdown stripping for plain text output."""

    def test_code_block_content_preserved(self) -> None:
        """Code block content should be extracted, not removed."""
        from confl.formatters import strip_markdown

        markdown = """```python
print("hello")
x = 42
```"""
        result = strip_markdown(markdown)
        assert 'print("hello")' in result
        assert "x = 42" in result
        assert "```" not in result

    def test_code_block_single_line(self) -> None:
        """Single-line code blocks should work."""
        from confl.formatters import strip_markdown

        markdown = "``` IPHONEOS_DEPLOYMENT_TARGET = 16.0; ```"
        result = strip_markdown(markdown)
        assert "IPHONEOS_DEPLOYMENT_TARGET = 16.0;" in result
        assert "```" not in result

    def test_code_block_with_language(self) -> None:
        """Code blocks with language tags should preserve code."""
        from confl.formatters import strip_markdown

        markdown = "```swift\nlet x = 42\n```"
        result = strip_markdown(markdown)
        assert "let x = 42" in result
        assert "swift" not in result
        assert "```" not in result

    def test_empty_code_block(self) -> None:
        """Empty code blocks should be handled gracefully."""
        from confl.formatters import strip_markdown

        markdown = "``` ```"
        result = strip_markdown(markdown)
        # Should not crash and should remove the backticks
        assert "```" not in result

    def test_inline_code_preserved(self) -> None:
        """Inline code content should be preserved."""
        from confl.formatters import strip_markdown

        markdown = "Use `variable_name` in the code."
        result = strip_markdown(markdown)
        assert "variable_name" in result
        assert "`" not in result

    def test_mixed_code_formatting(self) -> None:
        """Both code blocks and inline code should work together."""
        from confl.formatters import strip_markdown

        markdown = """Here is some `inline_code` and a block:
```java
public class Test {}
```"""
        result = strip_markdown(markdown)
        assert "inline_code" in result
        assert "public class Test {}" in result
        assert "`" not in result

    def test_bold_italic_removed(self) -> None:
        """Bold and italic formatting should be stripped."""
        from confl.formatters import strip_markdown

        markdown = "This is **bold** and *italic* text."
        result = strip_markdown(markdown)
        assert "bold" in result
        assert "italic" in result
        assert "**" not in result
        assert result.count("*") == 0

    def test_links_text_preserved(self) -> None:
        """Link text should be preserved, URLs removed."""
        from confl.formatters import strip_markdown

        markdown = "Check out [this link](https://example.com) for more."
        result = strip_markdown(markdown)
        assert "this link" in result
        assert "example.com" not in result
        assert "[" not in result
        assert "]" not in result

    def test_headers_removed(self) -> None:
        """Header markers should be removed."""
        from confl.formatters import strip_markdown

        markdown = "## My Header\nContent here"
        result = strip_markdown(markdown)
        assert "My Header" in result
        assert "##" not in result
