"""
DeepReader Skill - YouTube Parser
==================================
Fetches video metadata and transcripts/subtitles using the
``youtube_transcript_api`` library.  No API key required for
publicly available transcripts.
"""

from __future__ import annotations

import logging

import requests
from bs4 import BeautifulSoup

from .base import BaseParser, ParseResult

logger = logging.getLogger("deepreader.parsers.youtube")


class YouTubeParser(BaseParser):
    """Extract transcripts and metadata from YouTube videos."""

    name = "youtube"
    timeout = 25

    # Preferred language codes for transcripts (in priority order).
    preferred_languages: list[str] = ["en", "zh-Hans", "zh-Hant", "zh", "ja", "ko", "de", "fr", "es"]

    def can_handle(self, url: str) -> bool:
        from ..core.utils import is_youtube_url
        return is_youtube_url(url)

    def parse(self, url: str) -> ParseResult:
        """Fetch the YouTube video transcript and metadata."""
        from ..core.utils import extract_youtube_video_id

        video_id = extract_youtube_video_id(url)
        if not video_id:
            return ParseResult.failure(
                url,
                "Could not extract a valid YouTube video ID from this URL.",
            )

        # Step 1: Get video metadata from the page
        title, author, description = self._fetch_metadata(url)

        # Step 2: Get the transcript
        transcript_text, transcript_lang = self._fetch_transcript(video_id)

        if not transcript_text:
            # If no transcript available, still save what we have
            content_parts = []
            if description:
                content_parts.append(f"**Video Description:**\n\n{description}")
            content_parts.append(
                "\n\n> ⚠️ No transcript/subtitles available for this video. "
                "The video may not have captions enabled."
            )
            content = "\n".join(content_parts)
        else:
            content_parts = []
            if transcript_lang:
                content_parts.append(f"*Transcript language: {transcript_lang}*\n")
            content_parts.append(transcript_text)
            if description:
                content_parts.append(f"\n\n---\n\n**Video Description:**\n\n{description}")
            content = "\n".join(content_parts)

        from ..core.utils import clean_text, generate_excerpt

        content = clean_text(content)

        return ParseResult(
            url=url,
            title=title or f"YouTube Video ({video_id})",
            content=content,
            author=author,
            excerpt=generate_excerpt(content),
            tags=["youtube", "video"],
        )

    # ------------------------------------------------------------------
    # Transcript Extraction
    # ------------------------------------------------------------------

    def _fetch_transcript(self, video_id: str) -> tuple[str, str]:
        """Fetch the transcript for a YouTube video.

        Returns a tuple of ``(transcript_text, language_code)``.
        Returns ``("", "")`` if no transcript is available.
        """
        try:
            from youtube_transcript_api import YouTubeTranscriptApi

            # Try to get transcript in preferred languages first
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

                # Try to find a manually created transcript in preferred languages
                transcript = None
                lang_code = ""

                for lang in self.preferred_languages:
                    try:
                        transcript = transcript_list.find_manually_created_transcript([lang])
                        lang_code = lang
                        break
                    except Exception:  # noqa: BLE001
                        continue

                # Fall back to auto-generated transcripts
                if transcript is None:
                    for lang in self.preferred_languages:
                        try:
                            transcript = transcript_list.find_generated_transcript([lang])
                            lang_code = f"{lang} (auto-generated)"
                            break
                        except Exception:  # noqa: BLE001
                            continue

                # Last resort: get whatever is available
                if transcript is None:
                    try:
                        available = list(transcript_list)
                        if available:
                            transcript = available[0]
                            lang_code = transcript.language_code
                    except Exception:  # noqa: BLE001
                        pass

                if transcript is not None:
                    entries = transcript.fetch()
                    lines = [entry["text"] for entry in entries]
                    return self._format_transcript(lines), lang_code

            except Exception as exc:  # noqa: BLE001
                logger.warning("Transcript list API failed for %s: %s", video_id, exc)

                # Direct fetch as ultimate fallback
                try:
                    entries = YouTubeTranscriptApi.get_transcript(video_id)
                    lines = [entry["text"] for entry in entries]
                    return self._format_transcript(lines), "auto"
                except Exception as inner_exc:  # noqa: BLE001
                    logger.warning("Direct transcript fetch failed: %s", inner_exc)

        except ImportError:
            logger.error(
                "youtube_transcript_api is not installed. "
                "Run: pip install youtube-transcript-api"
            )

        return "", ""

    @staticmethod
    def _format_transcript(lines: list[str]) -> str:
        """Join transcript lines into clean paragraphs.

        Groups lines into paragraphs of ~5 sentences for readability.
        """
        if not lines:
            return ""

        paragraphs: list[str] = []
        current_paragraph: list[str] = []
        sentence_count = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue
            current_paragraph.append(line)
            # Count sentence-ending punctuation
            if any(line.endswith(p) for p in (".", "!", "?", "。", "！", "？")):
                sentence_count += 1
            if sentence_count >= 5:
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []
                sentence_count = 0

        # Don't forget the last paragraph
        if current_paragraph:
            paragraphs.append(" ".join(current_paragraph))

        return "\n\n".join(paragraphs)

    # ------------------------------------------------------------------
    # Metadata Extraction
    # ------------------------------------------------------------------

    def _fetch_metadata(self, url: str) -> tuple[str, str, str]:
        """Extract title, channel name, and description from the YouTube page.

        Returns ``(title, author, description)``.
        """
        try:
            resp = requests.get(url, headers=self._get_headers(), timeout=self.timeout)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            # Title: <meta property="og:title">
            title = ""
            og_title = soup.find("meta", property="og:title")
            if og_title:
                title = og_title.get("content", "")
            if not title:
                title_tag = soup.find("title")
                title = title_tag.get_text(strip=True) if title_tag else ""
                # Remove " - YouTube" suffix
                if title.endswith(" - YouTube"):
                    title = title[:-10].strip()

            # Author / channel
            author = ""
            link_author = soup.find("link", attrs={"itemprop": "name"})
            if link_author:
                author = link_author.get("content", "")
            if not author:
                og_author = soup.find("meta", property="og:video:tag")
                if og_author:
                    author = og_author.get("content", "")

            # Description
            description = ""
            og_desc = soup.find("meta", property="og:description")
            if og_desc:
                description = og_desc.get("content", "")

            return title, author, description

        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to fetch YouTube metadata for %s: %s", url, exc)
            return "", "", ""
