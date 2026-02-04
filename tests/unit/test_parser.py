"""Unit tests for ContentParser."""

import pytest
from mind_q_agent.discovery.parser import ContentParser, ParsedContent


class TestContentParser:
    """Tests for ContentParser class."""

    @pytest.fixture
    def parser(self):
        return ContentParser()

    def test_parse_basic_html(self, parser):
        """Should extract title and text from HTML."""
        html = """
        <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Hello World</h1>
            <p>This is a test paragraph.</p>
        </body>
        </html>
        """
        
        result = parser.parse(html, "http://example.com")
        
        assert result.title == "Test Page"
        assert "Hello World" in result.text
        assert "test paragraph" in result.text

    def test_parse_meta_description(self, parser):
        """Should extract meta description."""
        html = """
        <html>
        <head>
            <meta name="description" content="This is the description">
        </head>
        <body>Content</body>
        </html>
        """
        
        result = parser.parse(html, "http://example.com")
        
        assert result.description == "This is the description"

    def test_parse_meta_keywords(self, parser):
        """Should extract meta keywords."""
        html = """
        <html>
        <head>
            <meta name="keywords" content="python, testing, web">
        </head>
        <body>Content</body>
        </html>
        """
        
        result = parser.parse(html, "http://example.com")
        
        assert "python" in result.keywords
        assert "testing" in result.keywords

    def test_extract_links(self, parser):
        """Should extract and resolve links."""
        html = """
        <html>
        <body>
            <a href="/page1">Page 1</a>
            <a href="https://other.com/page2">Page 2</a>
            <a href="javascript:void(0)">Skip</a>
        </body>
        </html>
        """
        
        links = parser.extract_links(html, "http://example.com")
        
        assert "http://example.com/page1" in links
        assert "https://other.com/page2" in links
        assert len([l for l in links if "javascript" in l]) == 0

    def test_skip_script_and_style(self, parser):
        """Should not include script/style content in text."""
        html = """
        <html>
        <body>
            <script>var x = 1;</script>
            <style>.foo { color: red; }</style>
            <p>Real content here</p>
        </body>
        </html>
        """
        
        result = parser.parse(html, "http://example.com")
        
        assert "var x" not in result.text
        assert "color: red" not in result.text
        assert "Real content here" in result.text

    def test_truncate_long_text(self, parser):
        """Should truncate very long text."""
        parser.max_text_length = 100
        html = "<html><body>" + "a" * 200 + "</body></html>"
        
        result = parser.parse(html, "http://example.com")
        
        assert len(result.text) <= 103  # 100 + "..."
