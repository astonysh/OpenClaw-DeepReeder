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
from typing import Any

from .core.router import ParserRouter
from .core.storage import StorageManager
from .core.utils import extract_urls, redact_url_for_log, validate_external_url

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


_NOTEBOOKLM_FLAGS = ("--notebooklm", "/notebooklm", "#notebooklm")
_AUDIO_FLAGS = ("--audio", "/audio", "--podcast", "/podcast")


def _parse_notebooklm_flags(text: str) -> tuple[bool, bool]:
    """Parse explicit NotebookLM/audio flags from the user message."""
    lowered = text.lower()
    use_notebooklm = any(flag in lowered for flag in _NOTEBOOKLM_FLAGS)
    generate_audio = any(flag in lowered for flag in _AUDIO_FLAGS)

    # Audio implies NotebookLM usage.
    if generate_audio:
        use_notebooklm = True

    return use_notebooklm, generate_audio


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
        use_notebooklm, generate_audio = _parse_notebooklm_flags(text)

        results: list[str] = []
        errors: list[str] = []

        for url in urls:
            safe, reason = validate_external_url(url)
            if not safe:
                error_msg = (
                    f"❌ Blocked **{url}**\n"
                    f"   Reason: {reason}"
                )
                errors.append(error_msg)
                logger.warning("Blocked URL %s: %s", redact_url_for_log(url), reason)
                continue

            logger.info("Processing URL: %s", redact_url_for_log(url))

            # Step 2: Route to the correct parser
            parse_result = router.route(url)

            if not parse_result.success:
                error_msg = (
                    f"❌ Failed to read **{url}**\n"
                    f"   Reason: {parse_result.error}"
                )
                errors.append(error_msg)
                logger.warning("Parse failed for %s: %s", redact_url_for_log(url), parse_result.error)
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
                
                # --- NotebookLM Integration (explicit opt-in flags only) ---
                if use_notebooklm:
                    logger.info("NotebookLM integration triggered for %s", filepath)
                    from .integrations.notebooklm import NotebookLMIntegration
                    nl_integration = NotebookLMIntegration()

                    nl_result = nl_integration.run_sync(
                        filepath=filepath,
                        title=parse_result.title or "DeepReader Document",
                        generate_audio=generate_audio,
                    )

                    if "error" in nl_result:
                        errors.append(f"❌ NotebookLM upload failed: {nl_result['error']}")
                    else:
                        nb_id = nl_result.get("notebook_id")
                        success_msg += f"\n   📓 Notebook ID: {nb_id}"
                        if generate_audio and "audio_path" in nl_result:
                            success_msg += f"\n   🎙️ Audio Output: `{nl_result['audio_path']}`"

                results.append(success_msg)
                logger.info("Successfully saved %s", filepath)
            except Exception as exc:  # noqa: BLE001
                error_msg = (
                    f"❌ Parsed **{url}** but failed during save/post-processing.\n"
                    f"   Error: {exc}"
                )
                errors.append(error_msg)
                logger.error("Storage/post-process error for %s: %s", redact_url_for_log(url), exc)

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
