"""Tests for enhanced error messages."""

import pytest
from httpx import Response
from typer.testing import CliRunner

from confl.client import ApiError, handle_api_error
from confl.config import ConfigError, _validate_and_create_config
from confl.utils.blogpost_helpers import extract_blogpost_id
from confl.utils.page_helpers import extract_page_id

runner = CliRunner()


class TestApiErrorMessages:
    """Test enhanced API error messages."""

    def test_401_error_includes_suggestions(self):
        """401 errors should include actionable suggestions."""
        response = Response(
            status_code=401,
            json={"errors": [{"title": "Unauthorized", "detail": "Invalid credentials"}]},
        )

        with pytest.raises(ApiError) as exc_info:
            handle_api_error(response)

        error_msg = str(exc_info.value)
        assert "Authentication failed" in error_msg
        assert "confl auth status" in error_msg
        assert "confl auth login" in error_msg
        assert "api-tokens" in error_msg

    def test_403_error_includes_suggestions(self):
        """403 errors should include actionable suggestions."""
        response = Response(
            status_code=403,
            json={"errors": [{"title": "Forbidden", "detail": "Access denied"}]},
        )

        with pytest.raises(ApiError) as exc_info:
            handle_api_error(response)

        error_msg = str(exc_info.value)
        assert "Permission denied" in error_msg
        assert "permission to access" in error_msg
        assert "administrator" in error_msg

    def test_404_error_includes_suggestions(self):
        """404 errors should include actionable suggestions."""
        response = Response(
            status_code=404,
            json={"errors": [{"title": "Not Found", "detail": "Page not found"}]},
        )

        with pytest.raises(ApiError) as exc_info:
            handle_api_error(response)

        error_msg = str(exc_info.value)
        assert "Not found" in error_msg
        assert "deleted or moved" in error_msg
        assert "confl search" in error_msg

    def test_409_error_includes_suggestions(self):
        """409 errors should include actionable suggestions."""
        response = Response(
            status_code=409,
            json={"errors": [{"title": "Conflict", "detail": "Version mismatch"}]},
        )

        with pytest.raises(ApiError) as exc_info:
            handle_api_error(response)

        error_msg = str(exc_info.value)
        assert "Version conflict" in error_msg
        assert "Fetch the latest version" in error_msg
        assert "confl page get" in error_msg

    def test_429_error_includes_suggestions(self):
        """429 errors should include actionable suggestions."""
        response = Response(
            status_code=429,
            json={"errors": [{"title": "Rate Limit", "detail": "Too many requests"}]},
        )

        with pytest.raises(ApiError) as exc_info:
            handle_api_error(response)

        error_msg = str(exc_info.value)
        assert "Rate limit exceeded" in error_msg
        assert "Wait 60 seconds" in error_msg
        assert "delays between bulk operations" in error_msg


class TestConfigErrorMessages:
    """Test enhanced configuration error messages."""

    def test_invalid_site_error_message(self):
        """Invalid site should include format examples."""
        with pytest.raises(ConfigError) as exc_info:
            _validate_and_create_config("https://site.com", "user@example.com", "token")

        error_msg = str(exc_info.value)
        assert "Invalid site" in error_msg
        assert "mycompany.atlassian.net" in error_msg
        assert "not a full URL" in error_msg

    def test_invalid_email_error_message(self):
        """Invalid email should include format example."""
        with pytest.raises(ConfigError) as exc_info:
            _validate_and_create_config("site.atlassian.net", "invalid-email", "token")

        error_msg = str(exc_info.value)
        assert "Invalid email" in error_msg
        assert "user@example.com" in error_msg

    def test_empty_token_error_message(self):
        """Empty token should include creation instructions."""
        with pytest.raises(ConfigError) as exc_info:
            _validate_and_create_config("site.atlassian.net", "user@example.com", "")

        error_msg = str(exc_info.value)
        assert "API token cannot be empty" in error_msg
        assert "api-tokens" in error_msg
        assert "Create API token" in error_msg


class TestPageReferenceErrorMessages:
    """Test enhanced page reference error messages."""

    def test_invalid_page_reference_error_message(self):
        """Invalid page reference should include format examples."""
        with pytest.raises(ValueError) as exc_info:
            extract_page_id("invalid-ref")

        error_msg = str(exc_info.value)
        assert "Invalid page reference" in error_msg
        assert "numeric page ID" in error_msg
        assert "full Confluence page URL" in error_msg
        assert "confl page get 12345678" in error_msg
        assert "confl search" in error_msg

    def test_valid_numeric_id(self):
        """Valid numeric ID should work."""
        assert extract_page_id("12345678") == "12345678"

    def test_valid_url(self):
        """Valid URL should extract ID."""
        url = "https://company.atlassian.net/wiki/spaces/DEV/pages/12345678/Title"
        assert extract_page_id(url) == "12345678"


class TestBlogpostReferenceErrorMessages:
    """Test enhanced blogpost reference error messages."""

    def test_invalid_blogpost_reference_error_message(self):
        """Invalid blogpost reference should include format examples."""
        with pytest.raises(ValueError) as exc_info:
            extract_blogpost_id("invalid-ref")

        error_msg = str(exc_info.value)
        assert "Invalid blog post reference" in error_msg
        assert "numeric blog post ID" in error_msg
        assert "full Confluence blog post URL" in error_msg
        assert "confl blogpost get 12345678" in error_msg
        assert "confl search" in error_msg

    def test_valid_blogpost_numeric_id(self):
        """Valid numeric ID should work."""
        assert extract_blogpost_id("12345678") == "12345678"

    def test_valid_blogpost_url(self):
        """Valid URL should extract ID."""
        url = "https://company.atlassian.net/wiki/spaces/DEV/blogposts/12345678/Title"
        assert extract_blogpost_id(url) == "12345678"
