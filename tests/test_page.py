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
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage%2Catlas_doc_format",
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
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage%2Catlas_doc_format",
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
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage%2Catlas_doc_format",
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
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage%2Catlas_doc_format",
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
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage%2Catlas_doc_format",
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
            url="https://example.atlassian.net/wiki/api/v2/pages/99999999?body-format=storage%2Catlas_doc_format",
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
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage%2Catlas_doc_format",
            method="GET",
            status_code=401,
            json={"message": "Unauthorized"},
        )

        result = runner.invoke(app, ["page", "get", "12345678"])
        assert result.exit_code == 1
        assert "Authentication failed" in result.stderr

    def test_get_page_invalid_reference(self, mock_config_env: None) -> None:
        """Test getting a page with invalid reference."""
        result = runner.invoke(app, ["page", "get", "invalid-reference"])
        assert result.exit_code == 2
        assert "Invalid page reference" in result.stderr

    def test_get_page_markdown_warning(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test that --markdown flag shows warning (not yet implemented)."""
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
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage%2Catlas_doc_format",
            method="GET",
            json=page_data,
        )

        result = runner.invoke(app, ["page", "get", "12345678", "--markdown"])
        assert result.exit_code == 0
        assert "not yet implemented" in result.stderr.lower()


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
        assert "2026-01-10" in result.stdout
        assert "2026-01-12" in result.stdout

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
