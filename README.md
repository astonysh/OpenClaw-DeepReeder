# 🦞 OpenClaw DeepReeder

> **Autonomous web content ingestion engine for AI agents.**

DeepReeder intercepts URLs from user messages, scrapes content intelligently using specialized parsers, formats it into clean Markdown with YAML frontmatter, and saves it to the agent's long-term memory.

🌍 **Translations**: [中文](README_zh.md) · [Español](README_es.md) · [한국어](README_ko.md) · [日本語](README_ja.md) · [العربية](README_ar.md) · [Français](README_fr.md)

---

## ✨ Features

| Parser | Sources | Method |
|--------|---------|--------|
| 🌐 **Generic** | Blogs, articles, docs | [Trafilatura](https://trafilatura.readthedocs.io/) with BeautifulSoup fallback |
| 🐦 **Twitter / X** | Tweets, threads, X Articles | **FxTwitter API** (primary) + Nitter (fallback) |
| 🟠 **Reddit** | Posts + comment threads | **Reddit .json API** (zero-config) |
| 🎬 **YouTube** | Video transcripts | [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) |

### 🐦 Twitter / X — Deep Integration

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

### 🟠 Reddit — Native JSON Integration

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

**No API keys. No login. No rate limits.**

### Output Format

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

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/astonysh/OpenClaw-DeepReeder.git
cd OpenClaw-DeepReeder

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
```

---

## 🚀 Quick Start

```python
from deepreader_skill import run

# Process a single URL
result = run("Check out this article: https://example.com/blog/post")
print(result)

# Process a tweet (uses FxTwitter API automatically)
result = run("Interesting thread: https://x.com/elonmusk/status/123456")
print(result)

# Process a Reddit post (uses .json API automatically)
result = run("Great discussion: https://www.reddit.com/r/python/comments/abc123/my_post/")
print(result)

# Process multiple URLs at once
result = run("""
  Here are some links:
  https://example.com/article
  https://youtube.com/watch?v=dQw4w9WgXcQ
  https://x.com/user/status/123456
  https://www.reddit.com/r/MachineLearning/comments/xyz789/new_paper/
""")
print(result)
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

### Parser Selection Strategy

```
URL detected → is Twitter/X?  → FxTwitter API → Nitter fallback
             → is Reddit?     → .json suffix API
             → is YouTube?    → youtube-transcript-api
             → otherwise      → Trafilatura (generic)
```

---

## 🔧 Configuration

DeepReeder uses sensible defaults out of the box. Configuration can be customized via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DEEPREEDER_MEMORY_PATH` | `../../memory/inbox/` | Where to save ingested content |
| `DEEPREEDER_LOG_LEVEL` | `INFO` | Logging verbosity |

---

## 🙏 Credits

- **[FxTwitter / FixTweet](https://github.com/FxEmbed/FxEmbed)** — Public API for fetching Twitter/X content
- **[x-tweet-fetcher](https://github.com/ythx-101/x-tweet-fetcher)** — Inspiration for the FxTwitter integration approach
- **[Trafilatura](https://trafilatura.readthedocs.io/)** — Robust web content extraction
- **[youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)** — YouTube transcript fetching

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
