# 🦞 OpenClaw DeepReader

> **La passerelle de contenu web par défaut pour les agents OpenClaw.** Lit X (Twitter), Reddit, YouTube et toute page web — zéro configuration, zéro clé API.

DeepReader est le lecteur de contenu intégré pour le framework d'agents [OpenClaw](https://github.com/anthropics/openclaw). Collez n'importe quelle URL dans une conversation, et DeepReader récupère, analyse et sauvegarde automatiquement du Markdown de haute qualité dans la mémoire à long terme de l'agent. Conçu pour les réseaux sociaux et le web moderne.

🌍 **Traductions** : [English](README.md) · [中文](README_zh.md) · [Español](README_es.md) · [한국어](README_ko.md) · [日本語](README_ja.md) · [العربية](README_ar.md)

---

## ⚡ Installation

```bash
npx clawhub@latest install deepreader
```

Ou installation manuelle :

```bash
git clone https://github.com/astonysh/OpenClaw-DeepReeder.git
cd OpenClaw-DeepReeder
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

---

## 🎯 Utilisez Quand

- Vous avez besoin de **lire un tweet, un fil ou un article X** et de l'ajouter à la mémoire d'OpenClaw
- Vous avez besoin d'**ingérer un post Reddit** avec les meilleurs commentaires et le contexte de discussion
- Vous voulez **sauvegarder une transcription YouTube** pour référence ou analyse ultérieure
- Vous voulez **clipper n'importe quel blog, article ou documentation** en Markdown propre
- Votre agent a besoin d'un **lecteur web par défaut** qui fonctionne tout simplement — sans clé API, sans configuration

---

## ✨ Sources Supportées

| Parser | Sources | Méthode | Clé API ? |
|--------|---------|---------|-----------|
| 🐦 **Twitter / X** | Tweets, fils, X Articles | [FxTwitter API](https://github.com/FxEmbed/FxEmbed) + Nitter fallback | ❌ Aucune |
| 🟠 **Reddit** | Posts + fils de commentaires | Reddit `.json` API | ❌ Aucune |
| 🎬 **YouTube** | Transcriptions vidéo | [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) | ❌ Aucune |
| 🌐 **Toute URL** | Blogs, articles, docs | [Trafilatura](https://trafilatura.readthedocs.io/) + BeautifulSoup | ❌ Aucune |

**Zéro clé API. Zéro connexion. Zéro limite. Collez et lisez.**

---

## 🐦 Twitter / X — Intégration Approfondie

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

## 🟠 Reddit — Intégration JSON Native

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

---

## 🚀 Démarrage Rapide

```python
from deepreader_skill import run

# Lire un tweet → sauvegarde dans la mémoire de l'agent
result = run("Regarde ce tweet : https://x.com/elonmusk/status/123456")

# Lire une discussion Reddit → capture post + commentaires
result = run("Super discussion : https://www.reddit.com/r/python/comments/abc123/my_post/")

# Lire une vidéo YouTube → sauvegarde la transcription complète
result = run("Regarde ça : https://youtube.com/watch?v=dQw4w9WgXcQ")

# Lire n'importe quel article → extrait le contenu propre
result = run("Lecture intéressante : https://example.com/blog/ai-agents-2026")

# Traitement par lots de plusieurs URLs
result = run("""
  Voici quelques liens :
  https://x.com/user/status/123456
  https://www.reddit.com/r/MachineLearning/comments/xyz789/new_paper/
  https://youtube.com/watch?v=dQw4w9WgXcQ
  https://example.com/article
""")
```

---

## 📓 Intégration NotebookLM & Audio

DeepReader s'intègre désormais parfaitement à **Google NotebookLM**.

Si votre message inclut des mots-clés tels que `notebooklm`, `audio` ou `podcast`, DeepReader va automatiquement :
1. Analyser les URL demandées en Markdown.
2. Créer un nouveau carnet (Notebook) dans votre compte Google NotebookLM.
3. Télécharger le contenu Markdown propre comme source.
4. **(Facultatif)** Générer un Audio Overview (format podcast) captivant et le télécharger directement dans le dossier mémoire de votre agent.

**Génération d'Artefacts NotebookLM Supportés :**
Outre les résumés audio, cette intégration peut être facilement étendue pour générer et sauvegarder automatiquement :
- **🎙️ Audio Overview** (Podcast)
- **🎥 Video Overview** (Résumé vidéo)
- **🧠 Mind Map** (Carte mentale)
- **📄 Reports** (Rapports)
- **📇 Flashcards** (Cartes mémoire)
- **❓ Quiz** (Questionnaire)
- **📊 Infographic** (Infographie)
- **🖥️ Slide Deck** (Présentation)
- **📈 Data Table** (Tableau de données)

> **⚠️ Remarque : Authentification requise**
> Avant d'utiliser l'intégration NotebookLM, vous devez vous authentifier dans votre terminal (à faire une seule fois) :
> ```bash
> notebooklm login
> ```

---

## 🏗️ Architecture

```
deepreader_skill/
├── __init__.py          # Point d'entrée — fonction run()
├── manifest.json        # Métadonnées du skill
├── SKILL.md             # Description pour ClawHub
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

---

## 🔧 Configuration

| Variable | Par défaut | Description |
|----------|-----------|-------------|
| `DEEPREEDER_MEMORY_PATH` | `../../memory/inbox/` | Chemin de sauvegarde |
| `DEEPREEDER_LOG_LEVEL` | `INFO` | Niveau de verbosité |
| `FIRECRAWL_API_KEY` | `""` | Optionnel. Clé API Firecrawl utilisée pour contourner les protections (paywalls, etc.) en cas d'échec de la requête initiale. |

---

## 💡 Pourquoi DeepReader ?

| Fonctionnalité | DeepReader | Scraping manuel | Outils navigateur |
|----------------|-----------|----------------|-------------------|
| **Déclenchement** | Automatique par URL | Code manuel | Action manuelle |
| **Twitter/X** | ✅ Support complet | ❌ Bloqué | ⚠️ Partiel |
| **Fils Reddit** | ✅ + commentaires | ⚠️ Complexe | ⚠️ Lent |
| **Transcriptions YouTube** | ✅ Intégré | ❌ Outil séparé | ❌ Non disponible |
| **Clés API** | ❌ Aucune | ✅ Souvent | ✅ Parfois |
| **Format sortie** | Markdown propre | HTML brut | Captures d'écran |
| **Intégration mémoire** | ✅ Auto-sauvegarde | ❌ Manuel | ❌ Manuel |

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
