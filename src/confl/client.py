"""HTTP client for Confluence Cloud REST API v2 and v1.

Provides configured httpx clients for making API requests to Confluence.
Most functionality uses v2 API, but some features (like search) require v1.
"""

import base64
import logging
import sys
from typing import Any, cast

import httpx
from rich.console import Console

from confl.config import Config, ConfigError, get_config
from confl.context import ExecutionContext

console = Console(stderr=True)
logger = logging.getLogger(__name__)


def log_request(request: httpx.Request) -> None:
    """Log HTTP request details when debug mode is enabled."""
    logger.debug(f"HTTP Request: {request.method} {request.url}")
    if logger.isEnabledFor(logging.DEBUG):
        # Only format headers if we're actually logging
        headers = dict(request.headers)
        # Mask authorization header for security
        if "authorization" in headers:
            headers["authorization"] = "***MASKED***"
        logger.debug(f"  Headers: {headers}")
        if request.content:
            logger.debug(f"  Body: {request.content.decode('utf-8', errors='replace')}")


def log_response(response: httpx.Response) -> None:
    """Log HTTP response details when debug mode is enabled."""
    logger.debug(
        f"HTTP Response: {response.status_code} {response.reason_phrase} "
        f"({len(response.content)} bytes)"
    )
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"  Headers: {dict(response.headers)}")
        # Only log response body for non-binary content
        content_type = response.headers.get("content-type", "")
        if "json" in content_type or "text" in content_type:
            try:
                body = response.text[:1000]  # Limit to first 1000 chars
                if len(response.text) > 1000:
                    body += "... (truncated)"
                logger.debug(f"  Body: {body}")
            except Exception:
                logger.debug("  Body: (unable to decode)")


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


def get_client(context: ExecutionContext | None = None, profile: str | None = None) -> httpx.Client:
    """Get configured httpx client for Confluence API.

    Args:
        context: Execution context containing profile and debug settings.
                If None, gets context from CLI layer.
        profile: Configuration profile to use. If None, uses profile from context
                or default from CONFL_PROFILE.

    Returns:
        Configured httpx.Client ready for API calls

    Raises:
        ConfigError: If configuration is invalid or missing
        SystemExit: Exits with code 2 if configuration cannot be loaded
    """
    if context is None:
        # Import here to get CLI context without creating circular dependency at module level
        from confl.cli import get_context

        context = get_context()

    # Use profile from parameter, then context, then None for default
    if profile is None:
        profile = context.profile

    try:
        config = get_config(profile)
    except ConfigError as e:
        console.print(f"[red]Error:[/red] {e}", style="red")
        sys.exit(2)

    return create_client(config, context)


def create_client(config: Config, context: ExecutionContext | None = None) -> httpx.Client:
    """Create httpx client with the given configuration for API v2.

    Args:
        config: Configuration with site, email, and token
        context: Execution context with debug flag. If None, creates default context.

    Returns:
        Configured httpx.Client for v2 API
    """
    if context is None:
        context = ExecutionContext()

    # Encode credentials for Basic auth
    credentials = f"{config.email}:{config.token}"
    encoded = base64.b64encode(credentials.encode()).decode()

    # Add event hooks for debug logging if debug mode is enabled
    if context.debug:
        return httpx.Client(
            base_url=f"https://{config.site}/wiki/api/v2",
            headers={
                "Authorization": f"Basic {encoded}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=30.0,
            event_hooks={
                "request": [log_request],
                "response": [log_response],
            },
        )
    else:
        return httpx.Client(
            base_url=f"https://{config.site}/wiki/api/v2",
            headers={
                "Authorization": f"Basic {encoded}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )


def get_v1_client(context: ExecutionContext | None = None) -> httpx.Client:
    """Get configured httpx client for Confluence API v1.

    Args:
        context: Execution context with debug flag. If None, gets context from CLI layer.

    Returns:
        Configured httpx.Client ready for v1 API calls

    Raises:
        ConfigError: If configuration is invalid or missing
        SystemExit: Exits with code 2 if configuration cannot be loaded
    """
    if context is None:
        # Import here to get CLI context without creating circular dependency at module level
        from confl.cli import get_context

        context = get_context()

    try:
        config = get_config(context.profile)
    except ConfigError as e:
        console.print(f"[red]Error:[/red] {e}", style="red")
        sys.exit(2)

    return create_v1_client(config, context)


def create_v1_client(config: Config, context: ExecutionContext | None = None) -> httpx.Client:
    """Create httpx client with the given configuration for API v1.

    Args:
        config: Configuration with site, email, and token
        context: Execution context with debug flag. If None, creates default context.

    Returns:
        Configured httpx.Client for v1 API
    """
    if context is None:
        context = ExecutionContext()

    # Encode credentials for Basic auth
    credentials = f"{config.email}:{config.token}"
    encoded = base64.b64encode(credentials.encode()).decode()

    # Add event hooks for debug logging if debug mode is enabled
    if context.debug:
        return httpx.Client(
            base_url=f"https://{config.site}/wiki/rest/api",
            headers={
                "Authorization": f"Basic {encoded}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=30.0,
            event_hooks={
                "request": [log_request],
                "response": [log_response],
            },
        )
    else:
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
            f"Authentication failed: {message}\n\n"
            "Possible solutions:\n"
            "  • Check your credentials: confl auth status\n"
            "  • Re-authenticate: confl auth login\n"
            "  • Verify your API token is still valid at:\n"
            "    https://id.atlassian.com/manage-profile/security/api-tokens",
            status_code=status,
            response_data=error_data,
        )
    elif status == 403:
        raise ApiError(
            f"Permission denied: {message}\n\n"
            "Possible causes:\n"
            "  • Your account may not have permission to access this resource\n"
            "  • The page/space may be restricted\n"
            "  • Check with your Confluence administrator if you need access",
            status_code=status,
            response_data=error_data,
        )
    elif status == 404:
        raise ApiError(
            f"Not found: {message}\n\n"
            "Possible causes:\n"
            "  • The page/space may have been deleted or moved\n"
            "  • You may not have permission to view it\n"
            "  • The ID or URL may be incorrect\n"
            "Tip: Use 'confl search <query>' to find the resource",
            status_code=status,
            response_data=error_data,
        )
    elif status == 409:
        raise ApiError(
            f"Version conflict: {message}\n\n"
            "The page has been modified since you fetched it.\n"
            "Solution:\n"
            "  1. Fetch the latest version: confl page get <page-id>\n"
            "  2. Merge your changes with the latest content\n"
            "  3. Try updating again with the new version number",
            status_code=status,
            response_data=error_data,
        )
    elif status == 429:
        raise ApiError(
            f"Rate limit exceeded: {message}\n\n"
            "You're making requests too quickly.\n"
            "Solutions:\n"
            "  • Wait 60 seconds and try again\n"
            "  • Add delays between bulk operations\n"
            "  • Reduce the number of concurrent requests",
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
        limit: int | None = None,
        type_filter: str | None = None,
        status_filter: str | None = None,
        sort: str | None = None,
        favorited_by: str | None = None,
        labels: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """List spaces with optional filtering and sorting.

        Args:
            limit: Maximum number of results to return. If None, fetches all spaces.
                  If specified, fetches up to limit results (may require pagination).
            type_filter: Optional filter by space type (global, personal)
            status_filter: Optional filter by space status (current, archived)
            sort: Optional sort parameter (e.g., 'name', '-name' for descending)
            favorited_by: Optional account ID to filter by favorited spaces
            labels: Optional list of labels to filter spaces by

        Returns:
            List of space objects with metadata (id, key, name, type, status)

        Raises:
            ApiError: If the request fails
        """
        all_spaces: list[dict[str, Any]] = []
        cursor: str | None = None
        page_size = 100  # Fetch 100 per page for efficiency

        while True:
            params: dict[str, Any] = {"limit": str(page_size)}
            if type_filter:
                params["type"] = type_filter
            if status_filter:
                params["status"] = status_filter
            if sort:
                params["sort"] = sort
            if favorited_by:
                params["favorited-by"] = favorited_by
            if labels:
                params["labels"] = labels
            if cursor:
                params["cursor"] = cursor

            response = self.client.get("/spaces", params=params)

            if response.status_code != 200:
                handle_api_error(response)

            result = cast(dict[str, Any], response.json())
            spaces = cast(list[dict[str, Any]], result.get("results", []))
            all_spaces.extend(spaces)

            # Stop if we've reached the requested limit
            if limit is not None and len(all_spaces) >= limit:
                return all_spaces[:limit]

            # Check for next page
            links = result.get("_links", {})
            next_link = links.get("next")
            if not next_link:
                # No more pages
                break

            # Extract cursor from next link
            # The next link typically looks like: "/wiki/api/v2/spaces?cursor=..."
            if isinstance(next_link, str):
                # Parse cursor from URL string
                import urllib.parse

                parsed = urllib.parse.urlparse(next_link)
                query_params = urllib.parse.parse_qs(parsed.query)
                cursor = query_params.get("cursor", [None])[0]
            else:
                # Sometimes it's a dict with 'href' key
                cursor = None

            if not cursor:
                # Can't find cursor, stop pagination
                break

        return all_spaces

    def get_space(self, space_ref: str) -> dict[str, Any]:
        """Get a space by key or ID.

        Args:
            space_ref: Space key or numeric ID

        Returns:
            Space data including id, key, name, type, status, description

        Raises:
            ApiError: If the request fails or space not found (404)
        """
        # Check if space_ref is numeric (space ID) or not (space key)
        if space_ref.isdigit():
            # It's a numeric ID - use /spaces/{id} endpoint directly
            response = self.client.get(f"/spaces/{space_ref}")

            if response.status_code != 200:
                handle_api_error(response)

            return cast(dict[str, Any], response.json())
        else:
            # It's a space key - resolve to ID first, then fetch
            return self.get_space_by_key(space_ref)

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
        # Resolve space key to ID if needed
        if not space_ref.isdigit():
            space_data = self.get_space_by_key(space_ref)
            space_id = str(space_data["id"])
        else:
            space_id = space_ref

        # Build update payload with only provided fields
        payload: dict[str, Any] = {}

        if name:
            payload["name"] = name

        if description:
            payload["description"] = {"plain": {"value": description, "representation": "plain"}}

        response = self.client.put(f"/spaces/{space_id}", json=payload)

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
        # Resolve space key to ID if needed
        if not space_ref.isdigit():
            try:
                space_data = self.get_space_by_key(space_ref)
                space_id = str(space_data["id"])
            except ApiError as e:
                # If space key not found (404), treat same as if ID not found
                if e.status_code == 404:
                    return
                raise
        else:
            space_id = space_ref

        response = self.client.delete(f"/spaces/{space_id}")

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

    def list_blogposts(self, space_id: str | None = None, limit: int = 25) -> list[dict[str, Any]]:
        """List blog posts, optionally filtered by space.

        Args:
            space_id: Optional space ID to filter by
            limit: Maximum number of results to return (default 25)

        Returns:
            List of blog post objects with basic metadata (id, title, spaceId)

        Raises:
            ApiError: If the request fails
        """
        params: dict[str, Any] = {"limit": str(limit)}
        if space_id:
            params["space-id"] = space_id

        response = self.client.get("/blogposts", params=params)

        if response.status_code != 200:
            handle_api_error(response)

        result = cast(dict[str, Any], response.json())
        return cast(list[dict[str, Any]], result.get("results", []))

    def get_blogpost(self, blogpost_id: str) -> dict[str, Any]:
        """Get a blog post by ID.

        Args:
            blogpost_id: Blog post ID

        Returns:
            Blog post data including id, title, body content

        Raises:
            ApiError: If the request fails
        """
        response = self.client.get(
            f"/blogposts/{blogpost_id}",
            params={
                "body-format": "storage",
            },
        )

        if response.status_code != 200:
            handle_api_error(response)

        return cast(dict[str, Any], response.json())

    def create_blogpost(
        self,
        space_id: str,
        title: str,
        body: str,
    ) -> dict[str, Any]:
        """Create a new blog post in a space.

        Args:
            space_id: Space ID where blog post will be created
            title: Blog post title
            body: Blog post body content in storage format

        Returns:
            Created blog post data including new blog post ID, title, version, etc.

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

        response = self.client.post("/blogposts", json=payload)

        if response.status_code != 200:
            handle_api_error(response)

        return cast(dict[str, Any], response.json())

    def update_blogpost(
        self,
        blogpost_id: str,
        title: str,
        body: str,
        version_number: int,
    ) -> dict[str, Any]:
        """Update an existing blog post's content.

        Args:
            blogpost_id: Blog post ID to update
            title: New blog post title
            body: New blog post body content in storage format
            version_number: Current version number for optimistic locking

        Returns:
            Updated blog post data including id, title, body content, and new version

        Raises:
            ApiError: If the request fails, including version conflicts (409)
        """
        payload = {
            "id": blogpost_id,
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

        response = self.client.put(f"/blogposts/{blogpost_id}", json=payload)

        if response.status_code != 200:
            handle_api_error(response)

        return cast(dict[str, Any], response.json())

    def delete_blogpost(self, blogpost_id: str) -> None:
        """Delete a blog post by ID.

        Args:
            blogpost_id: Blog post ID to delete

        Raises:
            ApiError: If the request fails (except 404 which is handled gracefully)

        Note:
            Deletion in Confluence typically moves the blog post to trash (soft delete).
            404 errors are handled gracefully since the end result is the same:
            the blog post no longer exists.
        """
        response = self.client.delete(f"/blogposts/{blogpost_id}")

        # Accept both 204 (No Content - successful deletion) and 404 (already gone)
        if response.status_code == 204:
            return
        elif response.status_code == 404:
            # Blog post already deleted or doesn't exist - that's fine
            return
        else:
            handle_api_error(response)

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

    def list_footer_comments(
        self, page_id: str | None = None, limit: int = 25
    ) -> list[dict[str, Any]]:
        """List footer comments on a page or all footer comments.

        Args:
            page_id: Optional page ID to filter by. If None, lists all footer comments.
            limit: Maximum number of results to return (default 25)

        Returns:
            List of comment objects with id, body, author, created/modified dates

        Raises:
            ApiError: If the request fails
        """
        params: dict[str, Any] = {"limit": str(limit), "body-format": "storage"}

        if page_id:
            response = self.client.get(f"/pages/{page_id}/footer-comments", params=params)
        else:
            response = self.client.get("/footer-comments", params=params)

        if response.status_code != 200:
            handle_api_error(response)

        result = cast(dict[str, Any], response.json())
        return cast(list[dict[str, Any]], result.get("results", []))

    def get_footer_comment(self, comment_id: str) -> dict[str, Any]:
        """Get a footer comment by ID.

        Args:
            comment_id: Comment ID

        Returns:
            Comment object with id, body, author, created/modified dates

        Raises:
            ApiError: If the request fails
        """
        response = self.client.get(
            f"/footer-comments/{comment_id}", params={"body-format": "storage"}
        )

        if response.status_code != 200:
            handle_api_error(response)

        return cast(dict[str, Any], response.json())

    def create_footer_comment(
        self,
        body: str,
        page_id: str | None = None,
        blogpost_id: str | None = None,
        parent_comment_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a footer comment on a page or blog post, or as a reply to another comment.

        Args:
            body: Comment body in storage format
            page_id: Page ID to comment on (mutually exclusive with blogpost_id)
            blogpost_id: Blog post ID to comment on (mutually exclusive with page_id)
            parent_comment_id: Parent comment ID for replies

        Returns:
            Created comment object

        Raises:
            ApiError: If the request fails
            ValueError: If neither page_id nor blogpost_id is provided
        """
        if not page_id and not blogpost_id and not parent_comment_id:
            raise ValueError("Must provide either page_id, blogpost_id, or parent_comment_id")

        payload: dict[str, Any] = {
            "body": {
                "representation": "storage",
                "value": body,
            }
        }

        if page_id:
            payload["pageId"] = page_id
        elif blogpost_id:
            payload["blogPostId"] = blogpost_id

        if parent_comment_id:
            payload["parentCommentId"] = parent_comment_id

        response = self.client.post("/footer-comments", json=payload)

        if response.status_code != 200:
            handle_api_error(response)

        return cast(dict[str, Any], response.json())

    def update_footer_comment(self, comment_id: str, body: str) -> dict[str, Any]:
        """Update a footer comment.

        Args:
            comment_id: Comment ID to update
            body: New comment body in storage format

        Returns:
            Updated comment object

        Raises:
            ApiError: If the request fails
        """
        payload = {
            "body": {
                "representation": "storage",
                "value": body,
            }
        }

        response = self.client.put(f"/footer-comments/{comment_id}", json=payload)

        if response.status_code != 200:
            handle_api_error(response)

        return cast(dict[str, Any], response.json())

    def delete_footer_comment(self, comment_id: str) -> None:
        """Delete a footer comment.

        Args:
            comment_id: Comment ID to delete

        Raises:
            ApiError: If the request fails (except 404 which is handled gracefully)
        """
        response = self.client.delete(f"/footer-comments/{comment_id}")

        if response.status_code == 204:
            return
        elif response.status_code == 404:
            # Comment already deleted or doesn't exist - that's fine
            return
        else:
            handle_api_error(response)

    def list_inline_comments(
        self, page_id: str | None = None, limit: int = 25
    ) -> list[dict[str, Any]]:
        """List inline comments on a page or all inline comments.

        Args:
            page_id: Optional page ID to filter by. If None, lists all inline comments.
            limit: Maximum number of results to return (default 25)

        Returns:
            List of comment objects with id, body, author, created/modified dates

        Raises:
            ApiError: If the request fails
        """
        params: dict[str, Any] = {"limit": str(limit), "body-format": "storage"}

        if page_id:
            response = self.client.get(f"/pages/{page_id}/inline-comments", params=params)
        else:
            response = self.client.get("/inline-comments", params=params)

        if response.status_code != 200:
            handle_api_error(response)

        result = cast(dict[str, Any], response.json())
        return cast(list[dict[str, Any]], result.get("results", []))

    def get_inline_comment(self, comment_id: str) -> dict[str, Any]:
        """Get an inline comment by ID.

        Args:
            comment_id: Comment ID

        Returns:
            Comment object with id, body, author, created/modified dates

        Raises:
            ApiError: If the request fails
        """
        response = self.client.get(
            f"/inline-comments/{comment_id}", params={"body-format": "storage"}
        )

        if response.status_code != 200:
            handle_api_error(response)

        return cast(dict[str, Any], response.json())

    def list_page_versions(self, page_id: str, limit: int = 25) -> list[dict[str, Any]]:
        """List all versions of a page.

        Args:
            page_id: Page ID
            limit: Maximum number of results to return (default 25)

        Returns:
            List of version objects with number, message, createdAt, authorId, minorEdit

        Raises:
            ApiError: If the request fails
        """
        params: dict[str, Any] = {"limit": str(limit)}

        response = self.client.get(f"/pages/{page_id}/versions", params=params)

        if response.status_code != 200:
            handle_api_error(response)

        result = cast(dict[str, Any], response.json())
        return cast(list[dict[str, Any]], result.get("results", []))

    def get_page_version(self, page_id: str, version_number: int) -> dict[str, Any]:
        """Get a specific version of a page.

        Args:
            page_id: Page ID
            version_number: Version number to retrieve

        Returns:
            Page data from that version including id, title, body content

        Raises:
            ApiError: If the request fails
        """
        response = self.client.get(
            f"/pages/{page_id}/versions/{version_number}", params={"body-format": "storage"}
        )

        if response.status_code != 200:
            handle_api_error(response)

        return cast(dict[str, Any], response.json())

    def list_tasks(
        self,
        status: str | None = None,
        assigned_to: str | None = None,
        page_id: str | None = None,
        space_id: str | None = None,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """List tasks with optional filters.

        Args:
            status: Filter by status (complete, incomplete)
            assigned_to: Filter by assigned user Account ID
            page_id: Filter by page ID
            space_id: Filter by space ID
            limit: Maximum number of results to return (default 25)

        Returns:
            List of task objects with id, status, body, pageId, assignedTo, etc.

        Raises:
            ApiError: If the request fails
        """
        params: dict[str, Any] = {"limit": str(limit)}
        if status:
            params["status"] = status
        if assigned_to:
            params["assigned-to"] = assigned_to
        if page_id:
            params["page-id"] = page_id
        if space_id:
            params["space-id"] = space_id

        response = self.client.get("/tasks", params=params)

        if response.status_code != 200:
            handle_api_error(response)

        result = cast(dict[str, Any], response.json())
        return cast(list[dict[str, Any]], result.get("results", []))

    def get_task(self, task_id: str) -> dict[str, Any]:
        """Get a task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task data including id, status, body, pageId, assignedTo, etc.

        Raises:
            ApiError: If the request fails
        """
        # Task retrieval requires list with task-id filter
        params = {"task-id": task_id, "limit": "1"}
        response = self.client.get("/tasks", params=params)

        if response.status_code != 200:
            handle_api_error(response)

        result = cast(dict[str, Any], response.json())
        results = cast(list[dict[str, Any]], result.get("results", []))

        if not results:
            raise ApiError(f"Task not found: {task_id}", status_code=404)

        return results[0]

    def update_task(self, task_id: str, status: str) -> dict[str, Any]:
        """Update a task's status.

        Args:
            task_id: Task ID to update
            status: New status (complete or incomplete)

        Returns:
            Updated task data

        Raises:
            ApiError: If the request fails
        """
        payload = {"status": status}

        response = self.client.put(f"/tasks/{task_id}", json=payload)

        if response.status_code != 200:
            handle_api_error(response)

        return cast(dict[str, Any], response.json())

    def get_current_user(self) -> dict[str, Any]:
        """Get the current authenticated user.

        Returns:
            User data including accountId, displayName, etc.

        Raises:
            ApiError: If the request fails
        """
        response = self.client.get("/user/current")

        if response.status_code != 200:
            handle_api_error(response)

        return cast(dict[str, Any], response.json())
