"""
Web Content Parser for Discovery Loop.

Extracts text, metadata, and links from HTML content.
"""

import logging
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser

logger = logging.getLogger(__name__)


@dataclass
class ParsedContent:
    """Parsed web content."""
    url: str
    title: str
    text: str
    description: str
    keywords: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)


class SimpleHTMLParser(HTMLParser):
    """Simple HTML parser for text extraction."""
    
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.title = ""
        self.description = ""
        self.keywords = []
        self.links = []
        self._in_title = False
        self._in_script = False
        self._in_style = False
        self.metadata = {}

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == "title":
            self._in_title = True
        elif tag == "script":
            self._in_script = True
        elif tag == "style":
            self._in_style = True
        elif tag == "a" and "href" in attrs_dict:
            self.links.append(attrs_dict["href"])
        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            content = attrs_dict.get("content", "")
            if name == "description":
                self.description = content
            elif name == "keywords":
                self.keywords = [k.strip() for k in content.split(",")]
            elif name:
                self.metadata[name] = content

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "script":
            self._in_script = False
        elif tag == "style":
            self._in_style = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif not self._in_script and not self._in_style:
            text = data.strip()
            if text:
                self.text_parts.append(text)

    def get_text(self) -> str:
        """Get extracted text."""
        return " ".join(self.text_parts)


class ContentParser:
    """
    Web content parser.
    
    Extracts clean text, metadata, and links from HTML.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.max_text_length = self.config.get("max_text_length", 50000)

    def parse(self, html: str, url: str) -> ParsedContent:
        """
        Parse HTML content.
        
        Args:
            html: Raw HTML string.
            url: Source URL (for link resolution).
            
        Returns:
            ParsedContent with extracted data.
        """
        try:
            parser = SimpleHTMLParser()
            parser.feed(html)
            
            # Clean and truncate text
            text = self._clean_text(parser.get_text())
            if len(text) > self.max_text_length:
                text = text[:self.max_text_length] + "..."
            
            # Resolve relative links
            resolved_links = self._resolve_links(parser.links, url)
            
            return ParsedContent(
                url=url,
                title=parser.title.strip(),
                text=text,
                description=parser.description,
                keywords=parser.keywords,
                links=resolved_links,
                metadata=parser.metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to parse content from {url}: {e}")
            return ParsedContent(
                url=url,
                title="",
                text="",
                description="",
                keywords=[],
                links=[],
                metadata={}
            )

    def extract_links(self, html: str, base_url: str) -> List[str]:
        """
        Extract all links from HTML.
        
        Args:
            html: Raw HTML string.
            base_url: Base URL for resolving relative links.
            
        Returns:
            List of absolute URLs.
        """
        try:
            parser = SimpleHTMLParser()
            parser.feed(html)
            return self._resolve_links(parser.links, base_url)
        except Exception as e:
            logger.error(f"Failed to extract links: {e}")
            return []

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove common noise
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
        return text.strip()

    def _resolve_links(self, links: List[str], base_url: str) -> List[str]:
        """Resolve relative links to absolute URLs."""
        resolved = []
        for link in links:
            try:
                # Skip non-HTTP links
                if link.startswith(('javascript:', 'mailto:', '#', 'tel:')):
                    continue
                    
                # Resolve relative URLs
                absolute = urljoin(base_url, link)
                parsed = urlparse(absolute)
                
                # Only keep HTTP/HTTPS
                if parsed.scheme in ('http', 'https'):
                    resolved.append(absolute)
                    
            except Exception:
                continue
                
        return list(set(resolved))  # Deduplicate
