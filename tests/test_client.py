"""Tests for HTTP client."""

import base64

import httpx
import pytest
from pytest_httpx import HTTPXMock

from confl.client import ApiError, ConfluenceClient, create_client, get_client, handle_api_error
from confl.config import Config


def test_create_client():
    """Test creating client with config."""
    config = Config(
        site="mycompany.atlassian.net",
        email="user@example.com",
        token="test-token-123",
    )

    client = create_client(config)

    # Check base URL (httpx adds trailing slash)
    assert str(client.base_url) == "https://mycompany.atlassian.net/wiki/api/v2/"

    # Check auth header
    expected_creds = base64.b64encode(b"user@example.com:test-token-123").decode()
    assert client.headers["Authorization"] == f"Basic {expected_creds}"

    # Check other headers
    assert client.headers["Accept"] == "application/json"
    assert client.headers["Content-Type"] == "application/json"

    # Check timeout
    assert client.timeout.read == 30.0


def test_get_client_with_env_vars(monkeypatch):
    """Test get_client loads config from env vars."""
    monkeypatch.setenv("CONFL_SITE", "test.atlassian.net")
    monkeypatch.setenv("CONFL_EMAIL", "test@example.com")
    monkeypatch.setenv("CONFL_TOKEN", "token123")

    client = get_client()

    assert str(client.base_url) == "https://test.atlassian.net/wiki/api/v2/"
    expected_creds = base64.b64encode(b"test@example.com:token123").decode()
    assert client.headers["Authorization"] == f"Basic {expected_creds}"


def test_get_client_with_credentials_file(tmp_path, monkeypatch):
    """Test get_client loads config from credentials file."""
    # Setup credentials file
    config_dir = tmp_path / ".config" / "confl"
    config_dir.mkdir(parents=True)
    creds_file = config_dir / "credentials.toml"
    creds_file.write_text(
        'site = "file.atlassian.net"\nemail = "file@example.com"\ntoken = "file-token"\n'
    )

    # Point to test credentials file
    monkeypatch.setenv("HOME", str(tmp_path))
    # Clear any CONFL_ env vars
    for key in ["CONFL_SITE", "CONFL_EMAIL", "CONFL_TOKEN"]:
        monkeypatch.delenv(key, raising=False)

    client = get_client()

    assert str(client.base_url) == "https://file.atlassian.net/wiki/api/v2/"
    expected_creds = base64.b64encode(b"file@example.com:file-token").decode()
    assert client.headers["Authorization"] == f"Basic {expected_creds}"


def test_get_client_no_config_exits(monkeypatch, capsys):
    """Test get_client exits with code 2 when no config found."""
    # Clear env vars and ensure no credentials file
    for key in ["CONFL_SITE", "CONFL_EMAIL", "CONFL_TOKEN", "HOME"]:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("HOME", "/nonexistent")

    with pytest.raises(SystemExit) as exc_info:
        get_client()

    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "No configuration found" in captured.err


def test_get_client_invalid_config_exits(monkeypatch, capsys):
    """Test get_client exits with code 2 when config is invalid."""
    monkeypatch.setenv("CONFL_SITE", "https://bad-url")
    monkeypatch.setenv("CONFL_EMAIL", "invalid-email")
    monkeypatch.setenv("CONFL_TOKEN", "token")

    with pytest.raises(SystemExit) as exc_info:
        get_client()

    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "Invalid site" in captured.err


def test_handle_api_error_401():
    """Test handling 401 unauthorized error."""
    response = httpx.Response(
        status_code=401,
        json={"message": "Invalid credentials"},
    )

    with pytest.raises(ApiError) as exc_info:
        handle_api_error(response)

    assert exc_info.value.status_code == 401
    assert "Authentication failed" in str(exc_info.value)
    assert "confl auth status" in str(exc_info.value)


def test_handle_api_error_403():
    """Test handling 403 forbidden error."""
    response = httpx.Response(
        status_code=403,
        json={"message": "Insufficient permissions"},
    )

    with pytest.raises(ApiError) as exc_info:
        handle_api_error(response)

    assert exc_info.value.status_code == 403
    assert "Permission denied" in str(exc_info.value)


def test_handle_api_error_404():
    """Test handling 404 not found error."""
    response = httpx.Response(
        status_code=404,
        json={"message": "Page not found"},
    )

    with pytest.raises(ApiError) as exc_info:
        handle_api_error(response)

    assert exc_info.value.status_code == 404
    assert "Not found" in str(exc_info.value)


def test_handle_api_error_429():
    """Test handling 429 rate limit error."""
    response = httpx.Response(
        status_code=429,
        json={"message": "Too many requests"},
    )

    with pytest.raises(ApiError) as exc_info:
        handle_api_error(response)

    assert exc_info.value.status_code == 429
    assert "Rate limit exceeded" in str(exc_info.value)


def test_handle_api_error_400():
    """Test handling 400 bad request error."""
    response = httpx.Response(
        status_code=400,
        json={"message": "Invalid request"},
    )

    with pytest.raises(ApiError) as exc_info:
        handle_api_error(response)

    assert exc_info.value.status_code == 400
    assert "Client error (400)" in str(exc_info.value)


def test_handle_api_error_500():
    """Test handling 500 server error."""
    response = httpx.Response(
        status_code=500,
        json={"message": "Internal server error"},
    )

    with pytest.raises(ApiError) as exc_info:
        handle_api_error(response)

    assert exc_info.value.status_code == 500
    assert "Server error (500)" in str(exc_info.value)
    assert "try again later" in str(exc_info.value)


def test_handle_api_error_no_json():
    """Test handling error response without JSON body."""
    response = httpx.Response(
        status_code=500,
        text="Internal Server Error",
    )

    with pytest.raises(ApiError) as exc_info:
        handle_api_error(response)

    assert exc_info.value.status_code == 500
    assert "Internal Server Error" in str(exc_info.value)


def test_handle_api_error_empty_body():
    """Test handling error response with empty body."""
    response = httpx.Response(
        status_code=503,
        text="",
    )

    with pytest.raises(ApiError) as exc_info:
        handle_api_error(response)

    assert exc_info.value.status_code == 503
    assert "HTTP 503" in str(exc_info.value)


def test_api_error_properties():
    """Test ApiError properties."""
    error = ApiError("Test error message", status_code=404)

    assert str(error) == "Test error message"
    assert error.message == "Test error message"
    assert error.status_code == 404


def test_api_error_without_status():
    """Test ApiError without status code."""
    error = ApiError("Test error")

    assert str(error) == "Test error"
    assert error.message == "Test error"
    assert error.status_code is None


def test_confluence_client_get_page(httpx_mock: HTTPXMock):
    """Test getting a page by ID."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    # Mock successful response
    page_data = {
        "id": "12345",
        "status": "current",
        "title": "Test Page",
        "spaceId": "67890",
        "body": {
            "storage": {
                "value": "<p>Test content</p>",
                "representation": "storage",
            },
            "atlas_doc_format": {
                "value": '{"type":"doc","content":[]}',
                "representation": "atlas_doc_format",
            },
        },
        "version": {"number": 1},
    }

    httpx_mock.add_response(
        method="GET",
        url="https://test.atlassian.net/wiki/api/v2/pages/12345?body-format=storage%2Catlas_doc_format",
        json=page_data,
    )

    result = confluence.get_page("12345")

    assert result["id"] == "12345"
    assert result["title"] == "Test Page"
    assert result["body"]["storage"]["value"] == "<p>Test content</p>"


def test_confluence_client_get_page_not_found(httpx_mock: HTTPXMock):
    """Test getting a page that doesn't exist."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    httpx_mock.add_response(
        method="GET",
        url="https://test.atlassian.net/wiki/api/v2/pages/99999?body-format=storage%2Catlas_doc_format",
        status_code=404,
        json={"message": "Page not found"},
    )

    with pytest.raises(ApiError) as exc_info:
        confluence.get_page("99999")

    assert exc_info.value.status_code == 404
    assert "Not found" in str(exc_info.value)


def test_confluence_client_get_page_unauthorized(httpx_mock: HTTPXMock):
    """Test getting a page with invalid credentials."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="invalid",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    httpx_mock.add_response(
        method="GET",
        url="https://test.atlassian.net/wiki/api/v2/pages/12345?body-format=storage%2Catlas_doc_format",
        status_code=401,
        json={"message": "Invalid credentials"},
    )

    with pytest.raises(ApiError) as exc_info:
        confluence.get_page("12345")

    assert exc_info.value.status_code == 401
    assert "Authentication failed" in str(exc_info.value)


def test_confluence_client_list_pages(httpx_mock: HTTPXMock):
    """Test listing pages without space filter."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    # Mock successful response
    response_data = {
        "results": [
            {
                "id": "123",
                "status": "current",
                "title": "First Page",
                "spaceId": "111",
            },
            {
                "id": "456",
                "status": "current",
                "title": "Second Page",
                "spaceId": "222",
            },
        ],
        "_links": {},
    }

    httpx_mock.add_response(
        method="GET",
        url="https://test.atlassian.net/wiki/api/v2/pages?limit=25",
        json=response_data,
    )

    result = confluence.list_pages()

    assert len(result) == 2
    assert result[0]["id"] == "123"
    assert result[0]["title"] == "First Page"
    assert result[1]["id"] == "456"
    assert result[1]["title"] == "Second Page"


def test_confluence_client_list_pages_with_space_filter(httpx_mock: HTTPXMock):
    """Test listing pages with space filter."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    response_data = {
        "results": [
            {
                "id": "789",
                "status": "current",
                "title": "Dev Page",
                "spaceId": "333",
            },
        ],
        "_links": {},
    }

    httpx_mock.add_response(
        method="GET",
        url="https://test.atlassian.net/wiki/api/v2/pages?limit=25&space-key=DEV",
        json=response_data,
    )

    result = confluence.list_pages(space_key="DEV")

    assert len(result) == 1
    assert result[0]["id"] == "789"
    assert result[0]["title"] == "Dev Page"


def test_confluence_client_list_pages_with_limit(httpx_mock: HTTPXMock):
    """Test listing pages with custom limit."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    response_data = {
        "results": [
            {"id": "1", "status": "current", "title": "Page 1", "spaceId": "111"},
            {"id": "2", "status": "current", "title": "Page 2", "spaceId": "111"},
            {"id": "3", "status": "current", "title": "Page 3", "spaceId": "111"},
        ],
        "_links": {},
    }

    httpx_mock.add_response(
        method="GET",
        url="https://test.atlassian.net/wiki/api/v2/pages?limit=3",
        json=response_data,
    )

    result = confluence.list_pages(limit=3)

    assert len(result) == 3


def test_confluence_client_list_pages_empty_results(httpx_mock: HTTPXMock):
    """Test listing pages when no results found."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    response_data = {
        "results": [],
        "_links": {},
    }

    httpx_mock.add_response(
        method="GET",
        url="https://test.atlassian.net/wiki/api/v2/pages?limit=25",
        json=response_data,
    )

    result = confluence.list_pages()

    assert len(result) == 0
    assert result == []


def test_confluence_client_list_pages_unauthorized(httpx_mock: HTTPXMock):
    """Test listing pages with invalid credentials."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="invalid",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    httpx_mock.add_response(
        method="GET",
        url="https://test.atlassian.net/wiki/api/v2/pages?limit=25",
        status_code=401,
        json={"message": "Invalid credentials"},
    )

    with pytest.raises(ApiError) as exc_info:
        confluence.list_pages()

    assert exc_info.value.status_code == 401
    assert "Authentication failed" in str(exc_info.value)


def test_confluence_client_list_pages_forbidden(httpx_mock: HTTPXMock):
    """Test listing pages without proper permissions."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    httpx_mock.add_response(
        method="GET",
        url="https://test.atlassian.net/wiki/api/v2/pages?limit=25&space-key=PRIVATE",
        status_code=403,
        json={"message": "No access to space"},
    )

    with pytest.raises(ApiError) as exc_info:
        confluence.list_pages(space_key="PRIVATE")

    assert exc_info.value.status_code == 403
    assert "Permission denied" in str(exc_info.value)


def test_confluence_client_update_page(httpx_mock: HTTPXMock):
    """Test updating a page successfully."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    # Mock successful response
    updated_page_data = {
        "id": "12345",
        "status": "current",
        "title": "Updated Title",
        "spaceId": "67890",
        "body": {
            "storage": {
                "value": "<p>Updated content</p>",
                "representation": "storage",
            },
        },
        "version": {"number": 2},
    }

    httpx_mock.add_response(
        method="PUT",
        url="https://test.atlassian.net/wiki/api/v2/pages/12345",
        json=updated_page_data,
    )

    result = confluence.update_page(
        page_id="12345",
        title="Updated Title",
        body="<p>Updated content</p>",
        version_number=1,
    )

    assert result["id"] == "12345"
    assert result["title"] == "Updated Title"
    assert result["body"]["storage"]["value"] == "<p>Updated content</p>"
    assert result["version"]["number"] == 2

    # Verify request payload
    requests = httpx_mock.get_requests()
    assert len(requests) == 1
    request = requests[0]
    payload = request.read().decode()
    assert '"Updated Title"' in payload
    assert '"<p>Updated content</p>"' in payload
    assert '"number":1' in payload or '"number": 1' in payload


def test_confluence_client_update_page_version_conflict(httpx_mock: HTTPXMock):
    """Test updating a page with version conflict."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    httpx_mock.add_response(
        method="PUT",
        url="https://test.atlassian.net/wiki/api/v2/pages/12345",
        status_code=409,
        json={"message": "Version conflict"},
    )

    with pytest.raises(ApiError) as exc_info:
        confluence.update_page(
            page_id="12345",
            title="Updated Title",
            body="<p>Updated content</p>",
            version_number=1,
        )

    assert exc_info.value.status_code == 409
    assert "Version conflict" in str(exc_info.value)
    assert "modified since you fetched it" in str(exc_info.value)


def test_confluence_client_update_page_not_found(httpx_mock: HTTPXMock):
    """Test updating a page that doesn't exist."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    httpx_mock.add_response(
        method="PUT",
        url="https://test.atlassian.net/wiki/api/v2/pages/99999",
        status_code=404,
        json={"message": "Page not found"},
    )

    with pytest.raises(ApiError) as exc_info:
        confluence.update_page(
            page_id="99999",
            title="Updated Title",
            body="<p>Updated content</p>",
            version_number=1,
        )

    assert exc_info.value.status_code == 404
    assert "Not found" in str(exc_info.value)


def test_confluence_client_update_page_unauthorized(httpx_mock: HTTPXMock):
    """Test updating a page with invalid credentials."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="invalid",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    httpx_mock.add_response(
        method="PUT",
        url="https://test.atlassian.net/wiki/api/v2/pages/12345",
        status_code=401,
        json={"message": "Invalid credentials"},
    )

    with pytest.raises(ApiError) as exc_info:
        confluence.update_page(
            page_id="12345",
            title="Updated Title",
            body="<p>Updated content</p>",
            version_number=1,
        )

    assert exc_info.value.status_code == 401
    assert "Authentication failed" in str(exc_info.value)


def test_confluence_client_update_page_forbidden(httpx_mock: HTTPXMock):
    """Test updating a page without proper permissions."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    httpx_mock.add_response(
        method="PUT",
        url="https://test.atlassian.net/wiki/api/v2/pages/12345",
        status_code=403,
        json={"message": "Insufficient permissions to edit page"},
    )

    with pytest.raises(ApiError) as exc_info:
        confluence.update_page(
            page_id="12345",
            title="Updated Title",
            body="<p>Updated content</p>",
            version_number=1,
        )

    assert exc_info.value.status_code == 403
    assert "Permission denied" in str(exc_info.value)


def test_handle_api_error_409():
    """Test handling 409 version conflict error."""
    response = httpx.Response(
        status_code=409,
        json={"message": "Version conflict"},
    )

    with pytest.raises(ApiError) as exc_info:
        handle_api_error(response)

    assert exc_info.value.status_code == 409
    assert "Version conflict" in str(exc_info.value)
    assert "modified since you fetched it" in str(exc_info.value)


def test_confluence_client_get_space_by_key(httpx_mock: HTTPXMock):
    """Test getting a space by key."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    # Mock successful response
    space_data = {
        "results": [
            {
                "id": "12345",
                "key": "TEAM",
                "name": "Team Space",
                "type": "global",
                "status": "current",
                "authorId": "user123",
                "homepageId": "67890",
            }
        ],
        "_links": {"base": "https://test.atlassian.net/wiki"},
    }

    httpx_mock.add_response(
        method="GET",
        url="https://test.atlassian.net/wiki/api/v2/spaces?keys=TEAM",
        json=space_data,
    )

    result = confluence.get_space_by_key("TEAM")

    assert result["id"] == "12345"
    assert result["key"] == "TEAM"
    assert result["name"] == "Team Space"
    assert result["type"] == "global"


def test_confluence_client_get_space_by_key_not_found(httpx_mock: HTTPXMock):
    """Test getting a space that doesn't exist."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    # Mock response with empty results
    httpx_mock.add_response(
        method="GET",
        url="https://test.atlassian.net/wiki/api/v2/spaces?keys=NONEXIST",
        json={"results": [], "_links": {"base": "https://test.atlassian.net/wiki"}},
    )

    with pytest.raises(ApiError) as exc_info:
        confluence.get_space_by_key("NONEXIST")

    assert exc_info.value.status_code == 404
    assert "Space not found: NONEXIST" in str(exc_info.value)


def test_confluence_client_get_space_by_key_unauthorized(httpx_mock: HTTPXMock):
    """Test getting a space with invalid credentials."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="invalid",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    httpx_mock.add_response(
        method="GET",
        url="https://test.atlassian.net/wiki/api/v2/spaces?keys=TEAM",
        status_code=401,
        json={"message": "Invalid credentials"},
    )

    with pytest.raises(ApiError) as exc_info:
        confluence.get_space_by_key("TEAM")

    assert exc_info.value.status_code == 401
    assert "Authentication failed" in str(exc_info.value)


def test_confluence_client_get_space_by_key_forbidden(httpx_mock: HTTPXMock):
    """Test getting a space without proper permissions."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    httpx_mock.add_response(
        method="GET",
        url="https://test.atlassian.net/wiki/api/v2/spaces?keys=PRIVATE",
        status_code=403,
        json={"message": "No access to space"},
    )

    with pytest.raises(ApiError) as exc_info:
        confluence.get_space_by_key("PRIVATE")

    assert exc_info.value.status_code == 403
    assert "Permission denied" in str(exc_info.value)


def test_confluence_client_delete_page_success(httpx_mock: HTTPXMock):
    """Test deleting a page successfully."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    httpx_mock.add_response(
        method="DELETE",
        url="https://test.atlassian.net/wiki/api/v2/pages/12345",
        status_code=204,
    )

    # Should not raise any exception
    result = confluence.delete_page("12345")

    # Should return None
    assert result is None

    # Verify the request was made
    requests = httpx_mock.get_requests()
    assert len(requests) == 1
    assert requests[0].method == "DELETE"


def test_confluence_client_delete_page_already_deleted(httpx_mock: HTTPXMock):
    """Test deleting a page that's already deleted or doesn't exist (404)."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    httpx_mock.add_response(
        method="DELETE",
        url="https://test.atlassian.net/wiki/api/v2/pages/99999",
        status_code=404,
        json={"message": "Page not found"},
    )

    # Should not raise any exception - 404 is handled gracefully
    result = confluence.delete_page("99999")

    # Should return None
    assert result is None


def test_confluence_client_delete_page_unauthorized(httpx_mock: HTTPXMock):
    """Test deleting a page with invalid credentials."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    httpx_mock.add_response(
        method="DELETE",
        url="https://test.atlassian.net/wiki/api/v2/pages/12345",
        status_code=401,
        json={"message": "Invalid credentials"},
    )

    with pytest.raises(ApiError) as exc_info:
        confluence.delete_page("12345")

    assert exc_info.value.status_code == 401
    assert "Authentication failed" in str(exc_info.value)


def test_confluence_client_delete_page_forbidden(httpx_mock: HTTPXMock):
    """Test deleting a page without proper permissions."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    httpx_mock.add_response(
        method="DELETE",
        url="https://test.atlassian.net/wiki/api/v2/pages/12345",
        status_code=403,
        json={"message": "Insufficient permissions"},
    )

    with pytest.raises(ApiError) as exc_info:
        confluence.delete_page("12345")

    assert exc_info.value.status_code == 403
    assert "Permission denied" in str(exc_info.value)


def test_confluence_client_create_page(httpx_mock: HTTPXMock):
    """Test creating a page successfully."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    # Mock successful response
    created_page_data = {
        "id": "98765",
        "status": "current",
        "title": "New Page",
        "spaceId": "12345",
        "body": {
            "storage": {
                "value": "<p>New content</p>",
                "representation": "storage",
            },
        },
        "version": {"number": 1},
    }

    httpx_mock.add_response(
        method="POST",
        url="https://test.atlassian.net/wiki/api/v2/pages",
        json=created_page_data,
    )

    result = confluence.create_page(
        space_id="12345",
        title="New Page",
        body="<p>New content</p>",
    )

    assert result["id"] == "98765"
    assert result["title"] == "New Page"
    assert result["spaceId"] == "12345"
    assert result["body"]["storage"]["value"] == "<p>New content</p>"
    assert result["version"]["number"] == 1

    # Verify request payload
    requests = httpx_mock.get_requests()
    assert len(requests) == 1
    request = requests[0]
    payload = request.read().decode()
    assert '"New Page"' in payload
    assert '"<p>New content</p>"' in payload
    assert '"12345"' in payload


def test_confluence_client_create_page_with_parent(httpx_mock: HTTPXMock):
    """Test creating a page with a parent page."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    # Mock successful response
    created_page_data = {
        "id": "98765",
        "status": "current",
        "title": "Child Page",
        "spaceId": "12345",
        "parentId": "54321",
        "body": {
            "storage": {
                "value": "<p>Child content</p>",
                "representation": "storage",
            },
        },
        "version": {"number": 1},
    }

    httpx_mock.add_response(
        method="POST",
        url="https://test.atlassian.net/wiki/api/v2/pages",
        json=created_page_data,
    )

    result = confluence.create_page(
        space_id="12345",
        title="Child Page",
        body="<p>Child content</p>",
        parent_id="54321",
    )

    assert result["id"] == "98765"
    assert result["title"] == "Child Page"
    assert result["parentId"] == "54321"

    # Verify request payload includes parentId
    requests = httpx_mock.get_requests()
    assert len(requests) == 1
    request = requests[0]
    payload = request.read().decode()
    assert '"parentId"' in payload or '"parentId"' in payload
    assert '"54321"' in payload


def test_confluence_client_create_page_invalid_space(httpx_mock: HTTPXMock):
    """Test creating a page with invalid space ID."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    httpx_mock.add_response(
        method="POST",
        url="https://test.atlassian.net/wiki/api/v2/pages",
        status_code=400,
        json={"message": "Invalid space ID"},
    )

    with pytest.raises(ApiError) as exc_info:
        confluence.create_page(
            space_id="invalid",
            title="New Page",
            body="<p>Content</p>",
        )

    assert exc_info.value.status_code == 400
    assert "Client error (400)" in str(exc_info.value)


def test_confluence_client_create_page_duplicate_title(httpx_mock: HTTPXMock):
    """Test creating a page with duplicate title in space."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    httpx_mock.add_response(
        method="POST",
        url="https://test.atlassian.net/wiki/api/v2/pages",
        status_code=400,
        json={"message": "A page with this title already exists in the space"},
    )

    with pytest.raises(ApiError) as exc_info:
        confluence.create_page(
            space_id="12345",
            title="Existing Page",
            body="<p>Content</p>",
        )

    assert exc_info.value.status_code == 400
    assert "already exists" in str(exc_info.value)


def test_confluence_client_create_page_unauthorized(httpx_mock: HTTPXMock):
    """Test creating a page with invalid credentials."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="invalid",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    httpx_mock.add_response(
        method="POST",
        url="https://test.atlassian.net/wiki/api/v2/pages",
        status_code=401,
        json={"message": "Invalid credentials"},
    )

    with pytest.raises(ApiError) as exc_info:
        confluence.create_page(
            space_id="12345",
            title="New Page",
            body="<p>Content</p>",
        )

    assert exc_info.value.status_code == 401
    assert "Authentication failed" in str(exc_info.value)


def test_confluence_client_create_page_forbidden(httpx_mock: HTTPXMock):
    """Test creating a page without proper permissions."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    httpx_mock.add_response(
        method="POST",
        url="https://test.atlassian.net/wiki/api/v2/pages",
        status_code=403,
        json={"message": "Insufficient permissions to create pages in space"},
    )

    with pytest.raises(ApiError) as exc_info:
        confluence.create_page(
            space_id="12345",
            title="New Page",
            body="<p>Content</p>",
        )

    assert exc_info.value.status_code == 403
    assert "Permission denied" in str(exc_info.value)


def test_confluence_client_create_page_invalid_parent(httpx_mock: HTTPXMock):
    """Test creating a page with invalid parent ID."""
    config = Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="token123",
    )
    client = create_client(config)
    confluence = ConfluenceClient(client)

    httpx_mock.add_response(
        method="POST",
        url="https://test.atlassian.net/wiki/api/v2/pages",
        status_code=404,
        json={"message": "Parent page not found"},
    )

    with pytest.raises(ApiError) as exc_info:
        confluence.create_page(
            space_id="12345",
            title="Child Page",
            body="<p>Content</p>",
            parent_id="nonexistent",
        )

    assert exc_info.value.status_code == 404
    assert "Not found" in str(exc_info.value)
