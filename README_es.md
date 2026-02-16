# 🦞 OpenClaw DeepReeder

> **Motor autónomo de ingestión de contenido web para agentes de IA.**

DeepReeder intercepta URLs de los mensajes de usuario, extrae contenido de forma inteligente usando parsers especializados, lo formatea en Markdown limpio con metadatos YAML frontmatter, y lo guarda en la memoria a largo plazo del agente.

🌍 **Traducciones**: [English](README.md) · [中文](README_zh.md) · [한국어](README_ko.md) · [日本語](README_ja.md) · [العربية](README_ar.md) · [Français](README_fr.md)

---

## ✨ Características

| Parser | Fuentes | Método |
|--------|---------|--------|
| 🌐 **Genérico** | Blogs, artículos, documentación | [Trafilatura](https://trafilatura.readthedocs.io/) con fallback BeautifulSoup |
| 🐦 **Twitter / X** | Tweets, hilos, X Articles | **FxTwitter API** (principal) + Nitter (fallback) |
| 🎬 **YouTube** | Transcripciones de vídeo | [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) |

### 🐦 Twitter / X — Integración Profunda

Impulsado por la API de [FxTwitter](https://github.com/FxEmbed/FxEmbed). Inspirado en [x-tweet-fetcher](https://github.com/ythx-101/x-tweet-fetcher).

| Tipo de Contenido | Soporte |
|-------------------|---------|
| Tweets regulares | ✅ Texto completo + estadísticas |
| Tweets largos (Twitter Blue) | ✅ Texto completo |
| X Articles (contenido largo) | ✅ Artículo completo + recuento de palabras |
| Tweets citados | ✅ Contenido anidado incluido |
| Medios (imágenes, vídeo, GIF) | ✅ URLs extraídas |
| Hilos de respuestas | ✅ Vía Nitter fallback (primeras 5) |
| Estadísticas de interacción | ✅ ❤️ likes, 🔁 RTs, 👁️ vistas, 🔖 marcadores |

**Sin claves API. Sin inicio de sesión. Sin límites de velocidad.**

---

## 📦 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/astonysh/OpenClaw-DeepReeder.git
cd OpenClaw-DeepReeder

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -e .
```

---

## 🚀 Inicio Rápido

```python
from deepreader_skill import run

# Procesar una sola URL
result = run("Mira este artículo: https://example.com/blog/post")
print(result)

# Procesar un tweet (usa FxTwitter API automáticamente)
result = run("Hilo interesante: https://x.com/elonmusk/status/123456")
print(result)

# Procesar múltiples URLs a la vez
result = run("""
  Aquí hay algunos enlaces:
  https://example.com/article
  https://youtube.com/watch?v=dQw4w9WgXcQ
  https://x.com/user/status/123456
""")
print(result)
```

---

## 🏗️ Arquitectura

```
deepreader_skill/
├── __init__.py          # Punto de entrada — función run()
├── manifest.json        # Metadatos del skill y configuración de triggers
├── requirements.txt     # Dependencias
├── core/
│   ├── router.py        # Lógica de enrutamiento URL → Parser
│   ├── storage.py       # Generación y guardado de archivos Markdown
│   └── utils.py         # Extracción de URLs y utilidades
└── parsers/
    ├── base.py          # Parser base abstracto y modelo ParseResult
    ├── generic.py       # Parser genérico de artículos/blogs
    ├── twitter.py       # Parser Twitter/X (FxTwitter + Nitter)
    └── youtube.py       # Parser de transcripciones de YouTube
```

### Estrategia del Parser de Twitter

```
URL detectada → FxTwitter API (principal)
                  ↓ ¿éxito? → ✅ Resultado enriquecido (stats, media, artículos)
                  ↓ ¿fallo?
                Instancias Nitter (fallback)
                  ↓ ¿éxito? → ✅ Resultado básico + hilos de respuestas
                  ↓ ¿fallo? → ❌ Error descriptivo con diagnóstico
```

---

## 🔧 Configuración

DeepReeder funciona listo para usar con valores predeterminados sensatos. Se puede personalizar mediante variables de entorno:

| Variable | Predeterminado | Descripción |
|----------|---------------|-------------|
| `DEEPREEDER_MEMORY_PATH` | `../../memory/inbox/` | Ruta para guardar contenido |
| `DEEPREEDER_LOG_LEVEL` | `INFO` | Nivel de detalle del registro |

---

## 🙏 Créditos

- **[FxTwitter / FixTweet](https://github.com/FxEmbed/FxEmbed)** — API pública para obtener contenido de Twitter/X
- **[x-tweet-fetcher](https://github.com/ythx-101/x-tweet-fetcher)** — Inspiración para la integración de FxTwitter
- **[Trafilatura](https://trafilatura.readthedocs.io/)** — Extracción robusta de contenido web
- **[youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)** — Obtención de transcripciones de YouTube

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

1. Haz fork del repositorio
2. Crea una rama de funcionalidad (`git checkout -b feature/parser-increible`)
3. Haz commit de tus cambios (`git commit -m 'Agregar parser increíble'`)
4. Haz push a la rama (`git push origin feature/parser-increible`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está licenciado bajo la **Licencia MIT** — consulta el archivo [LICENSE](LICENSE) para más detalles.

---

<p align="center">
  Construido con 🦞 por <a href="https://github.com/astonysh">OpenClaw</a>
</p>
