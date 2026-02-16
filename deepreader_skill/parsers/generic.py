"""
DeepReader Skill - Generic Web Parser
=======================================
Uses **trafilatura** as the primary extraction engine, with a
BeautifulSoup fallback for edge cases.  Designed for blog posts,
news articles, documentation pages, and general web content.
"""

from __future__ import annotations

import logging

import requests
import trafilatura
from bs4 import BeautifulSoup

from .base import BaseParser, ParseResult

logger = logging.getLogger("deepreader.parsers.generic")


class GenericParser(BaseParser):
    """Extract main content from any web page using trafilatura."""

    name = "generic"

    def parse(self, url: str) -> ParseResult:
        """Fetch *url* and extract the article body via trafilatura."""
        try:
            html = self._fetch_html(url)
            if not html:
                return ParseResult.failure(url, "Failed to download page content.")

            # ------------------------------------------------------------------
            # Primary: trafilatura (best for article-style pages)
            # ------------------------------------------------------------------
            result = self._extract_with_trafilatura(url, html)
            if result and result.success and result.content:
                logger.info("Trafilatura extracted %d chars from %s", len(result.content), url)
                return result

            # ------------------------------------------------------------------
            # Fallback: BeautifulSoup heuristic extraction
            # ------------------------------------------------------------------
            logger.info("Trafilatura returned empty, trying BeautifulSoup fallback for %s", url)
            result = self._extract_with_beautifulsoup(url, html)
            if result and result.success and result.content:
                logger.info("BS4 extracted %d chars from %s", len(result.content), url)
                return result

            return ParseResult.failure(url, "Could not extract meaningful content from the page.")

        except requests.RequestException as exc:
            logger.error("HTTP error for %s: %s", url, exc)
            return ParseResult.failure(url, f"HTTP request failed: {exc}")
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected error parsing %s", url)
            return ParseResult.failure(url, f"Unexpected error: {exc}")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_html(self, url: str) -> str | None:
        """Download the raw HTML content of *url*."""
        response = requests.get(
            url,
            headers=self._get_headers(),
            timeout=self.timeout,
            allow_redirects=True,
        )
        response.raise_for_status()
        return response.text

    def _extract_with_trafilatura(self, url: str, html: str) -> ParseResult | None:
        """Use trafilatura to extract structured content."""
        # trafilatura.extract returns plain/markdown text
        extracted: str | None = trafilatura.extract(
            html,
            url=url,
            include_comments=False,
            include_tables=True,
            include_images=False,
            include_links=True,
            output_format="txt",
            favor_precision=True,
        )
        if not extracted:
            return None

        # Extract metadata via the dedicated trafilatura metadata API
        meta = trafilatura.metadata.extract_metadata(html, default_url=url)

        title = ""
        author = ""
        if meta:
            title = meta.title or ""
            author = meta.author or ""

        # If trafilatura didn't give us a title, fall back to <title> tag
        if not title:
            title = self._extract_title_from_html(html)

        from ..core.utils import clean_text, generate_excerpt

        content = clean_text(extracted)
        excerpt = generate_excerpt(content)

        return ParseResult(
            url=url,
            title=title,
            content=content,
            author=author,
            excerpt=excerpt,
        )

    def _extract_with_beautifulsoup(self, url: str, html: str) -> ParseResult | None:
        """Fallback extraction using BeautifulSoup heuristics."""
        soup = BeautifulSoup(html, "lxml")

        # Remove noisy elements
        for tag in soup.find_all(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Try to find the main article body
        article = (
            soup.find("article")
            or soup.find("main")
            or soup.find(attrs={"role": "main"})
            or soup.find("div", class_=lambda c: c and "content" in c)
        )
        if not article:
            article = soup.body

        if not article:
            return None

        text = article.get_text(separator="\n", strip=True)
        title = self._extract_title_from_html(html)

        from ..core.utils import clean_text, generate_excerpt

        content = clean_text(text)
        if len(content) < 50:
            return None

        return ParseResult(
            url=url,
            title=title,
            content=content,
            excerpt=generate_excerpt(content),
        )

    @staticmethod
    def _extract_title_from_html(html: str) -> str:
        """Extract the ``<title>`` tag from raw HTML."""
        soup = BeautifulSoup(html, "lxml")
        tag = soup.find("title")
        return tag.get_text(strip=True) if tag else ""
