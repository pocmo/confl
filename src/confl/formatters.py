"""Formatting utilities for human-readable output."""

from datetime import UTC, datetime


def format_file_size(size_bytes: int) -> str:
    """Format file size as human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.2 MB", "45 KB", "512 B")

    Examples:
        >>> format_file_size(1024)
        '1.0 KB'
        >>> format_file_size(1536000)
        '1.5 MB'
        >>> format_file_size(1610612736)
        '1.5 GB'
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def format_relative_time(iso_timestamp: str) -> str:
    """Format ISO timestamp as relative time.

    Args:
        iso_timestamp: ISO 8601 timestamp string

    Returns:
        Relative time string (e.g., "2 hours ago", "3 days ago", "just now")

    Examples:
        >>> format_relative_time("2024-01-15T12:00:00.000Z")
        '2 hours ago'  # if current time is 14:00
    """
    try:
        # Parse ISO timestamp
        if iso_timestamp.endswith("Z"):
            timestamp = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
        else:
            timestamp = datetime.fromisoformat(iso_timestamp)

        # Get current time in UTC
        now = datetime.now(UTC)

        # Ensure timestamp is timezone-aware
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)

        # Calculate difference
        diff = now - timestamp
        seconds = diff.total_seconds()

        # Format based on time difference
        if seconds < 60:
            return "just now"
        elif seconds < 3600:  # Less than 1 hour
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:  # Less than 1 day
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif seconds < 604800:  # Less than 1 week
            days = int(seconds / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
        elif seconds < 2592000:  # Less than 30 days
            weeks = int(seconds / 604800)
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        elif seconds < 31536000:  # Less than 1 year
            months = int(seconds / 2592000)
            return f"{months} month{'s' if months != 1 else ''} ago"
        else:
            years = int(seconds / 31536000)
            return f"{years} year{'s' if years != 1 else ''} ago"

    except (ValueError, AttributeError):
        # If parsing fails, return original or empty string
        return iso_timestamp.split("T")[0] if "T" in iso_timestamp else iso_timestamp


def format_duration(seconds: float) -> str:
    """Format duration in seconds as human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string (e.g., "1m 30s", "2h 15m", "45s")

    Examples:
        >>> format_duration(45)
        '45s'
        >>> format_duration(90)
        '1m 30s'
        >>> format_duration(3665)
        '1h 1m'
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:  # Less than 1 hour
        minutes = int(seconds / 60)
        remaining_seconds = int(seconds % 60)
        if remaining_seconds > 0:
            return f"{minutes}m {remaining_seconds}s"
        return f"{minutes}m"
    else:  # 1 hour or more
        hours = int(seconds / 3600)
        remaining_minutes = int((seconds % 3600) / 60)
        if remaining_minutes > 0:
            return f"{hours}h {remaining_minutes}m"
        return f"{hours}h"
