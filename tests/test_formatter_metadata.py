"""Tests for page and blogpost metadata formatting."""

from confl.formatters.blogpost_formatter import (
    format_blogpost_metadata,
    get_blogpost_content,
)
from confl.formatters.page_formatter import format_page_metadata, get_page_content


class TestFormatPageMetadata:
    """Tests for format_page_metadata function."""

    def test_minimal_page(self):
        """Test formatting page with minimal data."""
        page = {"title": "Test Page"}
        result = format_page_metadata(page)

        assert "Title: Test Page" in result
        assert "---" in result

    def test_page_with_space(self):
        """Test formatting page with space ID."""
        page = {"title": "Test Page", "spaceId": "SPACE123"}
        result = format_page_metadata(page)

        assert "Title: Test Page" in result
        assert "Space: SPACE123" in result
        assert "---" in result

    def test_page_with_author(self):
        """Test formatting page with author."""
        page = {
            "title": "Test Page",
            "version": {"authorId": "user123"},
        }
        result = format_page_metadata(page)

        assert "Title: Test Page" in result
        assert "Author: user123" in result
        assert "---" in result

    def test_page_with_timestamp(self):
        """Test formatting page with timestamp."""
        page = {
            "title": "Test Page",
            "version": {"createdAt": "2024-01-15T12:00:00.000Z"},
        }
        result = format_page_metadata(page)

        assert "Title: Test Page" in result
        assert "Updated:" in result
        assert "ago" in result or "just now" in result
        assert "---" in result

    def test_page_with_all_fields(self):
        """Test formatting page with all metadata fields."""
        page = {
            "title": "Complete Page",
            "spaceId": "SPACE123",
            "version": {
                "authorId": "user456",
                "createdAt": "2024-01-15T12:00:00.000Z",
            },
        }
        result = format_page_metadata(page)

        assert "Title: Complete Page" in result
        assert "Space: SPACE123" in result
        assert "Author: user456" in result
        assert "Updated:" in result
        assert "---" in result

    def test_page_with_empty_version(self):
        """Test formatting page with empty version object."""
        page = {"title": "Test Page", "version": {}}
        result = format_page_metadata(page)

        assert "Title: Test Page" in result
        assert "Author:" not in result
        assert "Updated:" not in result
        assert "---" in result


class TestGetPageContent:
    """Tests for get_page_content function."""

    def test_get_storage_format_content(self):
        """Test extracting content in storage format."""
        page = {
            "body": {
                "storage": {"value": "<p>Test content</p>"},
            }
        }
        result = get_page_content(page, "storage")
        assert result == "<p>Test content</p>"

    def test_get_atlas_doc_format_content(self):
        """Test extracting content in atlas_doc_format."""
        page = {
            "body": {
                "atlas_doc_format": {"value": '{"type": "doc", "content": []}'},
            }
        }
        result = get_page_content(page, "atlas_doc_format")
        assert result == '{"type": "doc", "content": []}'

    def test_get_content_default_format(self):
        """Test extracting content with default format."""
        page = {
            "body": {
                "storage": {"value": "<p>Default format</p>"},
            }
        }
        result = get_page_content(page)
        assert result == "<p>Default format</p>"

    def test_get_content_missing_body(self):
        """Test extracting content when body is missing."""
        page = {}
        result = get_page_content(page)
        assert result == ""

    def test_get_content_missing_format(self):
        """Test extracting content when format is missing."""
        page = {"body": {}}
        result = get_page_content(page, "storage")
        assert result == ""

    def test_get_content_missing_value(self):
        """Test extracting content when value is missing."""
        page = {"body": {"storage": {}}}
        result = get_page_content(page)
        assert result == ""


class TestFormatBlogpostMetadata:
    """Tests for format_blogpost_metadata function."""

    def test_minimal_blogpost(self):
        """Test formatting blog post with minimal data."""
        blogpost = {"title": "Test Post"}
        result = format_blogpost_metadata(blogpost)

        assert "Title: Test Post" in result
        assert "---" in result

    def test_blogpost_with_space(self):
        """Test formatting blog post with space ID."""
        blogpost = {"title": "Test Post", "spaceId": "BLOG123"}
        result = format_blogpost_metadata(blogpost)

        assert "Title: Test Post" in result
        assert "Space: BLOG123" in result
        assert "---" in result

    def test_blogpost_with_author(self):
        """Test formatting blog post with author."""
        blogpost = {
            "title": "Test Post",
            "version": {"authorId": "blogger123"},
        }
        result = format_blogpost_metadata(blogpost)

        assert "Title: Test Post" in result
        assert "Author: blogger123" in result
        assert "---" in result

    def test_blogpost_with_timestamp(self):
        """Test formatting blog post with timestamp."""
        blogpost = {
            "title": "Test Post",
            "version": {"createdAt": "2024-01-15T12:00:00.000Z"},
        }
        result = format_blogpost_metadata(blogpost)

        assert "Title: Test Post" in result
        assert "Published:" in result
        assert "ago" in result or "just now" in result
        assert "---" in result

    def test_blogpost_with_all_fields(self):
        """Test formatting blog post with all metadata fields."""
        blogpost = {
            "title": "Complete Post",
            "spaceId": "BLOG123",
            "version": {
                "authorId": "blogger456",
                "createdAt": "2024-01-15T12:00:00.000Z",
            },
        }
        result = format_blogpost_metadata(blogpost)

        assert "Title: Complete Post" in result
        assert "Space: BLOG123" in result
        assert "Author: blogger456" in result
        assert "Published:" in result
        assert "---" in result


class TestGetBlogpostContent:
    """Tests for get_blogpost_content function."""

    def test_get_storage_format_content(self):
        """Test extracting blog post content in storage format."""
        blogpost = {
            "body": {
                "storage": {"value": "<p>Blog content</p>"},
            }
        }
        result = get_blogpost_content(blogpost, "storage")
        assert result == "<p>Blog content</p>"

    def test_get_atlas_doc_format_content(self):
        """Test extracting blog post content in atlas_doc_format."""
        blogpost = {
            "body": {
                "atlas_doc_format": {"value": '{"type": "doc"}'},
            }
        }
        result = get_blogpost_content(blogpost, "atlas_doc_format")
        assert result == '{"type": "doc"}'

    def test_get_content_default_format(self):
        """Test extracting blog post content with default format."""
        blogpost = {
            "body": {
                "storage": {"value": "<p>Default content</p>"},
            }
        }
        result = get_blogpost_content(blogpost)
        assert result == "<p>Default content</p>"

    def test_get_content_missing_body(self):
        """Test extracting blog post content when body is missing."""
        blogpost = {}
        result = get_blogpost_content(blogpost)
        assert result == ""

    def test_get_content_missing_format(self):
        """Test extracting blog post content when format is missing."""
        blogpost = {"body": {}}
        result = get_blogpost_content(blogpost, "storage")
        assert result == ""

    def test_get_content_missing_value(self):
        """Test extracting blog post content when value is missing."""
        blogpost = {"body": {"storage": {}}}
        result = get_blogpost_content(blogpost)
        assert result == ""
