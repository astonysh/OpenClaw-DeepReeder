<div dir="rtl">

# 🦞 OpenClaw DeepReeder

> **محرك استيعاب محتوى الويب الذاتي لوكلاء الذكاء الاصطناعي.**

🌍 **الترجمات**: [English](README.md) · [中文](README_zh.md) · [Español](README_es.md) · [한국어](README_ko.md) · [日本語](README_ja.md) · [Français](README_fr.md)

---

## ✨ الميزات

| المحلل | المصادر | الطريقة |
|--------|---------|---------|
| 🌐 **عام** | مدونات، مقالات، وثائق | [Trafilatura](https://trafilatura.readthedocs.io/) مع BeautifulSoup احتياطي |
| 🐦 **Twitter / X** | تغريدات، سلاسل، مقالات X | **FxTwitter API** (رئيسي) + Nitter (احتياطي) |
| 🟠 **Reddit** | منشورات + سلاسل تعليقات | **Reddit .json API** (بدون إعداد) |
| 🎬 **YouTube** | نصوص الفيديو | [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) |

### 🟠 Reddit — تكامل JSON الأصلي

يستخدم لاحقة URL `.json` المدمجة في Reddit — **بدون مفاتيح API، بدون OAuth، بدون تسجيل**.

| نوع المحتوى | الدعم |
|-------------|-------|
| منشورات نصية | ✅ نص Markdown كامل |
| منشورات الروابط | ✅ URL + بيانات وصفية |
| أفضل التعليقات (مرتبة حسب النقاط) | ✅ حتى 15 تعليقاً |
| سلاسل الردود المتداخلة | ✅ حتى 3 مستويات عمق |
| الوسائط (صور، معارض، فيديو) | ✅ استخراج الروابط |
| إحصائيات المنشور | ✅ ⬆️ النقاط، 💬 عدد التعليقات |
| علامات Flair | ✅ مضمّنة |

**بدون مفاتيح API. بدون تسجيل دخول. بدون حدود للسرعة.**

---

## 📦 التثبيت

<div dir="ltr">

```bash
git clone https://github.com/astonysh/OpenClaw-DeepReeder.git
cd OpenClaw-DeepReeder
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

</div>

---

## 🚀 البداية السريعة

<div dir="ltr">

```python
from deepreader_skill import run

result = run("اطلع على هذا: https://example.com/blog/post")
print(result)

result = run("نقاش رائع: https://www.reddit.com/r/python/comments/abc123/my_post/")
print(result)
```

</div>

---

## 🏗️ الهيكل

<div dir="ltr">

```
deepreader_skill/
├── __init__.py          # نقطة الدخول — دالة run()
├── manifest.json        # بيانات المهارة الوصفية
├── requirements.txt     # قائمة التبعيات
├── core/
│   ├── router.py        # منطق توجيه URL → المحلل
│   ├── storage.py       # إنشاء وحفظ ملفات Markdown
│   └── utils.py         # استخراج URL ودوال مساعدة
└── parsers/
    ├── base.py          # المحلل الأساسي
    ├── generic.py       # محلل المقالات العام
    ├── twitter.py       # محلل Twitter/X
    ├── reddit.py        # محلل Reddit (.json API)
    └── youtube.py       # محلل نصوص YouTube
```

</div>

---

## 🙏 شكر وتقدير

- **[FxTwitter](https://github.com/FxEmbed/FxEmbed)** · **[x-tweet-fetcher](https://github.com/ythx-101/x-tweet-fetcher)** · **[Trafilatura](https://trafilatura.readthedocs.io/)** · **[youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)**

## 📄 الترخيص

**رخصة MIT** — راجع ملف [LICENSE](LICENSE) للتفاصيل.

<p align="center">صنع بـ 🦞 بواسطة <a href="https://github.com/astonysh">OpenClaw</a></p>

</div>
