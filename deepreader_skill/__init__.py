"""
DeepReader Skill for OpenClaw
==============================

An autonomous web content ingestion engine that:

1. Extracts URLs from user messages
2. Routes each URL to the appropriate specialized parser
3. Saves clean Markdown with YAML frontmatter to the agent's memory

Usage (from OpenClaw)::

    from deepreader_skill import run

    response = run("Check out this article: https://example.com/blog/post")
    # → Scrapes the article, saves to memory/inbox/, returns confirmation.

Supported URL types:
- **Generic** (blogs, articles, docs) → via trafilatura
- **Twitter / X** → via Nitter instances
- **YouTube** → via youtube_transcript_api
"""

from __future__ import annotations

import logging
import re
from typing import Any

from .core.router import ParserRouter
from .core.storage import StorageManager
from .core.utils import extract_urls

__version__ = "1.0.0"
__all__ = ["run"]

logger = logging.getLogger("deepreader")

# Configure logging if not already configured
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Singleton instances (lazy init)
# ---------------------------------------------------------------------------
_router: ParserRouter | None = None
_storage: StorageManager | None = None


_NOTEBOOKLM_KEYWORD_RE = re.compile(
    r"notebook\s*-?\s*l+\s*m\b",
    re.IGNORECASE,
)
_AUDIO_KEYWORD_RE = re.compile(
    r"\b(audio|podcast)\b|音频|播客",
    re.IGNORECASE,
)
# Matches patterns like "KB: SomeName", "notebook: SomeName", "add to SomeName",
# "归档到 KB: SomeName", "推送到 SomeName notebook"
_TARGET_NOTEBOOK_RE = re.compile(
    r"""
    (?:
        KB\s*:\s*|                          # "KB: Name"
        notebook\s*:\s*|                    # "notebook: Name"
        归档到\s*KB\s*:\s*|                 # "归档到 KB: Name"
        推送到\s*(?:KB\s*:\s*)?|            # "推送到 KB: Name" or "推送到 Name"
        add\s+to\s+(?:notebook\s+)?|        # "add to notebook Name"
        写入\s*(?:到\s*)?(?:KB\s*:\s*)?     # "写入到 KB: Name"
    )
    ([A-Za-z0-9\u4e00-\u9fff][\w\u4e00-\u9fff\s\-:]*?)  # notebook name
    (?=\s*(?:notebook|笔记本|$|\n|[,。，]))
    """,
    re.IGNORECASE | re.VERBOSE,
)


def _wants_notebooklm(text: str) -> bool:
    return bool(_NOTEBOOKLM_KEYWORD_RE.search(text))


def _wants_audio(text: str) -> bool:
    return bool(_AUDIO_KEYWORD_RE.search(text))


def _extract_target_notebook(text: str) -> str | None:
    """Extract an explicit target notebook name from user message.

    Returns the notebook name string if found, or None to trigger smart routing
    (auto-match by content title, or create new if no match).
    """
    m = _TARGET_NOTEBOOK_RE.search(text)
    if m:
        return m.group(1).strip()
    return None


def _get_router() -> ParserRouter:
    global _router
    if _router is None:
        _router = ParserRouter()
    return _router


def _get_storage() -> StorageManager:
    global _storage
    if _storage is None:
        _storage = StorageManager()
    return _storage


# ---------------------------------------------------------------------------
# Public API — OpenClaw Entry Point
# ---------------------------------------------------------------------------


def run(text: str, **kwargs: Any) -> str:
    """Main entry point for the DeepReader skill.

    Called by OpenClaw when a user message potentially contains URLs.

    Args:
        text:   The raw user message (may contain one or more URLs).
        kwargs: Reserved for future OpenClaw context (e.g. user_id,
                chat_id, config overrides).

    Returns:
        A human-readable status message summarizing what was processed.
        On failure, returns a graceful error description — never raises.
    """
    try:
        # Step 1: Extract URLs from the message
        urls = extract_urls(text)

        if not urls:
            return "🔍 No URL detected in your message."

        router = _get_router()
        storage = _get_storage()

        results: list[str] = []
        errors: list[str] = []

        for url in urls:
            logger.info("Processing URL: %s", url)

            # Step 2: Route to the correct parser
            parse_result = router.route(url)

            if not parse_result.success:
                error_msg = (
                    f"❌ Failed to read **{url}**\n"
                    f"   Reason: {parse_result.error}"
                )
                errors.append(error_msg)
                logger.warning("Parse failed for %s: %s", url, parse_result.error)
                continue

            # Step 3: Save to memory
            try:
                filepath = storage.save(parse_result)
                success_msg = (
                    f"✅ **{parse_result.title or 'Untitled'}**\n"
                    f"   Source: {url}\n"
                    f"   Saved to: `{filepath}`\n"
                    f"   Content: {len(parse_result.content)} characters"
                )
                
                # --- NotebookLM Integration ---
                use_notebooklm = _wants_notebooklm(text) or _wants_audio(text)
                generate_audio = _wants_audio(text)
                
                if use_notebooklm:
                    logger.info("NotebookLM integration triggered for %s", filepath)
                    from .integrations.notebooklm import NotebookLMIntegration
                    nl_integration = NotebookLMIntegration()

                    target_notebook = _extract_target_notebook(text)
                    logger.info("Target notebook: %s", target_notebook or "(smart routing)")

                    nl_result = nl_integration.run_sync(
                        filepath=filepath,
                        title=parse_result.title or "DeepReader Document",
                        generate_audio=generate_audio,
                        target_notebook=target_notebook,
                    )

                    if "error" in nl_result:
                        errors.append(f"❌ NotebookLM upload failed: {nl_result['error']}")
                    else:
                        nb_title = nl_result.get("notebook_title") or nl_result.get("notebook_id")
                        action = nl_result.get("action", "")
                        action_label = "added to existing" if action == "added_to_existing" else "created new"
                        success_msg += f"\n   📓 Notebook: **{nb_title}** ({action_label})"
                        if generate_audio and "audio_path" in nl_result:
                            success_msg += f"\n   🎙️ Audio Output: `{nl_result['audio_path']}`"

                results.append(success_msg)
                logger.info("Successfully saved %s", filepath)
            except OSError as exc:
                error_msg = (
                    f"❌ Parsed **{url}** but failed to save.\n"
                    f"   Error: {exc}"
                )
                errors.append(error_msg)
                logger.error("Storage error for %s: %s", url, exc)

        # Step 4: Build the response
        response_parts: list[str] = []

        if results:
            response_parts.append(f"📚 **DeepReader** — Processed {len(results)} URL(s):\n")
            response_parts.extend(results)

        if errors:
            if results:
                response_parts.append("\n---\n")
            response_parts.append(f"⚠️ {len(errors)} URL(s) had issues:\n")
            response_parts.extend(errors)

        return "\n\n".join(response_parts)

    except Exception as exc:  # noqa: BLE001
        logger.exception("DeepReader encountered an unexpected error")
        return (
            f"🚨 DeepReader encountered an unexpected error: {exc}\n"
            "The agent remains operational. Please try again or check the logs."
        )
