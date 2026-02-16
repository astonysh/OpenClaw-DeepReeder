# 🦞 OpenClaw DeepReeder

> **Moteur autonome d'ingestion de contenu web pour agents IA.**

DeepReeder intercepte les URLs des messages utilisateur, extrait le contenu intelligemment à l'aide de parsers spécialisés, le formate en Markdown propre avec des métadonnées YAML frontmatter, et le sauvegarde dans la mémoire à long terme de l'agent.

🌍 **Traductions** : [English](README.md) · [中文](README_zh.md) · [Español](README_es.md) · [한국어](README_ko.md) · [日本語](README_ja.md) · [العربية](README_ar.md)

---

## ✨ Fonctionnalités

| Parser | Sources | Méthode |
|--------|---------|---------|
| 🌐 **Générique** | Blogs, articles, documentation | [Trafilatura](https://trafilatura.readthedocs.io/) avec fallback BeautifulSoup |
| 🐦 **Twitter / X** | Tweets, fils, X Articles | **FxTwitter API** (principal) + Nitter (fallback) |
| 🟠 **Reddit** | Posts + fils de commentaires | **Reddit .json API** (sans configuration) |
| 🎬 **YouTube** | Transcriptions vidéo | [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) |

### 🐦 Twitter / X — Intégration Approfondie

Propulsé par l'API [FxTwitter](https://github.com/FxEmbed/FxEmbed). Inspiré par [x-tweet-fetcher](https://github.com/ythx-101/x-tweet-fetcher).

| Type de Contenu | Support |
|----------------|---------|
| Tweets classiques | ✅ Texte complet + statistiques d'engagement |
| Tweets longs (Twitter Blue) | ✅ Texte complet |
| X Articles (contenu long) | ✅ Article complet + nombre de mots |
| Tweets cités | ✅ Contenu imbriqué inclus |
| Médias (images, vidéo, GIF) | ✅ URLs extraites |
| Fils de réponses | ✅ Via Nitter fallback (5 premières) |
| Statistiques d'engagement | ✅ ❤️ likes, 🔁 RTs, 👁️ vues, 🔖 signets |

### 🟠 Reddit — Intégration JSON Native

Utilise le suffixe URL `.json` intégré de Reddit — **sans clé API, sans OAuth, sans inscription**.

| Type de Contenu | Support |
|----------------|---------|
| Self posts (texte) | ✅ Corps Markdown complet |
| Link posts | ✅ URL + métadonnées |
| Meilleurs commentaires (par score) | ✅ Jusqu'à 15 commentaires |
| Fils de réponses imbriqués | ✅ Jusqu'à 3 niveaux |
| Médias (images, galeries, vidéo) | ✅ URLs extraites |
| Statistiques du post | ✅ ⬆️ score, 💬 commentaires, ratio de votes |
| Tags Flair | ✅ Inclus |

**Sans clé API. Sans connexion. Sans limite de débit.**

---

## 📦 Installation

```bash
git clone https://github.com/astonysh/OpenClaw-DeepReeder.git
cd OpenClaw-DeepReeder
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## 🚀 Démarrage Rapide

```python
from deepreader_skill import run

# Traiter une URL
result = run("Regarde cet article : https://example.com/blog/post")
print(result)

# Traiter un post Reddit
result = run("Super discussion : https://www.reddit.com/r/python/comments/abc123/my_post/")
print(result)

# Traiter plusieurs URLs
result = run("""
  Voici quelques liens :
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
├── __init__.py          # Point d'entrée — fonction run()
├── manifest.json        # Métadonnées du skill
├── requirements.txt     # Dépendances
├── core/
│   ├── router.py        # Routage URL → Parser
│   ├── storage.py       # Génération et sauvegarde Markdown
│   └── utils.py         # Extraction d'URLs et utilitaires
└── parsers/
    ├── base.py          # Parser de base abstrait
    ├── generic.py       # Parser générique (Trafilatura)
    ├── twitter.py       # Parser Twitter/X (FxTwitter + Nitter)
    ├── reddit.py        # Parser Reddit (.json API)
    └── youtube.py       # Parser YouTube
```

### Stratégie de Sélection

```
URL détectée → Twitter/X?  → FxTwitter API → Nitter fallback
             → Reddit?     → .json suffix API
             → YouTube?    → youtube-transcript-api
             → autre?      → Trafilatura (générique)
```

---

## 🔧 Configuration

| Variable | Par défaut | Description |
|----------|-----------|-------------|
| `DEEPREEDER_MEMORY_PATH` | `../../memory/inbox/` | Chemin de sauvegarde |
| `DEEPREEDER_LOG_LEVEL` | `INFO` | Niveau de verbosité |

---

## 🙏 Remerciements

- **[FxTwitter / FixTweet](https://github.com/FxEmbed/FxEmbed)** — API publique pour Twitter/X
- **[x-tweet-fetcher](https://github.com/ythx-101/x-tweet-fetcher)** — Inspiration pour l'intégration FxTwitter
- **[Trafilatura](https://trafilatura.readthedocs.io/)** — Extraction de contenu web
- **[youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)** — Transcriptions YouTube

---

## 🤝 Contribuer

Les contributions sont les bienvenues !

1. Forkez le dépôt
2. Créez une branche (`git checkout -b feature/parser-genial`)
3. Commitez (`git commit -m 'Ajouter un parser génial'`)
4. Poussez (`git push origin feature/parser-genial`)
5. Ouvrez une Pull Request

---

## 📄 Licence

**Licence MIT** — consultez [LICENSE](LICENSE) pour plus de détails.

---

<p align="center">
  Construit avec 🦞 par <a href="https://github.com/astonysh">OpenClaw</a>
</p>
