"""
DeepReader Skill - Reddit Parser
==================================
Fetches Reddit posts and comments using Reddit's native ``.json``
URL suffix — **zero dependencies, zero API keys, zero configuration**.

How it works
------------
Reddit natively supports appending ``.json`` to any post URL, returning
the full post data + comment tree as structured JSON.  For example::

    https://www.reddit.com/r/python/comments/abc123/my_post/
    →  https://www.reddit.com/r/python/comments/abc123/my_post/.json

This approach requires:
- No API keys or OAuth tokens
- No external libraries (uses only ``urllib`` from stdlib)
- No registration or app creation

The only requirement is a descriptive ``User-Agent`` header to avoid
Reddit's generic rate-limiting (HTTP 429).

Content extracted
-----------------
- Post title, body (selftext), author, score, flair
- Subreddit info
- Top-level comments sorted by score (configurable limit)
- Nested reply threads (configurable depth)
- Media URLs (images, videos, galleries)
- Crosspost/link detection
"""

from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlparse

from .base import BaseParser, ParseResult

logger = logging.getLogger("deepreader.parsers.reddit")


class RedditParser(BaseParser):
    """Parse Reddit posts and comments via the native .json API."""

    name = "reddit"
    timeout = 30

    # Maximum number of top-level comments to include.
    max_comments: int = 15

    # Maximum reply nesting depth to include.
    max_reply_depth: int = 3

    # User-Agent for Reddit requests (required to avoid 429).
    reddit_user_agent: str = "DeepReeder/1.0 (OpenClaw Skill; +https://github.com/astonysh/OpenClaw-DeepReeder)"

    def can_handle(self, url: str) -> bool:
        """Return ``True`` for reddit.com URLs that look like post links."""
        from ..core.utils import is_reddit_url
        return is_reddit_url(url)

    def parse(self, url: str) -> ParseResult:
        """Fetch a Reddit post + comments via the .json suffix."""
        json_url = self._build_json_url(url)
        if not json_url:
            return ParseResult.failure(
                url,
                "Could not build a valid Reddit JSON URL. "
                "Expected format: https://www.reddit.com/r/subreddit/comments/id/title/",
            )

        max_attempts = 2
        last_error = ""

        for attempt in range(max_attempts):
            try:
                req = urllib.request.Request(
                    json_url,
                    headers={
                        "User-Agent": self.reddit_user_agent,
                        "Accept": "application/json",
                    },
                )
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    data = json.loads(resp.read().decode())

                return self._build_result(url, data)

            except urllib.error.HTTPError as exc:
                if exc.code == 429:
                    last_error = "Reddit rate limit hit (HTTP 429). Try again later."
                    if attempt < max_attempts - 1:
                        time.sleep(2)
                        continue
                elif exc.code == 404:
                    last_error = "Post not found (HTTP 404). It may be deleted or private."
                elif exc.code == 403:
                    last_error = "Access denied (HTTP 403). The subreddit may be private."
                else:
                    last_error = f"HTTP {exc.code}: {exc.reason}"
                return ParseResult.failure(url, last_error)

            except urllib.error.URLError:
                last_error = "Network error: failed to reach Reddit"
                if attempt < max_attempts - 1:
                    time.sleep(1)
                    continue

            except Exception as exc:  # noqa: BLE001
                last_error = f"Unexpected error: {exc}"
                logger.warning("Reddit parser unexpected error: %s", exc)
                break

        return ParseResult.failure(url, last_error)

    # ==================================================================
    #  Result Builder
    # ==================================================================

    def _build_result(self, original_url: str, data: list) -> ParseResult:
        """Transform Reddit JSON response into a ParseResult."""
        from ..core.utils import clean_text, generate_excerpt

        if not isinstance(data, list) or len(data) < 1:
            return ParseResult.failure(
                original_url, "Unexpected Reddit JSON structure."
            )

        # --- Post data (first element) ---
        try:
            post = data[0]["data"]["children"][0]["data"]
        except (KeyError, IndexError, TypeError):
            return ParseResult.failure(
                original_url, "Could not extract post data from Reddit JSON."
            )

        title = post.get("title", "Untitled")
        author = post.get("author", "[deleted]")
        subreddit = post.get("subreddit_name_prefixed", "r/unknown")
        score = post.get("score", 0)
        upvote_ratio = post.get("upvote_ratio", 0)
        num_comments = post.get("num_comments", 0)
        created_utc = post.get("created_utc", 0)
        selftext = post.get("selftext", "")
        flair = post.get("link_flair_text", "")
        is_self = post.get("is_self", True)
        post_url = post.get("url", "")
        permalink = post.get("permalink", "")

        # Format timestamp
        timestamp = ""
        if created_utc:
            dt = datetime.fromtimestamp(created_utc, tz=timezone.utc)
            timestamp = dt.strftime("%Y-%m-%d %H:%M UTC")

        # --- Build content ---
        content_parts: list[str] = []

        # Header
        content_parts.append(f"# {title}\n")
        content_parts.append(
            f"**{subreddit}** · u/{author} · {timestamp}\n"
        )

        # Stats line
        stats_line = (
            f"⬆️ {score:,} ({upvote_ratio:.0%} upvoted) · "
            f"💬 {num_comments:,} comments"
        )
        if flair:
            stats_line += f" · 🏷️ {flair}"
        content_parts.append(f"📊 {stats_line}\n")

        content_parts.append("---\n")

        # Post body
        if selftext:
            content_parts.append(selftext)
        elif not is_self and post_url:
            content_parts.append(f"🔗 **Link post**: [{post_url}]({post_url})")

        # --- Media detection ---
        media_parts = self._extract_media(post)
        if media_parts:
            content_parts.append("\n\n---\n### 🖼️ Media\n")
            content_parts.extend(media_parts)

        # --- Comments (second element) ---
        if len(data) >= 2:
            comments = self._extract_comments(data[1])
            if comments:
                content_parts.append("\n\n---\n### 💬 Top Comments\n")
                content_parts.extend(comments)

        full_content = clean_text("\n".join(content_parts))

        # --- Tags ---
        tags = ["reddit", subreddit.lower()]
        if flair:
            tags.append(flair.lower().replace(" ", "-"))
        if not is_self:
            tags.append("link-post")

        return ParseResult(
            url=original_url,
            title=f"[{subreddit}] {title}",
            content=full_content,
            author=f"u/{author}",
            excerpt=generate_excerpt(full_content),
            tags=tags,
        )

    # ==================================================================
    #  Comment Extraction
    # ==================================================================

    def _extract_comments(self, comment_listing: dict) -> list[str]:
        """Extract top-level comments sorted by score."""
        try:
            children = comment_listing["data"]["children"]
        except (KeyError, TypeError):
            return []

        # Filter out "more" comment stubs and deleted comments
        comments = []
        for child in children:
            if child.get("kind") != "t1":
                continue
            cdata = child.get("data", {})
            body = cdata.get("body", "")
            if not body or body == "[deleted]" or body == "[removed]":
                continue
            comments.append(cdata)

        # Sort by score (highest first)
        comments.sort(key=lambda c: c.get("score", 0), reverse=True)

        # Build formatted comment list
        result: list[str] = []
        for cdata in comments[: self.max_comments]:
            author = cdata.get("author", "[deleted]")
            score = cdata.get("score", 0)
            body = cdata.get("body", "").strip()

            # Format the comment
            result.append(f"**u/{author}** (⬆️ {score:,}):\n")
            # Indent comment body as blockquote
            quoted_body = "\n".join(f"> {line}" for line in body.split("\n"))
            result.append(f"{quoted_body}\n")

            # Extract nested replies (limited depth)
            replies = cdata.get("replies")
            if replies and isinstance(replies, dict):
                nested = self._extract_nested_replies(replies, depth=1)
                if nested:
                    result.extend(nested)

            result.append("")  # blank line between comments

        return result

    def _extract_nested_replies(
        self, reply_listing: dict, depth: int,
    ) -> list[str]:
        """Recursively extract nested replies up to max_reply_depth."""
        if depth >= self.max_reply_depth:
            return []

        try:
            children = reply_listing["data"]["children"]
        except (KeyError, TypeError):
            return []

        result: list[str] = []
        indent = "  " * depth

        for child in children[:5]:  # limit nested replies
            if child.get("kind") != "t1":
                continue
            cdata = child.get("data", {})
            body = cdata.get("body", "")
            if not body or body in ("[deleted]", "[removed]"):
                continue

            author = cdata.get("author", "[deleted]")
            score = cdata.get("score", 0)

            result.append(f"{indent}↳ **u/{author}** (⬆️ {score:,}):\n")
            quoted = "\n".join(
                f"{indent}> {line}" for line in body.strip().split("\n")
            )
            result.append(f"{quoted}\n")

            # Recurse deeper
            sub_replies = cdata.get("replies")
            if sub_replies and isinstance(sub_replies, dict):
                nested = self._extract_nested_replies(sub_replies, depth + 1)
                if nested:
                    result.extend(nested)

        return result

    # ==================================================================
    #  Media Extraction
    # ==================================================================

    def _extract_media(self, post: dict) -> list[str]:
        """Extract media URLs from a Reddit post."""
        parts: list[str] = []

        # Direct image URL
        url = post.get("url", "")
        if any(url.endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".gif", ".webp")):
            parts.append(f"![Image]({url})\n")

        # Reddit gallery
        if post.get("is_gallery"):
            media_metadata = post.get("media_metadata", {})
            for i, (_, media) in enumerate(media_metadata.items(), 1):
                if media.get("status") == "valid" and media.get("s", {}).get("u"):
                    img_url = media["s"]["u"].replace("&amp;", "&")
                    parts.append(f"![Gallery image {i}]({img_url})\n")

        # Reddit video
        reddit_video = (post.get("media") or {}).get("reddit_video", {})
        if reddit_video.get("fallback_url"):
            parts.append(f"🎬 Video: [{reddit_video['fallback_url']}]({reddit_video['fallback_url']})\n")

        # External video (e.g. YouTube embed)
        if post.get("is_video") and not reddit_video:
            parts.append(f"🎬 External video: [{url}]({url})\n")

        return parts

    # ==================================================================
    #  URL Utilities
    # ==================================================================

    @staticmethod
    def _build_json_url(url: str) -> str | None:
        """Convert a Reddit post URL to its .json API endpoint.

        Examples::
            https://www.reddit.com/r/python/comments/abc123/my_post/
            → https://www.reddit.com/r/python/comments/abc123/my_post/.json

            https://old.reddit.com/r/python/comments/abc123/
            → https://www.reddit.com/r/python/comments/abc123/.json
        """
        parsed = urlparse(url)

        # Validate it looks like a Reddit post URL
        if not parsed.path or "/comments/" not in parsed.path:
            return None

        # Normalize to www.reddit.com
        path = parsed.path.rstrip("/")

        # Append .json
        json_url = f"https://www.reddit.com{path}/.json"
        return json_url
