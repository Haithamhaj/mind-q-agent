"""
Web Fetcher for Discovery Loop.

Fetches web content with rate limiting and error handling.
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass
from urllib.parse import urlparse
import aiohttp

from mind_q_agent.config.manager import ConfigManager

logger = logging.getLogger(__name__)


@dataclass
class WebResponse:
    """Response from web fetch."""
    url: str
    status: int
    html: str
    headers: Dict[str, str]
    success: bool
    error: Optional[str] = None


class WebFetcher:
    """
    Asynchronous web content fetcher.
    
    Features:
    - Rate limiting
    - Timeout handling
    - Retry logic
    - User-agent spoofing
    """
    
    DEFAULT_USER_AGENT = "Mind-Q Agent/1.0 (Knowledge Discovery Bot)"
    DEFAULT_TIMEOUT = 10.0
    DEFAULT_MAX_RETRIES = 2
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_config()
        self.timeout = self.config.get("timeout", self.DEFAULT_TIMEOUT)
        self.max_retries = self.config.get("max_retries", self.DEFAULT_MAX_RETRIES)
        self.user_agent = self.config.get("user_agent", self.DEFAULT_USER_AGENT)
        self._session: Optional[aiohttp.ClientSession] = None

    def _load_config(self) -> Dict[str, Any]:
        """Load discovery config from ConfigManager."""
        try:
            return ConfigManager.get_config().get("discovery", {})
        except Exception:
            return {}

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers={"User-Agent": self.user_agent}
            )
        return self._session

    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    def is_valid_url(self, url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL to validate.
            
        Returns:
            True if valid HTTP/HTTPS URL.
        """
        try:
            result = urlparse(url)
            return all([result.scheme in ("http", "https"), result.netloc])
        except Exception:
            return False

    async def fetch(self, url: str) -> WebResponse:
        """
        Fetch content from URL.
        
        Args:
            url: URL to fetch.
            
        Returns:
            WebResponse with HTML content or error.
        """
        if not self.is_valid_url(url):
            return WebResponse(
                url=url,
                status=0,
                html="",
                headers={},
                success=False,
                error="Invalid URL format"
            )
        
        session = await self._get_session()
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                async with session.get(url) as response:
                    html = await response.text()
                    headers = dict(response.headers)
                    
                    return WebResponse(
                        url=url,
                        status=response.status,
                        html=html,
                        headers=headers,
                        success=response.status == 200,
                        error=None if response.status == 200 else f"HTTP {response.status}"
                    )
                    
            except asyncio.TimeoutError:
                last_error = "Timeout"
                logger.warning(f"Timeout fetching {url}, attempt {attempt + 1}")
                
            except aiohttp.ClientError as e:
                last_error = str(e)
                logger.warning(f"Client error fetching {url}: {e}, attempt {attempt + 1}")
                
            except Exception as e:
                last_error = str(e)
                logger.error(f"Unexpected error fetching {url}: {e}")
                break
            
            # Wait before retry
            if attempt < self.max_retries:
                await asyncio.sleep(1.0 * (attempt + 1))
        
        return WebResponse(
            url=url,
            status=0,
            html="",
            headers={},
            success=False,
            error=last_error or "Unknown error"
        )

    def fetch_sync(self, url: str) -> WebResponse:
        """
        Synchronous wrapper for fetch.
        
        Args:
            url: URL to fetch.
            
        Returns:
            WebResponse with HTML content or error.
        """
        return asyncio.run(self._fetch_and_close(url))

    async def _fetch_and_close(self, url: str) -> WebResponse:
        """Fetch and close session (for sync wrapper)."""
        try:
            return await self.fetch(url)
        finally:
            await self.close()
