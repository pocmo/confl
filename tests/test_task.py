"""Tests for task commands."""

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


class TestTaskListCommand:
    """Tests for task list command."""

    def test_list_tasks_default(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing tasks."""
        tasks_data = {
            "results": [
                {
                    "id": "123",
                    "status": "incomplete",
                    "body": {
                        "storage": {
                            "value": "<p>Review documentation</p>",
                            "representation": "storage",
                        }
                    },
                    "pageId": "456789",
                    "spaceId": "111",
                    "createdBy": "user123",
                    "createdAt": "2024-01-15T10:30:00Z",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/tasks?limit=25",
            method="GET",
            json=tasks_data,
        )

        result = runner.invoke(app, ["task", "list"])

        assert result.exit_code == 0
        assert "123" in result.stdout
        assert "incomplete" in result.stdout
        assert "Review documentation" in result.stdout

    def test_list_tasks_with_status_filter(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test listing tasks with status filter."""
        tasks_data = {
            "results": [
                {
                    "id": "456",
                    "status": "complete",
                    "body": {
                        "storage": {
                            "value": "<p>Complete task</p>",
                            "representation": "storage",
                        }
                    },
                    "pageId": "789",
                    "createdAt": "2024-01-15T10:30:00Z",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/tasks?limit=25&status=complete",
            method="GET",
            json=tasks_data,
        )

        result = runner.invoke(app, ["task", "list", "--status", "complete"])

        assert result.exit_code == 0
        assert "456" in result.stdout
        assert "complete" in result.stdout

    def test_list_tasks_with_page_filter(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test listing tasks filtered by page."""
        tasks_data = {"results": [{"id": "789", "status": "incomplete", "pageId": "123456"}]}

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/tasks?limit=25&page-id=123456",
            method="GET",
            json=tasks_data,
        )

        result = runner.invoke(app, ["task", "list", "--page", "123456"])

        assert result.exit_code == 0

    def test_list_tasks_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing tasks with JSON output."""
        tasks_data = {
            "results": [
                {
                    "id": "123",
                    "status": "incomplete",
                    "body": {"storage": {"value": "<p>Task</p>"}},
                    "pageId": "456",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/tasks?limit=25",
            method="GET",
            json=tasks_data,
        )

        result = runner.invoke(app, ["task", "list", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert data[0]["id"] == "123"

    def test_list_tasks_invalid_status(self, mock_config_env: None) -> None:
        """Test listing tasks with invalid status."""
        result = runner.invoke(app, ["task", "list", "--status", "invalid"])

        assert result.exit_code == 1
        assert "must be 'complete' or 'incomplete'" in result.stderr


class TestTaskGetCommand:
    """Tests for task get command."""

    def test_get_task_default(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a task."""
        task_data = {
            "results": [
                {
                    "id": "123",
                    "status": "incomplete",
                    "body": {
                        "storage": {
                            "value": "<p>Review documentation</p>",
                            "representation": "storage",
                        }
                    },
                    "pageId": "456789",
                    "spaceId": "111",
                    "createdBy": "user123",
                    "assignedTo": "user456",
                    "createdAt": "2024-01-15T10:30:00Z",
                    "dueAt": "2024-01-20T17:00:00Z",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/tasks?task-id=123&limit=1",
            method="GET",
            json=task_data,
        )

        result = runner.invoke(app, ["task", "get", "123"])

        assert result.exit_code == 0
        assert "ID:" in result.stdout
        assert "123" in result.stdout
        assert "Status:" in result.stdout
        assert "incomplete" in result.stdout
        assert "Page ID:" in result.stdout
        assert "456789" in result.stdout

    def test_get_task_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a task with JSON output."""
        task_data = {
            "results": [
                {
                    "id": "123",
                    "status": "complete",
                    "body": {"storage": {"value": "<p>Task</p>"}},
                    "pageId": "456",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/tasks?task-id=123&limit=1",
            method="GET",
            json=task_data,
        )

        result = runner.invoke(app, ["task", "get", "123", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["id"] == "123"
        assert data["status"] == "complete"

    def test_get_task_not_found(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting a non-existent task."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/tasks?task-id=999&limit=1",
            method="GET",
            json={"results": []},
        )

        result = runner.invoke(app, ["task", "get", "999"])

        assert result.exit_code == 1
        assert "Task not found" in result.stderr


class TestTaskUpdateCommand:
    """Tests for task update command."""

    def test_update_task_to_complete(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating task status to complete."""
        task_data = {
            "id": "123",
            "status": "complete",
            "body": {"storage": {"value": "<p>Task</p>"}},
            "pageId": "456",
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/tasks/123",
            method="PUT",
            json=task_data,
        )

        result = runner.invoke(app, ["task", "update", "123", "--status", "complete"])

        assert result.exit_code == 0
        assert "Updated task 123" in result.stdout
        assert "complete" in result.stdout

    def test_update_task_to_incomplete(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating task status to incomplete."""
        task_data = {"id": "123", "status": "incomplete"}

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/tasks/123",
            method="PUT",
            json=task_data,
        )

        result = runner.invoke(app, ["task", "update", "123", "--status", "incomplete"])

        assert result.exit_code == 0
        assert "Updated task 123" in result.stdout
        assert "incomplete" in result.stdout

    def test_update_task_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating task with JSON output."""
        task_data = {"id": "123", "status": "complete"}

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/tasks/123",
            method="PUT",
            json=task_data,
        )

        result = runner.invoke(app, ["task", "update", "123", "--status", "complete", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["id"] == "123"
        assert data["status"] == "complete"

    def test_update_task_dry_run(self, mock_config_env: None) -> None:
        """Test updating task in dry-run mode."""
        result = runner.invoke(app, ["task", "update", "123", "--status", "complete", "--dry-run"])

        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout
        assert "Would update task 123" in result.stdout
        assert "complete" in result.stdout

    def test_update_task_invalid_status(self, mock_config_env: None) -> None:
        """Test updating task with invalid status."""
        result = runner.invoke(app, ["task", "update", "123", "--status", "invalid"])

        assert result.exit_code == 1
        assert "must be 'complete' or 'incomplete'" in result.stderr

    def test_update_task_not_found(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test updating a non-existent task."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/tasks/999",
            method="PUT",
            status_code=404,
            json={
                "statusCode": 404,
                "data": {"authorized": True, "valid": True, "errors": [], "successful": False},
                "message": "Task not found",
            },
        )

        result = runner.invoke(app, ["task", "update", "999", "--status", "complete"])

        assert result.exit_code == 1
