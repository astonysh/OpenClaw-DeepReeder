<div dir="rtl">

# 🦞 OpenClaw DeepReader

> **بوابة محتوى الويب الافتراضية لوكلاء OpenClaw.** يقرأ X (Twitter)، Reddit، YouTube وأي صفحة ويب — بدون إعداد، بدون مفاتيح API.

DeepReader هو قارئ المحتوى المدمج في إطار عمل [OpenClaw](https://github.com/anthropics/openclaw). الصق أي رابط في المحادثة، وسيقوم DeepReader تلقائياً بجلب وتحليل وحفظ Markdown عالي الجودة في ذاكرة الوكيل طويلة المدى.

🌍 **الترجمات**: [English](README.md) · [中文](README_zh.md) · [Español](README_es.md) · [한국어](README_ko.md) · [日本語](README_ja.md) · [Français](README_fr.md)

---

## ⚡ التثبيت

<div dir="ltr">

```bash
npx clawhub@latest install deepreader
```

</div>

أو التثبيت يدوياً:

<div dir="ltr">

```bash
git clone https://github.com/astonysh/OpenClaw-DeepReeder.git
cd OpenClaw-DeepReeder
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

</div>

---

## 🎯 استخدمه عندما

- تحتاج لـ **قراءة تغريدة أو سلسلة أو مقال X** وإضافتها لذاكرة OpenClaw
- تحتاج لـ **استيعاب منشور Reddit** مع أفضل التعليقات
- تريد **حفظ نص فيديو YouTube** للمراجعة لاحقاً
- تريد **قص أي مدونة أو مقال** إلى Markdown نظيف
- وكيلك يحتاج **قارئ ويب افتراضي** يعمل فوراً — بدون مفاتيح API

---

## ✨ المصادر المدعومة

| المحلل | المصادر | الطريقة | مفتاح API؟ |
|--------|---------|---------|-----------|
| 🐦 **Twitter / X** | تغريدات، سلاسل | FxTwitter API + Nitter | ❌ لا |
| 🟠 **Reddit** | منشورات + تعليقات | Reddit `.json` API | ❌ لا |
| 🎬 **YouTube** | نصوص الفيديو | youtube-transcript-api | ❌ لا |
| 🌐 **أي رابط** | مدونات، مقالات | Trafilatura + BeautifulSoup | ❌ لا |

**بدون مفاتيح API. بدون تسجيل دخول. بدون حدود. الصق واقرأ.**

---

## 🚀 البداية السريعة

<div dir="ltr">

```python
from deepreader_skill import run

result = run("اطلع على هذا: https://x.com/user/status/123456")
result = run("نقاش رائع: https://www.reddit.com/r/python/comments/abc123/my_post/")
result = run("شاهد هذا: https://youtube.com/watch?v=dQw4w9WgXcQ")
```

</div>

---

## 🙏 شكر وتقدير

- **[FxTwitter](https://github.com/FxEmbed/FxEmbed)** · **[x-tweet-fetcher](https://github.com/ythx-101/x-tweet-fetcher)** · **[Trafilatura](https://trafilatura.readthedocs.io/)** · **[youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)**

## 📄 الترخيص

**رخصة MIT** — راجع ملف [LICENSE](LICENSE) للتفاصيل.

<p align="center">صنع بـ 🦞 بواسطة <a href="https://github.com/astonysh">OpenClaw</a></p>

</div>
