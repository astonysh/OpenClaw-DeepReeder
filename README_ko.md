# 🦞 OpenClaw DeepReeder

> **AI 에이전트를 위한 자율 웹 콘텐츠 수집 엔진.**

DeepReeder는 사용자 메시지에서 URL을 자동으로 감지하고, 전문 파서를 사용하여 콘텐츠를 지능적으로 스크래핑하며, YAML 프론트매터가 포함된 깔끔한 Markdown으로 변환하여 에이전트의 장기 메모리에 저장합니다.

🌍 **번역**: [English](README.md) · [中文](README_zh.md) · [Español](README_es.md) · [日本語](README_ja.md) · [العربية](README_ar.md) · [Français](README_fr.md)

---

## ✨ 기능

| 파서 | 소스 | 방법 |
|------|------|------|
| 🌐 **범용** | 블로그, 기사, 문서 | [Trafilatura](https://trafilatura.readthedocs.io/) + BeautifulSoup 대체 |
| 🐦 **Twitter / X** | 트윗, 스레드, X 아티클 | **FxTwitter API** (주력) + Nitter (대체) |
| 🎬 **YouTube** | 동영상 자막 | [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) |

### 🐦 Twitter / X — 심층 통합

[FxTwitter](https://github.com/FxEmbed/FxEmbed) API 기반. [x-tweet-fetcher](https://github.com/ythx-101/x-tweet-fetcher)에서 영감을 받았습니다.

| 콘텐츠 유형 | 지원 |
|------------|------|
| 일반 트윗 | ✅ 전체 텍스트 + 참여 통계 |
| 긴 트윗 (Twitter Blue) | ✅ 전체 텍스트 |
| X 아티클 (장문) | ✅ 전체 기사 + 단어 수 |
| 인용 트윗 | ✅ 중첩 콘텐츠 포함 |
| 미디어 (이미지, 동영상, GIF) | ✅ URL 추출 |
| 답글 스레드 | ✅ Nitter 대체를 통해 (처음 5개) |
| 참여 통계 | ✅ ❤️ 좋아요, 🔁 리트윗, 👁️ 조회, 🔖 북마크 |

**API 키 불필요. 로그인 불필요. 속도 제한 없음.**

---

## 📦 설치

```bash
# 저장소 클론
git clone https://github.com/astonysh/OpenClaw-DeepReeder.git
cd OpenClaw-DeepReeder

# 가상 환경 생성
python3 -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install -e .
```

---

## 🚀 빠른 시작

```python
from deepreader_skill import run

# 단일 URL 처리
result = run("이 기사를 확인하세요: https://example.com/blog/post")
print(result)

# 트윗 처리 (자동으로 FxTwitter API 사용)
result = run("흥미로운 스레드: https://x.com/elonmusk/status/123456")
print(result)

# 여러 URL 한번에 처리
result = run("""
  여기 몇 가지 링크가 있습니다:
  https://example.com/article
  https://youtube.com/watch?v=dQw4w9WgXcQ
  https://x.com/user/status/123456
""")
print(result)
```

---

## 🏗️ 아키텍처

```
deepreader_skill/
├── __init__.py          # 진입점 — run() 함수
├── manifest.json        # 스킬 메타데이터 및 트리거 설정
├── requirements.txt     # 의존성 목록
├── core/
│   ├── router.py        # URL → 파서 라우팅 로직
│   ├── storage.py       # Markdown 파일 생성 및 저장
│   └── utils.py         # URL 추출 및 유틸리티 함수
└── parsers/
    ├── base.py          # 추상 기본 파서 및 ParseResult 모델
    ├── generic.py       # 범용 기사/블로그 파서
    ├── twitter.py       # Twitter/X 파서 (FxTwitter + Nitter)
    └── youtube.py       # YouTube 자막 파서
```

### Twitter 파서 전략

```
URL 감지 → FxTwitter API (주력)
             ↓ 성공? → ✅ 풍부한 결과 (통계, 미디어, 기사)
             ↓ 실패?
           Nitter 인스턴스 (대체)
             ↓ 성공? → ✅ 기본 결과 + 답글 스레드
             ↓ 실패? → ❌ 친절한 오류 메시지 및 진단
```

---

## 🔧 설정

DeepReeder는 합리적인 기본값으로 바로 사용할 수 있습니다. 환경 변수로 설정을 변경할 수 있습니다:

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `DEEPREEDER_MEMORY_PATH` | `../../memory/inbox/` | 콘텐츠 저장 경로 |
| `DEEPREEDER_LOG_LEVEL` | `INFO` | 로깅 상세 수준 |

---

## 🙏 크레딧

- **[FxTwitter / FixTweet](https://github.com/FxEmbed/FxEmbed)** — Twitter/X 콘텐츠 가져오기용 공개 API
- **[x-tweet-fetcher](https://github.com/ythx-101/x-tweet-fetcher)** — FxTwitter 통합 접근 방식에 영감
- **[Trafilatura](https://trafilatura.readthedocs.io/)** — 강력한 웹 콘텐츠 추출
- **[youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)** — YouTube 자막 가져오기

---

## 🤝 기여

기여를 환영합니다!

1. 저장소를 Fork 합니다
2. 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-parser`)
3. 변경 사항을 커밋합니다 (`git commit -m '놀라운 파서 추가'`)
4. 브랜치를 푸시합니다 (`git push origin feature/amazing-parser`)
5. Pull Request를 엽니다

---

## 📄 라이선스

이 프로젝트는 **MIT 라이선스**에 따라 라이선스가 부여됩니다 — 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

<p align="center">
  <a href="https://github.com/astonysh">OpenClaw</a>에서 🦞 로 만들었습니다
</p>
