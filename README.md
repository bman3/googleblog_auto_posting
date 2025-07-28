# 구글 블로그 자동 포스팅 시스템

마크다운 파일을 구글 블로그(Blogger)에 자동으로 포스팅하는 Python 시스템입니다.

## 주요 기능

- 📝 마크다운 파일을 HTML로 변환하여 블로그에 포스팅
- 🤖 AI를 사용한 자동 콘텐츠 생성 (Google Gemini)
- 🖼️ 자동 AI 이미지 생성 (Hugging Face 완전 무료) + 스톡 이미지 (Unsplash, Pexels)
- 🔄 자동 스케줄링 포스팅
- 🏷️ 태그(라벨) 지원
- 📅 발행 날짜 설정
- 🖼️ 이미지 업로드 지원
- 📋 Front Matter를 통한 메타데이터 설정
- 🔐 Google OAuth 2.0 인증

## 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. Google API 설정

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. Blogger API v3 활성화
4. OAuth 2.0 클라이언트 ID 생성
   - 애플리케이션 유형: 데스크톱 앱
   - 리디렉션 URI: `http://localhost:8080`

### 3. 환경 변수 설정

`env_example.txt` 파일을 참고하여 `.env` 파일을 생성하세요:

```bash
# .env 파일 생성
cp env_example.txt .env
```

`.env` 파일에 다음 정보를 입력하세요:

```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
BLOG_ID=your_blog_id_here

# AI 서비스 API 키 (선택사항)
GEMINI_API_KEY=your_gemini_api_key_here

# 이미지 서비스 API 키 (선택사항)
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

### 4. 블로그 ID 찾기

블로그 URL에서 블로그 ID를 찾을 수 있습니다:
- `https://yourblog.blogspot.com` → `yourblog`
- 또는 Blogger 관리자 페이지에서 확인

## 사용법

### 기본 명령어

```bash
# 연결 테스트
python main.py --test

# 샘플 포스트 생성 및 포스팅
python main.py --sample

# 새로운 마크다운 파일 포스팅 (기본 동작)
python main.py

# 모든 마크다운 파일 포스팅
python main.py --post-all

# 자동 발행 모드로 포스팅
python main.py --auto-publish

# 포스트 목록 조회
python main.py --list-posts

# Gemini AI로 콘텐츠 생성
python main.py --ai-generate "파이썬 프로그래밍 기초"

# Gemini API 키 상태 확인
python main.py --ai-services

# AI 생성 후 자동 포스팅
python main.py --ai-generate "머신러닝 입문" --ai-auto-post

# 특정 스타일과 길이로 AI 콘텐츠 생성
python main.py --ai-generate "웹 개발 팁" --ai-style casual --ai-length long

# 이미지 없이 AI 콘텐츠 생성
python main.py --ai-generate "알고리즘 기초" --ai-no-images

# 30분마다 자동 포스팅
python main.py --schedule 30

### 마크다운 파일 작성

`posts/` 디렉토리에 마크다운 파일을 작성하세요. Front Matter를 사용하여 메타데이터를 설정할 수 있습니다:

```markdown
---
title: 포스트 제목
labels: 태그1, 태그2, 태그3
status: DRAFT  # DRAFT 또는 PUBLISHED
publish_date: 2024-01-01
---

# 포스트 제목

포스트 내용을 여기에 작성하세요.

## 소제목

- 목록 항목 1
- 목록 항목 2

### 코드 예제

```python
def hello_world():
    print("Hello, World!")
```

### 이미지

![이미지 설명](image.jpg)
```

## 디렉토리 구조

```
autopostinggoogleblog/
├── main.py                 # 메인 실행 파일
├── config.py              # 설정 관리
├── google_auth.py         # Google API 인증
├── blog_poster.py         # 블로그 포스팅 기능
├── markdown_processor.py  # 마크다운 처리
├── auto_poster.py         # 자동 포스팅 관리
├── requirements.txt       # Python 패키지 목록
├── env_example.txt        # 환경 변수 예제
├── README.md             # 사용법 설명
├── posts/                # 마크다운 파일 저장소
├── images/               # 이미지 파일 저장소
├── credentials.json      # Google API 인증 정보 (선택사항)
└── token.json           # 인증 토큰 (자동 생성)
```

## 고급 설정

### 환경 변수 옵션

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `GOOGLE_CLIENT_ID` | Google OAuth 클라이언트 ID | 필수 |
| `GOOGLE_CLIENT_SECRET` | Google OAuth 클라이언트 시크릿 | 필수 |
| `BLOG_ID` | 블로그 ID | 필수 |
| `POSTS_DIR` | 마크다운 파일 디렉토리 | `posts` |
| `IMAGES_DIR` | 이미지 파일 디렉토리 | `images` |
| `DEFAULT_STATUS` | 기본 포스팅 상태 | `DRAFT` |
| `AUTO_PUBLISH` | 자동 발행 여부 | `false` |
| `SCHEDULE_INTERVAL` | 스케줄링 간격 (초) | `3600` |

### 스케줄링

백그라운드에서 자동 포스팅을 실행하려면:

```bash
# 1시간마다 자동 포스팅
python main.py --schedule 60

# 30분마다 자동 포스팅
python main.py --schedule 30
```

## 문제 해결

### 인증 오류

1. Google Cloud Console에서 API가 활성화되어 있는지 확인
2. OAuth 2.0 클라이언트 ID가 올바른지 확인
3. `.env` 파일의 설정값이 정확한지 확인

### 포스팅 실패

1. 블로그 ID가 올바른지 확인
2. 마크다운 파일 형식이 올바른지 확인
3. 인터넷 연결 상태 확인

### 이미지 업로드 실패

1. 이미지 파일 경로가 올바른지 확인
2. 이미지 파일 크기가 적절한지 확인
3. 지원되는 이미지 형식인지 확인 (JPEG, PNG, GIF)

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여

버그 리포트나 기능 제안은 이슈를 통해 해주세요. 풀 리퀘스트도 환영합니다! 