"""Tests for search command."""

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


class TestSearchCommand:
    """Tests for 'confl search' command."""

    def test_search_with_raw_cql(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test search with raw CQL query."""
        search_results = {
            "results": [
                {
                    "content": {
                        "id": "123",
                        "type": "page",
                        "space": {"key": "DEV"},
                    },
                    "title": "API Documentation",
                },
                {
                    "content": {
                        "id": "456",
                        "type": "page",
                        "space": {"key": "DEV"},
                    },
                    "title": "Getting Started",
                },
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=space+%3D+DEV+AND+type+%3D+page&limit=25",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(app, ["search", "space = DEV AND type = page"])
        assert result.exit_code == 0
        assert "API Documentation" in result.stdout
        assert "Getting Started" in result.stdout
        assert "DEV" in result.stdout

    def test_search_with_text_flag(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test search with --text flag."""
        search_results = {
            "results": [
                {
                    "content": {
                        "id": "789",
                        "type": "page",
                        "space": {"key": "DOCS"},
                    },
                    "title": "Database Migration Guide",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=text+~+%22database+migration%22&limit=25",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(app, ["search", "--text", "database migration"])
        assert result.exit_code == 0
        assert "Database Migration Guide" in result.stdout
        assert "DOCS" in result.stdout

    def test_search_with_space_flag(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test search with --space flag."""
        search_results = {
            "results": [
                {
                    "content": {
                        "id": "111",
                        "type": "page",
                        "space": {"key": "ENG"},
                    },
                    "title": "Engineering Process",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=space+%3D+ENG&limit=25",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(app, ["search", "--space", "ENG"])
        assert result.exit_code == 0
        assert "Engineering Process" in result.stdout

    def test_search_with_type_flag(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test search with --type flag."""
        search_results = {
            "results": [
                {
                    "content": {
                        "id": "222",
                        "type": "blogpost",
                        "space": {"key": "NEWS"},
                    },
                    "title": "Product Release Notes",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=type+%3D+blogpost&limit=25",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(app, ["search", "--type", "blogpost"])
        assert result.exit_code == 0
        assert "Product Release Notes" in result.stdout
        assert "blogpost" in result.stdout

    def test_search_with_label_flag(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test search with --label flag."""
        search_results = {
            "results": [
                {
                    "content": {
                        "id": "333",
                        "type": "page",
                        "space": {"key": "ARCH"},
                    },
                    "title": "System Architecture",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=label+%3D+architecture&limit=25",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(app, ["search", "--label", "architecture"])
        assert result.exit_code == 0
        assert "System Architecture" in result.stdout

    def test_search_with_multiple_flags(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test search with multiple flags combined."""
        search_results = {
            "results": [
                {
                    "content": {
                        "id": "444",
                        "type": "page",
                        "space": {"key": "TEAM"},
                    },
                    "title": "Weekly Meeting Notes",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=text+~+%22meeting+notes%22+AND+space+%3D+TEAM+AND+type+%3D+page&limit=25",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(
            app,
            ["search", "--text", "meeting notes", "--space", "TEAM", "--type", "page"],
        )
        assert result.exit_code == 0
        assert "Weekly Meeting Notes" in result.stdout

    def test_search_with_all_flags(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test search with all four flags."""
        search_results = {
            "results": [
                {
                    "content": {
                        "id": "555",
                        "type": "page",
                        "space": {"key": "PROJ"},
                    },
                    "title": "Q4 Project Update",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=text+~+%22project+update%22+AND+space+%3D+PROJ+AND+type+%3D+page+AND+label+%3D+2024&limit=25",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(
            app,
            [
                "search",
                "--text",
                "project update",
                "--space",
                "PROJ",
                "--type",
                "page",
                "--label",
                "2024",
            ],
        )
        assert result.exit_code == 0
        assert "Q4 Project Update" in result.stdout

    def test_search_with_custom_limit(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test search with custom limit."""
        search_results = {"results": []}

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=space+%3D+DEV&limit=50",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(app, ["search", "--space", "DEV", "--limit", "50"])
        assert result.exit_code == 0

    def test_search_json_output(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test search with JSON output."""
        search_results = {
            "results": [
                {
                    "content": {
                        "id": "666",
                        "type": "page",
                        "space": {"key": "TEST"},
                    },
                    "title": "Test Page",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=space+%3D+TEST&limit=25",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(app, ["search", "--space", "TEST", "--json"])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert len(output) == 1
        assert output[0]["title"] == "Test Page"
        assert output[0]["content"]["id"] == "666"

    def test_search_empty_results(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test search with no results."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=space+%3D+EMPTY&limit=25",
            method="GET",
            json={"results": []},
        )

        result = runner.invoke(app, ["search", "--space", "EMPTY"])
        assert result.exit_code == 0
        assert "No results found" in result.stdout

    def test_search_missing_space_key(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test search result without space key."""
        search_results = {
            "results": [
                {
                    "content": {
                        "id": "777",
                        "type": "page",
                    },
                    "title": "Orphaned Page",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=type+%3D+page&limit=25",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(app, ["search", "--type", "page"])
        assert result.exit_code == 0
        assert "Orphaned Page" in result.stdout

    def test_search_untitled_content(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test search result without title."""
        search_results = {
            "results": [
                {
                    "content": {
                        "id": "888",
                        "type": "page",
                        "space": {"key": "TEST"},
                    },
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=space+%3D+TEST&limit=25",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(app, ["search", "--space", "TEST"])
        assert result.exit_code == 0
        assert "Untitled" in result.stdout

    def test_search_error_mixing_cql_and_flags(self, mock_config_env: None) -> None:
        """Test error when mixing raw CQL with flags."""
        result = runner.invoke(app, ["search", "space = DEV", "--text", "something"])
        assert result.exit_code == 1
        assert "Cannot use both raw CQL query and filter flags" in result.stderr

    def test_search_error_no_criteria(self, mock_config_env: None) -> None:
        """Test error when no search criteria provided."""
        result = runner.invoke(app, ["search"])
        assert result.exit_code == 1
        assert "No search criteria provided" in result.stderr

    def test_search_with_text_containing_quotes(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test search with text containing special characters."""
        search_results = {
            "results": [
                {
                    "content": {
                        "id": "999",
                        "type": "page",
                        "space": {"key": "DEV"},
                    },
                    "title": "The Best Solution",
                }
            ]
        }

        # CQL builder should escape quotes in text
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=text+~+%22The+%5C%22best%5C%22+solution%22&limit=25",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(app, ["search", "--text", 'The "best" solution'])
        assert result.exit_code == 0
        assert "The Best Solution" in result.stdout

    def test_search_with_space_containing_spaces(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test search with space key containing spaces."""
        search_results = {
            "results": [
                {
                    "content": {
                        "id": "1000",
                        "type": "page",
                        "space": {"key": "MY SPACE"},
                    },
                    "title": "Test Page",
                }
            ]
        }

        # CQL builder should quote space keys with spaces
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=space+%3D+%22MY+SPACE%22&limit=25",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(app, ["search", "--space", "MY SPACE"])
        assert result.exit_code == 0
        assert "Test Page" in result.stdout

    def test_search_api_error(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test handling of API errors."""
        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=invalid+query&limit=25",
            method="GET",
            status_code=400,
            json={
                "statusCode": 400,
                "message": "Invalid CQL query",
            },
        )

        result = runner.invoke(app, ["search", "invalid query"])
        assert result.exit_code == 1
        assert "Error" in result.stderr

    def test_search_api_error_json_output(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test API errors with JSON output mode."""
        error_response = {
            "statusCode": 400,
            "message": "Invalid CQL query",
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=space+%3D+BAD&limit=25",
            method="GET",
            status_code=400,
            json=error_response,
        )

        result = runner.invoke(app, ["search", "--space", "BAD", "--json"])
        assert result.exit_code == 1
        # In JSON mode, error response should be in stderr as JSON
        assert "Invalid CQL query" in result.stderr

    def test_search_displays_result_count(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test that result count is displayed."""
        search_results = {
            "results": [
                {
                    "content": {"id": "1", "type": "page", "space": {"key": "DEV"}},
                    "title": "Page 1",
                },
                {
                    "content": {"id": "2", "type": "page", "space": {"key": "DEV"}},
                    "title": "Page 2",
                },
                {
                    "content": {"id": "3", "type": "page", "space": {"key": "DEV"}},
                    "title": "Page 3",
                },
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=space+%3D+DEV&limit=25",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(app, ["search", "--space", "DEV"])
        assert result.exit_code == 0
        assert "Found 3 result(s)" in result.stdout

    def test_search_table_columns(self, httpx_mock: HTTPXMock, mock_config_env: None) -> None:
        """Test that table has correct columns."""
        search_results = {
            "results": [
                {
                    "content": {
                        "id": "12345",
                        "type": "page",
                        "space": {"key": "ENG"},
                    },
                    "title": "Engineering Guide",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=space+%3D+ENG&limit=25",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(app, ["search", "--space", "ENG"])
        assert result.exit_code == 0
        # Table should display type, ID, title, and space
        assert "page" in result.stdout
        assert "12345" in result.stdout
        assert "Engineering Guide" in result.stdout
        assert "ENG" in result.stdout

    def test_search_decodes_html_entities_in_titles(
        self, httpx_mock: HTTPXMock, mock_config_env: None
    ) -> None:
        """Test that HTML entities in titles are decoded."""
        search_results = {
            "results": [
                {
                    "content": {
                        "id": "1001",
                        "type": "page",
                        "space": {"key": "TEST"},
                    },
                    "title": "Monopoly Prioritization &amp; Stakeholder Interviews",
                },
                {
                    "content": {
                        "id": "1002",
                        "type": "page",
                        "space": {"key": "TEST"},
                    },
                    "title": "Q&amp;A Session &lt;Draft&gt;",
                },
            ]
        }

        httpx_mock.add_response(
            url="https://example.atlassian.net/wiki/rest/api/search?cql=space+%3D+TEST&limit=25",
            method="GET",
            json=search_results,
        )

        result = runner.invoke(app, ["search", "--space", "TEST"])
        assert result.exit_code == 0
        # HTML entities should be decoded in output
        assert "Monopoly Prioritization & Stakeholder Interviews" in result.stdout
        assert "Q&A Session <Draft>" in result.stdout
        # Raw HTML entities should NOT appear
        assert "&amp;" not in result.stdout
        assert "&lt;" not in result.stdout
        assert "&gt;" not in result.stdout
