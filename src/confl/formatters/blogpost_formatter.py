"""Formatting functions for blogpost display and output."""

from typing import Any

from confl.formatters import format_relative_time


def format_blogpost_metadata(blogpost: dict[str, Any]) -> str:
    """Format blog post metadata as a header.

    Args:
        blogpost: Blog post data from API

    Returns:
        Formatted metadata string
    """
    lines = []
    lines.append(f"Title: {blogpost.get('title', 'Untitled')}")

    # Space key
    if "spaceId" in blogpost:
        lines.append(f"Space: {blogpost['spaceId']}")

    # Author (from version history)
    version = blogpost.get("version", {})
    if "authorId" in version:
        lines.append(f"Author: {version['authorId']}")

    # Updated timestamp
    if "createdAt" in version:
        timestamp = version["createdAt"]
        relative_time = format_relative_time(timestamp)
        lines.append(f"Published: {relative_time}")

    lines.append("---")
    return "\n".join(lines)


def get_blogpost_content(blogpost: dict[str, Any], format_type: str = "storage") -> str:
    """Extract blog post content in the specified format.

    Args:
        blogpost: Blog post data from API
        format_type: Content format ("storage" or "atlas_doc_format")

    Returns:
        Blog post content as string
    """
    body = blogpost.get("body", {})
    format_data = body.get(format_type, {})
    value = format_data.get("value", "")
    return str(value)
