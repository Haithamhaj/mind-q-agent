"""Unit tests for WebFetcher."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from mind_q_agent.discovery.fetcher import WebFetcher, WebResponse


class TestWebFetcher:
    """Tests for WebFetcher class."""

    @pytest.fixture
    def fetcher(self):
        return WebFetcher(config={"timeout": 5.0, "max_retries": 1})

    def test_is_valid_url_http(self, fetcher):
        """Should accept HTTP URLs."""
        assert fetcher.is_valid_url("http://example.com") is True

    def test_is_valid_url_https(self, fetcher):
        """Should accept HTTPS URLs."""
        assert fetcher.is_valid_url("https://example.com/path") is True

    def test_is_valid_url_invalid(self, fetcher):
        """Should reject invalid URLs."""
        assert fetcher.is_valid_url("not-a-url") is False
        assert fetcher.is_valid_url("ftp://example.com") is False
        assert fetcher.is_valid_url("") is False

    def test_fetch_invalid_url(self, fetcher):
        """Should return error for invalid URL."""
        response = fetcher.fetch_sync("not-a-valid-url")
        
        assert response.success is False
        assert "Invalid URL" in response.error

    def test_fetch_sync_wrapper(self, fetcher):
        """Sync wrapper should work."""
        response = fetcher.fetch_sync("not-a-valid-url")
        
        assert response.success is False
        assert isinstance(response, WebResponse)
