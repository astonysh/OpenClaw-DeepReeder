"""
DeepReader Skill - Twitter / X Parser
=======================================
Hybrid strategy for reading tweets:

1. **Primary**:  FxTwitter public API — zero dependencies, reliable,
   supports regular tweets, long tweets, X Articles, quoted tweets,
   media, and engagement stats.
2. **Fallback**: Rotate through public Nitter instances to fetch tweet
   content (especially useful for fetching reply threads).

Why FxTwitter first?
---------------------
FxTwitter (api.fxtwitter.com) is a public, maintenance-free API that
returns structured JSON.  It is far more reliable than Nitter instances
which frequently go offline.  It also returns rich metadata (stats,
media, articles) that Nitter does not expose.

Nitter as fallback
-------------------
Nitter HTML scraping is retained as a secondary strategy, primarily
because it can extract reply threads (first N replies), which FxTwitter
does not provide.

Credits
--------
FxTwitter integration inspired by `x-tweet-fetcher` by ythx-101:
https://github.com/ythx-101/x-tweet-fetcher
"""

from __future__ import annotations

import json
import logging
import random
import re
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .base import BaseParser, ParseResult

logger = logging.getLogger("deepreader.parsers.twitter")


# ---------------------------------------------------------------------------
# Known public Nitter instances (community-maintained)
# Used only as fallback for reply-thread extraction.
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
    """Parse tweets from Twitter / X.

    Primary:   FxTwitter API (structured JSON, zero deps, rich metadata).
    Fallback:  Nitter HTML scraping (reply threads).
    """

    name = "twitter"
    timeout = 30

    # Maximum Nitter instances to try for reply extraction.
    max_nitter_retries: int = 3

    def can_handle(self, url: str) -> bool:
        """Return ``True`` for twitter.com / x.com URLs."""
        from ..core.utils import is_twitter_url
        return is_twitter_url(url)

    def parse(self, url: str) -> ParseResult:
        """Attempt to read a tweet — FxTwitter first, Nitter fallback."""
        tweet_info = self._extract_tweet_info(url)
        if not tweet_info:
            return ParseResult.failure(
                url,
                "Could not extract a valid tweet path from this URL. "
                "Expected format: https://twitter.com/user/status/123456",
            )

        username, tweet_id = tweet_info

        # ----- Strategy 1: FxTwitter API (primary) -----
        result = self._parse_fxtwitter(url, username, tweet_id)
        if result.success:
            return result

        logger.warning(
            "FxTwitter failed for %s, trying Nitter fallback: %s",
            url, result.error,
        )

        # ----- Strategy 2: Nitter HTML scraping (fallback) -----
        tweet_path = f"{username}/status/{tweet_id}"
        nitter_result = self._parse_nitter_fallback(url, tweet_path)
        if nitter_result.success:
            return nitter_result

        # ----- Both strategies failed -----
        return ParseResult.failure(
            url,
            f"⚠️ All strategies failed for this tweet.\n"
            f"FxTwitter error: {result.error}\n"
            f"Nitter error: {nitter_result.error}\n\n"
            f"The tweet URL was: {url}\n"
            f"This may be a deleted/private tweet, or a temporary service outage.",
        )

    # ==================================================================
    #  FxTwitter API — Primary Strategy
    # ==================================================================

    def _parse_fxtwitter(
        self, original_url: str, username: str, tweet_id: str,
    ) -> ParseResult:
        """Fetch tweet via the FxTwitter public JSON API."""
        api_url = f"https://api.fxtwitter.com/{username}/status/{tweet_id}"

        max_attempts = 2
        last_error = ""

        for attempt in range(max_attempts):
            try:
                req = urllib.request.Request(
                    api_url,
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    data = json.loads(resp.read().decode())

                if data.get("code") != 200:
                    last_error = (
                        f"FxTwitter returned code {data.get('code')}: "
                        f"{data.get('message', 'Unknown')}"
                    )
                    return ParseResult.failure(original_url, last_error)

                return self._build_result_from_fxtwitter(original_url, data)

            except urllib.error.HTTPError as exc:
                last_error = f"HTTP {exc.code}: {exc.reason}"
                return ParseResult.failure(original_url, last_error)

            except urllib.error.URLError:
                last_error = "Network error: failed to reach FxTwitter API"
                if attempt < max_attempts - 1:
                    time.sleep(1)
                    continue

            except Exception as exc:  # noqa: BLE001
                last_error = f"Unexpected error: {exc}"
                logger.warning("FxTwitter unexpected error: %s", exc)
                break

        return ParseResult.failure(original_url, last_error)

    def _build_result_from_fxtwitter(
        self, original_url: str, data: dict,
    ) -> ParseResult:
        """Transform FxTwitter JSON response into a ParseResult."""
        from ..core.utils import clean_text, generate_excerpt

        tweet = data["tweet"]
        author = tweet.get("author", {}).get("name", "")
        screen_name = tweet.get("author", {}).get("screen_name", "")
        created_at = tweet.get("created_at", "")
        tweet_text = tweet.get("text", "")
        is_article = bool(tweet.get("article"))
        is_note = tweet.get("is_note_tweet", False)

        # --- Engagement stats ---
        stats_line = (
            f"❤️ {tweet.get('likes', 0):,}  "
            f"🔁 {tweet.get('retweets', 0):,}  "
            f"🔖 {tweet.get('bookmarks', 0):,}  "
            f"👁️ {tweet.get('views', 0):,}  "
            f"💬 {tweet.get('replies', 0):,}"
        )

        content_parts: list[str] = []

        # --- X Article (long-form content) ---
        if is_article:
            article = tweet["article"]
            article_title = article.get("title", "")
            article_blocks = article.get("content", {}).get("blocks", [])
            article_text = "\n\n".join(
                b.get("text", "") for b in article_blocks if b.get("text", "")
            )
            word_count = len(article_text.split())

            title = f"📝 {article_title}" if article_title else f"X Article by @{screen_name}"

            content_parts.append(f"# {article_title}\n")
            content_parts.append(f"**By @{screen_name}** ({author}) · {created_at}\n")
            content_parts.append(f"📊 {stats_line}\n")
            content_parts.append(f"📐 {word_count:,} words\n")
            content_parts.append("---\n")
            content_parts.append(article_text)

        else:
            # --- Regular tweet / note tweet ---
            title = f"Tweet by @{screen_name}"
            if created_at:
                title += f" ({created_at})"

            content_parts.append(f"**@{screen_name}** ({author})\n")
            content_parts.append(f"🕐 {created_at}\n")
            content_parts.append(f"📊 {stats_line}\n")
            content_parts.append("---\n")
            content_parts.append(tweet_text)

            if is_note:
                content_parts.append("\n\n> 📝 *This is a Note Tweet (long-form)*")

        # --- Quoted tweet ---
        quote = tweet.get("quote")
        if quote:
            qt_author = quote.get("author", {}).get("screen_name", "unknown")
            qt_text = quote.get("text", "")
            content_parts.append("\n\n---\n### 🔁 Quoted Tweet\n")
            content_parts.append(f"> **@{qt_author}**: {qt_text}\n")
            qt_stats = (
                f"> ❤️ {quote.get('likes', 0):,}  "
                f"🔁 {quote.get('retweets', 0):,}  "
                f"👁️ {quote.get('views', 0):,}"
            )
            content_parts.append(qt_stats)

        # --- Media ---
        media = tweet.get("media", {})
        all_media = media.get("all", [])
        if all_media:
            content_parts.append("\n\n---\n### 🖼️ Media\n")
            for i, item in enumerate(all_media, 1):
                media_type = item.get("type", "unknown")
                media_url = item.get("url", "")
                if media_type == "photo":
                    content_parts.append(f"![Image {i}]({media_url})\n")
                elif media_type == "video":
                    content_parts.append(f"🎬 Video: [{media_url}]({media_url})\n")
                elif media_type == "gif":
                    content_parts.append(f"🎞️ GIF: [{media_url}]({media_url})\n")

        full_content = clean_text("\n".join(content_parts))

        tags = ["twitter"]
        if is_article:
            tags.append("x-article")
        if is_note:
            tags.append("note-tweet")
        if quote:
            tags.append("quote-tweet")
        if all_media:
            tags.append("has-media")

        return ParseResult(
            url=original_url,
            title=title,
            content=full_content,
            author=f"@{screen_name}" if screen_name else author,
            excerpt=generate_excerpt(full_content),
            tags=tags,
        )

    # ==================================================================
    #  Nitter HTML Scraping — Fallback Strategy
    # ==================================================================

    def _parse_nitter_fallback(self, original_url: str, tweet_path: str) -> ParseResult:
        """Try Nitter instances as a fallback (useful for reply threads)."""
        instances = random.sample(
            NITTER_INSTANCES,
            min(self.max_nitter_retries, len(NITTER_INSTANCES)),
        )

        last_error = ""
        for instance in instances:
            nitter_url = f"{instance}/{tweet_path}"
            logger.info("Trying Nitter fallback: %s", nitter_url)
            try:
                result = self._parse_nitter_page(original_url, nitter_url)
                if result.success:
                    return result
                last_error = result.error
            except requests.RequestException as exc:
                last_error = str(exc)
                logger.warning("Nitter %s failed: %s", instance, exc)
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                logger.warning("Nitter unexpected error: %s", exc)

        return ParseResult.failure(
            original_url,
            f"All Nitter instances failed. Last error: {last_error}",
        )

    def _parse_nitter_page(self, original_url: str, nitter_url: str) -> ParseResult:
        """Fetch and parse a single Nitter page."""
        resp = requests.get(
            nitter_url,
            headers=self._get_headers(),
            timeout=self.timeout,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        tweet_div = soup.find("div", class_="tweet-content") or soup.find(
            "div", class_="main-tweet"
        )
        if not tweet_div:
            return ParseResult.failure(
                original_url,
                f"Nitter page loaded but no content found at {nitter_url}",
            )

        tweet_text = tweet_div.get_text(separator="\n", strip=True)

        author_tag = soup.find("a", class_="fullname") or soup.find(
            "span", class_="username"
        )
        author = author_tag.get_text(strip=True) if author_tag else ""

        date_tag = soup.find("span", class_="tweet-date")
        timestamp = ""
        if date_tag:
            a_tag = date_tag.find("a")
            timestamp = a_tag.get("title", "") if a_tag else date_tag.get_text(strip=True)

        title = f"Tweet by {author}" if author else "Tweet"
        if timestamp:
            title += f" ({timestamp})"

        # Collect reply context
        replies: list[str] = []
        reply_divs = soup.find_all("div", class_="reply")
        for rd in reply_divs[:5]:
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
            tags=["twitter", "nitter-fallback"],
        )

    # ==================================================================
    #  URL Utilities
    # ==================================================================

    @staticmethod
    def _extract_tweet_info(url: str) -> tuple[str, str] | None:
        """Extract (username, tweet_id) from a Twitter URL.

        Returns ``None`` if the URL doesn't match the expected pattern.
        """
        match = re.search(
            r"(?:x\.com|twitter\.com)/([a-zA-Z0-9_]{1,15})/status/(\d+)", url,
        )
        if match:
            return match.group(1), match.group(2)
        return None

    @staticmethod
    def _extract_tweet_path(url: str) -> str | None:
        """Legacy: extract ``user/status/id`` path from a Twitter URL."""
        parsed = urlparse(url)
        match = re.match(r"^/([^/]+)/status/(\d+)", parsed.path)
        if match:
            return f"{match.group(1)}/status/{match.group(2)}"
        return None
