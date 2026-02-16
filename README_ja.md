# 🦞 OpenClaw DeepReeder

> **AIエージェント向け自律型Webコンテンツ取り込みエンジン。**

DeepReederはユーザーメッセージからURLを自動検出し、専用パーサーを使ってコンテンツをインテリジェントにスクレイピングし、YAMLフロントマター付きのクリーンなMarkdownに変換して、エージェントの長期メモリに保存します。

🌍 **翻訳**: [English](README.md) · [中文](README_zh.md) · [Español](README_es.md) · [한국어](README_ko.md) · [العربية](README_ar.md) · [Français](README_fr.md)

---

## ✨ 機能

| パーサー | ソース | 方法 |
|---------|--------|------|
| 🌐 **汎用** | ブログ、記事、ドキュメント | [Trafilatura](https://trafilatura.readthedocs.io/) + BeautifulSoup フォールバック |
| 🐦 **Twitter / X** | ツイート、スレッド、Xアーティクル | **FxTwitter API**（メイン）+ Nitter（フォールバック） |
| 🎬 **YouTube** | 動画字幕 | [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) |

### 🐦 Twitter / X — ディープインテグレーション

[FxTwitter](https://github.com/FxEmbed/FxEmbed) APIベース。[x-tweet-fetcher](https://github.com/ythx-101/x-tweet-fetcher)にインスパイアされました。

| コンテンツタイプ | サポート |
|----------------|---------|
| 通常のツイート | ✅ 全文 + エンゲージメント統計 |
| 長文ツイート（Twitter Blue） | ✅ 全文 |
| Xアーティクル（長文コンテンツ） | ✅ 完全な記事 + 単語数 |
| 引用ツイート | ✅ ネストされたコンテンツ含む |
| メディア（画像、動画、GIF） | ✅ URL抽出 |
| リプライスレッド | ✅ Nitterフォールバック経由（最初の5件） |
| エンゲージメント統計 | ✅ ❤️ いいね、🔁 RT、👁️ 閲覧、🔖 ブックマーク |

**APIキー不要。ログイン不要。レート制限なし。**

---

## 📦 インストール

```bash
# リポジトリをクローン
git clone https://github.com/astonysh/OpenClaw-DeepReeder.git
cd OpenClaw-DeepReeder

# 仮想環境を作成
python3 -m venv .venv
source .venv/bin/activate

# 依存関係をインストール
pip install -e .
```

---

## 🚀 クイックスタート

```python
from deepreader_skill import run

# 単一URLを処理
result = run("この記事をチェック: https://example.com/blog/post")
print(result)

# ツイートを処理（自動的にFxTwitter APIを使用）
result = run("興味深いスレッド: https://x.com/elonmusk/status/123456")
print(result)

# 複数のURLを一括処理
result = run("""
  いくつかのリンクがあります:
  https://example.com/article
  https://youtube.com/watch?v=dQw4w9WgXcQ
  https://x.com/user/status/123456
""")
print(result)
```

---

## 🏗️ アーキテクチャ

```
deepreader_skill/
├── __init__.py          # エントリポイント — run() 関数
├── manifest.json        # スキルメタデータとトリガー設定
├── requirements.txt     # 依存関係リスト
├── core/
│   ├── router.py        # URL → パーサールーティングロジック
│   ├── storage.py       # Markdownファイル生成・保存
│   └── utils.py         # URL抽出とユーティリティ関数
└── parsers/
    ├── base.py          # 抽象基底パーサーとParseResultモデル
    ├── generic.py       # 汎用記事/ブログパーサー
    ├── twitter.py       # Twitter/Xパーサー（FxTwitter + Nitter）
    └── youtube.py       # YouTube字幕パーサー
```

### Twitterパーサー戦略

```
URL検出 → FxTwitter API（メイン）
            ↓ 成功？ → ✅ リッチな結果（統計、メディア、記事）
            ↓ 失敗？
          Nitterインスタンス（フォールバック）
            ↓ 成功？ → ✅ 基本結果 + リプライスレッド
            ↓ 失敗？ → ❌ 診断付きエラーメッセージ
```

---

## 🔧 設定

DeepReederはデフォルト設定ですぐに使えます。環境変数でカスタマイズ可能です：

| 変数 | デフォルト | 説明 |
|------|-----------|------|
| `DEEPREEDER_MEMORY_PATH` | `../../memory/inbox/` | コンテンツの保存先 |
| `DEEPREEDER_LOG_LEVEL` | `INFO` | ログの詳細レベル |

---

## 🙏 クレジット

- **[FxTwitter / FixTweet](https://github.com/FxEmbed/FxEmbed)** — Twitter/Xコンテンツ取得用パブリックAPI
- **[x-tweet-fetcher](https://github.com/ythx-101/x-tweet-fetcher)** — FxTwitter統合アプローチのインスピレーション
- **[Trafilatura](https://trafilatura.readthedocs.io/)** — 高性能Webコンテンツ抽出
- **[youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)** — YouTube字幕取得

---

## 🤝 コントリビューション

コントリビューション歓迎です！

1. リポジトリをForkします
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-parser`)
3. 変更をコミット (`git commit -m '素晴らしいパーサーを追加'`)
4. ブランチをプッシュ (`git push origin feature/amazing-parser`)
5. Pull Requestを開きます

---

## 📄 ライセンス

このプロジェクトは**MITライセンス**の下でライセンスされています — 詳細は[LICENSE](LICENSE)ファイルをご覧ください。

---

<p align="center">
  <a href="https://github.com/astonysh">OpenClaw</a>が🦞で構築
</p>
