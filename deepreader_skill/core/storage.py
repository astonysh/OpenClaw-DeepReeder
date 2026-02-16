"""
DeepReader Skill - Storage Manager
====================================
Responsible for formatting extracted content into Markdown with
YAML frontmatter and persisting it to the agent's memory directory.
"""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from ..core.utils import build_filename, content_hash, generate_excerpt, get_domain, get_domain_tag
from ..parsers.base import ParseResult

logger = logging.getLogger("deepreader.storage")


class StorageManager:
    """Persist parsed content to the agent's long-term memory.

    By default, files are saved to ``../../memory/inbox/`` relative to
    the skill directory. This can be overridden via the constructor.

    File naming convention::

        YYYY-MM-DD_{sanitized_title}.md
    """

    def __init__(self, memory_dir: str | Path | None = None) -> None:
        """Initialize the storage manager.

        Args:
            memory_dir: Absolute or relative path to the memory inbox
                        directory.  Defaults to ``../../memory/inbox/``
                        relative to this file.
        """
        if memory_dir is None:
            # Default: ../../memory/inbox/ relative to the skill package
            skill_root = Path(__file__).resolve().parent.parent
            self._memory_dir = skill_root.parent.parent / "memory" / "inbox"
        else:
            self._memory_dir = Path(memory_dir)

        logger.info("StorageManager target directory: %s", self._memory_dir)

    def save(self, result: ParseResult) -> str:
        """Format and save a :class:`ParseResult` to the memory directory.

        Args:
            result: The successfully parsed content.

        Returns:
            The absolute path of the saved ``.md`` file.

        Raises:
            OSError: If the file cannot be written.
        """
        # Ensure directory exists
        self._memory_dir.mkdir(parents=True, exist_ok=True)

        # Build filename
        filename = build_filename(result.title, result.url)
        filepath = self._memory_dir / filename

        # Handle duplicate filenames
        if filepath.exists():
            stem = filepath.stem
            suffix = filepath.suffix
            counter = 1
            while filepath.exists():
                filepath = self._memory_dir / f"{stem}_{counter}{suffix}"
                counter += 1

        # Generate the Markdown content
        markdown = self._format_markdown(result)

        # Write to disk
        filepath.write_text(markdown, encoding="utf-8")
        logger.info("Saved content to %s (%d bytes)", filepath, len(markdown))

        return str(filepath)

    def _format_markdown(self, result: ParseResult) -> str:
        """Build the full Markdown document with YAML frontmatter.

        Output format::

            ---
            uuid: {uuid4}
            source: {url}
            date: {iso_date}
            type: external_resource
            tags: [imported, {domain_tag}]
            title: "{title}"
            author: "{author}"
            content_hash: {sha256}
            ---
            # {Title}

            ## Summary
            {excerpt or blank}

            ## Content
            {body text}
        """
        doc_uuid = str(uuid.uuid4())
        iso_date = datetime.now(timezone.utc).isoformat()
        domain = get_domain(result.url)
        domain_tag = get_domain_tag(result.url)

        # Build tags list
        tags = ["imported", domain_tag]
        if result.tags:
            tags.extend(result.tags)
        # Deduplicate while preserving order
        seen: set[str] = set()
        unique_tags: list[str] = []
        for tag in tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)
        tags_str = ", ".join(unique_tags)

        # Escape title for YAML (handle quotes)
        safe_title = result.title.replace('"', '\\"') if result.title else ""
        safe_author = result.author.replace('"', '\\"') if result.author else ""

        # Build the excerpt / summary
        excerpt = result.excerpt or generate_excerpt(result.content)

        # Assemble the document
        lines: list[str] = [
            "---",
            f"uuid: {doc_uuid}",
            f'source: "{result.url}"',
            f"date: {iso_date}",
            "type: external_resource",
            f"tags: [{tags_str}]",
        ]

        if safe_title:
            lines.append(f'title: "{safe_title}"')
        if safe_author:
            lines.append(f'author: "{safe_author}"')

        c_hash = content_hash(result.content)
        lines.append(f"content_hash: {c_hash}")
        lines.append("---")
        lines.append("")

        # Heading
        lines.append(f"# {result.title or 'Untitled'}")
        lines.append("")

        # Summary section
        lines.append("## Summary")
        lines.append("")
        if excerpt:
            lines.append(f"> {excerpt}")
        else:
            lines.append("*(To be filled by the Agent)*")
        lines.append("")

        # Content section
        lines.append("## Content")
        lines.append("")
        lines.append(result.content)
        lines.append("")

        return "\n".join(lines)

    @property
    def memory_dir(self) -> Path:
        """Return the resolved memory directory path."""
        return self._memory_dir
