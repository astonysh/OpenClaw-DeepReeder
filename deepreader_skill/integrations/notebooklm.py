"""
DeepReader Skill - NotebookLM Integration
=========================================
Pushes parsed Markdown content directly into Google NotebookLM and optionally generates Audio Overviews.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

# Provide a fallback if not installed, though it's in dependencies
try:
    from notebooklm import NotebookLMClient
    __HAS_NOTEBOOKLM__ = True
except ImportError:
    __HAS_NOTEBOOKLM__ = False

logger = logging.getLogger("deepreader.notebooklm")


class NotebookLMIntegration:
    """Manages integration with Google NotebookLM for DeepReader content.
    
    This requires a pre-authenticated session handled via `notebooklm login`.
    """
    
    def __init__(self) -> None:
        if not __HAS_NOTEBOOKLM__:
            logger.warning("notebooklm-py is not installed. NotebookLM integration will be disabled.")
            
    async def upload_and_generate_audio(
        self,
        filepath: str | Path,
        title: str,
        generate_audio: bool = False,
        audio_instructions: str | None = None
    ) -> dict[str, str | None]:
        """
        Create a new notebook, upload the given markdown file, and optionally generate an audio overview.
        
        Args:
            filepath: Path to the local markdown file saved by StorageManager.
            title: The title for the new notebook.
            generate_audio: If True, request an audio overview.
            audio_instructions: Optional instructions for the audio overview.
            
        Returns:
            A dict containing the notebook ID and optionally the path to the downloaded audio.
        """
        if not __HAS_NOTEBOOKLM__:
            return {"error": "notebooklm-py not installed"}
            
        filepath = Path(filepath)
        if not filepath.exists():
            return {"error": f"File not found: {filepath}"}
            
        try:
            # Authenticates via ~/.book_client_session created by `notebooklm login`
            async with await NotebookLMClient.from_storage() as client:
                logger.info("Creating NotebookLM instance titled: %s", title)
                nb = await client.notebooks.create(title)
                
                logger.info("Uploading %s to NotebookLM", filepath.name)
                # Ensure the file gets added and fully processed before proceeding
                await client.sources.add_file(nb.id, str(filepath), wait=True)
                
                result = {
                    "notebook_id": nb.id,
                    "title": title,
                }
                
                if generate_audio:
                    logger.info("Generating Audio Overview... (This may take a few minutes)")
                    instructions = audio_instructions or "Create an engaging, easy to follow podcast overview of this content."
                    status = await client.artifacts.generate_audio(nb.id, instructions=instructions)
                    
                    # Wait for completion - this takes minutes for full audio.
                    await client.artifacts.wait_for_completion(nb.id, status.task_id)
                    
                    # Download the generated mp3/mp4 to the same dir
                    audio_filepath = filepath.with_suffix(".mp3")
                    await client.artifacts.download_audio(nb.id, str(audio_filepath))
                    logger.info("Audio Overview saved to %s", audio_filepath)
                    
                    result["audio_path"] = str(audio_filepath)
                    
                return result
                
        except Exception as e:
            logger.exception("Failed to upload/generate NotebookLM content")
            return {"error": str(e)}

    def run_sync(self, filepath: str | Path, title: str, generate_audio: bool = False) -> dict[str, str | None]:
        """Synchronous wrapper for integration."""
        return asyncio.run(self.upload_and_generate_audio(filepath, title, generate_audio))
