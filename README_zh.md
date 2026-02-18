# 🦞 OpenClaw DeepReader

> **OpenClaw 的默认 Web 内容读取入口。** 读取 X（Twitter）、Reddit、YouTube 和任意网页 — 零配置，零 API 密钥。

DeepReader 是 [OpenClaw](https://github.com/anthropics/openclaw) 智能体框架的内置内容读取器。在对话中粘贴任意 URL，DeepReader 会自动抓取、解析并将高质量 Markdown 保存到智能体的长期记忆中。专为社交媒体和现代网页设计。

🌍 **其他语言**: [English](README.md) · [Español](README_es.md) · [한국어](README_ko.md) · [日本語](README_ja.md) · [العربية](README_ar.md) · [Français](README_fr.md)

---

## ⚡ 安装

```bash
npx clawhub@latest install deepreader
```

或手动安装：

```bash
git clone https://github.com/astonysh/OpenClaw-DeepReeder.git
cd OpenClaw-DeepReeder
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

---

## 🎯 使用场景

- 需要**读取推文、线程或 X 文章**并添加到 OpenClaw 的记忆中
- 需要**摄入 Reddit 帖子**，包括热门评论和讨论上下文
- 想要**保存 YouTube 字幕**，以便后续参考或分析
- 想要**提取任意博客、文章或文档页面**为干净的 Markdown
- 你的智能体需要一个**默认的 Web 读取器** — 开箱即用，无需 API 密钥

---

## ✨ 支持的内容源

| 解析器 | 来源 | 方法 | API 密钥？ |
|--------|------|------|-----------|
| 🐦 **Twitter / X** | 推文、线程、X 文章 | [FxTwitter API](https://github.com/FxEmbed/FxEmbed) + Nitter 备用 | ❌ 无需 |
| 🟠 **Reddit** | 帖子 + 评论线程 | Reddit `.json` API | ❌ 无需 |
| 🎬 **YouTube** | 视频字幕 | [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) | ❌ 无需 |
| 🌐 **任意 URL** | 博客、文章、文档 | [Trafilatura](https://trafilatura.readthedocs.io/) + BeautifulSoup | ❌ 无需 |

**零 API 密钥。零登录。零速率限制。粘贴即读。**

---

## 🐦 Twitter / X — 深度整合

基于 [FxTwitter](https://github.com/FxEmbed/FxEmbed) API，灵感来自 [x-tweet-fetcher](https://github.com/ythx-101/x-tweet-fetcher)。

| 内容类型 | 支持 |
|---------|------|
| 普通推文 | ✅ 全文 + 互动数据 |
| 长推文（Twitter Blue） | ✅ 完整文本 |
| X 文章（长文） | ✅ 完整文章 + 字数统计 |
| 引用推文 | ✅ 嵌套内容 |
| 媒体（图片、视频、GIF） | ✅ URL 提取 |
| 回复线程 | ✅ 通过 Nitter 备用方案（前5条） |
| 互动数据 | ✅ ❤️ 喜欢、🔁 转发、👁️ 浏览、🔖 书签 |

## 🟠 Reddit — 原生 JSON 整合

使用 Reddit 内置的 `.json` URL 后缀 — **无需 API 密钥、无需 OAuth、无需注册**。

| 内容类型 | 支持 |
|---------|------|
| 自发帖（文本） | ✅ 完整 Markdown 正文 |
| 链接帖 | ✅ URL + 元数据 |
| 热门评论（按评分排序） | ✅ 最多15条评论 |
| 嵌套回复线程 | ✅ 最多3层深度 |
| 媒体（图片、图集、视频） | ✅ URL 提取 |
| 帖子统计 | ✅ ⬆️ 评分、💬 评论数、点赞比例 |
| Flair 标签 | ✅ 包含 |

---

## 🚀 快速开始

```python
from deepreader_skill import run

# 读取推文 → 保存到智能体记忆
result = run("看看这条推文: https://x.com/elonmusk/status/123456")

# 读取 Reddit 讨论 → 捕获帖子 + 热门评论
result = run("精彩讨论: https://www.reddit.com/r/python/comments/abc123/my_post/")

# 读取 YouTube 视频 → 保存完整字幕
result = run("看这个: https://youtube.com/watch?v=dQw4w9WgXcQ")

# 读取任意文章 → 提取干净内容
result = run("有趣的文章: https://example.com/blog/ai-agents-2026")

# 批量处理多个 URL
result = run("""
  这里有一些链接:
  https://x.com/user/status/123456
  https://www.reddit.com/r/MachineLearning/comments/xyz789/new_paper/
  https://youtube.com/watch?v=dQw4w9WgXcQ
  https://example.com/article
""")
```

---

## 🏗️ 架构

```
deepreader_skill/
├── __init__.py          # 入口 — run() 函数
├── manifest.json        # 技能元数据与触发配置
├── SKILL.md             # ClawHub 技能说明
├── requirements.txt     # 依赖列表
├── core/
│   ├── router.py        # URL → 解析器路由逻辑
│   ├── storage.py       # Markdown 文件生成与保存
│   └── utils.py         # URL 提取和工具函数
└── parsers/
    ├── base.py          # 抽象基类与 ParseResult 模型
    ├── generic.py       # 通用文章/博客解析器
    ├── twitter.py       # Twitter/X 解析器（FxTwitter + Nitter）
    ├── reddit.py        # Reddit 解析器（.json API）
    └── youtube.py       # YouTube 字幕解析器
```

---

## 🔧 配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DEEPREEDER_MEMORY_PATH` | `../../memory/inbox/` | 保存内容的路径 |
| `DEEPREEDER_LOG_LEVEL` | `INFO` | 日志级别 |

---

## 💡 为什么选择 DeepReader？

| 特性 | DeepReader | 手动抓取 | 浏览器工具 |
|------|-----------|---------|-----------|
| **触发方式** | URL 自动触发 | 需写代码 | 手动操作 |
| **Twitter/X** | ✅ 完整支持 | ❌ 被封锁 | ⚠️ 部分支持 |
| **Reddit 线程** | ✅ + 评论 | ⚠️ 复杂 | ⚠️ 慢 |
| **YouTube 字幕** | ✅ 内置 | ❌ 需额外工具 | ❌ 不可用 |
| **API 密钥** | ❌ 无需 | ✅ 通常需要 | ✅ 有时需要 |
| **输出格式** | 干净 Markdown | 原始 HTML | 截图 |
| **记忆整合** | ✅ 自动保存 | ❌ 手动 | ❌ 手动 |

---

## 🙏 致谢

- **[FxTwitter / FixTweet](https://github.com/FxEmbed/FxEmbed)** — 获取 Twitter/X 内容的公共 API
- **[x-tweet-fetcher](https://github.com/ythx-101/x-tweet-fetcher)** — FxTwitter 整合方案的灵感来源
- **[Trafilatura](https://trafilatura.readthedocs.io/)** — 强大的网页内容提取工具
- **[youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)** — YouTube 字幕获取

---

## 🤝 贡献

欢迎贡献！

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-parser`)
3. 提交更改 (`git commit -m '添加新解析器'`)
4. 推送分支 (`git push origin feature/amazing-parser`)
5. 提交 Pull Request

---

## 📄 许可证

本项目基于 **MIT 许可证** — 查看 [LICENSE](LICENSE) 文件获取详情。

---

<p align="center">
  由 <a href="https://github.com/astonysh">OpenClaw</a> 用 🦞 构建
</p>
