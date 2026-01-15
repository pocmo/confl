"""Tests for blog post commands."""

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


class TestBlogpostListCommand:
    """Tests for blogpost list command."""

    def test_list_blogposts_default(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing blog posts in a space."""
        # Mock space lookup
        space_data = {"results": [{"id": "111111", "key": "DEV", "name": "Development"}]}
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json=space_data,
        )

        # Mock blogpost listing
        blogposts_data = {
            "results": [
                {
                    "id": "654321",
                    "title": "Release Notes v1.0",
                    "spaceId": "111111",
                    "version": {"createdAt": "2024-01-15T10:00:00Z"},
                }
            ]
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts?limit=25&space-id=111111",
            method="GET",
            json=blogposts_data,
        )

        result = runner.invoke(app, ["blogpost", "list", "--space", "DEV"])

        assert result.exit_code == 0
        assert "654321" in result.stdout
        assert "Release Notes v1.0" in result.stdout

    def test_list_blogposts_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing blog posts with JSON output."""
        # Mock space lookup
        space_data = {"results": [{"id": "111111", "key": "DEV", "name": "Development"}]}
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json=space_data,
        )

        # Mock blogpost listing
        blogposts_data = {
            "results": [
                {
                    "id": "654321",
                    "title": "Release Notes",
                    "spaceId": "111111",
                }
            ]
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts?limit=25&space-id=111111",
            method="GET",
            json=blogposts_data,
        )

        result = runner.invoke(app, ["blogpost", "list", "--space", "DEV", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert data[0]["id"] == "654321"

    def test_list_blogposts_empty(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing blog posts when space is empty."""
        # Mock space lookup
        space_data = {"results": [{"id": "111111", "key": "DEV", "name": "Development"}]}
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json=space_data,
        )

        # Mock empty blogpost listing
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts?limit=25&space-id=111111",
            method="GET",
            json={"results": []},
        )

        result = runner.invoke(app, ["blogpost", "list", "--space", "DEV"])

        assert result.exit_code == 0
        assert "No blog posts found" in result.stdout


class TestBlogpostGetCommand:
    """Tests for blogpost get command."""

    def test_get_blogpost_default(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a blog post with default rich output."""
        blogpost_data = {
            "id": "654321",
            "title": "Release Notes v1.0",
            "spaceId": "111111",
            "body": {
                "storage": {
                    "value": "<p>New features and improvements</p>",
                    "representation": "storage",
                }
            },
            "version": {"createdAt": "2024-01-15T10:00:00Z", "authorId": "user123"},
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts/654321?body-format=storage",
            method="GET",
            json=blogpost_data,
        )

        result = runner.invoke(app, ["blogpost", "get", "654321"])

        assert result.exit_code == 0
        assert "Release Notes v1.0" in result.stdout
        assert "111111" in result.stdout

    def test_get_blogpost_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a blog post with JSON output."""
        blogpost_data = {
            "id": "654321",
            "title": "Release Notes",
            "body": {
                "storage": {
                    "value": "<p>Content</p>",
                    "representation": "storage",
                }
            },
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts/654321?body-format=storage",
            method="GET",
            json=blogpost_data,
        )

        result = runner.invoke(app, ["blogpost", "get", "654321", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["id"] == "654321"
        assert data["title"] == "Release Notes"

    def test_get_blogpost_markdown(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a blog post with markdown output."""
        blogpost_data = {
            "id": "654321",
            "title": "Release Notes",
            "body": {
                "storage": {
                    "value": "<h1>Version 1.0</h1><p>New features</p>",
                    "representation": "storage",
                }
            },
            "version": {"createdAt": "2024-01-15T10:00:00Z"},
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts/654321?body-format=storage",
            method="GET",
            json=blogpost_data,
        )

        result = runner.invoke(app, ["blogpost", "get", "654321", "--markdown"])

        assert result.exit_code == 0
        assert "# Version 1.0" in result.stdout
        assert "New features" in result.stdout

    def test_get_blogpost_raw(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a blog post with raw storage format."""
        blogpost_data = {
            "id": "654321",
            "title": "Release Notes",
            "body": {
                "storage": {
                    "value": "<p>Raw content</p>",
                    "representation": "storage",
                }
            },
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts/654321?body-format=storage",
            method="GET",
            json=blogpost_data,
        )

        result = runner.invoke(app, ["blogpost", "get", "654321", "--raw"])

        assert result.exit_code == 0
        assert "<p>Raw content</p>" in result.stdout

    def test_get_blogpost_url_format(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a blog post by URL."""
        blogpost_data = {
            "id": "654321",
            "title": "Release Notes",
            "body": {
                "storage": {
                    "value": "<p>Content</p>",
                    "representation": "storage",
                }
            },
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts/654321?body-format=storage",
            method="GET",
            json=blogpost_data,
        )

        # Test with blogpost URL
        url = "https://example.atlassian.net/wiki/spaces/DEV/blogposts/654321/Title"
        result = runner.invoke(app, ["blogpost", "get", url])

        assert result.exit_code == 0
        assert "Release Notes" in result.stdout


class TestBlogpostCreateCommand:
    """Tests for blogpost create command."""

    def test_create_blogpost_with_body(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test creating a blog post with --body flag."""
        # Mock space lookup
        space_data = {"results": [{"id": "111111", "key": "DEV", "name": "Development"}]}
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json=space_data,
        )

        # Mock blogpost creation
        created_blogpost = {
            "id": "654321",
            "title": "New Post",
            "spaceId": "111111",
            "_links": {"webui": "/wiki/spaces/DEV/blogposts/654321"},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts",
            method="POST",
            json=created_blogpost,
        )

        result = runner.invoke(
            app,
            ["blogpost", "create", "--space", "DEV", "--title", "New Post", "--body", "# Content"],
        )

        assert result.exit_code == 0
        assert "654321" in result.stdout
        assert "created successfully" in result.stdout

    def test_create_blogpost_json_output(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test creating a blog post with JSON output."""
        # Mock space lookup
        space_data = {"results": [{"id": "111111", "key": "DEV", "name": "Development"}]}
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json=space_data,
        )

        # Mock blogpost creation
        created_blogpost = {
            "id": "654321",
            "title": "New Post",
            "spaceId": "111111",
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts",
            method="POST",
            json=created_blogpost,
        )

        result = runner.invoke(
            app,
            [
                "blogpost",
                "create",
                "--space",
                "DEV",
                "--title",
                "New Post",
                "--body",
                "Content",
                "--json",
            ],
        )

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["id"] == "654321"

    def test_create_blogpost_raw_format(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test creating a blog post with raw storage format."""
        # Mock space lookup
        space_data = {"results": [{"id": "111111", "key": "DEV", "name": "Development"}]}
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json=space_data,
        )

        # Mock blogpost creation
        created_blogpost = {
            "id": "654321",
            "title": "New Post",
            "spaceId": "111111",
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts",
            method="POST",
            json=created_blogpost,
        )

        result = runner.invoke(
            app,
            [
                "blogpost",
                "create",
                "--space",
                "DEV",
                "--title",
                "New Post",
                "--body",
                "<p>HTML</p>",
                "--raw",
            ],
        )

        assert result.exit_code == 0
        assert "654321" in result.stdout


class TestBlogpostUpdateCommand:
    """Tests for blogpost update command."""

    def test_update_blogpost_body(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating a blog post's body."""
        # Mock getting current blogpost
        current_blogpost = {
            "id": "654321",
            "title": "Existing Post",
            "body": {
                "storage": {
                    "value": "<p>Old content</p>",
                    "representation": "storage",
                }
            },
            "version": {"number": 1},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts/654321?body-format=storage",
            method="GET",
            json=current_blogpost,
        )

        # Mock update
        updated_blogpost = {
            "id": "654321",
            "title": "Existing Post",
            "version": {"number": 2},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts/654321",
            method="PUT",
            json=updated_blogpost,
        )

        result = runner.invoke(app, ["blogpost", "update", "654321", "--body", "# New content"])

        assert result.exit_code == 0
        assert "updated successfully" in result.stdout

    def test_update_blogpost_title(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating a blog post's title."""
        # Mock getting current blogpost
        current_blogpost = {
            "id": "654321",
            "title": "Old Title",
            "body": {
                "storage": {
                    "value": "<p>Content</p>",
                    "representation": "storage",
                }
            },
            "version": {"number": 1},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts/654321?body-format=storage",
            method="GET",
            json=current_blogpost,
        )

        # Mock update
        updated_blogpost = {
            "id": "654321",
            "title": "New Title",
            "version": {"number": 2},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts/654321",
            method="PUT",
            json=updated_blogpost,
        )

        result = runner.invoke(app, ["blogpost", "update", "654321", "--title", "New Title"])

        assert result.exit_code == 0
        assert "updated successfully" in result.stdout

    def test_update_blogpost_json_output(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test updating a blog post with JSON output."""
        # Mock getting current blogpost
        current_blogpost = {
            "id": "654321",
            "title": "Post",
            "body": {
                "storage": {
                    "value": "<p>Old</p>",
                    "representation": "storage",
                }
            },
            "version": {"number": 1},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts/654321?body-format=storage",
            method="GET",
            json=current_blogpost,
        )

        # Mock update
        updated_blogpost = {
            "id": "654321",
            "title": "Post",
            "version": {"number": 2},
        }
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts/654321",
            method="PUT",
            json=updated_blogpost,
        )

        result = runner.invoke(app, ["blogpost", "update", "654321", "--body", "New", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["id"] == "654321"
        assert data["version"]["number"] == 2


class TestBlogpostDeleteCommand:
    """Tests for blogpost delete command."""

    def test_delete_blogpost(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test deleting a blog post."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts/654321",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["blogpost", "delete", "654321"])

        assert result.exit_code == 0
        assert "deleted successfully" in result.stdout

    def test_delete_blogpost_json_output(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test deleting a blog post with JSON output."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts/654321",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["blogpost", "delete", "654321", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert data["blogpost_id"] == "654321"

    def test_delete_blogpost_url_format(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test deleting a blog post by URL."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts/654321",
            method="DELETE",
            status_code=204,
        )

        url = "https://example.atlassian.net/wiki/spaces/DEV/blogposts/654321/Title"
        result = runner.invoke(app, ["blogpost", "delete", url])

        assert result.exit_code == 0
        assert "deleted successfully" in result.stdout

    def test_delete_blogpost_with_yes_flag(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test deleting a blog post with --yes flag bypasses confirmation."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/blogposts/654321",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["blogpost", "delete", "654321", "--yes"])
        assert result.exit_code == 0
        assert "deleted successfully" in result.stdout
        # Should not contain confirmation prompt
        assert "Are you sure" not in result.stdout
