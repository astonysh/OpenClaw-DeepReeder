# 🦞 OpenClaw DeepReader

> **OpenClawエージェントのデフォルトWebコンテンツゲートウェイ。** X（Twitter）、Reddit、YouTube、あらゆるWebページを読み取り — ゼロ設定、ゼロAPIキー。

DeepReaderは[OpenClaw](https://github.com/anthropics/openclaw)エージェントフレームワークの組み込みコンテンツリーダーです。会話にURLを貼り付けるだけで、DeepReaderが自動的にフェッチ、パース、高品質なMarkdownをエージェントの長期メモリに保存します。

🌍 **翻訳**: [English](README.md) · [中文](README_zh.md) · [Español](README_es.md) · [한국어](README_ko.md) · [العربية](README_ar.md) · [Français](README_fr.md)

---

## ⚡ インストール

```bash
npx clawhub@latest install deepreader
```

または手動：

```bash
git clone https://github.com/astonysh/OpenClaw-DeepReeder.git
cd OpenClaw-DeepReeder
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

---

## 🎯 使用シナリオ

- **ツイート、スレッド、Xアーティクル**を読んでOpenClawメモリに追加
- **Reddit投稿**をコメントと共にインジェスト
- **YouTube字幕**を保存して後で参照
- **ブログ、記事、ドキュメント**をMarkdownにクリップ
- **デフォルトWebリーダー**として — APIキー不要

---

## ✨ 対応ソース

| パーサー | ソース | 方法 | APIキー？ |
|---------|--------|------|----------|
| 🐦 **Twitter / X** | ツイート、スレッド | [FxTwitter API](https://github.com/FxEmbed/FxEmbed) + Nitter | ❌ なし |
| 🟠 **Reddit** | 投稿 + コメント | Reddit `.json` API | ❌ なし |
| 🎬 **YouTube** | 動画字幕 | [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) | ❌ なし |
| 🌐 **すべてのURL** | ブログ、記事 | [Trafilatura](https://trafilatura.readthedocs.io/) + BeautifulSoup | ❌ なし |

**APIキーゼロ。ログインゼロ。レート制限ゼロ。貼り付けて読むだけ。**

---

## 🚀 クイックスタート

```python
from deepreader_skill import run

result = run("このツイートをチェック: https://x.com/elonmusk/status/123456")
result = run("素晴らしい議論: https://www.reddit.com/r/python/comments/abc123/my_post/")
result = run("これを見て: https://youtube.com/watch?v=dQw4w9WgXcQ")
result = run("興味深い記事: https://example.com/blog/ai-agents-2026")
```

---

## 💡 なぜDeepReader？

| 機能 | DeepReader | 手動スクレイピング | ブラウザツール |
|------|-----------|-----------------|--------------|
| **トリガー** | URL自動 | コード必要 | 手動 |
| **Twitter/X** | ✅ 完全 | ❌ ブロック | ⚠️ 部分 |
| **Reddit** | ✅ + コメント | ⚠️ 複雑 | ⚠️ 遅い |
| **YouTube字幕** | ✅ 内蔵 | ❌ 別ツール | ❌ 不可 |
| **APIキー** | ❌ 不要 | ✅ 必要 | ✅ 時々 |
| **出力** | Markdown | HTML | スクリーンショット |
| **メモリ統合** | ✅ 自動 | ❌ 手動 | ❌ 手動 |

---

## 🙏 クレジット

- **[FxTwitter](https://github.com/FxEmbed/FxEmbed)** · **[x-tweet-fetcher](https://github.com/ythx-101/x-tweet-fetcher)** · **[Trafilatura](https://trafilatura.readthedocs.io/)** · **[youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)**

## 📄 ライセンス

**MITライセンス** — [LICENSE](LICENSE)参照。

---

<p align="center">
  <a href="https://github.com/astonysh">OpenClaw</a>が🦞で構築
</p>
