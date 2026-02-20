# 🦞 OpenClaw DeepReader

> **La pasarela de contenido web predeterminada para agentes OpenClaw.** Lee X (Twitter), Reddit, YouTube y cualquier página web — sin configuración, sin claves API.

DeepReader es el lector de contenido integrado para el framework de agentes [OpenClaw](https://github.com/anthropics/openclaw). Pega cualquier URL en una conversación, y DeepReader automáticamente obtiene, analiza y guarda Markdown de alta calidad en la memoria a largo plazo del agente. Diseñado para redes sociales y la web moderna.

🌍 **Traducciones**: [English](README.md) · [中文](README_zh.md) · [한국어](README_ko.md) · [日本語](README_ja.md) · [العربية](README_ar.md) · [Français](README_fr.md)

---

## ⚡ Instalación

```bash
npx clawhub@latest install deepreader
```

O instala manualmente:

```bash
git clone https://github.com/astonysh/OpenClaw-DeepReeder.git
cd OpenClaw-DeepReeder
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

---

## 🎯 Úsalo Cuando

- Necesites **leer un tweet, hilo o artículo de X** y añadirlo a la memoria de OpenClaw
- Necesites **ingerir un post de Reddit** con los comentarios principales y contexto de discusión
- Quieras **guardar una transcripción de YouTube** para referencia o análisis posterior
- Quieras **recortar cualquier blog, artículo o documentación** en Markdown limpio
- Tu agente necesite un **lector web predeterminado** que simplemente funcione — sin claves API, sin configuración

---

## ✨ Fuentes Soportadas

| Parser | Fuentes | Método | ¿Clave API? |
|--------|---------|--------|-------------|
| 🐦 **Twitter / X** | Tweets, hilos, X Articles | [FxTwitter API](https://github.com/FxEmbed/FxEmbed) + Nitter fallback | ❌ Ninguna |
| 🟠 **Reddit** | Posts + hilos de comentarios | Reddit `.json` API | ❌ Ninguna |
| 🎬 **YouTube** | Transcripciones de vídeo | [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) | ❌ Ninguna |
| 🌐 **Cualquier URL** | Blogs, artículos, docs | [Trafilatura](https://trafilatura.readthedocs.io/) + BeautifulSoup | ❌ Ninguna |

**Sin claves API. Sin inicio de sesión. Sin límites. Pega y lee.**

---

## 🐦 Twitter / X — Integración Profunda

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

## 🟠 Reddit — Integración JSON Nativa

Usa el sufijo `.json` nativo de Reddit — **sin claves API, sin OAuth, sin registro**.

| Tipo de Contenido | Soporte |
|-------------------|---------| 
| Self posts (texto) | ✅ Cuerpo completo en Markdown |
| Link posts | ✅ URL + metadatos |
| Comentarios principales (por puntuación) | ✅ Hasta 15 comentarios |
| Hilos de respuestas anidados | ✅ Hasta 3 niveles |
| Medios (imágenes, galerías, vídeo) | ✅ URLs extraídas |
| Estadísticas del post | ✅ ⬆️ puntuación, 💬 comentarios, ratio de votos |
| Etiquetas Flair | ✅ Incluidas |

---

## 🚀 Inicio Rápido

```python
from deepreader_skill import run

# Leer un tweet → guarda en la memoria del agente
result = run("Mira este tweet: https://x.com/elonmusk/status/123456")

# Leer una discusión de Reddit → captura post + comentarios
result = run("Gran discusión: https://www.reddit.com/r/python/comments/abc123/my_post/")

# Leer un vídeo de YouTube → guarda transcripción completa
result = run("Mira esto: https://youtube.com/watch?v=dQw4w9WgXcQ")

# Leer cualquier artículo → extrae contenido limpio
result = run("Lectura interesante: https://example.com/blog/ai-agents-2026")

# Procesamiento por lotes de múltiples URLs
result = run("""
  Aquí hay algunos enlaces:
  https://x.com/user/status/123456
  https://www.reddit.com/r/MachineLearning/comments/xyz789/new_paper/
  https://youtube.com/watch?v=dQw4w9WgXcQ
  https://example.com/article
""")
```

---

## 📓 Integración de NotebookLM & Audio

DeepReader ahora se integra perfectamente con **Google NotebookLM**. 

Si tu mensaje incluye palabras clave como `notebooklm`, `audio` o `podcast`, DeepReader automáticamente:
1. Analizará las URLs solicitadas en Markdown.
2. Creará un nuevo Cuaderno (Notebook) en tu cuenta de Google NotebookLM.
3. Subirá el contenido Markdown impecable como fuente.
4. **(Opcional)** Generará un Audio Overview (formato podcast) atractivo y lo descargará directamente en la carpeta de memoria de tu agente.

**Generación de Artefactos de NotebookLM Soportados:**
Junto con los Resúmenes de Audio, esta integración se puede extender fácilmente para generar y guardar automáticamente:
- **🎙️ Audio Overview** (Podcast)
- **🎥 Video Overview** (Resumen en Vídeo)
- **🧠 Mind Map** (Mapa Mental)
- **📄 Reports** (Informes)
- **📇 Flashcards** (Tarjetas de Estudio)
- **❓ Quiz** (Cuestionario)
- **📊 Infographic** (Infografía)
- **🖥️ Slide Deck** (Presentación)
- **📈 Data Table** (Tabla de Datos)

> **⚠️ Nota: Autenticación Requerida**
> Antes de usar la integración con NotebookLM, debes autenticarte en tu terminal (esto solo se requiere una vez):
> ```bash
> notebooklm login
> ```

---

## 🏗️ Arquitectura

```
deepreader_skill/
├── __init__.py          # Punto de entrada — función run()
├── manifest.json        # Metadatos del skill y configuración de triggers
├── SKILL.md             # Descripción para ClawHub
├── requirements.txt     # Dependencias
├── core/
│   ├── router.py        # Lógica de enrutamiento URL → Parser
│   ├── storage.py       # Generación y guardado de archivos Markdown
│   └── utils.py         # Extracción de URLs y utilidades
└── parsers/
    ├── base.py          # Parser base abstracto y modelo ParseResult
    ├── generic.py       # Parser genérico de artículos/blogs
    ├── twitter.py       # Parser Twitter/X (FxTwitter + Nitter)
    ├── reddit.py        # Parser Reddit (.json API)
    └── youtube.py       # Parser de transcripciones de YouTube
```

---

## 🔧 Configuración

| Variable | Predeterminado | Descripción |
|----------|---------------|-------------|
| `DEEPREEDER_MEMORY_PATH` | `../../memory/inbox/` | Ruta para guardar contenido |
| `DEEPREEDER_LOG_LEVEL` | `INFO` | Nivel de detalle del registro |

---

## 💡 ¿Por Qué DeepReader?

| Característica | DeepReader | Scraping manual | Herramientas de navegador |
|---------------|-----------|----------------|--------------------------|
| **Activación** | Automática por URL | Código manual | Acción manual |
| **Twitter/X** | ✅ Soporte completo | ❌ Bloqueado | ⚠️ Parcial |
| **Hilos Reddit** | ✅ + comentarios | ⚠️ Complejo | ⚠️ Lento |
| **Transcripciones YouTube** | ✅ Integrado | ❌ Herramienta separada | ❌ No disponible |
| **Claves API** | ❌ Ninguna | ✅ Frecuentemente | ✅ A veces |
| **Formato de salida** | Markdown limpio | HTML crudo | Capturas de pantalla |
| **Integración de memoria** | ✅ Auto-guardado | ❌ Manual | ❌ Manual |

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
