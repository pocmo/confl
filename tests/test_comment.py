"""Tests for comment commands."""

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


class TestCommentListCommand:
    """Tests for comment list command."""

    def test_list_comments_default(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing comments on a page."""
        comments_data = {
            "results": [
                {
                    "id": "789012",
                    "body": {
                        "storage": {
                            "value": "<p>Great work on this page!</p>",
                            "representation": "storage",
                        }
                    },
                    "authorId": "user123",
                    "createdAt": "2024-01-15T10:30:00Z",
                    "version": {"createdAt": "2024-01-15T11:00:00Z"},
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/123456/footer-comments?limit=25&body-format=storage",
            method="GET",
            json=comments_data,
        )

        result = runner.invoke(app, ["comment", "list", "--page", "123456"])

        assert result.exit_code == 0
        assert "789012" in result.stdout
        assert "Great work" in result.stdout

    def test_list_comments_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing comments with JSON output."""
        comments_data = {
            "results": [
                {
                    "id": "789012",
                    "body": {
                        "storage": {
                            "value": "<p>Great work!</p>",
                            "representation": "storage",
                        }
                    },
                    "authorId": "user123",
                    "createdAt": "2024-01-15T10:30:00Z",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/123456/footer-comments?limit=25&body-format=storage",
            method="GET",
            json=comments_data,
        )

        result = runner.invoke(app, ["comment", "list", "--page", "123456", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert data[0]["id"] == "789012"


class TestCommentGetCommand:
    """Tests for comment get command."""

    def test_get_comment_default(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a comment."""
        comment_data = {
            "id": "789012",
            "body": {
                "storage": {
                    "value": "<p>Great work on this page!</p>",
                    "representation": "storage",
                }
            },
            "authorId": "user123",
            "createdAt": "2024-01-15T10:30:00Z",
            "version": {"createdAt": "2024-01-15T11:00:00Z"},
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/footer-comments/789012?body-format=storage",
            method="GET",
            json=comment_data,
        )

        result = runner.invoke(app, ["comment", "get", "789012"])

        assert result.exit_code == 0
        assert "789012" in result.stdout
        assert "Great work" in result.stdout
        assert "user123" in result.stdout

    def test_get_comment_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a comment with JSON output."""
        comment_data = {
            "id": "789012",
            "body": {
                "storage": {
                    "value": "<p>Great work!</p>",
                    "representation": "storage",
                }
            },
            "authorId": "user123",
            "createdAt": "2024-01-15T10:30:00Z",
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/footer-comments/789012?body-format=storage",
            method="GET",
            json=comment_data,
        )

        result = runner.invoke(app, ["comment", "get", "789012", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["id"] == "789012"

    def test_get_comment_markdown(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a comment with markdown output."""
        comment_data = {
            "id": "789012",
            "body": {
                "storage": {
                    "value": "<p>Great work on this page!</p>",
                    "representation": "storage",
                }
            },
            "authorId": "user123",
            "createdAt": "2024-01-15T10:30:00Z",
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/footer-comments/789012?body-format=storage",
            method="GET",
            json=comment_data,
        )

        result = runner.invoke(app, ["comment", "get", "789012", "--markdown"])

        assert result.exit_code == 0
        assert "Great work" in result.stdout


class TestCommentAddCommand:
    """Tests for comment add command."""

    def test_add_comment_to_page(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test adding a comment to a page."""
        result_data = {
            "id": "999888",
            "body": {
                "storage": {
                    "value": "<p>New comment</p>",
                    "representation": "storage",
                }
            },
            "authorId": "user123",
            "createdAt": "2024-01-15T12:00:00Z",
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/footer-comments",
            method="POST",
            json=result_data,
        )

        result = runner.invoke(app, ["comment", "add", "--page", "123456", "--body", "New comment"])

        assert result.exit_code == 0
        assert "Created comment" in result.stdout
        assert "999888" in result.stdout

    def test_add_comment_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test adding a comment with JSON output."""
        result_data = {
            "id": "999888",
            "body": {
                "storage": {
                    "value": "<p>New comment</p>",
                    "representation": "storage",
                }
            },
            "authorId": "user123",
            "createdAt": "2024-01-15T12:00:00Z",
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/footer-comments",
            method="POST",
            json=result_data,
        )

        result = runner.invoke(
            app,
            [
                "comment",
                "add",
                "--page",
                "123456",
                "--body",
                "New comment",
                "--json",
            ],
        )

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["id"] == "999888"

    def test_add_comment_missing_page_and_parent(self, mock_config_env: None) -> None:
        """Test that adding a comment requires page or parent."""
        result = runner.invoke(app, ["comment", "add", "--body", "Test"])

        assert result.exit_code == 1
        assert "Must provide either --page or --parent" in result.stderr


class TestCommentUpdateCommand:
    """Tests for comment update command."""

    def test_update_comment(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating a comment."""
        result_data = {
            "id": "789012",
            "body": {
                "storage": {
                    "value": "<p>Updated comment</p>",
                    "representation": "storage",
                }
            },
            "authorId": "user123",
            "createdAt": "2024-01-15T10:30:00Z",
            "version": {"createdAt": "2024-01-15T13:00:00Z"},
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/footer-comments/789012",
            method="PUT",
            json=result_data,
        )

        result = runner.invoke(app, ["comment", "update", "789012", "--body", "Updated comment"])

        assert result.exit_code == 0
        assert "Updated comment" in result.stdout
        assert "789012" in result.stdout

    def test_update_comment_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating a comment with JSON output."""
        result_data = {
            "id": "789012",
            "body": {
                "storage": {
                    "value": "<p>Updated comment</p>",
                    "representation": "storage",
                }
            },
            "authorId": "user123",
            "createdAt": "2024-01-15T10:30:00Z",
            "version": {"createdAt": "2024-01-15T13:00:00Z"},
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/footer-comments/789012",
            method="PUT",
            json=result_data,
        )

        result = runner.invoke(
            app,
            ["comment", "update", "789012", "--body", "Updated comment", "--json"],
        )

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["id"] == "789012"


class TestCommentDeleteCommand:
    """Tests for comment delete command."""

    def test_delete_comment_success(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test deleting a comment."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/footer-comments/789012",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["comment", "delete", "789012"])

        assert result.exit_code == 0
        assert "Deleted" in result.stdout
        assert "789012" in result.stdout

    def test_delete_comment_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test deleting a comment with JSON output."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/footer-comments/789012",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["comment", "delete", "789012", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert data["id"] == "789012"

    def test_delete_comment_with_yes_flag(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test deleting a comment with --yes flag bypasses confirmation."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/footer-comments/789012",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["comment", "delete", "789012", "--yes"])
        assert result.exit_code == 0
        assert "Deleted comment" in result.stdout
        # Should not contain confirmation prompt
        assert "Are you sure" not in result.stdout
