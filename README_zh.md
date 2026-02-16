# 🦞 OpenClaw DeepReeder

> **面向 AI 智能体的自主网页内容摄取引擎。**

DeepReeder 自动拦截用户消息中的 URL，使用专用解析器智能抓取内容，将其格式化为带有 YAML 前置信息的干净 Markdown，并保存到智能体的长期记忆中。

🌍 **其他语言**: [English](README.md) · [Español](README_es.md) · [한국어](README_ko.md) · [日本語](README_ja.md) · [العربية](README_ar.md) · [Français](README_fr.md)

---

## ✨ 功能特性

| 解析器 | 来源 | 方法 |
|--------|------|------|
| 🌐 **通用** | 博客、文章、文档 | [Trafilatura](https://trafilatura.readthedocs.io/) + BeautifulSoup 备用方案 |
| 🐦 **Twitter / X** | 推文、线程、X 文章 | **FxTwitter API**（主力） + Nitter（备用） |
| 🟠 **Reddit** | 帖子 + 评论线程 | **Reddit .json API**（零配置） |
| 🎬 **YouTube** | 视频字幕 | [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) |

### 🐦 Twitter / X — 深度整合

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

### 🟠 Reddit — 原生 JSON 整合

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

**无需 API 密钥。无需登录。无速率限制。**

---

## 📦 安装

```bash
# 克隆仓库
git clone https://github.com/astonysh/OpenClaw-DeepReeder.git
cd OpenClaw-DeepReeder

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -e .
```

---

## 🚀 快速开始

```python
from deepreader_skill import run

# 处理单个 URL
result = run("看看这篇文章: https://example.com/blog/post")
print(result)

# 处理推文（自动使用 FxTwitter API）
result = run("有趣的推文: https://x.com/elonmusk/status/123456")
print(result)

# 处理 Reddit 帖子（自动使用 .json API）
result = run("精彩讨论: https://www.reddit.com/r/python/comments/abc123/my_post/")
print(result)

# 批量处理多个 URL
result = run("""
  这里有一些链接:
  https://example.com/article
  https://youtube.com/watch?v=dQw4w9WgXcQ
  https://x.com/user/status/123456
  https://www.reddit.com/r/MachineLearning/comments/xyz789/new_paper/
""")
print(result)
```

---

## 🏗️ 架构

```
deepreader_skill/
├── __init__.py          # 入口 — run() 函数
├── manifest.json        # 技能元数据与触发配置
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

### 解析器选择策略

```
检测到 URL → Twitter/X？ → FxTwitter API → Nitter 备用
           → Reddit？    → .json 后缀 API
           → YouTube？   → youtube-transcript-api
           → 其他        → Trafilatura（通用）
```

---

## 🔧 配置

DeepReeder 开箱即用，使用合理的默认值。可通过环境变量自定义配置：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DEEPREEDER_MEMORY_PATH` | `../../memory/inbox/` | 保存内容的路径 |
| `DEEPREEDER_LOG_LEVEL` | `INFO` | 日志级别 |

---

## 🙏 致谢

- **[FxTwitter / FixTweet](https://github.com/FxEmbed/FxEmbed)** — 获取 Twitter/X 内容的公共 API
- **[x-tweet-fetcher](https://github.com/ythx-101/x-tweet-fetcher)** — FxTwitter 整合方案的灵感来源
- **[Trafilatura](https://trafilatura.readthedocs.io/)** — 强大的网页内容提取工具
- **[youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)** — YouTube 字幕获取

---

## 🤝 贡献

欢迎贡献！您可以：

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
