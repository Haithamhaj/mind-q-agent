"""Unit tests for DiscoveryEngine."""

import pytest
from unittest.mock import MagicMock, AsyncMock
from mind_q_agent.discovery.engine import DiscoveryEngine, DiscoveryResult
from mind_q_agent.discovery.fetcher import WebResponse
from mind_q_agent.discovery.parser import ParsedContent


class TestDiscoveryEngine:
    """Tests for DiscoveryEngine class."""

    @pytest.fixture
    def mock_fetcher(self):
        fetcher = MagicMock()
        fetcher.fetch = AsyncMock(return_value=WebResponse(
            url="http://example.com",
            status=200,
            html="<html><body>Test</body></html>",
            headers={},
            success=True
        ))
        fetcher.close = AsyncMock()
        return fetcher

    @pytest.fixture
    def mock_parser(self):
        parser = MagicMock()
        parser.parse = MagicMock(return_value=ParsedContent(
            url="http://example.com",
            title="Test",
            text="Test content",
            description="",
            keywords=[],
            links=[]
        ))
        return parser

    @pytest.fixture
    def engine(self, mock_fetcher, mock_parser):
        return DiscoveryEngine(
            fetcher=mock_fetcher,
            parser=mock_parser,
            config={"max_pages": 5}
        )

    def test_add_seed_urls(self, engine):
        """Should add URLs to queue."""
        engine.add_seed_urls(["http://a.com", "http://b.com"])
        
        assert len(engine._queue) == 2

    def test_is_allowed_no_restrictions(self, engine):
        """Should allow all when no domain restrictions."""
        engine.allowed_domains = set()
        
        assert engine._is_allowed("http://any.com") is True

    def test_is_allowed_with_restrictions(self, engine):
        """Should filter by domain."""
        engine.allowed_domains = {"example.com", "test.com"}
        
        assert engine._is_allowed("http://example.com/page") is True
        assert engine._is_allowed("http://other.com/page") is False

    def test_discover_basic(self, engine, mock_fetcher, mock_parser):
        """Should fetch and parse seed URLs."""
        import asyncio
        result = asyncio.run(engine.discover(seed_urls=["http://example.com"]))
        
        assert result.pages_fetched == 1
        assert result.pages_parsed == 1

    def test_discover_with_callback(self, engine, mock_fetcher, mock_parser):
        """Should call content callback."""
        import asyncio
        callback = MagicMock()
        
        result = asyncio.run(engine.discover(
            seed_urls=["http://example.com"],
            on_content=callback
        ))
        
        assert result.pages_ingested == 1
        callback.assert_called_once()

    def test_reset(self, engine):
        """Should clear state."""
        engine._visited.add("http://test.com")
        engine._queue.append("http://test2.com")
        
        engine.reset()
        
        assert len(engine._visited) == 0
        assert len(engine._queue) == 0
