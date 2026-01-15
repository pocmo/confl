"""Tests for space commands."""

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


class TestSpaceListCommand:
    """Tests for 'confl space list' command."""

    def test_list_spaces_default(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing spaces with default output."""
        spaces_data = {
            "results": [
                {
                    "id": "123",
                    "key": "DEV",
                    "name": "Development",
                    "type": "global",
                    "status": "current",
                },
                {
                    "id": "456",
                    "key": "TEST",
                    "name": "Testing",
                    "type": "global",
                    "status": "current",
                },
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?limit=25",
            method="GET",
            json=spaces_data,
        )

        result = runner.invoke(app, ["space", "list"])
        assert result.exit_code == 0
        assert "DEV" in result.stdout
        assert "Development" in result.stdout
        assert "TEST" in result.stdout
        assert "Testing" in result.stdout

    def test_list_spaces_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing spaces with JSON output."""
        spaces_data = {
            "results": [
                {
                    "id": "123",
                    "key": "DEV",
                    "name": "Development",
                    "type": "global",
                    "status": "current",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?limit=25",
            method="GET",
            json=spaces_data,
        )

        result = runner.invoke(app, ["space", "list", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert len(output) == 1
        assert output[0]["key"] == "DEV"

    def test_list_spaces_with_type_filter(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test listing spaces with type filter."""
        spaces_data = {"results": []}

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?limit=25&type=global",
            method="GET",
            json=spaces_data,
        )

        result = runner.invoke(app, ["space", "list", "--type", "global"])
        assert result.exit_code == 0

    def test_list_spaces_with_status_filter(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test listing spaces with status filter."""
        spaces_data = {"results": []}

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?limit=25&status=current",
            method="GET",
            json=spaces_data,
        )

        result = runner.invoke(app, ["space", "list", "--status", "current"])
        assert result.exit_code == 0

    def test_list_spaces_empty(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing spaces when none exist."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?limit=25",
            method="GET",
            json={"results": []},
        )

        result = runner.invoke(app, ["space", "list"])
        assert result.exit_code == 0
        assert "No spaces found" in result.stdout


class TestSpaceGetCommand:
    """Tests for 'confl space get' command."""

    def test_get_space_by_key(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a space by key."""
        space_data = {
            "id": "123",
            "key": "DEV",
            "name": "Development",
            "type": "global",
            "status": "current",
            "description": {"plain": {"value": "Development team space"}},
            "homepageId": "456",
            "authorId": "user123",
            "createdAt": "2024-01-15T10:00:00.000Z",
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/DEV",
            method="GET",
            json=space_data,
        )

        result = runner.invoke(app, ["space", "get", "DEV"])
        assert result.exit_code == 0
        assert "Key: DEV" in result.stdout
        assert "Name: Development" in result.stdout
        assert "Type: global" in result.stdout
        assert "Status: current" in result.stdout

    def test_get_space_by_id(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a space by ID."""
        space_data = {
            "id": "123",
            "key": "DEV",
            "name": "Development",
            "type": "global",
            "status": "current",
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/123",
            method="GET",
            json=space_data,
        )

        result = runner.invoke(app, ["space", "get", "123"])
        assert result.exit_code == 0
        assert "Key: DEV" in result.stdout

    def test_get_space_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a space with JSON output."""
        space_data = {
            "id": "123",
            "key": "DEV",
            "name": "Development",
            "type": "global",
            "status": "current",
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/DEV",
            method="GET",
            json=space_data,
        )

        result = runner.invoke(app, ["space", "get", "DEV", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["key"] == "DEV"

    def test_get_space_not_found(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a non-existent space."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/NOTFOUND",
            method="GET",
            status_code=404,
            json={
                "errors": [
                    {
                        "status": 404,
                        "title": "Not Found",
                        "detail": "Space not found",
                    }
                ]
            },
        )

        result = runner.invoke(app, ["space", "get", "NOTFOUND"])
        assert result.exit_code == 1
        assert "Not found" in result.stderr


class TestSpaceCreateCommand:
    """Tests for 'confl space create' command."""

    def test_create_space_minimal(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test creating a space with minimal parameters."""
        created_space = {
            "id": "123",
            "key": "NEW",
            "name": "New Space",
            "type": "global",
            "status": "current",
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces",
            method="POST",
            json=created_space,
        )

        result = runner.invoke(app, ["space", "create", "--key", "NEW", "--name", "New Space"])
        assert result.exit_code == 0
        assert "Space created" in result.stdout
        assert "NEW" in result.stdout

    def test_create_space_with_description(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test creating a space with description."""
        created_space = {
            "id": "123",
            "key": "NEW",
            "name": "New Space",
            "type": "global",
            "status": "current",
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces",
            method="POST",
            json=created_space,
        )

        result = runner.invoke(
            app,
            [
                "space",
                "create",
                "--key",
                "NEW",
                "--name",
                "New Space",
                "--description",
                "Test description",
            ],
        )
        assert result.exit_code == 0
        assert "Space created" in result.stdout

    def test_create_space_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test creating a space with JSON output."""
        created_space = {
            "id": "123",
            "key": "NEW",
            "name": "New Space",
            "type": "global",
            "status": "current",
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces",
            method="POST",
            json=created_space,
        )

        result = runner.invoke(
            app, ["space", "create", "--key", "NEW", "--name", "New Space", "--json"]
        )
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["key"] == "NEW"

    def test_create_space_duplicate_key(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test creating a space with duplicate key."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces",
            method="POST",
            status_code=400,
            json={
                "errors": [
                    {
                        "status": 400,
                        "title": "Bad Request",
                        "detail": "Space key already exists",
                    }
                ]
            },
        )

        result = runner.invoke(app, ["space", "create", "--key", "DUP", "--name", "Duplicate"])
        assert result.exit_code == 1
        assert "error" in result.stderr.lower()


class TestSpaceUpdateCommand:
    """Tests for 'confl space update' command."""

    def test_update_space_name(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating a space name."""
        updated_space = {
            "id": "123",
            "key": "DEV",
            "name": "New Name",
            "type": "global",
            "status": "current",
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/DEV",
            method="PUT",
            json=updated_space,
        )

        result = runner.invoke(app, ["space", "update", "DEV", "--name", "New Name"])
        assert result.exit_code == 0
        assert "Space updated" in result.stdout

    def test_update_space_description(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating a space description."""
        updated_space = {
            "id": "123",
            "key": "DEV",
            "name": "Development",
            "type": "global",
            "status": "current",
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/DEV",
            method="PUT",
            json=updated_space,
        )

        result = runner.invoke(app, ["space", "update", "DEV", "--description", "New description"])
        assert result.exit_code == 0
        assert "Space updated" in result.stdout

    def test_update_space_no_params(self, mock_config_env: None) -> None:
        """Test updating a space with no parameters."""
        result = runner.invoke(app, ["space", "update", "DEV"])
        assert result.exit_code == 2
        assert "At least one" in result.stderr

    def test_update_space_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating a space with JSON output."""
        updated_space = {
            "id": "123",
            "key": "DEV",
            "name": "New Name",
            "type": "global",
            "status": "current",
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/DEV",
            method="PUT",
            json=updated_space,
        )

        result = runner.invoke(app, ["space", "update", "DEV", "--name", "New Name", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["name"] == "New Name"


class TestSpaceDeleteCommand:
    """Tests for 'confl space delete' command."""

    def test_delete_space(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test deleting a space."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/DEV",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["space", "delete", "DEV"])
        assert result.exit_code == 0
        assert "Space deleted" in result.stdout

    def test_delete_space_by_id(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test deleting a space by ID."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/123",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["space", "delete", "123"])
        assert result.exit_code == 0
        assert "Space deleted" in result.stdout

    def test_delete_space_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test deleting a space with JSON output."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/DEV",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["space", "delete", "DEV", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["status"] == "deleted"

    def test_delete_space_not_found(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test deleting a non-existent space (should succeed)."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/NOTFOUND",
            method="DELETE",
            status_code=404,
        )

        result = runner.invoke(app, ["space", "delete", "NOTFOUND"])
        assert result.exit_code == 0  # 404 is treated as success
        assert "Space deleted" in result.stdout

    def test_delete_space_with_yes_flag(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test deleting a space with --yes flag bypasses confirmation."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/DEV",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["space", "delete", "DEV", "--yes"])
        assert result.exit_code == 0
        assert "Space deleted" in result.stdout
        # Should not contain confirmation prompt
        assert "Are you sure" not in result.stdout
