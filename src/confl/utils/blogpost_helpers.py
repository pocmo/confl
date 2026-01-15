"""Helper functions for blogpost operations."""

import re


def extract_blogpost_id(ref: str) -> str:
    """Extract blog post ID from a reference (ID or URL).

    Args:
        ref: Blog post reference - either a numeric ID or Confluence URL

    Returns:
        Blog post ID as string

    Raises:
        ValueError: If the reference is invalid
    """
    # If it's just a number, return it
    if ref.isdigit():
        return ref

    # Try to extract from URL
    # URL patterns:
    # https://company.atlassian.net/wiki/spaces/KEY/blog/2024/01/15/12345678/Title
    # https://company.atlassian.net/wiki/spaces/KEY/blogposts/12345678/Title
    match = re.search(r"/blogposts?/(\d+)", ref)
    if not match:
        # Try alternate pattern with date path
        match = re.search(r"/blog/\d{4}/\d{2}/\d{2}/(\d+)", ref)

    if match:
        return match.group(1)

    raise ValueError(
        f"Invalid blog post reference: {ref!r}\n\n"
        "Blog post references must be either:\n"
        "  • A numeric blog post ID (e.g., 12345678)\n"
        "  • A full Confluence blog post URL\n\n"
        "Examples:\n"
        "  confl blogpost get 12345678\n"
        '  confl blogpost get "https://company.atlassian.net/wiki/spaces/DEV/blogposts/12345678"\n\n'
        "Tip: Use 'confl search <query> --type blogpost' to find blog post IDs"
    )
