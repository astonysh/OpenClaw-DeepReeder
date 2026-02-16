"""
DeepReader Skill - Twitter / X Parser
=======================================
Strategy-pattern implementation for reading tweets:

1. **Primary**:  Rotate through public Nitter instances to fetch tweet
   content without any API keys.
2. **Fallback**: Gracefully degrade with informative guidance on how to
   plug in a scraping service (ZenRows, ScrapingBee) or browser cookies.

Why Nitter?
-----------
Twitter's official API is paywalled and rate-limited.  Nitter is an
open-source alternative frontend that serves tweets as plain HTML,
making extraction trivial.  However, public instances may go down,
so we rotate through several and retry.

Extending with a paid scraping service
---------------------------------------
If all Nitter instances fail, you can integrate a proxy/rendering
service.  See the ``_fallback_scrape`` method for detailed guidance
on where to plug in ZenRows or browser cookies.
"""

from __future__ import annotations

import logging
import random
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .base import BaseParser, ParseResult

logger = logging.getLogger("deepreader.parsers.twitter")


# ---------------------------------------------------------------------------
# Known public Nitter instances (community-maintained)
# Update this list periodically – instances come and go.
# ---------------------------------------------------------------------------
NITTER_INSTANCES: list[str] = [
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.woodland.cafe",
    "https://nitter.1d4.us",
    "https://nitter.kavin.rocks",
    "https://nitter.unixfox.eu",
    "https://nitter.d420.de",
    "https://nitter.moomoo.me",
]


class TwitterParser(BaseParser):
    """Parse tweets from Twitter / X via Nitter relay instances."""

    name = "twitter"
    timeout = 20

    # Maximum number of Nitter instances to try before giving up.
    max_retries: int = 4

    def can_handle(self, url: str) -> bool:
        """Return ``True`` for twitter.com / x.com URLs."""
        from ..core.utils import is_twitter_url
        return is_twitter_url(url)

    def parse(self, url: str) -> ParseResult:
        """Attempt to read a tweet via Nitter, with graceful fallbacks."""
        tweet_path = self._extract_tweet_path(url)
        if not tweet_path:
            return ParseResult.failure(
                url,
                "Could not extract a valid tweet path from this URL. "
                "Expected format: https://twitter.com/user/status/123456",
            )

        # Shuffle instances to spread load and improve resilience.
        instances = random.sample(
            NITTER_INSTANCES,
            min(self.max_retries, len(NITTER_INSTANCES)),
        )

        last_error = ""
        for instance in instances:
            nitter_url = f"{instance}/{tweet_path}"
            logger.info("Trying Nitter instance: %s", nitter_url)
            try:
                result = self._parse_nitter(url, nitter_url)
                if result.success:
                    return result
                last_error = result.error
            except requests.RequestException as exc:
                last_error = str(exc)
                logger.warning("Nitter instance %s failed: %s", instance, exc)
                continue
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                logger.warning("Unexpected error with %s: %s", instance, exc)
                continue

        # ------------------------------------------------------------------
        # All Nitter instances failed → fallback
        # ------------------------------------------------------------------
        return self._fallback_scrape(url, last_error)

    # ------------------------------------------------------------------
    # Nitter HTML Parsing
    # ------------------------------------------------------------------

    def _parse_nitter(self, original_url: str, nitter_url: str) -> ParseResult:
        """Fetch and parse a single Nitter page."""
        resp = requests.get(
            nitter_url,
            headers=self._get_headers(),
            timeout=self.timeout,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # --- Tweet body ---
        tweet_div = soup.find("div", class_="tweet-content") or soup.find(
            "div", class_="main-tweet"
        )
        if not tweet_div:
            return ParseResult.failure(
                original_url,
                f"Nitter page loaded but no tweet content found at {nitter_url}",
            )

        tweet_text = tweet_div.get_text(separator="\n", strip=True)

        # --- Author ---
        author_tag = soup.find("a", class_="fullname") or soup.find(
            "span", class_="username"
        )
        author = author_tag.get_text(strip=True) if author_tag else ""

        # --- Timestamp ---
        date_tag = soup.find("span", class_="tweet-date")
        timestamp = ""
        if date_tag:
            a_tag = date_tag.find("a")
            timestamp = a_tag.get("title", "") if a_tag else date_tag.get_text(strip=True)

        # Build a nice title
        title = f"Tweet by {author}" if author else "Tweet"
        if timestamp:
            title += f" ({timestamp})"

        # Collect reply context if present
        replies: list[str] = []
        reply_divs = soup.find_all("div", class_="reply")
        for rd in reply_divs[:5]:  # limit to first 5 replies
            reply_content = rd.find("div", class_="tweet-content")
            if reply_content:
                replies.append(reply_content.get_text(separator=" ", strip=True))

        content_parts = [tweet_text]
        if replies:
            content_parts.append("\n\n---\n### Replies\n")
            for i, reply in enumerate(replies, 1):
                content_parts.append(f"**Reply {i}:** {reply}\n")

        from ..core.utils import clean_text, generate_excerpt

        full_content = clean_text("\n".join(content_parts))

        return ParseResult(
            url=original_url,
            title=title,
            content=full_content,
            author=author,
            excerpt=generate_excerpt(full_content),
            tags=["twitter"],
        )

    # ------------------------------------------------------------------
    # Fallback Strategy
    # ------------------------------------------------------------------

    def _fallback_scrape(self, url: str, last_error: str) -> ParseResult:
        """Produce a graceful degradation result with integration guidance.

        .. rubric:: How to extend with a paid scraping service

        **Option A – ZenRows / ScrapingBee:**

        1. Sign up at https://www.zenrows.com/ or https://www.scrapingbee.com/
        2. Obtain your API key.
        3. Replace the body of this method with::

                import requests
                api_key = "YOUR_ZENROWS_API_KEY"
                params = {
                    "url": url,
                    "apikey": api_key,
                    "js_render": "true",
                    "premium_proxy": "true",
                }
                resp = requests.get("https://api.zenrows.com/v1/", params=params)
                html = resp.text
                # Then parse 'html' with BeautifulSoup to extract tweet text.

        **Option B – Browser Cookies:**

        1. Export your Twitter session cookies (e.g. with the *EditThisCookie*
           browser extension) as a Netscape-format ``cookies.txt`` file.
        2. Place the file at ``deepreader_skill/twitter_cookies.txt``.
        3. Modify ``_fetch_with_cookies()`` below to load and send them::

                import http.cookiejar
                jar = http.cookiejar.MozillaCookieJar("twitter_cookies.txt")
                jar.load()
                session = requests.Session()
                session.cookies = jar
                resp = session.get(url, headers=self._get_headers())

        **Option C – Playwright / Selenium headless browser:**

        For the most reliable extraction, you can use a headless browser.
        This is heavier but handles JavaScript-rendered content::

                from playwright.sync_api import sync_playwright
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    page.goto(url, wait_until="networkidle")
                    html = page.content()
                    browser.close()
                # Then parse 'html' as above.

        Returns a :class:`ParseResult` with ``success=False`` and the
        guidance embedded in the error message.
        """
        error_msg = (
            f"⚠️ All Nitter instances failed for this tweet.\n"
            f"Last error: {last_error}\n\n"
            f"The tweet URL was: {url}\n\n"
            f"💡 To improve Twitter support, consider:\n"
            f"  1. Updating the NITTER_INSTANCES list in twitter.py\n"
            f"  2. Integrating a paid scraping service (ZenRows/ScrapingBee)\n"
            f"  3. Using browser cookies for authenticated access\n"
            f"  See the _fallback_scrape() docstring for detailed instructions."
        )
        logger.warning("Twitter fallback triggered for %s", url)
        return ParseResult.failure(url, error_msg)

    # ------------------------------------------------------------------
    # URL Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_tweet_path(url: str) -> str | None:
        """Extract the tweet path (``user/status/id``) from a Twitter URL.

        Returns ``None`` if the URL doesn't match the expected pattern.
        """
        parsed = urlparse(url)
        # Match patterns like /username/status/1234567890
        match = re.match(r"^/([^/]+)/status/(\d+)", parsed.path)
        if match:
            return f"{match.group(1)}/status/{match.group(2)}"
        return None
