"""Tests for HTTP client."""

import base64

import httpx
import pytest

from confl.client import ApiError, create_client, get_client, handle_api_error
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
