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

```python
from deepreader_skill import run

# Automatic — triggered when message contains URLs
result = run("Check this out: https://x.com/user/status/123456")

# Reddit post with comments
result = run("https://www.reddit.com/r/python/comments/abc123/my_post/")

# YouTube transcript
result = run("https://youtube.com/watch?v=dQw4w9WgXcQ")

# Any webpage
result = run("https://example.com/blog/interesting-article")

# Multiple URLs at once
result = run("""
  https://x.com/user/status/123456
  https://www.reddit.com/r/MachineLearning/comments/xyz789/
  https://example.com/article
""")
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
