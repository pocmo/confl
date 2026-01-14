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
    elif status == 409:
        raise ApiError(
            f"Version conflict: {message}\n"
            "The page has been modified since you fetched it. "
            "Fetch the latest version and try again.",
            status_code=status,
        )
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
                "body-format": "storage",
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

    def update_page(
        self,
        page_id: str,
        title: str,
        body: str,
        version_number: int,
    ) -> dict[str, Any]:
        """Update an existing page's content.

        Args:
            page_id: Page ID to update
            title: New page title
            body: New page body content in storage format
            version_number: Current version number for optimistic locking

        Returns:
            Updated page data including id, title, body content, and new version

        Raises:
            ApiError: If the request fails, including version conflicts (409)
        """
        payload = {
            "id": page_id,
            "status": "current",
            "title": title,
            "body": {
                "representation": "storage",
                "value": body,
            },
            "version": {
                "number": version_number,
            },
        }

        response = self.client.put(f"/pages/{page_id}", json=payload)

        if response.status_code != 200:
            handle_api_error(response)

        return cast(dict[str, Any], response.json())

    def get_space_by_key(self, space_key: str) -> dict[str, Any]:
        """Get a space by its key.

        Args:
            space_key: Space key (e.g., "TEAM")

        Returns:
            Space data including id, key, name, type, and other metadata

        Raises:
            ApiError: If the request fails or space not found (404)
        """
        response = self.client.get("/spaces", params={"keys": space_key})

        if response.status_code != 200:
            handle_api_error(response)

        result = cast(dict[str, Any], response.json())
        results = cast(list[dict[str, Any]], result.get("results", []))

        # API returns array of results; should have exactly one match
        if not results:
            raise ApiError(f"Space not found: {space_key}", status_code=404)

        return results[0]

    def create_page(
        self,
        space_id: str,
        title: str,
        body: str,
        parent_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a new page in a space.

        Args:
            space_id: Space ID where page will be created
            title: Page title
            body: Page body content in storage format
            parent_id: Optional parent page ID for hierarchy

        Returns:
            Created page data including new page ID, title, version, etc.

        Raises:
            ApiError: If the request fails (e.g., duplicate title, invalid space)
        """
        payload: dict[str, Any] = {
            "spaceId": space_id,
            "status": "current",
            "title": title,
            "body": {
                "representation": "storage",
                "value": body,
            },
        }

        if parent_id:
            payload["parentId"] = parent_id

        response = self.client.post("/pages", json=payload)

        if response.status_code != 200:
            handle_api_error(response)

        return cast(dict[str, Any], response.json())

    def delete_page(self, page_id: str) -> None:
        """Delete a page by ID.

        Args:
            page_id: Page ID to delete

        Raises:
            ApiError: If the request fails (except 404 which is handled gracefully)

        Note:
            Deletion in Confluence typically moves the page to trash (soft delete).
            404 errors are handled gracefully since the end result is the same:
            the page no longer exists.
        """
        response = self.client.delete(f"/pages/{page_id}")

        # Accept both 204 (No Content - successful deletion) and 404 (already gone)
        if response.status_code == 204:
            return
        elif response.status_code == 404:
            # Page already deleted or doesn't exist - that's fine
            return
        else:
            handle_api_error(response)
