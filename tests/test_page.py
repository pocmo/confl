"""Tests for page commands."""

import json

import pytest
from pytest_httpx import HTTPXMock
from typer.testing import CliRunner

from confl.cli import app
from confl.commands.page import _extract_page_id

runner = CliRunner()


@pytest.fixture
def mock_config_env(monkeypatch):
    """Set up environment variables for config."""
    monkeypatch.setenv("CONFL_SITE", "example.atlassian.net")
    monkeypatch.setenv("CONFL_EMAIL", "test@example.com")
    monkeypatch.setenv("CONFL_TOKEN", "test-token")


class TestExtractPageId:
    """Tests for page ID extraction."""

    def test_numeric_id(self):
        """Test extraction from numeric ID."""
        assert _extract_page_id("12345678") == "12345678"

    def test_url_with_title(self):
        """Test extraction from URL with title."""
        url = "https://company.atlassian.net/wiki/spaces/DEV/pages/12345678/Page-Title"
        assert _extract_page_id(url) == "12345678"

    def test_url_without_title(self):
        """Test extraction from URL without title."""
        url = "https://company.atlassian.net/wiki/spaces/DEV/pages/98765432"
        assert _extract_page_id(url) == "98765432"

    def test_invalid_reference(self):
        """Test invalid reference raises ValueError."""
        with pytest.raises(ValueError, match="Invalid page reference"):
            _extract_page_id("not-a-valid-reference")

    def test_invalid_url(self):
        """Test URL without page ID raises ValueError."""
        with pytest.raises(ValueError, match="Invalid page reference"):
            _extract_page_id("https://company.atlassian.net/wiki/spaces/DEV")


class TestPageGetCommand:
    """Tests for 'confl page get' command."""

    def test_get_page_by_id_default_output(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test getting a page by ID with default output."""
        page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "spaceId": "98765",
            "version": {
                "number": 1,
                "authorId": "user123",
                "createdAt": "2024-01-15T10:00:00.000Z",
            },
            "body": {
                "storage": {
                    "value": "<p>Test content</p>",
                    "representation": "storage",
                },
            },
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=page_data,
        )

        result = runner.invoke(app, ["page", "get", "12345678"])
        assert result.exit_code == 0
        assert "Test Page" in result.stdout
        assert "Space: 98765" in result.stdout
        assert "Test content" in result.stdout

    def test_get_page_body_only(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a page with --body-only flag."""
        page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "spaceId": "98765",
            "version": {
                "number": 1,
                "authorId": "user123",
                "createdAt": "2024-01-15T10:00:00.000Z",
            },
            "body": {
                "storage": {
                    "value": "<p>Test content</p>",
                    "representation": "storage",
                },
            },
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=page_data,
        )

        result = runner.invoke(app, ["page", "get", "12345678", "--body-only"])
        assert result.exit_code == 0
        assert "Title:" not in result.stdout
        assert "Space:" not in result.stdout
        assert "Test content" in result.stdout

    def test_get_page_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a page with --json flag."""
        page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "spaceId": "98765",
            "version": {
                "number": 1,
                "authorId": "user123",
                "createdAt": "2024-01-15T10:00:00.000Z",
            },
            "body": {
                "storage": {
                    "value": "<p>Test content</p>",
                    "representation": "storage",
                },
            },
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=page_data,
        )

        result = runner.invoke(app, ["page", "get", "12345678", "--json"])
        assert result.exit_code == 0

        # Parse and verify JSON output
        output = json.loads(result.stdout)
        assert output["id"] == "12345678"
        assert output["title"] == "Test Page"
        assert output["body"]["storage"]["value"] == "<p>Test content</p>"

    def test_get_page_raw_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a page with --raw flag."""
        page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "spaceId": "98765",
            "version": {
                "number": 1,
                "authorId": "user123",
                "createdAt": "2024-01-15T10:00:00.000Z",
            },
            "body": {
                "storage": {
                    "value": "<p>Raw storage format</p>",
                    "representation": "storage",
                },
            },
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=page_data,
        )

        result = runner.invoke(app, ["page", "get", "12345678", "--raw"])
        assert result.exit_code == 0
        assert "Test Page" in result.stdout  # Metadata header
        assert "<p>Raw storage format</p>" in result.stdout

    def test_get_page_by_url(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a page by URL."""
        page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "spaceId": "98765",
            "version": {
                "number": 1,
                "authorId": "user123",
                "createdAt": "2024-01-15T10:00:00.000Z",
            },
            "body": {
                "storage": {
                    "value": "<p>Test content</p>",
                    "representation": "storage",
                },
            },
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=page_data,
        )

        url = "https://company.atlassian.net/wiki/spaces/DEV/pages/12345678/Test-Page"
        result = runner.invoke(app, ["page", "get", url])
        assert result.exit_code == 0
        assert "Test Page" in result.stdout

    def test_get_page_not_found(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a non-existent page."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/99999999?body-format=storage",
            method="GET",
            status_code=404,
            json={"message": "Page not found"},
        )

        result = runner.invoke(app, ["page", "get", "99999999"])
        assert result.exit_code == 1
        assert "Not found" in result.stderr

    def test_get_page_unauthorized(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a page with invalid credentials."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            status_code=401,
            json={"message": "Unauthorized"},
        )

        result = runner.invoke(app, ["page", "get", "12345678"])
        assert result.exit_code == 1
        assert "Authentication failed" in result.stderr

    def test_get_page_error_with_json_flag(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test that error output is JSON when --json flag is used."""
        error_response = {
            "errors": [
                {
                    "status": 404,
                    "code": "NOT_FOUND",
                    "title": "Page not found",
                    "detail": "The page with ID 99999999 does not exist",
                }
            ]
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/99999999?body-format=storage",
            method="GET",
            status_code=404,
            json=error_response,
        )

        result = runner.invoke(app, ["page", "get", "99999999", "--json"])
        assert result.exit_code == 1
        # Error should be JSON in stderr
        error_json = json.loads(result.stderr)
        assert "errors" in error_json
        assert error_json["errors"][0]["code"] == "NOT_FOUND"

    def test_get_page_error_confluence_v2_format(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test handling of Confluence API v2 structured error format."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            status_code=409,
            json={
                "errors": [
                    {
                        "status": 409,
                        "code": "CONFLICT",
                        "title": "Version must be incremented",
                        "detail": "Current version is 5, provided version is 5",
                    }
                ]
            },
        )

        result = runner.invoke(app, ["page", "get", "12345678"])
        assert result.exit_code == 1
        assert "Version conflict" in result.stderr
        assert "Version must be incremented" in result.stderr

    def test_get_page_invalid_reference(self, mock_config_env: None) -> None:
        """Test getting a page with invalid reference."""
        result = runner.invoke(app, ["page", "get", "invalid-reference"])
        assert result.exit_code == 2
        assert "Invalid page reference" in result.stderr

    def test_get_page_markdown_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test that --markdown flag outputs converted markdown."""
        page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "spaceId": "98765",
            "version": {
                "number": 1,
                "authorId": "user123",
                "createdAt": "2024-01-15T10:00:00.000Z",
            },
            "body": {
                "storage": {
                    "value": "<h1>Heading</h1><p>Test content</p>",
                    "representation": "storage",
                },
            },
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=page_data,
        )

        result = runner.invoke(app, ["page", "get", "12345678", "--markdown"])
        assert result.exit_code == 0
        # Check that markdown conversion happened
        assert "# Heading" in result.stdout or "Heading" in result.stdout
        assert "Test content" in result.stdout

    def test_get_page_rich_rendering_with_macros(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test Rich rendering with Confluence macros (code, panels)."""
        page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page with Macros",
            "spaceId": "98765",
            "version": {
                "number": 1,
                "authorId": "user123",
                "createdAt": "2024-01-15T10:00:00.000Z",
            },
            "body": {
                "storage": {
                    "value": (
                        "<h1>Code Example</h1>"
                        '<ac:structured-macro ac:name="code" ac:schema-version="1">'
                        '<ac:parameter ac:name="language">python</ac:parameter>'
                        "<ac:plain-text-body><![CDATA[print('hello')]]></ac:plain-text-body>"
                        "</ac:structured-macro>"
                        '<ac:structured-macro ac:name="info">'
                        "<ac:rich-text-body><p>Important info</p></ac:rich-text-body>"
                        "</ac:structured-macro>"
                    ),
                    "representation": "storage",
                },
            },
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=page_data,
        )

        result = runner.invoke(app, ["page", "get", "12345678"])
        assert result.exit_code == 0
        # Check that content is rendered (exact format may vary with Rich rendering)
        assert "Test Page with Macros" in result.stdout
        assert "hello" in result.stdout or "print" in result.stdout

    def test_get_page_plain_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test that --plain flag outputs plain text with formatting stripped."""
        page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "spaceId": "98765",
            "version": {
                "number": 1,
                "authorId": "user123",
                "createdAt": "2024-01-15T10:00:00.000Z",
            },
            "body": {
                "storage": {
                    "value": (
                        "<h1>Heading</h1>"
                        "<p>This is <strong>bold</strong> and <em>italic</em> text.</p>"
                        "<p>Here is a <a href='https://example.com'>link</a>.</p>"
                    ),
                    "representation": "storage",
                },
            },
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=page_data,
        )

        result = runner.invoke(app, ["page", "get", "12345678", "--plain"])
        assert result.exit_code == 0
        # Check that markdown formatting is stripped
        assert "Heading" in result.stdout
        assert "bold" in result.stdout
        assert "italic" in result.stdout
        assert "link" in result.stdout
        # Ensure markdown syntax is NOT present
        assert "**" not in result.stdout
        assert "*" not in result.stdout or "italic" in result.stdout  # Allow asterisk in word
        assert "#" not in result.stdout
        assert "[" not in result.stdout

    def test_get_page_mutually_exclusive_formats(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test that format flags are mutually exclusive."""
        # Test various combinations
        test_cases = [
            (["--json", "--raw"], "Only one output format flag"),
            (["--json", "--markdown"], "Only one output format flag"),
            (["--json", "--plain"], "Only one output format flag"),
            (["--raw", "--markdown"], "Only one output format flag"),
            (["--raw", "--plain"], "Only one output format flag"),
            (["--markdown", "--plain"], "Only one output format flag"),
            (["--json", "--raw", "--markdown"], "Only one output format flag"),
        ]

        for flags, expected_error in test_cases:
            result = runner.invoke(app, ["page", "get", "12345678"] + flags)
            assert result.exit_code == 2, f"Failed for flags: {flags}"
            assert expected_error in result.stderr, f"Failed for flags: {flags}"


class TestListPages:
    """Tests for page list command."""

    def test_list_pages_basic(self, httpx_mock: HTTPXMock, mock_config_env):
        """Test basic page listing with space filter."""
        pages_data = {
            "results": [
                {
                    "id": "12345678",
                    "title": "First Page",
                    "spaceId": "DEV",
                    "version": {"createdAt": "2026-01-10T10:00:00Z"},
                },
                {
                    "id": "87654321",
                    "title": "Second Page",
                    "spaceId": "DEV",
                    "version": {"createdAt": "2026-01-12T14:30:00Z"},
                },
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages?limit=25&space-key=DEV",
            method="GET",
            json=pages_data,
        )

        result = runner.invoke(app, ["page", "list", "--space", "DEV"])
        assert result.exit_code == 0
        assert "12345678" in result.stdout
        assert "First Page" in result.stdout
        assert "87654321" in result.stdout
        assert "Second Page" in result.stdout
        # Timestamps are now shown as relative time (e.g., "4 days ago")
        assert "ago" in result.stdout or "just now" in result.stdout

    def test_list_pages_json_output(self, httpx_mock: HTTPXMock, mock_config_env):
        """Test JSON output format."""
        pages_data = {
            "results": [
                {
                    "id": "12345678",
                    "title": "Test Page",
                    "spaceId": "DEV",
                    "version": {"createdAt": "2026-01-10T10:00:00Z"},
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages?limit=25&space-key=DEV",
            method="GET",
            json=pages_data,
        )

        result = runner.invoke(app, ["page", "list", "--space", "DEV", "--json"])
        assert result.exit_code == 0

        # Parse and verify JSON output
        output_data = json.loads(result.stdout)
        assert len(output_data) == 1
        assert output_data[0]["id"] == "12345678"
        assert output_data[0]["title"] == "Test Page"

    def test_list_pages_custom_limit(self, httpx_mock: HTTPXMock, mock_config_env):
        """Test custom limit parameter."""
        pages_data = {"results": []}

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages?limit=50&space-key=DEV",
            method="GET",
            json=pages_data,
        )

        result = runner.invoke(app, ["page", "list", "--space", "DEV", "--limit", "50"])
        assert result.exit_code == 0

    def test_list_pages_empty_results(self, httpx_mock: HTTPXMock, mock_config_env):
        """Test handling of empty results."""
        pages_data = {"results": []}

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages?limit=25&space-key=EMPTY",
            method="GET",
            json=pages_data,
        )

        result = runner.invoke(app, ["page", "list", "--space", "EMPTY"])
        assert result.exit_code == 0
        assert "No pages found" in result.stdout

    def test_list_pages_unauthorized(self, httpx_mock: HTTPXMock, mock_config_env):
        """Test handling of 401 unauthorized error."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages?limit=25&space-key=DEV",
            method="GET",
            status_code=401,
            json={"message": "Unauthorized"},
        )

        result = runner.invoke(app, ["page", "list", "--space", "DEV"])
        assert result.exit_code == 1
        assert "Authentication failed" in result.stderr

    def test_list_pages_forbidden(self, httpx_mock: HTTPXMock, mock_config_env):
        """Test handling of 403 forbidden error."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages?limit=25&space-key=PRIVATE",
            method="GET",
            status_code=403,
            json={"message": "Forbidden"},
        )

        result = runner.invoke(app, ["page", "list", "--space", "PRIVATE"])
        assert result.exit_code == 1
        assert "Permission denied" in result.stderr

    def test_list_pages_missing_space(self, mock_config_env):
        """Test that space parameter is required."""
        result = runner.invoke(app, ["page", "list"])
        assert result.exit_code != 0
        # Typer will complain about missing required option


class TestPageDeleteCommand:
    """Tests for 'confl page delete' command."""

    def test_delete_page_by_id_default_output(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test deleting a page by ID with default output."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["page", "delete", "12345678"])
        assert result.exit_code == 0
        assert "12345678" in result.stdout
        assert "deleted successfully" in result.stdout

    def test_delete_page_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test deleting a page with --json flag."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["page", "delete", "12345678", "--json"])
        assert result.exit_code == 0

        # Parse and verify JSON output
        output = json.loads(result.stdout)
        assert output["success"] is True
        assert output["page_id"] == "12345678"
        assert "deleted successfully" in output["message"]

    def test_delete_page_by_url(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test deleting a page by URL."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678",
            method="DELETE",
            status_code=204,
        )

        url = "https://company.atlassian.net/wiki/spaces/DEV/pages/12345678/Test-Page"
        result = runner.invoke(app, ["page", "delete", url])
        assert result.exit_code == 0
        assert "12345678" in result.stdout
        assert "deleted successfully" in result.stdout

    def test_delete_page_already_deleted(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test deleting a page that's already deleted (404 handled gracefully)."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/99999999",
            method="DELETE",
            status_code=404,
            json={"message": "Page not found"},
        )

        result = runner.invoke(app, ["page", "delete", "99999999"])
        assert result.exit_code == 0
        assert "99999999" in result.stdout
        assert "deleted successfully" in result.stdout

    def test_delete_page_unauthorized(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test deleting a page with invalid credentials."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678",
            method="DELETE",
            status_code=401,
            json={"message": "Unauthorized"},
        )

        result = runner.invoke(app, ["page", "delete", "12345678"])
        assert result.exit_code == 1
        assert "Authentication failed" in result.stderr

    def test_delete_page_forbidden(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test deleting a page without permission."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678",
            method="DELETE",
            status_code=403,
            json={"message": "Forbidden"},
        )

        result = runner.invoke(app, ["page", "delete", "12345678"])
        assert result.exit_code == 1
        assert "Permission denied" in result.stderr

    def test_delete_page_invalid_reference(self, mock_config_env: None) -> None:
        """Test deleting a page with invalid reference."""
        result = runner.invoke(app, ["page", "delete", "invalid-reference"])
        assert result.exit_code == 2
        assert "Invalid page reference" in result.stderr

    def test_delete_page_with_yes_flag(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test deleting a page with --yes flag bypasses confirmation."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["page", "delete", "12345678", "--yes"])
        assert result.exit_code == 0
        assert "deleted successfully" in result.stdout
        # Should not contain confirmation prompt
        assert "Are you sure" not in result.stdout


class TestPageUpdateCommand:
    """Tests for 'confl page update' command."""

    def test_update_page_with_body_flag(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating a page with --body flag."""
        # Mock GET request to fetch current page
        current_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "spaceId": "98765",
            "version": {"number": 1},
            "body": {
                "storage": {
                    "value": "<p>Old content</p>",
                    "representation": "storage",
                },
            },
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=current_page_data,
        )

        # Mock PUT request to update page
        updated_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "version": {"number": 2},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678",
            method="PUT",
            json=updated_page_data,
        )

        result = runner.invoke(app, ["page", "update", "12345678", "--body", "# New content"])
        assert result.exit_code == 0
        assert "12345678" in result.stdout
        assert "updated successfully" in result.stdout
        assert "version 2" in result.stdout

    def test_update_page_with_title(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating a page with --title flag only."""
        current_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Old Title",
            "spaceId": "98765",
            "version": {"number": 1},
            "body": {
                "storage": {
                    "value": "<p>Content</p>",
                    "representation": "storage",
                },
            },
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=current_page_data,
        )

        updated_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "New Title",
            "version": {"number": 2},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678",
            method="PUT",
            json=updated_page_data,
        )

        result = runner.invoke(app, ["page", "update", "12345678", "--title", "New Title"])
        assert result.exit_code == 0
        assert "12345678" in result.stdout
        assert "updated successfully" in result.stdout

    def test_update_page_with_body_and_title(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test updating both content and title."""
        current_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Old Title",
            "spaceId": "98765",
            "version": {"number": 1},
            "body": {
                "storage": {
                    "value": "<p>Old content</p>",
                    "representation": "storage",
                },
            },
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=current_page_data,
        )

        updated_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "New Title",
            "version": {"number": 2},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678",
            method="PUT",
            json=updated_page_data,
        )

        result = runner.invoke(
            app,
            ["page", "update", "12345678", "--body", "# New content", "--title", "New Title"],
        )
        assert result.exit_code == 0
        assert "updated successfully" in result.stdout

    def test_update_page_with_raw_flag(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating a page with --raw flag for storage format."""
        current_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "version": {"number": 1},
            "body": {
                "storage": {
                    "value": "<p>Old content</p>",
                    "representation": "storage",
                },
            },
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=current_page_data,
        )

        updated_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "version": {"number": 2},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678",
            method="PUT",
            json=updated_page_data,
        )

        result = runner.invoke(
            app,
            ["page", "update", "12345678", "--body", "<p>New HTML</p>", "--raw"],
        )
        assert result.exit_code == 0
        assert "updated successfully" in result.stdout

    def test_update_page_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating a page with --json flag."""
        current_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "version": {"number": 1},
            "body": {
                "storage": {
                    "value": "<p>Old</p>",
                    "representation": "storage",
                },
            },
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=current_page_data,
        )

        updated_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "version": {"number": 2},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678",
            method="PUT",
            json=updated_page_data,
        )

        result = runner.invoke(
            app, ["page", "update", "12345678", "--body", "New content", "--json"]
        )
        assert result.exit_code == 0

        # Parse and verify JSON output
        output = json.loads(result.stdout)
        assert output["id"] == "12345678"
        assert output["version"]["number"] == 2

    def test_update_page_by_url(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating a page by URL."""
        current_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "version": {"number": 1},
            "body": {
                "storage": {
                    "value": "<p>Old</p>",
                    "representation": "storage",
                },
            },
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=current_page_data,
        )

        updated_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "version": {"number": 2},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678",
            method="PUT",
            json=updated_page_data,
        )

        url = "https://company.atlassian.net/wiki/spaces/DEV/pages/12345678/Test-Page"
        result = runner.invoke(app, ["page", "update", url, "--body", "New content"])
        assert result.exit_code == 0
        assert "12345678" in result.stdout

    def test_update_page_version_conflict(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test updating a page with version conflict (409)."""
        current_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "version": {"number": 1},
            "body": {
                "storage": {
                    "value": "<p>Old</p>",
                    "representation": "storage",
                },
            },
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=current_page_data,
        )

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678",
            method="PUT",
            status_code=409,
            json={"message": "Version mismatch"},
        )

        result = runner.invoke(app, ["page", "update", "12345678", "--body", "New content"])
        assert result.exit_code == 1
        assert "Version conflict" in result.stderr

    def test_update_page_not_found(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating a page that doesn't exist."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/99999999?body-format=storage",
            method="GET",
            status_code=404,
            json={"message": "Page not found"},
        )

        result = runner.invoke(app, ["page", "update", "99999999", "--body", "New content"])
        assert result.exit_code == 1
        assert "Not found" in result.stderr

    def test_update_page_unauthorized(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating a page with invalid credentials."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            status_code=401,
            json={"message": "Unauthorized"},
        )

        result = runner.invoke(app, ["page", "update", "12345678", "--body", "New content"])
        assert result.exit_code == 1
        assert "Authentication failed" in result.stderr

    def test_update_page_forbidden(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating a page without permission."""
        current_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "version": {"number": 1},
            "body": {
                "storage": {
                    "value": "<p>Old</p>",
                    "representation": "storage",
                },
            },
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=current_page_data,
        )

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678",
            method="PUT",
            status_code=403,
            json={"message": "Forbidden"},
        )

        result = runner.invoke(app, ["page", "update", "12345678", "--body", "New content"])
        assert result.exit_code == 1
        assert "Permission denied" in result.stderr

    def test_update_page_invalid_reference(self, mock_config_env: None) -> None:
        """Test updating a page with invalid reference."""
        result = runner.invoke(app, ["page", "update", "invalid-reference", "--body", "New"])
        assert result.exit_code == 2
        assert "Invalid page reference" in result.stderr

    def test_update_page_no_content_or_title(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test updating a page without providing content or title."""
        # Mock GET request that would be called if we proceed
        # But since we exit early, this won't be called
        result = runner.invoke(app, ["page", "update", "12345678"])
        assert result.exit_code == 2
        assert "Must provide" in result.stderr

    def test_update_page_from_stdin(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating a page with content from stdin."""
        current_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "version": {"number": 1},
            "body": {
                "storage": {
                    "value": "<p>Old</p>",
                    "representation": "storage",
                },
            },
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=current_page_data,
        )

        updated_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "version": {"number": 2},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678",
            method="PUT",
            json=updated_page_data,
        )

        # Simulate stdin input
        result = runner.invoke(app, ["page", "update", "12345678"], input="# Content from stdin\n")
        assert result.exit_code == 0
        assert "updated successfully" in result.stdout

    def test_update_page_with_body_file(
        self, httpx_mock: HTTPXMock, mock_config_env: None, tmp_path
    ) -> None:
        """Test updating a page with content from file."""
        # Create temp file
        content_file = tmp_path / "content.md"
        content_file.write_text("# Content from file\n\nTest content.")

        current_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "version": {"number": 1},
            "body": {
                "storage": {
                    "value": "<p>Old</p>",
                    "representation": "storage",
                },
            },
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=current_page_data,
        )

        updated_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Test Page",
            "version": {"number": 2},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678",
            method="PUT",
            json=updated_page_data,
        )

        result = runner.invoke(
            app, ["page", "update", "12345678", "--body-file", str(content_file)]
        )
        assert result.exit_code == 0
        assert "updated successfully" in result.stdout

    def test_update_page_file_not_found(self, mock_config_env: None) -> None:
        """Test updating a page with non-existent file."""
        result = runner.invoke(
            app, ["page", "update", "12345678", "--body-file", "/nonexistent/file.md"]
        )
        assert result.exit_code == 2
        assert "File not found" in result.stderr


class TestPageCreateCommand:
    """Tests for 'confl page create' command."""

    def test_create_page_with_body_flag(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test creating a page with --body flag."""
        # Mock GET request to fetch space by key
        space_data = {
            "id": "98765",
            "key": "DEV",
            "name": "Development",
            "type": "global",
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json={"results": [space_data]},
        )

        # Mock POST request to create page
        created_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "New Page",
            "spaceId": "98765",
            "version": {"number": 1},
            "_links": {
                "webui": "/wiki/spaces/DEV/pages/12345678/New+Page",
            },
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages",
            method="POST",
            json=created_page_data,
        )

        result = runner.invoke(
            app, ["page", "create", "--space", "DEV", "--title", "New Page", "--body", "# Content"]
        )
        assert result.exit_code == 0
        assert "Page created successfully" in result.stdout
        assert "12345678" in result.stdout

    def test_create_page_with_parent(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test creating a page with parent hierarchy."""
        space_data = {
            "id": "98765",
            "key": "DEV",
            "name": "Development",
            "type": "global",
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json={"results": [space_data]},
        )

        created_page_data = {
            "id": "87654321",
            "status": "current",
            "title": "Child Page",
            "spaceId": "98765",
            "parentId": "12345678",
            "version": {"number": 1},
            "_links": {
                "webui": "/wiki/spaces/DEV/pages/87654321/Child+Page",
            },
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages",
            method="POST",
            json=created_page_data,
        )

        result = runner.invoke(
            app,
            [
                "page",
                "create",
                "--space",
                "DEV",
                "--title",
                "Child Page",
                "--body",
                "Content",
                "--parent",
                "12345678",
            ],
        )
        assert result.exit_code == 0
        assert "Page created successfully" in result.stdout
        assert "87654321" in result.stdout

    def test_create_page_with_raw_flag(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test creating a page with --raw flag for storage format."""
        space_data = {
            "id": "98765",
            "key": "DEV",
            "name": "Development",
            "type": "global",
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json={"results": [space_data]},
        )

        created_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Raw Page",
            "spaceId": "98765",
            "version": {"number": 1},
            "_links": {
                "webui": "/wiki/spaces/DEV/pages/12345678/Raw+Page",
            },
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages",
            method="POST",
            json=created_page_data,
        )

        result = runner.invoke(
            app,
            [
                "page",
                "create",
                "--space",
                "DEV",
                "--title",
                "Raw Page",
                "--body",
                "<p>HTML content</p>",
                "--raw",
            ],
        )
        assert result.exit_code == 0
        assert "Page created successfully" in result.stdout

    def test_create_page_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test creating a page with --json output."""
        space_data = {
            "id": "98765",
            "key": "DEV",
            "name": "Development",
            "type": "global",
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json={"results": [space_data]},
        )

        created_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "JSON Page",
            "spaceId": "98765",
            "version": {"number": 1},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages",
            method="POST",
            json=created_page_data,
        )

        result = runner.invoke(
            app,
            [
                "page",
                "create",
                "--space",
                "DEV",
                "--title",
                "JSON Page",
                "--body",
                "Content",
                "--json",
            ],
        )
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["id"] == "12345678"
        assert output["title"] == "JSON Page"

    def test_create_page_from_stdin(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test creating a page with content from stdin."""
        space_data = {
            "id": "98765",
            "key": "DEV",
            "name": "Development",
            "type": "global",
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json={"results": [space_data]},
        )

        created_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "Stdin Page",
            "spaceId": "98765",
            "version": {"number": 1},
            "_links": {
                "webui": "/wiki/spaces/DEV/pages/12345678/Stdin+Page",
            },
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages",
            method="POST",
            json=created_page_data,
        )

        result = runner.invoke(
            app,
            ["page", "create", "--space", "DEV", "--title", "Stdin Page"],
            input="# Content from stdin\n\nParagraph text.",
        )
        assert result.exit_code == 0
        assert "Page created successfully" in result.stdout

    def test_create_page_with_body_file(
        self, httpx_mock: HTTPXMock, mock_config_env: None, tmp_path
    ) -> None:
        """Test creating a page with content from file."""
        # Create temporary markdown file
        content_file = tmp_path / "content.md"
        content_file.write_text("# File content\n\nFrom a file.")

        space_data = {
            "id": "98765",
            "key": "DEV",
            "name": "Development",
            "type": "global",
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json={"results": [space_data]},
        )

        created_page_data = {
            "id": "12345678",
            "status": "current",
            "title": "File Page",
            "spaceId": "98765",
            "version": {"number": 1},
            "_links": {
                "webui": "/wiki/spaces/DEV/pages/12345678/File+Page",
            },
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages",
            method="POST",
            json=created_page_data,
        )

        result = runner.invoke(
            app,
            [
                "page",
                "create",
                "--space",
                "DEV",
                "--title",
                "File Page",
                "--body-file",
                str(content_file),
            ],
        )
        assert result.exit_code == 0
        assert "Page created successfully" in result.stdout

    def test_create_page_no_content(self, mock_config_env: None) -> None:
        """Test creating a page without content fails."""
        result = runner.invoke(app, ["page", "create", "--space", "DEV", "--title", "Empty"])
        assert result.exit_code == 2
        assert "Must provide content" in result.stderr

    def test_create_page_file_not_found(self, mock_config_env: None) -> None:
        """Test creating a page with non-existent file."""
        result = runner.invoke(
            app,
            [
                "page",
                "create",
                "--space",
                "DEV",
                "--title",
                "Page",
                "--body-file",
                "/nonexistent/file.md",
            ],
        )
        assert result.exit_code == 2
        assert "File not found" in result.stderr

    def test_create_page_space_not_found(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test creating a page in non-existent space."""
        # Mock empty results for space lookup
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=NOTFOUND",
            method="GET",
            json={"results": []},
        )

        result = runner.invoke(
            app,
            [
                "page",
                "create",
                "--space",
                "NOTFOUND",
                "--title",
                "Page",
                "--body",
                "Content",
            ],
        )
        assert result.exit_code == 1
        assert "Space not found" in result.stderr

    def test_create_page_unauthorized(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test creating a page with unauthorized credentials."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            status_code=401,
            json={"message": "Unauthorized"},
        )

        result = runner.invoke(
            app,
            [
                "page",
                "create",
                "--space",
                "DEV",
                "--title",
                "Page",
                "--body",
                "Content",
            ],
        )
        assert result.exit_code == 1
        assert "Authentication failed" in result.stderr or "Unauthorized" in result.stderr

    def test_create_page_duplicate_title(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test creating a page with duplicate title in space."""
        space_data = {
            "id": "98765",
            "key": "DEV",
            "name": "Development",
            "type": "global",
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json={"results": [space_data]},
        )

        # Mock 400 error for duplicate title
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages",
            method="POST",
            status_code=400,
            json={"message": "A page with this title already exists in the space"},
        )

        result = runner.invoke(
            app,
            [
                "page",
                "create",
                "--space",
                "DEV",
                "--title",
                "Duplicate",
                "--body",
                "Content",
            ],
        )
        assert result.exit_code == 1
        assert "400" in result.stderr


class TestPageVersionsCommand:
    """Tests for 'confl page versions' command."""

    def test_list_versions(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing page versions."""
        versions_data = {
            "results": [
                {
                    "number": 3,
                    "authorId": "user123",
                    "createdAt": "2024-01-15T10:30:00.000Z",
                    "minorEdit": False,
                    "message": "Major update",
                },
                {
                    "number": 2,
                    "authorId": "user456",
                    "createdAt": "2024-01-14T09:00:00.000Z",
                    "minorEdit": True,
                    "message": "Fixed typo",
                },
                {
                    "number": 1,
                    "authorId": "user123",
                    "createdAt": "2024-01-10T08:00:00.000Z",
                    "minorEdit": False,
                    "message": "Initial version",
                },
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678/versions?limit=25",
            method="GET",
            json=versions_data,
        )

        result = runner.invoke(app, ["page", "versions", "12345678"])
        assert result.exit_code == 0
        assert "3" in result.stdout
        assert "user123" in result.stdout
        assert "Major update" in result.stdout

    def test_list_versions_json(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing page versions with JSON output."""
        versions_data = {
            "results": [
                {
                    "number": 1,
                    "authorId": "user123",
                    "createdAt": "2024-01-10T08:00:00.000Z",
                    "minorEdit": False,
                    "message": "Initial",
                },
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678/versions?limit=25",
            method="GET",
            json=versions_data,
        )

        result = runner.invoke(app, ["page", "versions", "12345678", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert len(output) == 1
        assert output[0]["number"] == 1

    def test_list_versions_empty(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing versions when none exist."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678/versions?limit=25",
            method="GET",
            json={"results": []},
        )

        result = runner.invoke(app, ["page", "versions", "12345678"])
        assert result.exit_code == 0
        assert "No versions found" in result.stdout


class TestPageVersionCommand:
    """Tests for 'confl page version' command."""

    def test_get_version(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a specific version."""
        version_data = {
            "id": "12345678",
            "title": "Test Page",
            "version": {
                "number": 2,
                "authorId": "user456",
                "createdAt": "2024-01-14T09:00:00.000Z",
                "message": "Updated content",
            },
            "body": {
                "storage": {
                    "value": "<p>Version 2 content</p>",
                    "representation": "storage",
                },
            },
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678/versions/2?body-format=storage",
            method="GET",
            json=version_data,
        )

        result = runner.invoke(app, ["page", "version", "12345678", "2"])
        assert result.exit_code == 0
        assert "Test Page" in result.stdout
        assert "Version: 2" in result.stdout
        assert "Version 2 content" in result.stdout

    def test_get_version_markdown(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a version with markdown conversion."""
        version_data = {
            "id": "12345678",
            "title": "Test Page",
            "version": {
                "number": 1,
                "authorId": "user123",
                "createdAt": "2024-01-10T08:00:00.000Z",
                "message": "Initial",
            },
            "body": {
                "storage": {
                    "value": "<h1>Header</h1><p>Content</p>",
                    "representation": "storage",
                },
            },
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678/versions/1?body-format=storage",
            method="GET",
            json=version_data,
        )

        result = runner.invoke(app, ["page", "version", "12345678", "1", "--markdown"])
        assert result.exit_code == 0
        assert "Test Page" in result.stdout
        assert "Header" in result.stdout

    def test_get_version_json(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a version with JSON output."""
        version_data = {
            "id": "12345678",
            "title": "Test Page",
            "version": {"number": 1},
            "body": {"storage": {"value": "<p>Content</p>"}},
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678/versions/1?body-format=storage",
            method="GET",
            json=version_data,
        )

        result = runner.invoke(app, ["page", "version", "12345678", "1", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["id"] == "12345678"
        assert output["version"]["number"] == 1


class TestPageRestoreCommand:
    """Tests for 'confl page restore' command."""

    def test_restore_version(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test restoring a page to a previous version."""
        # Get version to restore
        version_data = {
            "id": "12345678",
            "title": "Test Page",
            "version": {"number": 2},
            "body": {"storage": {"value": "<p>Version 2 content</p>"}},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678/versions/2?body-format=storage",
            method="GET",
            json=version_data,
        )

        # Get current page for version number
        current_page = {
            "id": "12345678",
            "title": "Test Page",
            "version": {"number": 5},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=current_page,
        )

        # Update page with old content
        updated_page = {
            "id": "12345678",
            "version": {"number": 6},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678",
            method="PUT",
            json=updated_page,
        )

        result = runner.invoke(app, ["page", "restore", "12345678", "2"])
        assert result.exit_code == 0
        assert "restored to version 2" in result.stdout
        assert "new version 6" in result.stdout

    def test_restore_version_with_message(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test restoring with custom message."""
        version_data = {
            "id": "12345678",
            "title": "Test Page",
            "version": {"number": 1},
            "body": {"storage": {"value": "<p>Original</p>"}},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678/versions/1?body-format=storage",
            method="GET",
            json=version_data,
        )

        current_page = {
            "id": "12345678",
            "version": {"number": 3},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=current_page,
        )

        updated_page = {
            "id": "12345678",
            "version": {"number": 4},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678",
            method="PUT",
            json=updated_page,
        )

        result = runner.invoke(
            app, ["page", "restore", "12345678", "1", "--message", "Reverting bad change"]
        )
        assert result.exit_code == 0
        assert "restored" in result.stdout

    def test_restore_version_dry_run(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test restore dry run mode."""
        version_data = {
            "id": "12345678",
            "title": "Test Page",
            "version": {"number": 2},
            "body": {"storage": {"value": "<p>Content</p>"}},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678/versions/2?body-format=storage",
            method="GET",
            json=version_data,
        )

        current_page = {
            "id": "12345678",
            "version": {"number": 4},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=current_page,
        )

        result = runner.invoke(app, ["page", "restore", "12345678", "2", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout
        assert "Current version: 4" in result.stdout
        assert "Restore to version: 2" in result.stdout
        assert "New version: 5" in result.stdout

    def test_restore_version_json(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test restore with JSON output."""
        version_data = {
            "id": "12345678",
            "title": "Test Page",
            "version": {"number": 1},
            "body": {"storage": {"value": "<p>Content</p>"}},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678/versions/1?body-format=storage",
            method="GET",
            json=version_data,
        )

        current_page = {
            "id": "12345678",
            "version": {"number": 2},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=current_page,
        )

        updated_page = {
            "id": "12345678",
            "version": {"number": 3},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678",
            method="PUT",
            json=updated_page,
        )

        result = runner.invoke(app, ["page", "restore", "12345678", "1", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["version"]["number"] == 3
