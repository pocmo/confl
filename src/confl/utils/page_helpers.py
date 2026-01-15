"""Helper functions for page operations."""

import re


def extract_page_id(ref: str) -> str:
    """Extract page ID from a reference (ID or URL).

    Args:
        ref: Page reference - either a numeric ID or Confluence URL

    Returns:
        Page ID as string

    Raises:
        ValueError: If the reference is invalid
    """
    # If it's just a number, return it
    if ref.isdigit():
        return ref

    # Try to extract from URL
    # URL patterns:
    # https://company.atlassian.net/wiki/spaces/KEY/pages/12345678/Title
    # https://company.atlassian.net/wiki/spaces/KEY/pages/12345678
    match = re.search(r"/pages/(\d+)", ref)
    if match:
        return match.group(1)

    raise ValueError(
        f"Invalid page reference: {ref!r}\n\n"
        "Page references must be either:\n"
        "  • A numeric page ID (e.g., 12345678)\n"
        "  • A full Confluence page URL\n\n"
        "Examples:\n"
        "  confl page get 12345678\n"
        '  confl page get "https://company.atlassian.net/wiki/spaces/DEV/pages/12345678"\n\n'
        "Tip: Use 'confl search <query>' to find page IDs"
    )
