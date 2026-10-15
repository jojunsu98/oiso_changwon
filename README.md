<img src="assets/logo_wide.png" width="180" align="right" alt="오이소창원 로고">

# 오이소창원 Lite

> 창원 전입 청년의 첫 180일 동안 놓치기 쉬운 혜택과 할 일을 내 조건으로 판정하고, 일정과 다음 행동으로 정리하는 AI 정착 코디네이터
>
> **슬로건: 창원에서 너의 내일을 응원해!**

[![Vercel Lite checks](https://github.com/jojunsu98/oiso_changwon/actions/workflows/vercel-lite-check.yml/badge.svg?branch=codyssey-vercel-lite)](https://github.com/jojunsu98/oiso_changwon/actions/workflows/vercel-lite-check.yml)

- **개발 브랜치:** `codyssey-vercel-lite`
- **Vercel 배포 URL:** 배포 후 기입
- **기존 Streamlit 서비스:** https://oisochangwon-4fuybothxlr78qnnaappqv.streamlit.app/
- **서비스 기획서:** [docs/codyssey-service-plan.md](docs/codyssey-service-plan.md)

> **현재 상태:** 프론트엔드와 Python API 1차 구현 및 자동 테스트 완료. Vercel 환경 변수 설정, 실제 배포, 브라우저 동작 검증과 제출용 캡처는 아직 필요하다.

---

## 1. 프로젝트 소개

오이소창원 Lite는 기존 팀 프로젝트 **「오이소창원 — AI 기반 창원 정착 지원 Agent」**의 콘셉트를 그대로 유지하면서, 코디세이 「AI 웹 개발: 내 아이디어를 현실로, AI 웹 서비스 빌딩」 개인 미션의 기술 요건에 맞춰 다시 구현한 웹 버전이다.

콘셉트를 바꾼 것이 아니라 구현 구조만 다음과 같이 전환했다.

```text
기존: Streamlit + Python 단일 웹앱
변경: HTML/CSS/JavaScript 프론트엔드
      + Vercel Python Functions 백엔드
      + OpenAI API
```

### 그대로 유지한 핵심

- 서비스명·로고·슬로건·색상
- 창원 전입·전입 예정 청년이라는 타겟
- 첫 180일 정착 지원이라는 문제 정의
- `내 조건 → 판정 → 일정 → 안내` 사용자 여정
- 맞춤 혜택·생활 정보·불편사항·지역말·AI Agent 기능 축
- 정책을 4단계로 판정하고 자격을 단정하지 않는 정보 원칙
- 팀이 검증한 정책·민원·지역말·생활 활동 데이터

### Lite에서 경량화한 부분

- 이메일 알림
- 영구 상태 저장
- 캘린더 파일·전체 정착 리포트 생성
- 기존 Streamlit의 모든 세부 화면

위 부가 기능은 과제 필수 요건이 아니므로 제외하고, 사용자 입력 → JavaScript `fetch()` → Python API → AI 응답 → 화면 표시 흐름에 집중했다.

---

## 2. 주요 기능

### 맞춤 혜택 판정

사용자가 다음 정보를 입력한다.

- 만 나이
- 창원 전입일
- 현재 하는 일
- 창원 사업장 재직 여부
- 전입 전 타지역 거주 기간
- 차량 보유 여부

`api/recommend.py`가 기존 정책 규칙 모듈을 호출해 정책 24건을 아래 네 단계로 분류한다.

1. 해당 가능
2. 조건부 해당 가능
3. 직접 확인
4. 해당 없음

그 후 OpenAI API가 규칙 판정 결과만 바탕으로 우선 확인할 정책과 다음 행동을 짧게 설명한다.

### 오이소창원 AI 코디네이터

사용자가 자연어로 질문하면 `api/chat.py`가 다음 데이터에서 관련 내용을 먼저 검색한다.

- 창원·청년 정책
- 불편사항 접수 창구
- 경상도 지역말
- 창원 생활·활동 정보

AI에는 검색된 검증 자료만 전달한다. 자료에 없는 금액·날짜·연락처·자격 조건은 만들지 않도록 제한한다.

### 반응형 화면

한 페이지 안에 다음 섹션을 두고 메뉴로 이동한다.

- 홈
- 서비스
- 맞춤 혜택
- 생활 안내
- AI 코디네이터
- 서비스 안내

데스크톱·태블릿·모바일에서 레이아웃이 단계적으로 2열에서 1열로 전환된다.

### 실패 처리

- 필수값 누락
- 잘못된 입력 형식
- 질문 빈값·길이 초과
- OpenAI API 키 미설정
- API 4xx·5xx 오류
- 응답 지연·타임아웃
- 검색 자료 부족
- 긴급·생명 위기 표현의 고정 안전 안내

---

## 3. 기술 스택

| 영역 | 기술 |
|---|---|
| 프론트엔드 | HTML5, CSS3, Vanilla JavaScript |
| 백엔드 | Python, Vercel Python Functions |
| AI | OpenAI Responses API |
| 데이터 | JSON, 기존 Python 정책 판정 모듈 |
| 배포 | Vercel |
| 형상 관리 | GitHub |
| 테스트 | Python `unittest`, GitHub Actions |

프레임워크인 React·Vue는 사용하지 않았다.

---

## 4. 전체 동작 흐름

### 맞춤 혜택

```text
사용자 조건 입력
→ js/app.js가 입력값 검증
→ fetch('/api/recommend')
→ api/recommend.py
→ src/policy_matcher.py 규칙 판정
→ OpenAI API가 판정 결과 요약
→ JSON 응답
→ JavaScript가 AI 요약·단계별 개수·정책 카드를 화면에 표시
```

### AI 코디네이터

```text
사용자 질문 입력
→ fetch('/api/chat')
→ api/chat.py가 로컬 검증 데이터 검색
→ 관련 자료만 OpenAI API에 전달
→ 근거 기반 답변과 출처 카드 반환
→ JavaScript가 채팅 화면에 표시
```

---

## 5. 프로젝트 구조

이 브랜치는 기존 팀 프로젝트에서 분기했기 때문에 Streamlit 원본 파일도 남아 있다. Vercel Lite 구현에 직접 사용하는 핵심 파일은 아래와 같다.

```text
oiso_changwon/
├── index.html                       # 바닐라 프론트엔드 화면
├── css/
│   └── style.css                    # 반응형 디자인
├── js/
│   └── app.js                       # 폼·fetch·렌더링·오류 처리
├── api/
│   ├── recommend.py                 # 정책 판정 + AI 브리핑
│   └── chat.py                      # 검증 자료 검색 + AI 답변
├── assets/
│   ├── logo_wide.png
│   └── logo_icon.png
├── data/
│   ├── policies_mvp.json
│   ├── complaint_channels.json
│   ├── dialects_core30.json
│   └── activities_mvp.json
├── src/
│   ├── policy_matcher.py
│   └── policy_engine.py
├── tests/
│   └── test_vercel_lite.py
├── docs/
│   └── codyssey-service-plan.md
├── .github/workflows/
│   └── vercel-lite-check.yml
├── .env.example
├── requirements.txt
├── vercel.json
└── README.md
```

---

## 6. 로컬 실행 방법

### 준비물

- Git
- Python 3.12 권장
- Node.js와 Vercel CLI
- OpenAI API 키

### 저장소 내려받기

```powershell
git clone -b codyssey-vercel-lite https://github.com/jojunsu98/oiso_changwon.git
cd oiso_changwon
```

### Python 가상환경과 패키지 설치

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

PowerShell에서 스크립트 실행 정책 오류가 날 경우 현재 창에서만 다음 명령을 실행한다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Vercel CLI 설치

```powershell
npm install -g vercel
```

### 환경 변수

`.env.example`을 참고해 프로젝트 루트에 `.env.local`을 만든다.

```text
OPENAI_API_KEY=실제_API_키
OPENAI_MODEL=gpt-4.1-mini
```

실제 키가 들어 있는 `.env.local`은 GitHub에 올리지 않는다.

### 로컬 실행

```powershell
vercel dev
```

터미널에 표시된 로컬 주소로 접속한다. 보통 다음 형태다.

```text
http://localhost:3000
```

---

## 7. Vercel 배포 방법

1. Vercel에 로그인한다.
2. `Add New` → `Project`를 누른다.
3. GitHub 저장소 `jojunsu98/oiso_changwon`을 선택한다.
4. 배포 대상 브랜치를 `codyssey-vercel-lite`로 설정한다.
5. Framework Preset은 `Other`로 확인한다.
6. Root Directory는 저장소 루트 `.`로 둔다.
7. Environment Variables에 다음 값을 추가한다.

```text
OPENAI_API_KEY = 실제 OpenAI API 키
OPENAI_MODEL = gpt-4.1-mini
```

8. `Deploy`를 누른다.
9. 배포 후 `/api/recommend`, `/api/chat` 엔드포인트와 전체 화면을 테스트한다.
10. 정상 확인 후 이 README의 배포 URL을 실제 주소로 바꾼다.

> Vercel의 Git 연결 화면에서 특정 브랜치를 바로 프로덕션으로 선택할 수 없는 경우, 우선 Preview Deployment를 만든 뒤 Project Settings → Git에서 Production Branch를 `codyssey-vercel-lite`로 지정한다.

---

## 8. 환경 변수

| 변수명 | 필수 | 설명 |
|---|---:|---|
| `OPENAI_API_KEY` | 예 | 서버에서 OpenAI API를 호출할 때 사용 |
| `OPENAI_MODEL` | 아니요 | 기본값 `gpt-4.1-mini`; 계정에서 사용 가능한 모델로 변경 가능 |

API 키를 `index.html`, `js/app.js`, README, 캡처 화면에 직접 입력하지 않는다.

---

## 9. 테스트

### 로컬 자동 테스트

```powershell
python -m py_compile api/recommend.py api/chat.py src/policy_matcher.py src/policy_engine.py
python -m unittest tests/test_vercel_lite.py -v
node --check js/app.js
```

### GitHub Actions

`codyssey-vercel-lite` 브랜치에 코드가 올라오면 다음을 자동 검사한다.

- Python 패키지 설치
- Python 문법 검사
- `vercel.json` JSON 형식 검사
- 프로필 입력 검증
- 기존 정책 24건 판정 호출
- 정책·민원·지역말 검색
- 위기 표현 안전 경로

### 수동 테스트 입력

#### 정상 입력

```text
나이: 28
전입일: 2026-09-20
하는 일: 직장인
창원 사업장 재직: 예
전입 전 타지역 거주: 3년 이상
차량: 없음
```

예상 결과:

- 정책 24건을 네 단계로 구분
- 기업노동자 전입 지원금 등 우선 정책 표시
- AI 정착 브리핑 표시
- 공식 확인 링크 표시

#### 빈 입력

필수값을 비운 채 제출하면 브라우저가 제출을 막고 입력 안내를 표시한다.

#### AI 질문

```text
욕봤데이는 무슨 뜻이야?
```

예상 결과:

- `수고했다, 고생했다`라는 뜻을 자료 범위에서 안내
- 사람 검수 한계를 짧게 표시
- 참고 자료 표시

---

## 10. 보안과 개인정보

- OpenAI API 키는 Vercel 서버 환경 변수로만 관리한다.
- 브라우저에는 키를 전달하지 않는다.
- 실제 키가 담긴 파일은 커밋하지 않는다.
- 실명·전화번호·주민등록번호를 입력받지 않는다.
- 요청 본문 크기와 질문 길이를 제한한다.
- 서버 로그와 사용자 오류 메시지를 분리한다.
- 정책 자격은 참고 판정이며 최종 결정은 담당 기관에 있다.
- 긴급 상황은 AI가 판단하지 않고 112·119 등 즉시 연락 경로를 안내한다.

키가 노출되었다면 Git 기록에서 파일만 지우는 것으로 끝내지 않고 해당 키를 폐기하고 재발급해야 한다.

---

## 11. 오류 처리 방식

| 오류 | 처리 방식 |
|---|---|
| 필수값 누락 | 프론트·백엔드 양쪽 검증, HTTP 400 |
| 잘못된 형식 | 항목별 오류 메시지, HTTP 400 |
| API 키 미설정 | 정책 규칙 결과는 유지, AI 비활성 안내 또는 HTTP 503 |
| OpenAI API 오류 | 규칙 결과 유지 또는 HTTP 502, 재시도 안내 |
| 응답 지연 | 브라우저에서 35~40초 후 요청 중단 |
| 자료 없음 | 임의 답변 대신 질문 구체화 안내 |
| 예상하지 못한 서버 오류 | 내부 원인은 배포 로그에 남기고 사용자에게 일반 안내 |

---

## 12. 과제 요구사항 대응

| 필수 요구사항 | 구현 위치 | 상태 |
|---|---|---|
| 3개 이상 페이지·섹션 | `index.html` 6개 섹션 | 구현 완료 |
| 메뉴 이동 | 상단 내비게이션 | 구현 완료 |
| 순수 HTML/CSS/JS | `index.html`, `css/`, `js/` | 구현 완료 |
| 반응형 | `style.css` 미디어 쿼리 | 코드 구현, 실기기 확인 필요 |
| 사용자 입력 | 맞춤 폼·채팅 폼 | 구현 완료 |
| AI 결과 표시 | 정착 브리핑·AI 채팅 | 코드 구현, 실제 API 확인 필요 |
| 빈 입력 오류 | HTML·JavaScript·Python 검증 | 구현 완료 |
| API 오류 | 4xx·5xx 메시지 처리 | 구현 완료 |
| 지연 처리 | `AbortController` | 구현 완료 |
| Python `api/` | `api/recommend.py`, `api/chat.py` | 구현 완료 |
| `fetch('/api/...')` | `js/app.js` | 구현 완료 |
| 환경 변수 | `.env.example`, 서버 코드 | 구현 완료 |
| GitHub | `codyssey-vercel-lite` 브랜치 | 완료 |
| Vercel 배포 | 배포 URL | 미완료 |
| 서비스 기획서 | `docs/codyssey-service-plan.md` | 완료 |
| 증빙 캡처 | 배포 후 제작 | 미완료 |

---

## 13. 출처와 기여 범위

기존 오이소창원은 **조준수·이혜경·이미영**이 참여한 팀 프로젝트다. Lite 버전은 팀 프로젝트 전체를 개인 단독 제작물로 표현하지 않는다.

> 본 서비스는 기존 팀 프로젝트 「오이소창원」의 공동 기획·검증 데이터·브랜드 자산을 기반으로 하며, 조준수가 코디세이 개인 미션에서 순수 HTML/CSS/JavaScript 프론트엔드와 Vercel Python Functions 구조로 재구현한 학습용 Lite 버전입니다.

### 이번 개인 미션에서 새로 구현한 범위

- 순수 HTML 화면 구조
- 반응형 CSS
- JavaScript 입력 검증·API 요청·결과 렌더링
- Vercel Python Functions
- OpenAI API 연동·오류 처리
- 개인 미션용 기획서·README·테스트

### 기존 팀 자산에서 재사용한 범위

- 서비스 콘셉트·브랜드·로고·슬로건
- 정책·민원·지역말·생활 활동 데이터
- 정책 판정 원칙과 기존 규칙 모듈

---

## 14. 남은 작업

1. Vercel 프로젝트 생성 및 GitHub 브랜치 연결
2. 환경 변수 입력
3. 실제 OpenAI 호출 검증
4. 데스크톱·모바일 화면 검수
5. 정상·빈 입력·API 오류 테스트
6. 제출용 스크린샷과 AI 코딩 과정 증빙 제작
7. 배포 URL과 실제 실행 결과를 README에 반영
