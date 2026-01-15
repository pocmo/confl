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
            url="https://example.atlassian.net/wiki/api/v2/spaces?limit=100",
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
            url="https://example.atlassian.net/wiki/api/v2/spaces?limit=100",
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
            url="https://example.atlassian.net/wiki/api/v2/spaces?limit=100&type=global",
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
            url="https://example.atlassian.net/wiki/api/v2/spaces?limit=100&status=current",
            method="GET",
            json=spaces_data,
        )

        result = runner.invoke(app, ["space", "list", "--status", "current"])
        assert result.exit_code == 0

    def test_list_spaces_empty(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing spaces when none exist."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?limit=100",
            method="GET",
            json={"results": []},
        )

        result = runner.invoke(app, ["space", "list"])
        assert result.exit_code == 0
        assert "No spaces found" in result.stdout

    def test_list_spaces_with_limit(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing spaces with explicit limit."""
        spaces_data = {
            "results": [
                {
                    "id": "123",
                    "key": "DEV",
                    "name": "Development",
                    "type": "global",
                    "status": "current",
                },
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?limit=100",
            method="GET",
            json=spaces_data,
        )

        result = runner.invoke(app, ["space", "list", "--limit", "10"])
        assert result.exit_code == 0
        assert "DEV" in result.stdout

    def test_list_spaces_pagination(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test that list_spaces follows pagination to get all results."""
        # First page
        page1_data = {
            "results": [
                {
                    "id": "123",
                    "key": "DEV",
                    "name": "Development",
                    "type": "global",
                    "status": "current",
                },
            ],
            "_links": {"next": "/wiki/api/v2/spaces?cursor=abc123"},
        }

        # Second page (last page, no next link)
        page2_data = {
            "results": [
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
            url="https://example.atlassian.net/wiki/api/v2/spaces?limit=100",
            method="GET",
            json=page1_data,
        )

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?limit=100&cursor=abc123",
            method="GET",
            json=page2_data,
        )

        result = runner.invoke(app, ["space", "list"])
        assert result.exit_code == 0
        # Both spaces from both pages should be present
        assert "DEV" in result.stdout
        assert "TEST" in result.stdout


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

        # When key is provided, should use /spaces?keys={key} endpoint
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json={"results": [space_data]},
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

        # When key is provided, should use /spaces?keys={key} endpoint
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json={"results": [space_data]},
        )

        result = runner.invoke(app, ["space", "get", "DEV", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["key"] == "DEV"

    def test_get_space_not_found(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a non-existent space."""
        # When key is provided and not found, get_space_by_key returns empty results
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=NOTFOUND",
            method="GET",
            json={"results": []},
        )

        result = runner.invoke(app, ["space", "get", "NOTFOUND"])
        assert result.exit_code == 1
        assert "not found" in result.stderr.lower()

    def test_get_space_with_numeric_id_directly(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test that numeric IDs bypass key resolution and use /spaces/{id} directly."""
        space_data = {
            "id": "123",
            "key": "DEV",
            "name": "Development",
            "type": "global",
            "status": "current",
        }

        # Should call /spaces/123 directly, not /spaces?keys=123
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/123",
            method="GET",
            json=space_data,
        )

        result = runner.invoke(app, ["space", "get", "123"])
        assert result.exit_code == 0
        assert "Key: DEV" in result.stdout


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
        # First resolves key to ID
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json={"results": [{"id": "123", "key": "DEV", "name": "Development"}]},
        )

        updated_space = {
            "id": "123",
            "key": "DEV",
            "name": "New Name",
            "type": "global",
            "status": "current",
        }

        # Then updates using numeric ID
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/123",
            method="PUT",
            json=updated_space,
        )

        result = runner.invoke(app, ["space", "update", "DEV", "--name", "New Name"])
        assert result.exit_code == 0
        assert "Space updated" in result.stdout

    def test_update_space_description(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating a space description."""
        # First resolves key to ID
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json={"results": [{"id": "123", "key": "DEV", "name": "Development"}]},
        )

        updated_space = {
            "id": "123",
            "key": "DEV",
            "name": "Development",
            "type": "global",
            "status": "current",
        }

        # Then updates using numeric ID
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/123",
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
        # First resolves key to ID
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json={"results": [{"id": "123", "key": "DEV", "name": "Development"}]},
        )

        updated_space = {
            "id": "123",
            "key": "DEV",
            "name": "New Name",
            "type": "global",
            "status": "current",
        }

        # Then updates using numeric ID
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/123",
            method="PUT",
            json=updated_space,
        )

        result = runner.invoke(app, ["space", "update", "DEV", "--name", "New Name", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["name"] == "New Name"

    def test_update_space_with_numeric_id_directly(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test that numeric IDs bypass key resolution for update."""
        updated_space = {
            "id": "123",
            "key": "DEV",
            "name": "New Name",
            "type": "global",
            "status": "current",
        }

        # Should call /spaces/123 directly, not resolve key first
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/123",
            method="PUT",
            json=updated_space,
        )

        result = runner.invoke(app, ["space", "update", "123", "--name", "New Name"])
        assert result.exit_code == 0
        assert "Space updated" in result.stdout


class TestSpaceDeleteCommand:
    """Tests for 'confl space delete' command."""

    def test_delete_space(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test deleting a space."""
        # First resolves key to ID
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json={"results": [{"id": "123", "key": "DEV", "name": "Development"}]},
        )

        # Then deletes using numeric ID
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/123",
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
        # First resolves key to ID
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json={"results": [{"id": "123", "key": "DEV", "name": "Development"}]},
        )

        # Then deletes using numeric ID
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/123",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["space", "delete", "DEV", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["status"] == "deleted"

    def test_delete_space_not_found(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test deleting a non-existent space (should succeed)."""
        # Key resolution fails - space not found
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=NOTFOUND",
            method="GET",
            json={"results": []},
        )

        result = runner.invoke(app, ["space", "delete", "NOTFOUND"])
        assert result.exit_code == 0  # 404 is treated as success
        assert "Space deleted" in result.stdout

    def test_delete_space_with_numeric_id_directly(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test that numeric IDs bypass key resolution for delete."""
        # Should call /spaces/123 directly, not resolve key first
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/123",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["space", "delete", "123"])
        assert result.exit_code == 0
        assert "Space deleted" in result.stdout

    def test_delete_space_with_yes_flag(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test deleting a space with --yes flag bypasses confirmation."""
        # First resolves key to ID
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json={"results": [{"id": "123", "key": "DEV", "name": "Development"}]},
        )

        # Then deletes using numeric ID
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces/123",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["space", "delete", "DEV", "--yes"])
        assert result.exit_code == 0
        assert "Space deleted" in result.stdout
        # Should not contain confirmation prompt
        assert "Are you sure" not in result.stdout


class TestSpaceSearchCommand:
    """Tests for 'confl space search' command."""

    def test_search_spaces_basic(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test basic space search."""
        search_results = {
            "results": [
                {
                    "space": {
                        "id": "123",
                        "key": "DEV",
                        "name": "Development",
                        "type": "global",
                    }
                },
                {
                    "space": {
                        "id": "456",
                        "key": "DEVOPS",
                        "name": "DevOps Team",
                        "type": "global",
                    }
                },
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=type%3Dspace+AND+title%7E%22Dev%22&limit=25",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(app, ["space", "search", "Dev"])
        assert result.exit_code == 0
        assert "DEV" in result.stdout
        assert "Development" in result.stdout
        assert "DEVOPS" in result.stdout
        assert "DevOps Team" in result.stdout
        assert "Found 2 space(s)" in result.stdout

    def test_search_spaces_with_type_filter(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test space search with type filter."""
        search_results = {
            "results": [
                {
                    "space": {
                        "id": "123",
                        "key": "~user123",
                        "name": "Personal Space",
                        "type": "personal",
                    }
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=type%3Dspace+AND+title%7E%22Personal%22+AND+space.type%3Dpersonal&limit=25",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(app, ["space", "search", "Personal", "--type", "personal"])
        assert result.exit_code == 0
        assert "~user123" in result.stdout
        assert "Personal Space" in result.stdout

    def test_search_spaces_with_invalid_type(self, mock_config_env: None) -> None:
        """Test space search with invalid type filter."""
        result = runner.invoke(app, ["space", "search", "Test", "--type", "invalid"])
        assert result.exit_code == 2
        assert "must be 'global' or 'personal'" in result.stderr

    def test_search_spaces_with_limit(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test space search with custom limit."""
        search_results = {"results": []}

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=type%3Dspace+AND+title%7E%22Test%22&limit=10",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(app, ["space", "search", "Test", "--limit", "10"])
        assert result.exit_code == 0

    def test_search_spaces_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test space search with JSON output."""
        search_results = {
            "results": [
                {
                    "space": {
                        "id": "123",
                        "key": "DEV",
                        "name": "Development",
                        "type": "global",
                    }
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=type%3Dspace+AND+title%7E%22Dev%22&limit=25",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(app, ["space", "search", "Dev", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert len(output) == 1
        assert output[0]["key"] == "DEV"
        assert output[0]["name"] == "Development"
        assert output[0]["type"] == "global"
        assert output[0]["id"] == "123"

    def test_search_spaces_no_results(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test space search with no results."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=type%3Dspace+AND+title%7E%22NonExistent%22&limit=25",
            method="GET",
            json={"results": []},
        )

        result = runner.invoke(app, ["space", "search", "NonExistent"])
        assert result.exit_code == 0
        assert "No spaces found matching your query" in result.stdout

    def test_search_spaces_decodes_html_entities(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test that space search decodes HTML entities in space names."""
        search_results = {
            "results": [
                {
                    "space": {
                        "id": "123",
                        "key": "TEST",
                        "name": "Test &amp; Development",
                        "type": "global",
                    }
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=type%3Dspace+AND+title%7E%22Test%22&limit=25",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(app, ["space", "search", "Test"])
        assert result.exit_code == 0
        assert "Test & Development" in result.stdout
        assert "&amp;" not in result.stdout
