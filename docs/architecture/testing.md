# Testing Strategy

How we test `confl` without hitting production Confluence.

## Overview

All tests must run **offline** without making real API calls. We use HTTP mocking to intercept `httpx` requests and return predefined responses.

## Mocking Library: pytest-httpx

We use **pytest-httpx** for HTTP mocking because:
- Simple, declarative pytest fixture API
- Built specifically for httpx and pytest integration
- Easy for agents to understand and write
- Sufficient for our needs (no complex routing required)
- Supports both sync and async clients (we use sync)

### Why not respx?
- More flexible/complex than needed (we don't need route matching or ORM-style patterns)
- pytest-httpx's simpler API aligns better with "simple first" principle

### Why not VCR cassettes?
- Adds maintenance burden (must re-record on API changes)
- Risk of leaking secrets (tokens/emails) into cassettes
- Hand-crafted fixtures give better control for testing edge cases
- Our test needs are simple enough that manual mocking isn't burdensome

## Test Structure

### Unit Tests
Test individual functions/modules in isolation with mocked dependencies.

**Location:** `tests/test_*.py`

**Example:**
```python
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
```

### Integration Tests
Test command flow end-to-end with mocked HTTP responses.

**Example:**
```python
def test_page_get_success(httpx_mock):
    """Test getting a page by ID."""
    httpx_mock.add_response(
        url="https://mycompany.atlassian.net/wiki/api/v2/pages/123456",
        json={
            "id": "123456",
            "title": "My Page",
            "body": {"storage": {"value": "<p>Content</p>"}}
        }
    )
    
    result = runner.invoke(app, ["page", "get", "123456"])
    
    assert result.exit_code == 0
    assert "My Page" in result.stdout
```

## Fixture Organization

### Response Fixtures
Store common API response shapes as pytest fixtures when reused across tests.

**Location:** `tests/conftest.py`

**Example:**
```python
@pytest.fixture
def sample_page():
    """Sample Confluence page response."""
    return {
        "id": "123456",
        "title": "Test Page",
        "spaceId": "SPACE1",
        "status": "current",
        "body": {
            "storage": {
                "value": "<p>Page content</p>",
                "representation": "storage"
            }
        }
    }
```

### Client Fixtures
Use `monkeypatch` to mock config/credentials for client tests.

**Example:**
```python
def test_get_client_with_env_vars(monkeypatch):
    """Test get_client loads config from env vars."""
    monkeypatch.setenv("CONFL_SITE", "test.atlassian.net")
    monkeypatch.setenv("CONFL_EMAIL", "test@example.com")
    monkeypatch.setenv("CONFL_TOKEN", "token123")
    
    client = get_client()
    
    assert str(client.base_url) == "https://test.atlassian.net/wiki/api/v2/"
```

## What to Test

### Must Test
- Command parsing and validation (bad args → exit code 2)
- API error handling (401, 403, 404, 429, 500 → exit code 1)
- Success paths (happy path → exit code 0)
- Output formatting (text/JSON modes)
- Config loading (env vars, credentials file, errors)

### Don't Need to Test
- httpx internals (library is well-tested)
- Confluence API behavior (trust their docs)
- Network failures (out of scope for CLI logic)

## Test Naming

Use descriptive names that explain what's being tested:
```python
test_page_get_success()
test_page_get_not_found()
test_page_create_with_missing_title()
test_auth_login_invalid_site_format()
```

## Running Tests

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/test_client.py

# Specific test
uv run pytest tests/test_client.py::test_create_client

# With coverage
uv run pytest --cov=confl --cov-report=term-missing
```

## Agent Guidelines

When writing tests:
1. **Mock at the HTTP layer** using `httpx_mock` fixture
2. **Test one thing** per test function
3. **Use descriptive assertions** that show what went wrong
4. **Keep fixtures simple** - avoid complex setup
5. **Test error cases** - don't just test happy paths
6. **Use existing patterns** - look at `tests/test_client.py` for examples

Example test structure:
```python
def test_command_scenario(httpx_mock):
    """Test description in imperative mood."""
    # Arrange: Setup mock responses
    httpx_mock.add_response(
        url="...",
        json={...}
    )
    
    # Act: Run the command
    result = runner.invoke(app, ["entity", "action", "args"])
    
    # Assert: Check results
    assert result.exit_code == 0
    assert "expected output" in result.stdout
```

## References

- [pytest-httpx documentation](https://github.com/Colin-b/pytest_httpx)
- [pytest fixtures guide](https://docs.pytest.org/en/stable/fixture.html)
- [httpx Response creation](https://www.python-httpx.org/api/#response)
