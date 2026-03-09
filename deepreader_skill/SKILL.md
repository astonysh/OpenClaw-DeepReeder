---
name: DeepReader
description: The default web content reader for OpenClaw. Reads X (Twitter), Reddit, YouTube, and any webpage into clean Markdown — zero API keys required. Use when you need to ingest social media posts, articles, or video transcripts into agent memory.
---

# DeepReader

The default web content reader for OpenClaw agents. Automatically detects URLs in messages, fetches content using specialized parsers, and saves clean Markdown with YAML frontmatter to agent memory.

## Use when

1. A user shares a **tweet, thread, or X article** and you need to read its content
2. A user shares a **Reddit post** and you need the discussion + top comments
3. A user shares a **YouTube video** and you need the transcript
4. A user shares **any blog, article, or documentation URL** and you need the text
5. You need to **batch-read multiple URLs** from a single message

## Supported sources

| Source | Method | API Key? |
|--------|--------|----------|
| Twitter / X | FxTwitter API + Nitter fallback | None |
| Reddit | .json suffix API | None |
| YouTube | youtube-transcript-api | None |
| Any URL | Trafilatura + BeautifulSoup | None |

## Usage

**Preferred: Shell runner** (auto-activates the .venv):

```bash
# Single URL
~/.openclaw/skills/deepreader/run.sh "https://example.com/article"

# With trigger phrase
~/.openclaw/skills/deepreader/run.sh "读这个 https://x.com/user/status/123456"

# Pipe URL
echo "https://youtube.com/watch?v=abc" | ~/.openclaw/skills/deepreader/run.sh

# Multiple URLs
~/.openclaw/skills/deepreader/run.sh "https://example.com/a https://example.com/b"
```

**IMPORTANT**: Always use `run.sh` (not bare `python3`) to ensure the correct virtual environment with all dependencies is activated.

Python API (for direct .venv use only):

```python
from deepreader_skill import run

result = run("https://example.com/blog/interesting-article")
result = run("https://youtube.com/watch?v=dQw4w9WgXcQ")
result = run("https://www.reddit.com/r/python/comments/abc123/my_post/")
```

## Output

Content is saved as `.md` files with structured YAML frontmatter:

```yaml
---
title: "Tweet by @user"
source_url: "https://x.com/user/status/123456"
domain: "x.com"
parser: "twitter"
ingested_at: "2026-02-16T12:00:00Z"
content_hash: "sha256:..."
word_count: 350
---
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DEEPREEDER_MEMORY_PATH` | `../../memory/inbox/` | Where to save ingested content |
| `DEEPREEDER_LOG_LEVEL` | `INFO` | Logging verbosity |

## How it works

```
URL detected → is Twitter/X?  → FxTwitter API → Nitter fallback
             → is Reddit?     → .json suffix API
             → is YouTube?    → youtube-transcript-api
             → otherwise      → Trafilatura (generic)
```

Triggers automatically when any message contains `https://` or `http://`.
