"""CQL (Confluence Query Language) query builder utilities.

Provides helper functions to build CQL queries from flags for the search command.
CQL supports various operators and conditions. This module handles proper quoting
and escaping of values.

Reference: https://developer.atlassian.com/cloud/confluence/advanced-searching-using-cql/
"""


def build_cql_query(
    text: str | None = None,
    space: str | None = None,
    content_type: str | None = None,
    label: str | None = None,
) -> str:
    """Build a CQL query from search parameters.

    Combines multiple conditions with AND logic. Each parameter is properly
    quoted and escaped for CQL syntax.

    Args:
        text: Text to search for in page content (uses 'text ~' operator)
        space: Space key to filter by (uses 'space =' operator)
        content_type: Content type to filter by: 'page', 'blogpost', etc. (uses 'type =' operator)
        label: Label to filter by (uses 'label =' operator)

    Returns:
        CQL query string combining all provided conditions with AND

    Examples:
        >>> build_cql_query(text="API docs", space="DEV")
        'text ~ "API docs" AND space = DEV'

        >>> build_cql_query(space="MARKETING", content_type="page", label="draft")
        'space = MARKETING AND type = page AND label = draft'

        >>> build_cql_query(text="meeting notes")
        'text ~ "meeting notes"'
    """
    conditions = []

    if text is not None:
        # Text search uses the ~ (contains) operator and requires quoting
        conditions.append(f'text ~ "{_escape_cql_string(text)}"')

    if space is not None:
        # Space keys are alphanumeric, typically don't need quoting
        # but we'll quote them if they contain special characters
        conditions.append(f"space = {_quote_if_needed(space)}")

    if content_type is not None:
        # Content types are simple keywords (page, blogpost, etc.)
        conditions.append(f"type = {content_type}")

    if label is not None:
        # Labels should be quoted if they contain spaces or special chars
        conditions.append(f"label = {_quote_if_needed(label)}")

    return " AND ".join(conditions)


def _escape_cql_string(value: str) -> str:
    """Escape special characters in CQL string values.

    CQL strings use double quotes, so we need to escape:
    - Double quotes as \"
    - Backslashes as \\

    Args:
        value: String to escape

    Returns:
        Escaped string safe for use in CQL
    """
    # Escape backslashes first (to avoid double-escaping)
    value = value.replace("\\", "\\\\")
    # Then escape double quotes
    value = value.replace('"', '\\"')
    return value


def _quote_if_needed(value: str) -> str:
    """Quote a CQL value if it contains spaces or special characters.

    CQL identifiers (like space keys, labels) don't need quotes if they're
    simple alphanumeric strings. But if they contain spaces or special
    characters, they need to be quoted.

    Args:
        value: Value to potentially quote

    Returns:
        Quoted or unquoted value as appropriate
    """
    # Check if value contains spaces or special CQL characters
    if any(char in value for char in [" ", "=", "~", "!", "<", ">", "(", ")", ",", '"']):
        # Quote and escape the value
        return f'"{_escape_cql_string(value)}"'
    else:
        # No quoting needed for simple identifiers
        return value
