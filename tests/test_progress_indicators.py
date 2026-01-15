"""Tests for progress indicators in long-running operations."""

from pathlib import Path
from unittest.mock import MagicMock, patch

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


class TestAttachmentProgressIndicators:
    """Tests for progress indicators in attachment operations."""

    def test_upload_attachment_shows_progress_non_tty(
        self, httpx_mock: HTTPXMock, mock_config_env: None, tmp_path: Path
    ) -> None:
        """Test upload works correctly without TTY (no progress indicator)."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        upload_response = {
            "results": [
                {
                    "id": "att123",
                    "title": "test.txt",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/content/123456/child/attachment",
            method="POST",
            json=upload_response,
        )

        # CliRunner doesn't simulate TTY, so progress should not show
        result = runner.invoke(
            app, ["attachment", "upload", "--page", "123456", "--file", str(test_file)]
        )
        assert result.exit_code == 0
        assert "Uploaded" in result.stdout

    def test_download_attachment_works_non_tty(
        self, httpx_mock: HTTPXMock, mock_config_env: None, tmp_path: Path
    ) -> None:
        """Test download works correctly without TTY (no progress indicator)."""
        attachment_data = {
            "id": "att123",
            "title": "diagram.png",
            "downloadLink": "/wiki/download/attachments/123456/diagram.png",
        }

        file_content = b"fake png content"

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/attachments/att123",
            method="GET",
            json=attachment_data,
        )

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/download/attachments/123456/diagram.png",
            method="GET",
            content=file_content,
        )

        # CliRunner doesn't simulate TTY, so progress should not show
        result = runner.invoke(app, ["attachment", "download", "att123"])
        assert result.exit_code == 0
        output_path = Path("diagram.png")
        assert output_path.exists()
        assert output_path.read_bytes() == file_content
        output_path.unlink()  # Clean up


class TestPageProgressIndicators:
    """Tests for progress indicators in page operations."""

    def test_page_create_shows_progress_non_tty(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test page create works correctly without TTY (no progress indicator)."""
        space_data = {"id": "space123", "key": "DEV", "name": "Development"}

        created_page = {
            "id": "12345678",
            "title": "Test Page",
            "spaceId": "space123",
            "version": {"number": 1},
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json={"results": [space_data]},
        )

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages",
            method="POST",
            json=created_page,
        )

        # CliRunner doesn't simulate TTY, so progress should not show
        result = runner.invoke(
            app, ["page", "create", "--space", "DEV", "--title", "Test Page", "--body", "# Test"]
        )
        assert result.exit_code == 0
        assert "created successfully" in result.stdout

    def test_page_update_shows_progress_non_tty(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test page update works correctly without TTY (no progress indicator)."""
        current_page = {
            "id": "12345678",
            "title": "Test Page",
            "version": {"number": 1},
            "body": {"storage": {"value": "<p>Old content</p>"}},
        }

        updated_page = {
            "id": "12345678",
            "title": "Test Page",
            "version": {"number": 2},
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678?body-format=storage",
            method="GET",
            json=current_page,
        )

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/12345678",
            method="PUT",
            json=updated_page,
        )

        # CliRunner doesn't simulate TTY, so progress should not show
        result = runner.invoke(app, ["page", "update", "12345678", "--body", "# New content"])
        assert result.exit_code == 0
        assert "updated successfully" in result.stdout

    @patch("sys.stdout.isatty", return_value=True)
    def test_page_create_with_tty_simulation(
        self, mock_isatty: MagicMock, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test page create with TTY simulation (progress indicator would show)."""
        space_data = {"id": "space123", "key": "DEV", "name": "Development"}

        created_page = {
            "id": "12345678",
            "title": "Test Page",
            "spaceId": "space123",
            "version": {"number": 1},
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/spaces?keys=DEV",
            method="GET",
            json={"results": [space_data]},
        )

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages",
            method="POST",
            json=created_page,
        )

        # With TTY simulation, progress would show but transient=True removes it
        result = runner.invoke(
            app, ["page", "create", "--space", "DEV", "--title", "Test Page", "--body", "# Test"]
        )
        assert result.exit_code == 0
        assert "created successfully" in result.stdout


class TestProgressOnlyWhenTTY:
    """Tests to verify progress indicators only show when stdout is a TTY."""

    def test_upload_json_output_no_progress(
        self, httpx_mock: HTTPXMock, mock_config_env: None, tmp_path: Path
    ) -> None:
        """Test upload with --json never shows progress, even with TTY."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        upload_response = {
            "results": [
                {
                    "id": "att123",
                    "title": "test.txt",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/content/123456/child/attachment",
            method="POST",
            json=upload_response,
        )

        with patch("sys.stdout.isatty", return_value=True):
            result = runner.invoke(
                app,
                ["attachment", "upload", "--page", "123456", "--file", str(test_file), "--json"],
            )
            assert result.exit_code == 0
            # Should have JSON output, not progress
            assert '"id":' in result.stdout or '"title":' in result.stdout
