"""Tests for attachment commands."""

import json
from pathlib import Path

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


class TestAttachmentListCommand:
    """Tests for 'confl attachment list' command."""

    def test_list_attachments_default(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing attachments with default output."""
        attachments_data = {
            "results": [
                {
                    "id": "att123",
                    "title": "diagram.png",
                    "mediaType": "image/png",
                    "fileSize": 51200,
                },
                {
                    "id": "att456",
                    "title": "document.pdf",
                    "mediaType": "application/pdf",
                    "fileSize": 2048000,
                },
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/123456/attachments?limit=25",
            method="GET",
            json=attachments_data,
        )

        result = runner.invoke(app, ["attachment", "list", "--page", "123456"])
        assert result.exit_code == 0
        assert "att123" in result.stdout
        assert "diagram.png" in result.stdout
        assert "att456" in result.stdout
        assert "document.pdf" in result.stdout

    def test_list_attachments_json_output(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test listing attachments with JSON output."""
        attachments_data = {
            "results": [
                {
                    "id": "att123",
                    "title": "diagram.png",
                    "mediaType": "image/png",
                    "fileSize": 1024,
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/123456/attachments?limit=25",
            method="GET",
            json=attachments_data,
        )

        result = runner.invoke(app, ["attachment", "list", "--page", "123456", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert len(output) == 1
        assert output[0]["id"] == "att123"

    def test_list_attachments_empty(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test listing attachments when none exist."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/123456/attachments?limit=25",
            method="GET",
            json={"results": []},
        )

        result = runner.invoke(app, ["attachment", "list", "--page", "123456"])
        assert result.exit_code == 0
        assert "No attachments found" in result.stdout

    def test_list_attachments_page_not_found(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test listing attachments for non-existent page."""
        error_data = {
            "errors": [
                {
                    "status": 404,
                    "title": "Not Found",
                    "detail": "Page with ID 999999 not found",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/999999/attachments?limit=25",
            method="GET",
            status_code=404,
            json=error_data,
        )

        result = runner.invoke(app, ["attachment", "list", "--page", "999999"])
        assert result.exit_code == 1
        assert "Not found" in result.stderr or "Not Found" in result.stderr


class TestAttachmentGetCommand:
    """Tests for 'confl attachment get' command."""

    def test_get_attachment_default(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting attachment metadata with default output."""
        attachment_data = {
            "id": "att123",
            "title": "diagram.png",
            "mediaType": "image/png",
            "fileSize": 51200,
            "webuiLink": "/wiki/spaces/DEV/pages/123456?preview=/att123",
            "downloadLink": "/wiki/download/attachments/123456/diagram.png",
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/attachments/att123",
            method="GET",
            json=attachment_data,
        )

        result = runner.invoke(app, ["attachment", "get", "att123"])
        assert result.exit_code == 0
        assert "att123" in result.stdout
        assert "diagram.png" in result.stdout
        assert "image/png" in result.stdout

    def test_get_attachment_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting attachment metadata with JSON output."""
        attachment_data = {
            "id": "att123",
            "title": "diagram.png",
            "mediaType": "image/png",
            "fileSize": 1024,
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/attachments/att123",
            method="GET",
            json=attachment_data,
        )

        result = runner.invoke(app, ["attachment", "get", "att123", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["id"] == "att123"

    def test_get_attachment_not_found(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test getting non-existent attachment."""
        error_data = {
            "errors": [
                {
                    "status": 404,
                    "title": "Not Found",
                    "detail": "Attachment not found",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/attachments/att999",
            method="GET",
            status_code=404,
            json=error_data,
        )

        result = runner.invoke(app, ["attachment", "get", "att999"])
        assert result.exit_code == 1
        assert "Not found" in result.stderr or "Not Found" in result.stderr


class TestAttachmentDownloadCommand:
    """Tests for 'confl attachment download' command."""

    def test_download_attachment_default_filename(
        self, httpx_mock: HTTPXMock, mock_config_env: None, tmp_path: Path
    ) -> None:
        """Test downloading attachment with default filename."""
        attachment_data = {
            "id": "att123",
            "title": "diagram.png",
            "mediaType": "image/png",
            "fileSize": 10,
            "downloadLink": "/wiki/download/attachments/123456/diagram.png",
        }

        file_content = b"PNG_DATA\x89\x50"

        # Mock metadata request
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/attachments/att123",
            method="GET",
            json=attachment_data,
        )

        # Mock download request
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/download/attachments/123456/diagram.png",
            method="GET",
            content=file_content,
        )

        # Change to tmp directory for test
        import os

        os.chdir(tmp_path)

        result = runner.invoke(app, ["attachment", "download", "att123"])
        assert result.exit_code == 0
        assert "Downloaded" in result.stdout
        assert "diagram.png" in result.stdout

        # Verify file was created
        downloaded = tmp_path / "diagram.png"
        assert downloaded.exists()
        assert downloaded.read_bytes() == file_content

    def test_download_attachment_custom_output(
        self, httpx_mock: HTTPXMock, mock_config_env: None, tmp_path: Path
    ) -> None:
        """Test downloading attachment with custom output path."""
        attachment_data = {
            "id": "att123",
            "title": "diagram.png",
            "downloadLink": "/wiki/download/attachments/123456/diagram.png",
        }

        file_content = b"PNG_DATA"

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

        output_path = tmp_path / "custom_name.png"
        result = runner.invoke(
            app, ["attachment", "download", "att123", "--output", str(output_path)]
        )
        assert result.exit_code == 0
        assert output_path.exists()
        assert output_path.read_bytes() == file_content

    def test_download_attachment_not_found(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test downloading non-existent attachment."""
        error_data = {
            "errors": [{"status": 404, "title": "Not Found", "detail": "Attachment not found"}]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/attachments/att999",
            method="GET",
            status_code=404,
            json=error_data,
        )

        result = runner.invoke(app, ["attachment", "download", "att999"])
        assert result.exit_code == 1


class TestAttachmentUploadCommand:
    """Tests for 'confl attachment upload' command."""

    def test_upload_attachment_success(
        self, httpx_mock: HTTPXMock, mock_config_env: None, tmp_path: Path
    ) -> None:
        """Test uploading an attachment."""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        upload_response = {
            "results": [
                {
                    "id": "att123",
                    "title": "test.txt",
                    "type": "attachment",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/content/123456/child/attachment",
            method="POST",
            json=upload_response,
        )

        result = runner.invoke(
            app, ["attachment", "upload", "--page", "123456", "--file", str(test_file)]
        )
        assert result.exit_code == 0
        assert "Uploaded" in result.stdout
        assert "test.txt" in result.stdout

    def test_upload_attachment_with_comment(
        self, httpx_mock: HTTPXMock, mock_config_env: None, tmp_path: Path
    ) -> None:
        """Test uploading an attachment with comment."""
        test_file = tmp_path / "doc.pdf"
        test_file.write_bytes(b"PDF content")

        upload_response = {
            "results": [
                {
                    "id": "att456",
                    "title": "doc.pdf",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/content/123456/child/attachment",
            method="POST",
            json=upload_response,
        )

        result = runner.invoke(
            app,
            [
                "attachment",
                "upload",
                "--page",
                "123456",
                "--file",
                str(test_file),
                "--comment",
                "Updated docs",
            ],
        )
        assert result.exit_code == 0

    def test_upload_attachment_file_not_found(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test uploading non-existent file."""
        result = runner.invoke(
            app,
            ["attachment", "upload", "--page", "123456", "--file", "/nonexistent/file.txt"],
        )
        assert result.exit_code == 1
        assert "File not found" in result.stderr

    def test_upload_attachment_json_output(
        self, httpx_mock: HTTPXMock, mock_config_env: None, tmp_path: Path
    ) -> None:
        """Test uploading attachment with JSON output."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

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

        result = runner.invoke(
            app, ["attachment", "upload", "--page", "123456", "--file", str(test_file), "--json"]
        )
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["id"] == "att123"


class TestAttachmentDeleteCommand:
    """Tests for 'confl attachment delete' command."""

    def test_delete_attachment_success(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test deleting an attachment."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/attachments/att123",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["attachment", "delete", "att123"])
        assert result.exit_code == 0
        assert "Deleted" in result.stdout

    def test_delete_attachment_already_deleted(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test deleting an already deleted attachment (idempotent)."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/attachments/att123",
            method="DELETE",
            status_code=404,
        )

        result = runner.invoke(app, ["attachment", "delete", "att123"])
        assert result.exit_code == 0
        assert "Deleted" in result.stdout

    def test_delete_attachment_json_output(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test deleting attachment with JSON output."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/attachments/att123",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["attachment", "delete", "att123", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["success"] is True
        assert output["id"] == "att123"

    def test_delete_attachment_with_yes_flag(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test deleting an attachment with --yes flag bypasses confirmation."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/attachments/att123",
            method="DELETE",
            status_code=204,
        )

        result = runner.invoke(app, ["attachment", "delete", "att123", "--yes"])
        assert result.exit_code == 0
        assert "Deleted attachment" in result.stdout
        # Should not contain confirmation prompt
        assert "Are you sure" not in result.stdout


class TestPageIdExtraction:
    """Tests for page ID extraction from URLs."""

    def test_extract_id_from_url(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test extracting page ID from URL."""
        attachments_data = {"results": []}

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/123456/attachments?limit=25",
            method="GET",
            json=attachments_data,
        )

        result = runner.invoke(
            app,
            [
                "attachment",
                "list",
                "--page",
                "https://example.atlassian.net/wiki/spaces/DEV/pages/123456/Page+Title",
            ],
        )
        assert result.exit_code == 0

    def test_extract_id_from_relative_url(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test extracting page ID from relative URL."""
        attachments_data = {"results": []}

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/api/v2/pages/789/attachments?limit=25",
            method="GET",
            json=attachments_data,
        )

        result = runner.invoke(
            app, ["attachment", "list", "--page", "/wiki/spaces/DEV/pages/789/Title"]
        )
        assert result.exit_code == 0
