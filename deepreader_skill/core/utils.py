"""
DeepReader Skill - Utility Functions
=====================================
Helper functions for URL extraction, text cleaning,
filename sanitization, and content hashing.
"""

from __future__ import annotations

import hashlib
import ipaddress
import re
import socket
import unicodedata
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse

import tldextract


# ---------------------------------------------------------------------------
# URL Extraction
# ---------------------------------------------------------------------------

# Robust URL regex – captures http(s) URLs in free-form text.
_URL_PATTERN = re.compile(
    r"https?://"                   # scheme
    r"(?:[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=%])+",  # rest of URI chars
    re.IGNORECASE,
)


def extract_urls(text: str) -> list[str]:
    """Return a deduplicated, order-preserved list of URLs found in *text*."""
    seen: set[str] = set()
    urls: list[str] = []
    for match in _URL_PATTERN.finditer(text):
        url = match.group(0).rstrip(".,;:!?)")  # strip trailing punctuation
        if url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


# ---------------------------------------------------------------------------
# URL Safety Helpers
# ---------------------------------------------------------------------------

_ALLOWED_SCHEMES = {"http", "https"}
_BLOCKED_HOSTS = {
    "localhost",
    "localhost.localdomain",
}
_BLOCKED_HOST_SUFFIXES = (
    ".local",
    ".internal",
    ".lan",
    ".home",
)


def _is_non_public_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Return ``True`` for loopback/private/link-local/etc. addresses."""
    return any(
        [
            ip.is_private,
            ip.is_loopback,
            ip.is_link_local,
            ip.is_multicast,
            ip.is_reserved,
            ip.is_unspecified,
        ]
    )


def _resolve_ips(hostname: str) -> set[str]:
    """Resolve hostname to IPs (both v4/v6 when available)."""
    ips: set[str] = set()
    for result in socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP):
        sockaddr = result[4]
        if sockaddr:
            ips.add(sockaddr[0])
    return ips


def validate_external_url(url: str) -> tuple[bool, str]:
    """Validate that *url* is safe for outbound fetches.

    Blocks local/internal destinations to mitigate SSRF.
    """
    parsed = urlparse(url)

    if parsed.scheme.lower() not in _ALLOWED_SCHEMES:
        return False, "Only http/https URLs are allowed."

    hostname = (parsed.hostname or "").strip().lower().rstrip(".")
    if not hostname:
        return False, "URL is missing a hostname."

    if hostname in _BLOCKED_HOSTS or any(hostname.endswith(s) for s in _BLOCKED_HOST_SUFFIXES):
        return False, "Local/internal hostnames are blocked."

    # Literal IP host
    try:
        ip_obj = ipaddress.ip_address(hostname)
        if _is_non_public_ip(ip_obj):
            return False, f"Blocked non-public IP: {ip_obj}"
        return True, ""
    except ValueError:
        pass

    # DNS hostname
    try:
        resolved_ips = _resolve_ips(hostname)
    except socket.gaierror as exc:
        return False, f"DNS resolution failed: {exc}"

    if not resolved_ips:
        return False, "DNS resolution returned no IP addresses."

    for ip_str in resolved_ips:
        ip_obj = ipaddress.ip_address(ip_str)
        if _is_non_public_ip(ip_obj):
            return False, f"Hostname resolves to non-public IP: {ip_str}"

    return True, ""


def redact_url_for_log(url: str) -> str:
    """Redact query/fragment from URLs before logging."""
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return url

    cleaned = urlunparse(parsed._replace(query="", fragment=""))
    if parsed.query or parsed.fragment:
        return f"{cleaned} [query redacted]"
    return cleaned


# ---------------------------------------------------------------------------
# Domain Helpers
# ---------------------------------------------------------------------------

def get_domain(url: str) -> str:
    """Return a normalized domain label for *url*."""
    hostname = (urlparse(url).hostname or "").lower()
    if not hostname:
        return "unknown"

    try:
        ipaddress.ip_address(hostname)
        return hostname
    except ValueError:
        pass

    extracted = tldextract.extract(url)
    if extracted.domain and extracted.suffix:
        return f"{extracted.domain}.{extracted.suffix}".lower()
    if extracted.domain:
        return extracted.domain.lower()
    return hostname


def get_domain_tag(url: str) -> str:
    """Return a clean, tag-safe domain label (e.g. ``'twitter_com'``)."""
    return get_domain(url).replace(".", "_")


# ---------------------------------------------------------------------------
# Text Cleaning
# ---------------------------------------------------------------------------

_WHITESPACE_RUNS = re.compile(r"[ \t]+")
_BLANK_LINES = re.compile(r"\n{3,}")


def clean_text(text: str) -> str:
    """Normalize whitespace and remove excessive blank lines."""
    text = _WHITESPACE_RUNS.sub(" ", text)
    text = _BLANK_LINES.sub("\n\n", text)
    return text.strip()


def generate_excerpt(text: str, max_length: int = 280) -> str:
    """Generate a short excerpt from the beginning of *text*."""
    cleaned = clean_text(text)
    if len(cleaned) <= max_length:
        return cleaned
    # Cut at last space before max_length to avoid mid-word breaks.
    truncated = cleaned[:max_length].rsplit(" ", 1)[0]
    return f"{truncated}…"


# ---------------------------------------------------------------------------
# Filename Helpers
# ---------------------------------------------------------------------------

_SLUG_UNSAFE = re.compile(r"[^\w\s-]", re.UNICODE)
_SLUG_SEPARATOR = re.compile(r"[-\s]+")


def sanitize_title(title: str, max_length: int = 80) -> str:
    """Convert *title* into a filesystem-safe slug.

    Example::

        >>> sanitize_title("Hello, World!  An Article — 2024")
        'hello-world-an-article-2024'
    """
    # Normalize unicode, strip accents
    value = unicodedata.normalize("NFKD", title)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = _SLUG_UNSAFE.sub("", value).strip().lower()
    value = _SLUG_SEPARATOR.sub("-", value)
    return value[:max_length].rstrip("-")


def build_filename(title: str | None, url: str) -> str:
    """Build a ``YYYY-MM-DD_{slug}.md`` filename.

    Falls back to a URL hash if *title* is empty.
    """
    date_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if title:
        slug = sanitize_title(title)
    else:
        slug = hashlib.sha256(url.encode()).hexdigest()[:12]
    return f"{date_prefix}_{slug}.md"


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def content_hash(text: str) -> str:
    """Return a SHA-256 hex digest for deduplication checks."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# URL Classification
# ---------------------------------------------------------------------------

_TWITTER_DOMAINS = {"twitter.com", "x.com", "mobile.twitter.com", "mobile.x.com"}
_YOUTUBE_DOMAINS = {"youtube.com", "youtu.be", "www.youtube.com", "m.youtube.com"}
_REDDIT_DOMAINS = {
    "reddit.com", "www.reddit.com", "old.reddit.com",
    "new.reddit.com", "np.reddit.com", "m.reddit.com",
}


def is_twitter_url(url: str) -> bool:
    """Return ``True`` if *url* points to Twitter / X."""
    parsed = urlparse(url)
    return parsed.hostname in _TWITTER_DOMAINS if parsed.hostname else False


def is_youtube_url(url: str) -> bool:
    """Return ``True`` if *url* points to YouTube."""
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    return hostname in _YOUTUBE_DOMAINS


def is_reddit_url(url: str) -> bool:
    """Return ``True`` if *url* points to Reddit."""
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    return hostname in _REDDIT_DOMAINS and "/comments/" in parsed.path


def extract_youtube_video_id(url: str) -> str | None:
    """Extract the video ID from a YouTube URL.

    Supports:
    - ``https://www.youtube.com/watch?v=VIDEO_ID``
    - ``https://youtu.be/VIDEO_ID``
    - ``https://www.youtube.com/embed/VIDEO_ID``
    - ``https://www.youtube.com/shorts/VIDEO_ID``
    """
    parsed = urlparse(url)

    # youtu.be short links
    if parsed.hostname and "youtu.be" in parsed.hostname:
        return parsed.path.lstrip("/").split("/")[0] or None

    # Standard /watch?v= links
    from urllib.parse import parse_qs
    qs = parse_qs(parsed.query)
    if "v" in qs:
        return qs["v"][0]

    # /embed/ or /shorts/ paths
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) >= 2 and path_parts[0] in ("embed", "shorts", "v"):
        return path_parts[1]

    return None
