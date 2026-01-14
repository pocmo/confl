"""HTTP client for Confluence Cloud REST API v2.

Provides a configured httpx client for making API requests to Confluence.
"""

import base64
import sys
from typing import Any, cast

import httpx
from rich.console import Console

from confl.config import Config, ConfigError, get_config

console = Console(stderr=True)


class ApiError(Exception):
    """Raised when Confluence API returns an error."""

    def __init__(self, message: str, status_code: int | None = None):
        """Initialize API error.

        Args:
            message: Human-readable error message
            status_code: HTTP status code if available
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def get_client() -> httpx.Client:
    """Get configured httpx client for Confluence API.

    Returns:
        Configured httpx.Client ready for API calls

    Raises:
        ConfigError: If configuration is invalid or missing
        SystemExit: Exits with code 2 if configuration cannot be loaded
    """
    try:
        config = get_config()
    except ConfigError as e:
        console.print(f"[red]Error:[/red] {e}", style="red")
        sys.exit(2)

    return create_client(config)


def create_client(config: Config) -> httpx.Client:
    """Create httpx client with the given configuration.

    Args:
        config: Configuration with site, email, and token

    Returns:
        Configured httpx.Client
    """
    # Encode credentials for Basic auth
    credentials = f"{config.email}:{config.token}"
    encoded = base64.b64encode(credentials.encode()).decode()

    return httpx.Client(
        base_url=f"https://{config.site}/wiki/api/v2",
        headers={
            "Authorization": f"Basic {encoded}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=30.0,
    )


def handle_api_error(response: httpx.Response) -> None:
    """Handle API error responses and raise ApiError.

    Args:
        response: HTTP response from Confluence API

    Raises:
        ApiError: Always raised with appropriate message
    """
    status = response.status_code

    # Try to extract error message from response body
    try:
        error_data = response.json()
        message = error_data["message"] if "message" in error_data else str(error_data)
    except Exception:
        message = response.text or f"HTTP {status}"

    # Provide context based on status code
    if status == 401:
        raise ApiError(
            f"Authentication failed: {message}\nCheck your credentials with 'confl auth status'",
            status_code=status,
        )
    elif status == 403:
        raise ApiError(
            f"Permission denied: {message}\nYour credentials may not have access to this resource",
            status_code=status,
        )
    elif status == 404:
        raise ApiError(f"Not found: {message}", status_code=status)
    elif status == 429:
        raise ApiError(
            f"Rate limit exceeded: {message}\nPlease wait before making more requests",
            status_code=status,
        )
    elif 400 <= status < 500:
        raise ApiError(f"Client error ({status}): {message}", status_code=status)
    elif 500 <= status < 600:
        raise ApiError(
            f"Server error ({status}): {message}\n"
            "Confluence API is experiencing issues. Please try again later.",
            status_code=status,
        )
    else:
        raise ApiError(f"Unexpected error ({status}): {message}", status_code=status)


class ConfluenceClient:
    """High-level client for Confluence API operations."""

    def __init__(self, client: httpx.Client):
        """Initialize Confluence client.

        Args:
            client: Configured httpx client
        """
        self.client = client

    def get_page(self, page_id: str) -> dict[str, Any]:
        """Get a page by ID.

        Args:
            page_id: Page ID

        Returns:
            Page data including id, title, body content

        Raises:
            ApiError: If the request fails
        """
        response = self.client.get(
            f"/pages/{page_id}",
            params={
                "body-format": "storage,atlas_doc_format",
            },
        )

        if response.status_code != 200:
            handle_api_error(response)

        return cast(dict[str, Any], response.json())

    def list_pages(self, space_key: str | None = None, limit: int = 25) -> list[dict[str, Any]]:
        """List pages, optionally filtered by space.

        Args:
            space_key: Optional space key to filter by
            limit: Maximum number of results to return (default 25)

        Returns:
            List of page objects with basic metadata (id, title, spaceId)

        Raises:
            ApiError: If the request fails
        """
        params: dict[str, Any] = {"limit": str(limit)}
        if space_key:
            params["space-key"] = space_key

        response = self.client.get("/pages", params=params)

        if response.status_code != 200:
            handle_api_error(response)

        result = cast(dict[str, Any], response.json())
        return cast(list[dict[str, Any]], result.get("results", []))
