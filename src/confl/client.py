"""HTTP client for Confluence Cloud REST API v2 and v1.

Provides configured httpx clients for making API requests to Confluence.
Most functionality uses v2 API, but some features (like search) require v1.
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

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
    ):
        """Initialize API error.

        Args:
            message: Human-readable error message
            status_code: HTTP status code if available
            response_data: Raw API error response data (for --json output)
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data


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
    """Create httpx client with the given configuration for API v2.

    Args:
        config: Configuration with site, email, and token

    Returns:
        Configured httpx.Client for v2 API
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


def get_v1_client() -> httpx.Client:
    """Get configured httpx client for Confluence API v1.

    Returns:
        Configured httpx.Client ready for v1 API calls

    Raises:
        ConfigError: If configuration is invalid or missing
        SystemExit: Exits with code 2 if configuration cannot be loaded
    """
    try:
        config = get_config()
    except ConfigError as e:
        console.print(f"[red]Error:[/red] {e}", style="red")
        sys.exit(2)

    return create_v1_client(config)


def create_v1_client(config: Config) -> httpx.Client:
    """Create httpx client with the given configuration for API v1.

    Args:
        config: Configuration with site, email, and token

    Returns:
        Configured httpx.Client for v1 API
    """
    # Encode credentials for Basic auth
    credentials = f"{config.email}:{config.token}"
    encoded = base64.b64encode(credentials.encode()).decode()

    return httpx.Client(
        base_url=f"https://{config.site}/wiki/rest/api",
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
    error_data = None

    # Try to parse structured error response
    # Confluence API v2 format:
    # {"errors": [{"status": 404, "code": "...", "title": "...", "detail": "..."}]}
    try:
        error_data = response.json()

        # Extract first error from errors array if present
        if isinstance(error_data, dict) and "errors" in error_data:
            errors = error_data["errors"]
            if errors and len(errors) > 0:
                first_error = errors[0]
                # Build message from title and detail
                title = first_error.get("title", "")
                detail = first_error.get("detail", "")
                if title and detail:
                    message = f"{title}\n{detail}"
                elif title:
                    message = title
                elif detail:
                    message = detail
                else:
                    message = str(first_error)
            else:
                message = str(error_data)
        # Fallback: look for "message" field
        elif isinstance(error_data, dict) and "message" in error_data:
            message = error_data["message"]
        else:
            message = str(error_data)
    except Exception:
        # Failed to parse JSON - use raw text
        error_data = None
        message = response.text or f"HTTP {status}"

    # Provide context based on status code
    if status == 401:
        raise ApiError(
            f"Authentication failed: {message}\nCheck your credentials with 'confl auth status'",
            status_code=status,
            response_data=error_data,
        )
    elif status == 403:
        raise ApiError(
            f"Permission denied: {message}\nYour credentials may not have access to this resource",
            status_code=status,
            response_data=error_data,
        )
    elif status == 404:
        raise ApiError(f"Not found: {message}", status_code=status, response_data=error_data)
    elif status == 409:
        raise ApiError(
            f"Version conflict: {message}\n"
            "The page has been modified since you fetched it. "
            "Fetch the latest version and try again.",
            status_code=status,
            response_data=error_data,
        )
    elif status == 429:
        raise ApiError(
            f"Rate limit exceeded: {message}\nPlease wait before making more requests",
            status_code=status,
            response_data=error_data,
        )
    elif 400 <= status < 500:
        raise ApiError(
            f"Client error ({status}): {message}", status_code=status, response_data=error_data
        )
    elif 500 <= status < 600:
        raise ApiError(
            f"Server error ({status}): {message}\n"
            "Confluence API is experiencing issues. Please try again later.",
            status_code=status,
            response_data=error_data,
        )
    else:
        raise ApiError(
            f"Unexpected error ({status}): {message}",
            status_code=status,
            response_data=error_data,
        )


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

    def list_spaces(
        self,
        limit: int = 25,
        type_filter: str | None = None,
        status_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        """List spaces with optional filtering.

        Args:
            limit: Maximum number of results to return (default 25)
            type_filter: Optional filter by space type (global, personal)
            status_filter: Optional filter by space status (current, archived)

        Returns:
            List of space objects with metadata (id, key, name, type, status)

        Raises:
            ApiError: If the request fails
        """
        params: dict[str, Any] = {"limit": str(limit)}
        if type_filter:
            params["type"] = type_filter
        if status_filter:
            params["status"] = status_filter

        response = self.client.get("/spaces", params=params)

        if response.status_code != 200:
            handle_api_error(response)

        result = cast(dict[str, Any], response.json())
        return cast(list[dict[str, Any]], result.get("results", []))

    def get_space(self, space_ref: str) -> dict[str, Any]:
        """Get a space by key or ID.

        Args:
            space_ref: Space key or numeric ID

        Returns:
            Space data including id, key, name, type, status, description

        Raises:
            ApiError: If the request fails or space not found (404)
        """
        # API accepts both IDs and keys in the same endpoint
        response = self.client.get(f"/spaces/{space_ref}")

        if response.status_code != 200:
            handle_api_error(response)

        return cast(dict[str, Any], response.json())

    def create_space(self, key: str, name: str, description: str | None = None) -> dict[str, Any]:
        """Create a new space.

        Args:
            key: Space key (unique short identifier)
            name: Space name
            description: Optional space description

        Returns:
            Created space data including id, key, name

        Raises:
            ApiError: If the request fails (e.g., duplicate key, invalid parameters)
        """
        payload: dict[str, Any] = {
            "key": key,
            "name": name,
        }

        if description:
            payload["description"] = {"plain": {"value": description, "representation": "plain"}}

        response = self.client.post("/spaces", json=payload)

        if response.status_code != 200:
            handle_api_error(response)

        return cast(dict[str, Any], response.json())

    def update_space(
        self, space_ref: str, name: str | None = None, description: str | None = None
    ) -> dict[str, Any]:
        """Update space details.

        Args:
            space_ref: Space key or numeric ID
            name: New space name (optional)
            description: New space description (optional)

        Returns:
            Updated space data

        Raises:
            ApiError: If the request fails
        """
        # Build update payload with only provided fields
        payload: dict[str, Any] = {}

        if name:
            payload["name"] = name

        if description:
            payload["description"] = {"plain": {"value": description, "representation": "plain"}}

        # API accepts both IDs and keys in the same endpoint
        response = self.client.put(f"/spaces/{space_ref}", json=payload)

        if response.status_code != 200:
            handle_api_error(response)

        return cast(dict[str, Any], response.json())

    def delete_space(self, space_ref: str) -> None:
        """Delete a space by key or ID.

        Args:
            space_ref: Space key or numeric ID

        Raises:
            ApiError: If the request fails (except 404 which is handled gracefully)
        """
        # API accepts both IDs and keys in the same endpoint
        response = self.client.delete(f"/spaces/{space_ref}")

        # Accept both 204 (No Content - successful deletion) and 404 (already gone)
        if response.status_code == 204:
            return
        elif response.status_code == 404:
            # Space already deleted or doesn't exist - that's fine
            return
        else:
            handle_api_error(response)

    def list_attachments(self, page_id: str, limit: int = 25) -> list[dict[str, Any]]:
        """List attachments on a page.

        Args:
            page_id: Page ID to list attachments for
            limit: Maximum number of results to return (default 25)

        Returns:
            List of attachment objects with metadata (id, title, mediaType, fileSize, etc.)

        Raises:
            ApiError: If the request fails
        """
        params: dict[str, Any] = {"limit": str(limit)}
        response = self.client.get(f"/pages/{page_id}/attachments", params=params)

        if response.status_code != 200:
            handle_api_error(response)

        result = cast(dict[str, Any], response.json())
        return cast(list[dict[str, Any]], result.get("results", []))

    def get_attachment(self, attachment_id: str) -> dict[str, Any]:
        """Get attachment metadata by ID.

        Args:
            attachment_id: Attachment ID

        Returns:
            Attachment metadata including id, title, mediaType, fileSize, downloadLink

        Raises:
            ApiError: If the request fails or attachment not found (404)
        """
        response = self.client.get(f"/attachments/{attachment_id}")

        if response.status_code != 200:
            handle_api_error(response)

        return cast(dict[str, Any], response.json())

    def download_attachment(self, download_link: str) -> bytes:
        """Download attachment content.

        Args:
            download_link: Relative download link from attachment metadata

        Returns:
            Raw file bytes

        Raises:
            ApiError: If the download fails
        """
        # download_link is relative (e.g., "/wiki/download/attachments/...")
        # We need to make absolute URL
        # Client base_url is "https://{site}/wiki/api/v2"
        # We need "https://{site}/wiki/download/..."

        # Extract site from base URL (before /wiki)
        base_url_str = str(self.client.base_url)
        # e.g., "https://example.atlassian.net/wiki/api/v2"
        # Extract: "https://example.atlassian.net"
        site_url = base_url_str.split("/wiki/")[0]

        # Make full download URL (download_link already has /wiki prefix)
        download_url = f"{site_url}{download_link}"

        # Use a separate request (not through base_url) to download
        response = self.client.get(download_url)

        if response.status_code != 200:
            handle_api_error(response)

        return response.content

    def upload_attachment(
        self, page_id: str, file_path: str, comment: str | None = None
    ) -> dict[str, Any]:
        """Upload a file attachment to a page.

        Note: Uses v1 API as v2 doesn't support upload yet.

        Args:
            page_id: Page ID to attach file to
            file_path: Path to file to upload
            comment: Optional comment for the attachment

        Returns:
            Attachment metadata from v1 API response

        Raises:
            ApiError: If the upload fails
            FileNotFoundError: If file_path doesn't exist
        """
        import mimetypes
        from pathlib import Path

        file = Path(file_path)
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(str(file))
        if not mime_type:
            mime_type = "application/octet-stream"

        # Build v1 API URL
        # Client base is https://{site}/wiki/api/v2
        # We need https://{site}/wiki/rest/api/content/{pageId}/child/attachment
        base_url_str = str(self.client.base_url)
        # Extract site URL (before /wiki)
        site_url = base_url_str.split("/wiki/")[0]
        upload_url = f"{site_url}/wiki/rest/api/content/{page_id}/child/attachment"

        # Prepare multipart form data
        files = {"file": (file.name, file.open("rb"), mime_type)}
        data = {}
        if comment:
            data["comment"] = comment

        # Need X-Atlassian-Token header for CSRF protection
        headers = {
            "X-Atlassian-Token": "no-check",
        }

        # Make request with multipart/form-data
        response = self.client.post(upload_url, files=files, data=data, headers=headers)

        if response.status_code not in (200, 201):
            handle_api_error(response)

        # v1 API returns results array
        result = cast(dict[str, Any], response.json())
        results = result.get("results", [])
        if results:
            return cast(dict[str, Any], results[0])
        return result

    def delete_attachment(self, attachment_id: str) -> None:
        """Delete an attachment by ID.

        Args:
            attachment_id: Attachment ID

        Raises:
            ApiError: If the request fails (except 404 which is handled gracefully)
        """
        response = self.client.delete(f"/attachments/{attachment_id}")

        # Accept both 204 (No Content - successful deletion) and 404 (already gone)
        if response.status_code == 204:
            return
        elif response.status_code == 404:
            # Attachment already deleted or doesn't exist - that's fine
            return
        else:
            handle_api_error(response)

    def list_page_labels(self, page_id: str, limit: int = 25) -> list[dict[str, Any]]:
        """List labels on a page.

        Args:
            page_id: Page ID
            limit: Maximum number of results to return (default 25)

        Returns:
            List of label objects with id, name, prefix

        Raises:
            ApiError: If the request fails
        """
        params: dict[str, Any] = {"limit": str(limit)}
        response = self.client.get(f"/pages/{page_id}/labels", params=params)

        if response.status_code != 200:
            handle_api_error(response)

        result = cast(dict[str, Any], response.json())
        return cast(list[dict[str, Any]], result.get("results", []))

    def add_labels_to_page(self, page_id: str, labels: list[str]) -> list[dict[str, Any]]:
        """Add labels to a page.

        Note: Uses v1 API as v2 doesn't support label modification yet.

        Args:
            page_id: Page ID
            labels: List of label names to add

        Returns:
            List of added label objects from v1 API response

        Raises:
            ApiError: If the request fails
        """
        # Build v1 API URL
        # Client base is https://{site}/wiki/api/v2
        # We need https://{site}/wiki/rest/api/content/{pageId}/label
        base_url_str = str(self.client.base_url)
        site_url = base_url_str.split("/wiki/")[0]
        add_labels_url = f"{site_url}/wiki/rest/api/content/{page_id}/label"

        # Build request body - array of {prefix, name} objects
        # Most labels use "global" prefix
        label_objects = [{"prefix": "global", "name": label} for label in labels]

        response = self.client.post(add_labels_url, json=label_objects)

        if response.status_code not in (200, 201):
            handle_api_error(response)

        # v1 API returns results array
        result = cast(dict[str, Any], response.json())
        results = result.get("results", [])
        return cast(list[dict[str, Any]], results)

    def remove_label_from_page(self, page_id: str, label_name: str) -> None:
        """Remove a label from a page.

        Note: Uses v1 API as v2 doesn't support label modification yet.

        Args:
            page_id: Page ID
            label_name: Label name to remove

        Raises:
            ApiError: If the request fails (except 404 which is handled gracefully)
        """
        # Build v1 API URL
        # Client base is https://{site}/wiki/api/v2
        # We need https://{site}/wiki/rest/api/content/{pageId}/label?name={labelName}
        base_url_str = str(self.client.base_url)
        site_url = base_url_str.split("/wiki/")[0]
        remove_label_url = f"{site_url}/wiki/rest/api/content/{page_id}/label"

        response = self.client.delete(remove_label_url, params={"name": label_name})

        # Accept both 204 (No Content - successful deletion) and 404 (label not found)
        if response.status_code == 204:
            return
        elif response.status_code == 404:
            # Label already removed or doesn't exist - that's fine
            return
        else:
            handle_api_error(response)

    def find_label_by_name(self, label_name: str) -> dict[str, Any] | None:
        """Find a label by name.

        Args:
            label_name: Label name to search for

        Returns:
            Label object with id, name, prefix, or None if not found

        Raises:
            ApiError: If the request fails
        """
        # Search all labels - API doesn't support direct name lookup
        # We'll fetch up to 250 labels (max limit) and search
        response = self.client.get("/labels", params={"limit": "250"})

        if response.status_code != 200:
            handle_api_error(response)

        result = cast(dict[str, Any], response.json())
        labels = cast(list[dict[str, Any]], result.get("results", []))

        # Find matching label (case-insensitive)
        label_name_lower = label_name.lower()
        for label in labels:
            if label.get("name", "").lower() == label_name_lower:
                return label

        return None

    def list_pages_by_label(self, label_id: str, limit: int = 25) -> list[dict[str, Any]]:
        """List pages with a specific label.

        Args:
            label_id: Label ID
            limit: Maximum number of results to return (default 25)

        Returns:
            List of page objects

        Raises:
            ApiError: If the request fails
        """
        params: dict[str, Any] = {"limit": str(limit)}
        response = self.client.get(f"/labels/{label_id}/pages", params=params)

        if response.status_code != 200:
            handle_api_error(response)

        result = cast(dict[str, Any], response.json())
        return cast(list[dict[str, Any]], result.get("results", []))

    def list_blogposts_by_label(self, label_id: str, limit: int = 25) -> list[dict[str, Any]]:
        """List blog posts with a specific label.

        Args:
            label_id: Label ID
            limit: Maximum number of results to return (default 25)

        Returns:
            List of blog post objects

        Raises:
            ApiError: If the request fails
        """
        params: dict[str, Any] = {"limit": str(limit)}
        response = self.client.get(f"/labels/{label_id}/blogposts", params=params)

        if response.status_code != 200:
            handle_api_error(response)

        result = cast(dict[str, Any], response.json())
        return cast(list[dict[str, Any]], result.get("results", []))

    def list_attachments_by_label(self, label_id: str, limit: int = 25) -> list[dict[str, Any]]:
        """List attachments with a specific label.

        Args:
            label_id: Label ID
            limit: Maximum number of results to return (default 25)

        Returns:
            List of attachment objects

        Raises:
            ApiError: If the request fails
        """
        params: dict[str, Any] = {"limit": str(limit)}
        response = self.client.get(f"/labels/{label_id}/attachments", params=params)

        if response.status_code != 200:
            handle_api_error(response)

        result = cast(dict[str, Any], response.json())
        return cast(list[dict[str, Any]], result.get("results", []))

    def search_content(self, cql: str, limit: int = 25) -> list[dict[str, Any]]:
        """Search for content using CQL (Confluence Query Language).

        Note: Uses v1 API as v2 doesn't support search yet.

        Args:
            cql: CQL query string (e.g., "space = DEV AND type = page")
            limit: Maximum number of results to return (default 25)

        Returns:
            List of search result objects with id, title, type, url, etc.

        Raises:
            ApiError: If the request fails
        """
        # Build v1 API URL
        # Client base is https://{site}/wiki/api/v2
        # We need https://{site}/wiki/rest/api/search
        base_url_str = str(self.client.base_url)
        # Extract site URL (before /wiki)
        site_url = base_url_str.split("/wiki/")[0]
        search_url = f"{site_url}/wiki/rest/api/search"

        params: dict[str, Any] = {
            "cql": cql,
            "limit": str(limit),
        }

        response = self.client.get(search_url, params=params)

        if response.status_code != 200:
            handle_api_error(response)

        result = cast(dict[str, Any], response.json())
        return cast(list[dict[str, Any]], result.get("results", []))
