# 🦞 OpenClaw DeepReeder

> **Autonomous web content ingestion engine for AI agents.**

DeepReeder intercepts URLs from user messages, scrapes content intelligently using specialized parsers, formats it into clean Markdown with YAML frontmatter, and saves it to the agent's long-term memory.

---

## ✨ Features

| Parser | Sources | Method |
|--------|---------|--------|
| 🌐 **Generic** | Blogs, articles, docs | [Trafilatura](https://trafilatura.readthedocs.io/) with BeautifulSoup fallback |
| 🐦 **Twitter / X** | Tweets & threads | Nitter instance proxying |
| 🎬 **YouTube** | Video transcripts | [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) |

### Output Format

Every piece of content is saved as a `.md` file with structured YAML frontmatter:

```yaml
---
title: "Article Title"
source_url: "https://example.com/article"
domain: "example.com"
parser: "generic"
ingested_at: "2026-02-16T12:00:00Z"
content_hash: "sha256:abc123..."
word_count: 1500
---

# Article Title

The clean, extracted content goes here...
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

# Process multiple URLs at once
result = run("""
  Here are some links:
  https://example.com/article
  https://youtube.com/watch?v=dQw4w9WgXcQ
  https://x.com/user/status/123456
""")
print(result)
```

### Example Output

```
📚 DeepReader — Processed 3 URL(s):

✅ How to Build AI Agents
   Source: https://example.com/article
   Saved to: memory/inbox/20260216_120000_how-to-build-ai-agents.md
   Content: 3200 characters

✅ Rick Astley - Never Gonna Give You Up
   Source: https://youtube.com/watch?v=dQw4w9WgXcQ
   Saved to: memory/inbox/20260216_120001_rick-astley-never-gonna.md
   Content: 15000 characters

✅ @user's tweet
   Source: https://x.com/user/status/123456
   Saved to: memory/inbox/20260216_120002_user-tweet.md
   Content: 280 characters
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
    ├── base.py           # Abstract base parser & ParseResult model
    ├── generic.py        # Generic article/blog parser
    ├── twitter.py        # Twitter/X parser (via Nitter)
    └── youtube.py        # YouTube transcript parser
```

---

## 🔧 Configuration

DeepReeder uses sensible defaults out of the box. Configuration can be customized via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DEEPREEDER_MEMORY_PATH` | `../../memory/inbox/` | Where to save ingested content |
| `DEEPREEDER_LOG_LEVEL` | `INFO` | Logging verbosity |

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

## 🔗 Links

- **Repository**: [github.com/astonysh/OpenClaw-DeepReeder](https://github.com/astonysh/OpenClaw-DeepReeder)
- **Issues**: [github.com/astonysh/OpenClaw-DeepReeder/issues](https://github.com/astonysh/OpenClaw-DeepReeder/issues)

---

<p align="center">
  Built with 🦞 by <a href="https://github.com/astonysh">OpenClaw</a>
</p>
