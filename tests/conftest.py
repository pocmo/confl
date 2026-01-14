"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_page():
    """Sample Confluence page response from API v2.

    Represents a typical page with storage format body content.
    Based on: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-id-get
    """
    return {
        "id": "123456",
        "status": "current",
        "title": "Sample Page",
        "spaceId": "98765",
        "authorId": "557058:f1c5e1e2-8a6f-4e4d-8e9a-1234567890ab",
        "createdAt": "2024-01-15T10:30:00.000Z",
        "version": {
            "number": 3,
            "message": "Updated content",
            "minorEdit": False,
            "authorId": "557058:f1c5e1e2-8a6f-4e4d-8e9a-1234567890ab",
            "createdAt": "2024-01-15T14:22:00.000Z",
        },
        "body": {
            "storage": {
                "value": "<p>This is sample page content with <strong>formatting</strong>.</p>",
                "representation": "storage",
            },
            "atlas_doc_format": {
                "value": (
                    '{"type":"doc","version":1,"content":[{"type":"paragraph",'
                    '"content":[{"type":"text","text":"This is sample page content with "},'
                    '{"type":"text","text":"formatting","marks":[{"type":"strong"}]},'
                    '{"type":"text","text":"."}]}]}'
                ),
                "representation": "atlas_doc_format",
            },
        },
        "_links": {
            "webui": "/wiki/spaces/TEST/pages/123456/Sample+Page",
            "editui": "/wiki/pages/resumedraft.action?draftId=123456",
            "tinyui": "/wiki/x/ABCD",
        },
    }


@pytest.fixture
def sample_page_minimal():
    """Minimal page response with only required fields.

    Useful for testing edge cases where optional fields are missing.
    """
    return {
        "id": "789012",
        "status": "current",
        "title": "Minimal Page",
        "spaceId": "98765",
    }


@pytest.fixture
def sample_space():
    """Sample Confluence space response from API v2.

    Based on: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-space/
    """
    return {
        "id": "98765",
        "key": "TEST",
        "name": "Test Space",
        "type": "global",
        "status": "current",
        "authorId": "557058:f1c5e1e2-8a6f-4e4d-8e9a-1234567890ab",
        "createdAt": "2023-06-01T09:00:00.000Z",
        "homepageId": "123456",
        "description": {
            "plain": {
                "value": "A test space for development",
                "representation": "plain",
            }
        },
        "_links": {
            "webui": "/wiki/spaces/TEST",
        },
    }


@pytest.fixture
def sample_page_list():
    """Sample paginated list of pages from API v2.

    Represents the structure returned by list endpoints.
    """
    return {
        "results": [
            {
                "id": "123456",
                "status": "current",
                "title": "First Page",
                "spaceId": "98765",
            },
            {
                "id": "123457",
                "status": "current",
                "title": "Second Page",
                "spaceId": "98765",
            },
        ],
        "_links": {
            "next": "/wiki/api/v2/pages?cursor=abc123",
        },
    }


@pytest.fixture
def api_error_404():
    """Sample 404 Not Found error response.

    Standard error format returned by Confluence API v2.
    """
    return {
        "statusCode": 404,
        "data": {
            "authorized": True,
            "valid": True,
            "allowedInReadOnlyMode": True,
            "errors": [],
            "successful": False,
        },
        "message": "Page not found",
        "reason": "Not Found",
    }


@pytest.fixture
def api_error_401():
    """Sample 401 Unauthorized error response."""
    return {
        "statusCode": 401,
        "message": "Unauthorized",
        "reason": "Unauthorized",
    }


@pytest.fixture
def api_error_403():
    """Sample 403 Forbidden error response."""
    return {
        "statusCode": 403,
        "data": {
            "authorized": False,
            "valid": True,
            "allowedInReadOnlyMode": False,
            "errors": [],
            "successful": False,
        },
        "message": "Forbidden - insufficient permissions",
        "reason": "Forbidden",
    }


@pytest.fixture
def api_error_429():
    """Sample 429 Rate Limit error response."""
    return {
        "statusCode": 429,
        "message": "Rate limit exceeded",
        "reason": "Too Many Requests",
    }


@pytest.fixture
def api_error_500():
    """Sample 500 Internal Server Error response."""
    return {
        "statusCode": 500,
        "message": "Internal server error",
        "reason": "Internal Server Error",
    }
