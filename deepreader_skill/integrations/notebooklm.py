"""
DeepReader Skill - NotebookLM Integration
=========================================
Pushes parsed Markdown content into Google NotebookLM.

Smart routing:
  - If a notebook whose title contains the content title (or a user-supplied
    notebook name) already exists, the file is added to that notebook.
  - Otherwise a new notebook is created.

Optionally generates an Audio Overview after the source is indexed.
"""

from __future__ import annotations

import asyncio
import logging
import os
import threading
from pathlib import Path
from typing import Optional

try:
    from notebooklm import NotebookLMClient
    __HAS_NOTEBOOKLM__ = True
except ImportError:
    __HAS_NOTEBOOKLM__ = False

logger = logging.getLogger("deepreader.notebooklm")


class NotebookLMIntegration:
    """Manages integration with Google NotebookLM for DeepReader content.

    Requires a pre-authenticated session: run `notebooklm login` once to
    create `~/.book_client_session`.
    """

    def __init__(self) -> None:
        if not __HAS_NOTEBOOKLM__:
            logger.warning(
                "notebooklm-py is not installed. NotebookLM integration disabled."
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    async def _find_notebook(client, keyword: str) -> Optional[object]:
        """Return the first notebook whose title contains *keyword* (case-insensitive).

        Returns None if no match is found.
        """
        try:
            notebooks = await client.notebooks.list()
        except Exception:
            logger.warning("Could not list notebooks; will create a new one.")
            return None

        kw_lower = keyword.lower()
        for nb in notebooks:
            if kw_lower in nb.title.lower():
                logger.info(
                    "Found existing notebook: '%s' (%s)", nb.title, nb.id
                )
                return nb
        return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def upload_and_generate_audio(
        self,
        filepath: str | Path,
        title: str,
        generate_audio: bool = False,
        audio_instructions: Optional[str] = None,
        target_notebook: Optional[str] = None,
    ) -> dict[str, str | None]:
        """Upload a markdown file to NotebookLM (smart routing) and optionally
        generate an Audio Overview.

        Args:
            filepath: Local markdown file produced by StorageManager.
            title: Content title — used for new-notebook creation and as the
                   default search keyword when *target_notebook* is not set.
            generate_audio: Request an Audio Overview if True.
            audio_instructions: Custom instructions for the audio generation.
            target_notebook: Optional keyword to search for an existing notebook.
                             If omitted, *title* is used as the search term.
                             Pass ``"__new__"`` to always create a fresh notebook.

        Returns:
            dict with ``notebook_id``, ``notebook_title``, ``action``
            (``"added_to_existing"`` or ``"created_new"``), and optionally
            ``audio_path`` / ``audio_task_id`` / ``audio_status``.
        """
        if not __HAS_NOTEBOOKLM__:
            return {"error": "notebooklm-py not installed"}

        filepath = Path(filepath)
        if not filepath.exists():
            return {"error": f"File not found: {filepath}"}

        try:
            async with await NotebookLMClient.from_storage() as client:
                # ---- Notebook resolution ----------------------------------------
                force_new = (target_notebook == "__new__")
                search_kw = target_notebook if target_notebook and not force_new else title

                nb = None
                if not force_new:
                    nb = await self._find_notebook(client, search_kw)

                if nb is None:
                    logger.info("Creating new notebook: %s", title)
                    nb = await client.notebooks.create(title)
                    action = "created_new"
                else:
                    action = "added_to_existing"

                logger.info(
                    "Uploading %s → notebook '%s' (%s) [%s]",
                    filepath.name, nb.title, nb.id, action,
                )
                await client.sources.add_file(nb.id, str(filepath), wait=True)

                result: dict[str, str | None] = {
                    "notebook_id": nb.id,
                    "notebook_title": nb.title,
                    "action": action,
                }

                # ---- Audio Overview (optional) ----------------------------------
                if generate_audio:
                    logger.info("Generating Audio Overview (this may take minutes)…")
                    instructions = (
                        audio_instructions
                        or "Create an engaging, easy-to-follow podcast overview of this content."
                    )
                    status = await client.artifacts.generate_audio(
                        nb.id, instructions=instructions
                    )
                    timeout = float(
                        os.getenv("DEEPREEDER_NOTEBOOKLM_AUDIO_TIMEOUT", "1800")
                    )
                    try:
                        await client.artifacts.wait_for_completion(
                            nb.id, status.task_id, timeout=timeout
                        )
                    except TimeoutError:
                        logger.warning(
                            "Audio still generating after %.0fs (task_id=%s)",
                            timeout, status.task_id,
                        )
                        result["audio_task_id"] = status.task_id
                        result["audio_status"] = "timeout"
                        return result

                    audio_filepath = filepath.with_suffix(".mp3")
                    await client.artifacts.download_audio(nb.id, str(audio_filepath))
                    logger.info("Audio Overview saved to %s", audio_filepath)
                    result["audio_path"] = str(audio_filepath)
                    result["audio_task_id"] = status.task_id
                    result["audio_status"] = "completed"

                return result

        except Exception as e:
            logger.exception("Failed to upload/generate NotebookLM content")
            message = str(e)
            if any(
                tok in message.lower()
                for tok in ("storage_state", "login", "auth", "session")
            ):
                message = (
                    f"{message}. Run `notebooklm login` to refresh the session."
                )
            return {"error": message}

    def run_sync(
        self,
        filepath: str | Path,
        title: str,
        generate_audio: bool = False,
        target_notebook: Optional[str] = None,
    ) -> dict[str, str | None]:
        """Synchronous wrapper around :meth:`upload_and_generate_audio`."""
        coro = self.upload_and_generate_audio(
            filepath, title, generate_audio, target_notebook=target_notebook
        )

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)

        result: dict[str, str | None] = {}
        error: dict[str, str | None] = {}

        def _runner() -> None:
            try:
                result.update(asyncio.run(coro))
            except Exception as exc:  # noqa: BLE001
                logger.exception("NotebookLM sync wrapper failed")
                error["error"] = str(exc)

        thread = threading.Thread(target=_runner, daemon=True)
        thread.start()
        thread.join()
        return error or result
