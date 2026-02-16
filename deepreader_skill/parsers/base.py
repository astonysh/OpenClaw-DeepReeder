"""
DeepReader Skill - Abstract Base Parser
========================================
All content parsers must inherit from :class:`BaseParser` and implement
the :meth:`parse` method.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

logger = logging.getLogger("deepreader.parsers")


@dataclass
class ParseResult:
    """Structured output from a parser.

    Attributes:
        url:      The original URL that was parsed.
        title:    Extracted page / post / video title.
        content:  The main body text in Markdown format.
        author:   Author name if available.
        excerpt:  A short summary / excerpt.
        tags:     Additional tags derived from the content.
        success:  Whether the parse operation succeeded.
        error:    Human-readable error message on failure.
    """

    url: str
    title: str = ""
    content: str = ""
    author: str = ""
    excerpt: str = ""
    tags: list[str] = field(default_factory=list)
    success: bool = True
    error: str = ""

    @classmethod
    def failure(cls, url: str, error: str) -> ParseResult:
        """Convenience constructor for a failed parse."""
        return cls(url=url, success=False, error=error)


class BaseParser(ABC):
    """Abstract base class for all DeepReader content parsers.

    Subclasses **must** implement :meth:`parse`.  They may optionally
    override :meth:`can_handle` for more granular URL matching beyond
    what the router provides.
    """

    # Friendly name for logging / debugging.
    name: str = "base"

    # Default request timeout in seconds.
    timeout: int = 30

    # Default User-Agent string for HTTP requests.
    user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    def can_handle(self, url: str) -> bool:  # noqa: ARG002
        """Return ``True`` if this parser should handle the given *url*.

        The default implementation always returns ``True``.  Override in
        subclasses for domain-specific checks.
        """
        return True

    @abstractmethod
    def parse(self, url: str) -> ParseResult:
        """Fetch and parse the content at *url*.

        Returns a :class:`ParseResult` — even on failure (use
        ``ParseResult.failure(...)``).
        """
        ...

    def _get_headers(self) -> dict[str, str]:
        """Return default HTTP headers."""
        return {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
