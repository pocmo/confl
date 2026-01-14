"""Tests for label commands."""

import json

import pytest
from pytest_httpx import HTTPXMock
from typer.testing import CliRunner

from confl.cli import app

runner = CliRunner()


@pytest.fixture
def mock_config_env(monkeypatch):
    """Set up environment variables for config."""
    monkeypatch.setenv("CONFL_SITE", "example.atlassian.net")
    monkeypatch.setenv("CONFL_EMAIL", "test@example.com")
    monkeypatch.setenv("CONFL_TOKEN", "test-token")


class TestLabelListCommand:
    """Tests for 'confl label list' command."""

    def test_list_labels_default(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing labels with default output."""
        labels_data = {
            "results": [
                {"id": "1", "name": "architecture", "prefix": "global"},
                {"id": "2", "name": "design", "prefix": "global"},
                {"id": "3", "name": "docs", "prefix": "global"},
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/123456/labels?limit=25",
            method="GET",
            json=labels_data,
        )

        result = runner.invoke(app, ["label", "list", "--page", "123456"])
        assert result.exit_code == 0
        assert "architecture" in result.stdout
        assert "design" in result.stdout
        assert "docs" in result.stdout

    def test_list_labels_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing labels with JSON output."""
        labels_data = {
            "results": [
                {"id": "1", "name": "test-label", "prefix": "global"},
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/123456/labels?limit=25",
            method="GET",
            json=labels_data,
        )

        result = runner.invoke(app, ["label", "list", "--page", "123456", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert len(output) == 1
        assert output[0]["name"] == "test-label"

    def test_list_labels_empty(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing labels when none exist."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/123456/labels?limit=25",
            method="GET",
            json={"results": []},
        )

        result = runner.invoke(app, ["label", "list", "--page", "123456"])
        assert result.exit_code == 0
        assert "No labels found" in result.stdout

    def test_list_labels_with_url(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing labels with page URL instead of ID."""
        labels_data = {
            "results": [
                {"id": "1", "name": "architecture", "prefix": "global"},
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/123456/labels?limit=25",
            method="GET",
            json=labels_data,
        )

        result = runner.invoke(
            app,
            [
                "label",
                "list",
                "--page",
                "https://example.atlassian.net/wiki/spaces/DEV/pages/123456/Test",
            ],
        )
        assert result.exit_code == 0
        assert "architecture" in result.stdout

    def test_list_labels_page_not_found(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing labels for non-existent page."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/999999/labels?limit=25",
            method="GET",
            status_code=404,
            json={"errors": [{"status": 404, "title": "Not found", "detail": "Page not found"}]},
        )

        result = runner.invoke(app, ["label", "list", "--page", "999999"])
        assert result.exit_code == 1
        assert "Not found" in result.stderr


class TestLabelAddCommand:
    """Tests for 'confl label add' command."""

    def test_add_single_label(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test adding a single label to a page."""
        v1_response = {
            "results": [
                {"id": "1", "name": "new-label", "prefix": "global"},
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/content/123456/label",
            method="POST",
            json=v1_response,
        )

        result = runner.invoke(app, ["label", "add", "--page", "123456", "new-label"])
        assert result.exit_code == 0
        assert "Added 1 label(s)" in result.stdout
        assert "new-label" in result.stdout

    def test_add_multiple_labels(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test adding multiple labels to a page."""
        v1_response = {
            "results": [
                {"id": "1", "name": "label1", "prefix": "global"},
                {"id": "2", "name": "label2", "prefix": "global"},
                {"id": "3", "name": "label3", "prefix": "global"},
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/content/123456/label",
            method="POST",
            json=v1_response,
        )

        result = runner.invoke(
            app, ["label", "add", "--page", "123456", "label1", "label2", "label3"]
        )
        assert result.exit_code == 0
        assert "Added 3 label(s)" in result.stdout
        assert "label1" in result.stdout
        assert "label2" in result.stdout
        assert "label3" in result.stdout

    def test_add_label_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test adding labels with JSON output."""
        v1_response = {
            "results": [
                {"id": "1", "name": "test-label", "prefix": "global"},
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/content/123456/label",
            method="POST",
            json=v1_response,
        )

        result = runner.invoke(app, ["label", "add", "--page", "123456", "test-label", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert len(output) == 1
        assert output[0]["name"] == "test-label"

    def test_add_label_with_url(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test adding label with page URL instead of ID."""
        v1_response = {
            "results": [
                {"id": "1", "name": "new-label", "prefix": "global"},
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/content/123456/label",
            method="POST",
            json=v1_response,
        )

        result = runner.invoke(
            app,
            [
                "label",
                "add",
                "--page",
                "https://example.atlassian.net/wiki/spaces/DEV/pages/123456/Test",
                "new-label",
            ],
        )
        assert result.exit_code == 0
        assert "Added 1 label(s)" in result.stdout

    def test_add_label_page_not_found(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test adding label to non-existent page."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/content/999999/label",
            method="POST",
            status_code=404,
            json={"message": "Page not found"},
        )

        result = runner.invoke(app, ["label", "add", "--page", "999999", "test-label"])
        assert result.exit_code == 1
        assert "Error" in result.stderr


class TestLabelRemoveCommand:
    """Tests for 'confl label remove' command."""

    def test_remove_label(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test removing a label from a page."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/content/123456/label?name=old-label",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["label", "remove", "--page", "123456", "old-label"])
        assert result.exit_code == 0
        assert "Removed label 'old-label'" in result.stdout

    def test_remove_label_already_gone(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test removing a label that's already been removed (idempotent)."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/content/123456/label?name=old-label",
            method="DELETE",
            status_code=404,
        )

        result = runner.invoke(app, ["label", "remove", "--page", "123456", "old-label"])
        assert result.exit_code == 0
        assert "Removed label 'old-label'" in result.stdout

    def test_remove_label_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test removing label with JSON output."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/content/123456/label?name=test-label",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["label", "remove", "--page", "123456", "test-label", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["status"] == "success"
        assert output["label"] == "test-label"

    def test_remove_label_with_url(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test removing label with page URL instead of ID."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/content/123456/label?name=old-label",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(
            app,
            [
                "label",
                "remove",
                "--page",
                "https://example.atlassian.net/wiki/spaces/DEV/pages/123456/Test",
                "old-label",
            ],
        )
        assert result.exit_code == 0
        assert "Removed label 'old-label'" in result.stdout


class TestLabelSearchCommand:
    """Tests for 'confl label search' command."""

    def test_search_by_label(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test searching content by label."""
        # First request: find label by name
        labels_data = {
            "results": [
                {"id": "123", "name": "architecture", "prefix": "global"},
                {"id": "456", "name": "design", "prefix": "global"},
            ]
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/labels?limit=250",
            method="GET",
            json=labels_data,
        )

        # Second request: get pages with this label
        pages_data = {
            "results": [
                {"id": "111", "title": "Architecture Doc"},
                {"id": "222", "title": "System Design"},
            ]
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/labels/123/pages?limit=25",
            method="GET",
            json=pages_data,
        )

        # Third request: get blogposts with this label
        blogposts_data = {"results": []}
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/labels/123/blogposts?limit=25",
            method="GET",
            json=blogposts_data,
        )

        # Fourth request: get attachments with this label
        attachments_data = {"results": []}
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/labels/123/attachments?limit=25",
            method="GET",
            json=attachments_data,
        )

        result = runner.invoke(app, ["label", "search", "architecture"])
        assert result.exit_code == 0
        assert "Architecture Doc" in result.stdout
        assert "System Design" in result.stdout

    def test_search_by_label_with_blogposts(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test searching content by label including blogposts."""
        # Find label
        labels_data = {
            "results": [
                {"id": "123", "name": "release-notes", "prefix": "global"},
            ]
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/labels?limit=250",
            method="GET",
            json=labels_data,
        )

        # Get pages
        pages_data = {"results": []}
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/labels/123/pages?limit=25",
            method="GET",
            json=pages_data,
        )

        # Get blogposts
        blogposts_data = {
            "results": [
                {"id": "333", "title": "Release v1.0"},
                {"id": "444", "title": "Release v2.0"},
            ]
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/labels/123/blogposts?limit=25",
            method="GET",
            json=blogposts_data,
        )

        # Get attachments
        attachments_data = {"results": []}
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/labels/123/attachments?limit=25",
            method="GET",
            json=attachments_data,
        )

        result = runner.invoke(app, ["label", "search", "release-notes"])
        assert result.exit_code == 0
        assert "Blog Posts" in result.stdout
        assert "Release v1.0" in result.stdout
        assert "Release v2.0" in result.stdout

    def test_search_by_label_json_output(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test searching by label with JSON output."""
        # Find label
        labels_data = {
            "results": [
                {"id": "123", "name": "test", "prefix": "global"},
            ]
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/labels?limit=250",
            method="GET",
            json=labels_data,
        )

        # Get pages
        pages_data = {"results": [{"id": "111", "title": "Test Page"}]}
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/labels/123/pages?limit=25",
            method="GET",
            json=pages_data,
        )

        # Get blogposts
        blogposts_data = {"results": []}
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/labels/123/blogposts?limit=25",
            method="GET",
            json=blogposts_data,
        )

        # Get attachments
        attachments_data = {"results": []}
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/labels/123/attachments?limit=25",
            method="GET",
            json=attachments_data,
        )

        result = runner.invoke(app, ["label", "search", "test", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["label"]["name"] == "test"
        assert len(output["pages"]) == 1
        assert output["pages"][0]["title"] == "Test Page"

    def test_search_label_not_found(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test searching for non-existent label."""
        labels_data = {"results": []}
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/labels?limit=250",
            method="GET",
            json=labels_data,
        )

        result = runner.invoke(app, ["label", "search", "nonexistent"])
        assert result.exit_code == 0
        assert "Label 'nonexistent' not found" in result.stderr

    def test_search_label_no_content(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test searching by label when no content has that label."""
        # Find label
        labels_data = {
            "results": [
                {"id": "123", "name": "unused", "prefix": "global"},
            ]
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/labels?limit=250",
            method="GET",
            json=labels_data,
        )

        # Empty results for all content types
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/labels/123/pages?limit=25",
            method="GET",
            json={"results": []},
        )
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/labels/123/blogposts?limit=25",
            method="GET",
            json={"results": []},
        )
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/labels/123/attachments?limit=25",
            method="GET",
            json={"results": []},
        )

        result = runner.invoke(app, ["label", "search", "unused"])
        assert result.exit_code == 0
        assert "No content found with this label" in result.stdout
