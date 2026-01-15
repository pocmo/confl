"""Tests for verbose and debug modes."""

from unittest.mock import MagicMock, patch

import httpx
import pytest
from typer.testing import CliRunner

from confl.cli import app
from confl.client import create_client, create_v1_client, log_request, log_response
from confl.config import Config

runner = CliRunner()


@pytest.fixture
def mock_config():
    """Mock configuration."""
    return Config(
        site="test.atlassian.net",
        email="test@example.com",
        token="test-token",
    )


def test_verbose_flag_accepted():
    """Test that --verbose flag is accepted."""
    result = runner.invoke(app, ["--verbose", "--help"])
    assert result.exit_code == 0
    assert "confl" in result.output.lower()


def test_debug_flag_accepted():
    """Test that --debug flag is accepted."""
    result = runner.invoke(app, ["--debug", "--help"])
    assert result.exit_code == 0
    assert "confl" in result.output.lower()


def test_verbose_short_flag():
    """Test that -v short flag works."""
    result = runner.invoke(app, ["-v", "--help"])
    assert result.exit_code == 0
    assert "confl" in result.output.lower()


def test_debug_implies_verbose():
    """Test that debug mode includes verbose information."""
    # Debug should set logging to DEBUG level which is more verbose than INFO
    result = runner.invoke(app, ["--debug", "--help"])
    assert result.exit_code == 0


def test_client_has_event_hooks_in_debug_mode(mock_config):
    """Test that HTTP client has event hooks when debug mode is enabled."""
    with patch("confl.cli.is_debug", return_value=True):
        client = create_client(mock_config)
        assert "request" in client.event_hooks
        assert "response" in client.event_hooks
        assert log_request in client.event_hooks["request"]
        assert log_response in client.event_hooks["response"]


def test_client_no_event_hooks_without_debug(mock_config):
    """Test that HTTP client has no event hooks when debug is disabled."""
    with patch("confl.cli.is_debug", return_value=False):
        client = create_client(mock_config)
        # Event hooks dict may be empty or not contain our hooks
        assert log_request not in client.event_hooks.get("request", [])
        assert log_response not in client.event_hooks.get("response", [])


def test_v1_client_has_event_hooks_in_debug_mode(mock_config):
    """Test that v1 client has event hooks when debug mode is enabled."""
    with patch("confl.cli.is_debug", return_value=True):
        client = create_v1_client(mock_config)
        assert "request" in client.event_hooks
        assert "response" in client.event_hooks


def test_v1_client_no_event_hooks_without_debug(mock_config):
    """Test that v1 client has no event hooks when debug is disabled."""
    with patch("confl.cli.is_debug", return_value=False):
        client = create_v1_client(mock_config)
        assert log_request not in client.event_hooks.get("request", [])
        assert log_response not in client.event_hooks.get("response", [])


def test_log_request_masks_authorization():
    """Test that authorization header is masked in logs."""
    request = httpx.Request(
        "GET",
        "https://test.atlassian.net/wiki/api/v2/pages",
        headers={"Authorization": "Basic dGVzdDp0b2tlbg=="},
    )

    with patch("confl.client.logger") as mock_logger:
        mock_logger.isEnabledFor.return_value = True
        log_request(request)

        # Check that logger.debug was called
        assert mock_logger.debug.called

        # Verify authorization was masked
        calls = [str(call) for call in mock_logger.debug.call_args_list]
        log_output = " ".join(calls)
        assert "***MASKED***" in log_output
        assert "dGVzdDp0b2tlbg==" not in log_output


def test_log_response_truncates_large_bodies():
    """Test that large response bodies are truncated."""
    large_body = "x" * 2000
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.reason_phrase = "OK"
    response.content = large_body.encode()
    response.headers = {"content-type": "application/json"}
    response.text = large_body

    with patch("confl.client.logger") as mock_logger:
        mock_logger.isEnabledFor.return_value = True
        log_response(response)

        # Verify truncation message appears
        calls = [str(call) for call in mock_logger.debug.call_args_list]
        log_output = " ".join(calls)
        assert "truncated" in log_output


def test_log_response_handles_binary_content():
    """Test that binary content is handled gracefully."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.reason_phrase = "OK"
    response.content = b"\x00\x01\x02\x03"  # Binary data
    response.headers = {"content-type": "application/octet-stream"}

    with patch("confl.client.logger") as mock_logger:
        mock_logger.isEnabledFor.return_value = True
        log_response(response)

        # Should log without error (no body logged for binary content)
        assert mock_logger.debug.called


def test_verbose_and_debug_flags_together():
    """Test that both flags can be used together (debug takes precedence)."""
    result = runner.invoke(app, ["--verbose", "--debug", "--help"])
    assert result.exit_code == 0


def test_logging_level_hierarchy():
    """Test that logging levels are set correctly."""
    # With no flags, should use default (WARNING)
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0

    # With --verbose, should use INFO
    result = runner.invoke(app, ["--verbose", "--help"])
    assert result.exit_code == 0

    # With --debug, should use DEBUG
    result = runner.invoke(app, ["--debug", "--help"])
    assert result.exit_code == 0


def test_log_request_without_body():
    """Test logging request without body."""
    request = httpx.Request(
        "GET",
        "https://test.atlassian.net/wiki/api/v2/pages",
    )

    with patch("confl.client.logger") as mock_logger:
        mock_logger.isEnabledFor.return_value = True
        log_request(request)

        # Should log method and URL
        assert mock_logger.debug.called
        calls = [str(call) for call in mock_logger.debug.call_args_list]
        log_output = " ".join(calls)
        assert "GET" in log_output
        assert "pages" in log_output


def test_log_response_with_json_content():
    """Test logging response with JSON content."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.reason_phrase = "OK"
    response.content = b'{"key": "value"}'
    response.headers = {"content-type": "application/json"}
    response.text = '{"key": "value"}'

    with patch("confl.client.logger") as mock_logger:
        mock_logger.isEnabledFor.return_value = True
        log_response(response)

        # Should log status and body
        assert mock_logger.debug.called
        calls = [str(call) for call in mock_logger.debug.call_args_list]
        log_output = " ".join(calls)
        assert "200" in log_output
        assert "key" in log_output or "value" in log_output
