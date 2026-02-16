"""
DeepReader Skill - Parser Router
==================================
Decides which parser to use based on URL domain/pattern analysis.
Follows the **Strategy Pattern** — parsers are registered and
selected dynamically.
"""

from __future__ import annotations

import logging
from typing import Sequence

from ..core.utils import is_reddit_url, is_twitter_url, is_youtube_url
from ..parsers.base import BaseParser, ParseResult
from ..parsers.generic import GenericParser
from ..parsers.reddit import RedditParser
from ..parsers.twitter import TwitterParser
from ..parsers.youtube import YouTubeParser

logger = logging.getLogger("deepreader.router")


class ParserRouter:
    """Select and execute the appropriate parser for a given URL.

    The router maintains an ordered list of specialized parsers.  For
    each URL, it iterates through the list and uses the first parser
    whose :meth:`can_handle` returns ``True``.  If no specialized
    parser matches, the :class:`GenericParser` is used as a fallback.

    Usage::

        router = ParserRouter()
        result = router.route("https://twitter.com/user/status/123")
        # → uses TwitterParser

        result = router.route("https://example.com/blog/post")
        # → uses GenericParser
    """

    def __init__(
        self,
        extra_parsers: Sequence[BaseParser] | None = None,
    ) -> None:
        """Initialize with default + optional extra parsers.

        Args:
            extra_parsers: Additional parser instances to register.
                           They are checked **before** the built-in
                           parsers, allowing user overrides.
        """
        # Specialized parsers (checked in order)
        self._parsers: list[BaseParser] = []

        # Register user-supplied parsers first (highest priority)
        if extra_parsers:
            self._parsers.extend(extra_parsers)

        # Built-in specialized parsers
        self._parsers.extend([
            TwitterParser(),
            YouTubeParser(),
            RedditParser(),
        ])

        # Fallback parser (always matches)
        self._fallback = GenericParser()

        logger.info(
            "ParserRouter initialized with %d specialized parsers + generic fallback",
            len(self._parsers),
        )

    def route(self, url: str) -> ParseResult:
        """Determine the correct parser and execute it.

        Args:
            url: The URL to parse.

        Returns:
            A :class:`ParseResult` with the extracted content or an
            error description.
        """
        # Check specialized parsers first
        for parser in self._parsers:
            if parser.can_handle(url):
                logger.info("Routing %s → %s parser", url, parser.name)
                return parser.parse(url)

        # Fallback to generic parser
        logger.info("Routing %s → generic parser (fallback)", url)
        return self._fallback.parse(url)

    def register_parser(self, parser: BaseParser, priority: bool = False) -> None:
        """Register a new parser at runtime.

        Args:
            parser:   The parser instance to add.
            priority: If ``True``, insert at the beginning of the list
                      (highest priority). Otherwise append.
        """
        if priority:
            self._parsers.insert(0, parser)
        else:
            # Insert before the fallback position
            self._parsers.append(parser)
        logger.info("Registered new parser: %s (priority=%s)", parser.name, priority)

    @property
    def available_parsers(self) -> list[str]:
        """Return names of all registered parsers (including fallback)."""
        names = [p.name for p in self._parsers]
        names.append(self._fallback.name)
        return names
