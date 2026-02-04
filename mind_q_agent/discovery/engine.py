"""
Discovery Engine for Web Content.

Orchestrates the discovery loop: fetch → parse → ingest.
"""

import logging
import asyncio
from typing import Set, List, Optional, Dict, Any
from dataclasses import dataclass
from collections import deque

from mind_q_agent.discovery.fetcher import WebFetcher
from mind_q_agent.discovery.parser import ContentParser, ParsedContent
from mind_q_agent.config.manager import ConfigManager

logger = logging.getLogger(__name__)


@dataclass
class DiscoveryResult:
    """Result of a discovery run."""
    pages_fetched: int
    pages_parsed: int
    pages_ingested: int
    links_discovered: int
    errors: int


class DiscoveryEngine:
    """
    Web discovery engine.
    
    Crawls URLs, extracts content, and feeds to ingestion pipeline.
    """
    
    def __init__(
        self,
        fetcher: Optional[WebFetcher] = None,
        parser: Optional[ContentParser] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.fetcher = fetcher or WebFetcher()
        self.parser = parser or ContentParser()
        self.config = config or self._load_config()
        
        self.max_pages = self.config.get("max_pages", 10)
        self.allowed_domains: Set[str] = set(self.config.get("allowed_domains", []))
        
        self._visited: Set[str] = set()
        self._queue: deque = deque()

    def _load_config(self) -> Dict[str, Any]:
        """Load discovery config."""
        try:
            return ConfigManager.get_config().get("discovery", {})
        except Exception:
            return {}

    def add_seed_urls(self, urls: List[str]):
        """Add seed URLs to discovery queue."""
        for url in urls:
            if url not in self._visited:
                self._queue.append(url)

    def _is_allowed(self, url: str) -> bool:
        """Check if URL domain is allowed."""
        if not self.allowed_domains:
            return True  # No restrictions
            
        from urllib.parse import urlparse
        try:
            domain = urlparse(url).netloc
            return any(d in domain for d in self.allowed_domains)
        except Exception:
            return False

    async def discover(
        self,
        seed_urls: Optional[List[str]] = None,
        on_content: Optional[callable] = None
    ) -> DiscoveryResult:
        """
        Run discovery loop.
        
        Args:
            seed_urls: Initial URLs to crawl.
            on_content: Callback for each parsed content (for ingestion).
            
        Returns:
            DiscoveryResult with statistics.
        """
        if seed_urls:
            self.add_seed_urls(seed_urls)
        
        pages_fetched = 0
        pages_parsed = 0
        pages_ingested = 0
        links_discovered = 0
        errors = 0
        
        try:
            while self._queue and pages_fetched < self.max_pages:
                url = self._queue.popleft()
                
                if url in self._visited:
                    continue
                    
                self._visited.add(url)
                
                # Fetch
                logger.info(f"Fetching: {url}")
                response = await self.fetcher.fetch(url)
                pages_fetched += 1
                
                if not response.success:
                    logger.warning(f"Failed to fetch {url}: {response.error}")
                    errors += 1
                    continue
                
                # Parse
                content = self.parser.parse(response.html, url)
                pages_parsed += 1
                
                # Discover new links
                for link in content.links:
                    if link not in self._visited and self._is_allowed(link):
                        self._queue.append(link)
                        links_discovered += 1
                
                # Callback for ingestion
                if on_content and content.text:
                    try:
                        on_content(content)
                        pages_ingested += 1
                    except Exception as e:
                        logger.error(f"Ingestion callback failed: {e}")
                        errors += 1
                
                # Rate limiting
                await asyncio.sleep(0.5)
                
        finally:
            await self.fetcher.close()
        
        logger.info(f"Discovery complete: {pages_fetched} fetched, {pages_parsed} parsed")
        
        return DiscoveryResult(
            pages_fetched=pages_fetched,
            pages_parsed=pages_parsed,
            pages_ingested=pages_ingested,
            links_discovered=links_discovered,
            errors=errors
        )

    def discover_sync(
        self,
        seed_urls: Optional[List[str]] = None,
        on_content: Optional[callable] = None
    ) -> DiscoveryResult:
        """Synchronous wrapper for discover."""
        return asyncio.run(self.discover(seed_urls, on_content))

    def reset(self):
        """Reset discovery state."""
        self._visited.clear()
        self._queue.clear()
