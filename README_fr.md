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

**Sans clé API. Sans connexion. Sans limite de débit.**

---

## 📦 Installation

```bash
# Cloner le dépôt
git clone https://github.com/astonysh/OpenClaw-DeepReeder.git
cd OpenClaw-DeepReeder

# Créer un environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -e .
```

---

## 🚀 Démarrage Rapide

```python
from deepreader_skill import run

# Traiter une seule URL
result = run("Regarde cet article : https://example.com/blog/post")
print(result)

# Traiter un tweet (utilise automatiquement l'API FxTwitter)
result = run("Fil intéressant : https://x.com/elonmusk/status/123456")
print(result)

# Traiter plusieurs URLs en une fois
result = run("""
  Voici quelques liens :
  https://example.com/article
  https://youtube.com/watch?v=dQw4w9WgXcQ
  https://x.com/user/status/123456
""")
print(result)
```

---

## 🏗️ Architecture

```
deepreader_skill/
├── __init__.py          # Point d'entrée — fonction run()
├── manifest.json        # Métadonnées du skill et configuration des triggers
├── requirements.txt     # Liste des dépendances
├── core/
│   ├── router.py        # Logique de routage URL → Parser
│   ├── storage.py       # Génération et sauvegarde des fichiers Markdown
│   └── utils.py         # Extraction d'URLs et fonctions utilitaires
└── parsers/
    ├── base.py          # Parser de base abstrait et modèle ParseResult
    ├── generic.py       # Parser générique d'articles/blogs
    ├── twitter.py       # Parser Twitter/X (FxTwitter + Nitter)
    └── youtube.py       # Parser de transcriptions YouTube
```

### Stratégie du Parser Twitter

```
URL détectée → FxTwitter API (principal)
                 ↓ succès ? → ✅ Résultat enrichi (stats, médias, articles)
                 ↓ échec ?
               Instances Nitter (fallback)
                 ↓ succès ? → ✅ Résultat basique + fils de réponses
                 ↓ échec ? → ❌ Message d'erreur explicatif avec diagnostic
```

---

## 🔧 Configuration

DeepReeder fonctionne immédiatement avec des valeurs par défaut raisonnables. La configuration peut être personnalisée via des variables d'environnement :

| Variable | Par défaut | Description |
|----------|-----------|-------------|
| `DEEPREEDER_MEMORY_PATH` | `../../memory/inbox/` | Chemin de sauvegarde du contenu |
| `DEEPREEDER_LOG_LEVEL` | `INFO` | Niveau de verbosité des journaux |

---

## 🙏 Remerciements

- **[FxTwitter / FixTweet](https://github.com/FxEmbed/FxEmbed)** — API publique pour récupérer le contenu Twitter/X
- **[x-tweet-fetcher](https://github.com/ythx-101/x-tweet-fetcher)** — Inspiration pour l'approche d'intégration FxTwitter
- **[Trafilatura](https://trafilatura.readthedocs.io/)** — Extraction robuste de contenu web
- **[youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)** — Récupération de transcriptions YouTube

---

## 🤝 Contribuer

Les contributions sont les bienvenues !

1. Forkez le dépôt
2. Créez une branche de fonctionnalité (`git checkout -b feature/parser-genial`)
3. Commitez vos changements (`git commit -m 'Ajouter un parser génial'`)
4. Poussez la branche (`git push origin feature/parser-genial`)
5. Ouvrez une Pull Request

---

## 📄 Licence

Ce projet est sous licence **MIT** — consultez le fichier [LICENSE](LICENSE) pour plus de détails.

---

<p align="center">
  Construit avec 🦞 par <a href="https://github.com/astonysh">OpenClaw</a>
</p>
