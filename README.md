# 🦞 OpenClaw DeepReader

> **The default web content gateway for OpenClaw agents.** Read X (Twitter), Reddit, YouTube, and any webpage — zero config, zero API keys.

DeepReader is the built-in content reader for the [OpenClaw](https://github.com/anthropics/openclaw) agent framework. Paste any URL into a conversation, and DeepReader automatically fetches, parses, and saves high-quality Markdown to your agent's long-term memory. Built for social media and the modern web.

🌍 **Translations**: [中文](README_zh.md) · [Español](README_es.md) · [한국어](README_ko.md) · [日本語](README_ja.md) · [العربية](README_ar.md) · [Français](README_fr.md)

---

## ⚡ Install

```bash
npx clawhub@latest install deepreader
```

Or install manually:

```bash
git clone https://github.com/astonysh/OpenClaw-DeepReeder.git
cd OpenClaw-DeepReeder
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

---

## 🎯 Use When

- You need to **read a tweet, thread, or X article** and add it to OpenClaw's memory
- You need to **ingest a Reddit post** with top comments and discussion context
- You want to **save a YouTube transcript** for later reference or analysis
- You want to **clip any blog, article, or documentation page** into clean Markdown
- Your agent needs a **default web reader** that just works — no API keys, no setup

---

## ✨ Supported Sources

| Parser | Sources | Method | API Key? |
|--------|---------|--------|----------|
| 🐦 **Twitter / X** | Tweets, threads, X Articles | [FxTwitter API](https://github.com/FxEmbed/FxEmbed) + Nitter fallback | ❌ None |
| 🟠 **Reddit** | Posts + comment threads | Reddit `.json` API | ❌ None |
| 🎬 **YouTube** | Video transcripts | [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) | ❌ None |
| 🌐 **Any URL** | Blogs, articles, docs | [Trafilatura](https://trafilatura.readthedocs.io/) + BeautifulSoup | ❌ None |

**Zero API keys. Zero login. Zero rate limits. Just paste and read.**

---

## 🐦 Twitter / X — Deep Integration

Powered by [FxTwitter](https://github.com/FxEmbed/FxEmbed) API with Nitter fallback. Inspired by [x-tweet-fetcher](https://github.com/ythx-101/x-tweet-fetcher).

| Content Type | Support |
|-------------|---------|
| Regular tweets | ✅ Full text + engagement stats |
| Long tweets (Twitter Blue) | ✅ Full text |
| X Articles (long-form) | ✅ Complete article text + word count |
| Quoted tweets | ✅ Nested content included |
| Media (images, video, GIF) | ✅ URLs extracted |
| Reply threads | ✅ Via Nitter fallback (first 5) |
| Engagement stats | ✅ ❤️ likes, 🔁 RTs, 👁️ views, 🔖 bookmarks |

## 🟠 Reddit — Native JSON Integration

Uses Reddit's built-in `.json` URL suffix — **no API keys, no OAuth, no registration**.

| Content Type | Support |
|-------------|---------|
| Self posts (text) | ✅ Full markdown body |
| Link posts | ✅ URL + metadata |
| Top comments (sorted by score) | ✅ Up to 15 comments |
| Nested reply threads | ✅ Up to 3 levels deep |
| Media (images, galleries, video) | ✅ URLs extracted |
| Post stats | ✅ ⬆️ score, 💬 comment count, upvote ratio |
| Flair tags | ✅ Included |

---

## 🚀 Quick Start

```python
from deepreader_skill import run

# Read a tweet → saves to agent memory
result = run("Check out this tweet: https://x.com/elonmusk/status/123456")

# Read a Reddit discussion → captures post + top comments
result = run("Great thread: https://www.reddit.com/r/python/comments/abc123/my_post/")

# Read a YouTube video → saves full transcript
result = run("Watch this: https://youtube.com/watch?v=dQw4w9WgXcQ")

# Read any article → extracts clean content
result = run("Interesting read: https://example.com/blog/ai-agents-2026")

# Batch process multiple URLs at once
result = run("""
  Here are some links to read:
  https://x.com/user/status/123456
  https://www.reddit.com/r/MachineLearning/comments/xyz789/new_paper/
  https://youtube.com/watch?v=dQw4w9WgXcQ
  https://example.com/article
""")
```

---

## 📓 NotebookLM & Audio Integration

DeepReader now seamlessly integrates with **Google NotebookLM**. 

Use explicit flags to opt in:
- `--notebooklm` (or `/notebooklm`) → upload to NotebookLM
- `--audio` / `--podcast` (or `/audio`) → upload + generate Audio Overview

When these flags are present, DeepReader will:
1. Parse the requested URLs into Markdown.
2. Create a new Notebook in your Google NotebookLM account.
3. Upload the Markdown content as a source.
4. **(Optional)** Generate an Audio Overview and download it to the memory folder.

**Supported NotebookLM Artifacts Generation:**
Along with Audio Overviews, this integration can easily be extended to automatically generate and save:
- **🎙️ Audio Overview** (Podcast)
- **🎥 Video Overview**
- **🧠 Mind Map**
- **📄 Reports**
- **📇 Flashcards**
- **❓ Quiz**
- **📊 Infographic**
- **🖥️ Slide Deck**
- **📈 Data Table**

> **⚠️ Note: Authentication Required**
> Before using the NotebookLM integration, you must authenticate in your terminal (this only needs to be done once):
> ```bash
> notebooklm login
> ```

---

## 📄 Output Format

Every piece of content is saved as a `.md` file with structured YAML frontmatter:

```yaml
---
title: "[r/python] How I built an AI agent framework"
source_url: "https://www.reddit.com/r/python/comments/abc123/..."
domain: "reddit.com"
parser: "reddit"
ingested_at: "2026-02-16T12:00:00Z"
content_hash: "sha256:abc123..."
word_count: 2500
---

# How I built an AI agent framework

**r/python** · u/developer123 · 2026-02-16 12:00 UTC
📊 ⬆️ 847 (96% upvoted) · 💬 234 comments · 🏷️ Discussion

---

Post body goes here...

---
### 💬 Top Comments

**u/expert_dev** (⬆️ 342):
> This is a really well-structured approach...
```

---

## 🏗️ Architecture

```
deepreader_skill/
├── __init__.py          # Entry point — run() function
├── manifest.json        # Skill metadata & trigger config
├── requirements.txt     # Dependencies
├── core/
│   ├── router.py        # URL → Parser routing logic
│   ├── storage.py       # Markdown file generation & saving
│   └── utils.py         # URL extraction & helper utilities
└── parsers/
    ├── base.py          # Abstract base parser & ParseResult model
    ├── generic.py       # Generic article/blog parser (Trafilatura)
    ├── twitter.py       # Twitter/X parser (FxTwitter + Nitter)
    ├── reddit.py        # Reddit parser (.json API)
    └── youtube.py       # YouTube transcript parser
```

### Router Strategy

```
URL detected → is Twitter/X?  → FxTwitter API → Nitter fallback
             → is Reddit?     → .json suffix API
             → is YouTube?    → youtube-transcript-api
             → otherwise      → Trafilatura (generic)
```

---

## 🔧 Configuration

DeepReader uses sensible defaults out of the box. Configuration can be customized via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DEEPREEDER_MEMORY_PATH` | `../../memory/inbox/` | Where to save ingested content (absolute path, or relative to repo root) |
| `DEEPREEDER_LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## 💡 Why DeepReader?

| Feature | DeepReader | Manual scraping | Browser tools |
|---------|-----------|----------------|---------------|
| **Trigger** | Automatic on URL | Manual code | Manual action |
| **Twitter/X** | ✅ Full support | ❌ Blocked | ⚠️ Partial |
| **Reddit threads** | ✅ + comments | ⚠️ Complex | ⚠️ Slow |
| **YouTube transcripts** | ✅ Built-in | ❌ Separate tool | ❌ Not available |
| **API keys needed** | ❌ None | ✅ Often | ✅ Sometimes |
| **Output format** | Clean Markdown | Raw HTML | Screenshots |
| **Memory integration** | ✅ Auto-save | ❌ Manual | ❌ Manual |

---

## 🙏 Credits

- **[FxTwitter / FixTweet](https://github.com/FxEmbed/FxEmbed)** — Public API for fetching Twitter/X content
- **[x-tweet-fetcher](https://github.com/ythx-101/x-tweet-fetcher)** — Inspiration for the FxTwitter integration approach
- **[Trafilatura](https://trafilatura.readthedocs.io/)** — Robust web content extraction
- **[youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)** — YouTube transcript fetching
- **[notebooklm-py](https://github.com/teng-lin/notebooklm-py)** — Google NotebookLM integration for audio generation

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-parser`)
3. Commit your changes (`git commit -m 'Add amazing parser'`)
4. Push to the branch (`git push origin feature/amazing-parser`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with 🦞 by <a href="https://github.com/astonysh">OpenClaw</a>
</p>
