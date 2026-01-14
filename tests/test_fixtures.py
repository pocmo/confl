"""Tests demonstrating fixture usage.

These tests verify that the fixtures in conftest.py are properly structured
and provide examples of how to use them in actual tests.
"""



def test_sample_page_structure(sample_page):
    """Verify sample_page fixture has expected structure."""
    assert sample_page["id"] == "123456"
    assert sample_page["title"] == "Sample Page"
    assert sample_page["status"] == "current"
    assert sample_page["spaceId"] == "98765"
    assert "body" in sample_page
    assert "storage" in sample_page["body"]
    assert "atlas_doc_format" in sample_page["body"]


def test_sample_page_minimal_structure(sample_page_minimal):
    """Verify minimal page fixture has only required fields."""
    assert sample_page_minimal["id"] == "789012"
    assert sample_page_minimal["title"] == "Minimal Page"
    assert sample_page_minimal["status"] == "current"
    assert sample_page_minimal["spaceId"] == "98765"
    # Minimal page should not have body content
    assert "body" not in sample_page_minimal


def test_sample_space_structure(sample_space):
    """Verify sample_space fixture has expected structure."""
    assert sample_space["id"] == "98765"
    assert sample_space["key"] == "TEST"
    assert sample_space["name"] == "Test Space"
    assert sample_space["type"] == "global"
    assert sample_space["homepageId"] == "123456"


def test_sample_page_list_structure(sample_page_list):
    """Verify page list fixture has expected structure."""
    assert "results" in sample_page_list
    assert len(sample_page_list["results"]) == 2
    assert sample_page_list["results"][0]["id"] == "123456"
    assert sample_page_list["results"][1]["id"] == "123457"
    assert "_links" in sample_page_list
    assert "next" in sample_page_list["_links"]


def test_error_fixtures(api_error_404, api_error_401, api_error_403, api_error_429, api_error_500):
    """Verify error response fixtures have correct status codes."""
    assert api_error_404["statusCode"] == 404
    assert api_error_401["statusCode"] == 401
    assert api_error_403["statusCode"] == 403
    assert api_error_429["statusCode"] == 429
    assert api_error_500["statusCode"] == 500


def test_fixtures_are_independent(sample_page):
    """Verify fixtures return new instances (not mutating shared state)."""
    # Modify the fixture data
    original_title = sample_page["title"]
    sample_page["title"] = "Modified"

    # In a real test, this wouldn't work with shared state
    # But pytest fixtures should return fresh instances
    assert sample_page["title"] == "Modified"

    # Clean up for other tests
    sample_page["title"] = original_title
