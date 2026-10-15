<img src="assets/logo_wide.png" width="180" align="right" alt="오이소창원 로고">

# 오이소창원 Lite

> 창원 전입 청년의 첫 180일을 돕는 AI 정착 코디네이터  
> 코디세이 「AI 웹 개발: 내 아이디어를 현실로, AI 웹 서비스 빌딩」 개인 미션

## 바로가기

- **배포 서비스:** https://oiso-changwon-lite.vercel.app
- **과제용 브랜치:** `codyssey-vercel-lite`
- **제출 패키지:** [submission/codyssey-ai-web-service](https://github.com/jojunsu98/oiso_changwon/tree/codyssey-vercel-lite/submission/codyssey-ai-web-service)
- **Google Drive 제출 폴더:** https://drive.google.com/drive/folders/1fvFPov8IEI4ycado1T78TsZJ3_fvU7w5

## 프로젝트 상태

| 항목 | 상태 |
|---|---|
| HTML/CSS/JavaScript 프론트엔드 | 완료 |
| Vercel Python Functions | 완료 |
| 정책 24건 규칙 판정 | 완료 |
| AI 코디네이터 | 완료 |
| 모바일 반응형 | 완료 |
| Vercel Production 배포 | 완료 |
| 실제 API 테스트 | 완료 |
| 데스크톱·모바일·AI·오류 증빙 | 완료 |
| README·기획서·발표자료·제출 패키지 | 완료 |

## 1. 서비스 소개

**오이소창원 Lite**는 창원으로 전입했거나 전입을 준비하는 청년이 흩어진 정책·생활 정보를 한곳에서 확인하도록 돕는 웹서비스다.

- **타겟:** 창원 전입·전입 예정 청년
- **핵심 흐름:** 내 조건 입력 → 정책 판정 → 일정·다음 행동 → AI 안내
- **서비스 원칙:** 정책 자격은 규칙으로 비교하고, AI는 검증 자료 범위 안에서 설명한다.
- **슬로건:** 창원에서 너의 내일을 응원해!

## 2. 기존 오이소창원과의 관계

기존 팀 프로젝트 「오이소창원 — AI 기반 창원 정착 지원 Agent」의 목적·타겟·브랜드·검증 데이터·정보 원칙을 유지하고, 이번 개인 미션에서 기술 구조를 다시 구현했다.

| 구분 | 기존 서비스 | Lite 버전 |
|---|---|---|
| 프론트엔드 | Streamlit | 순수 HTML/CSS/JavaScript |
| 백엔드 | Streamlit 내부 Python | Vercel Python Functions |
| 배포 | Streamlit Community Cloud | Vercel |
| AI 호출 | 기존 Agent 흐름 | Gemini 우선, OpenAI 대체 호출 |
| 핵심 콘셉트 | 창원 전입 청년 정착 지원 | 동일 |

Lite는 콘셉트를 바꾼 서비스가 아니라, 코디세이 과제 구조에 맞게 구현 범위를 경량화한 버전이다.

## 3. 주요 기능

### 맞춤 혜택 판정

사용자가 입력한 조건을 정책 24건과 비교한다.

- 만 나이
- 창원 전입일
- 현재 하는 일
- 창원 사업장 재직 여부
- 전입 전 타지역 거주 기간
- 차량 보유 여부

결과는 다음 네 단계로 구분한다.

- `해당 가능`
- `조건부 해당 가능`
- `직접 확인`
- `해당 없음`

### AI 정착 브리핑

규칙 판정 결과 중 우선 확인할 정책과 다음 행동을 AI가 짧게 설명한다. 최종 자격을 AI가 단정하지 않는다.

### AI 코디네이터

정책·민원·지역말·생활 활동 자료에서 관련 내용을 검색한 뒤, 검증된 자료 범위 안에서 답변한다.

### 안전·오류 처리

- 빈 입력 및 500자 초과 질문 차단
- 자료가 없으면 추측 대신 질문 구체화 안내
- API 장애 시 사용자 안내
- 화재·사고·위기 표현은 일반 AI 답변보다 109·112·119 경로를 우선 안내

## 4. 페이지·섹션

한 개의 반응형 페이지에 6개 메뉴·섹션을 구성했다.

1. 홈
2. 서비스
3. 맞춤 혜택
4. 생활 안내
5. AI 코디네이터
6. 안내

## 5. 기술 구조

```text
사용자 입력
  ↓
HTML 폼·텍스트 입력
  ↓
JavaScript 검증 및 fetch 요청
  ↓
/api/recommend 또는 /api/chat
  ↓
Vercel Python Function
  ├─ 정책 규칙 판정
  ├─ 검증 JSON 검색
  └─ Gemini 우선 / OpenAI 대체 호출
  ↓
JSON 응답
  ↓
JavaScript가 결과를 화면에 표시
```

## 6. 기술 스택

| 영역 | 기술 |
|---|---|
| 프론트엔드 | HTML5, CSS3, Vanilla JavaScript |
| 백엔드 | Python 3, Vercel Python Functions |
| AI | Gemini API 우선, OpenAI Responses API 대체 |
| 데이터 | 정책·민원·지역말·생활 활동 JSON |
| 배포 | Vercel |
| 형상 관리 | GitHub, GitHub Actions |

## 7. 프로젝트 구조

```text
.
├── index.html
├── css/
│   └── style.css
├── js/
│   └── app.js
├── api/
│   ├── _ai_provider.py
│   ├── recommend.py
│   └── chat.py
├── data/
├── src/
├── assets/
├── tests/
├── docs/
│   └── codyssey-service-plan.md
├── submission/
│   └── codyssey-ai-web-service/
├── requirements.txt
├── vercel.json
└── README.md
```

## 8. 환경 변수

실제 키는 코드·README·스크린샷에 넣지 않는다.

| 변수명 | 용도 | 필수 여부 |
|---|---|---|
| `GEMINI_API_KEY` | 기본 AI 응답 생성 | 기본 제공자 사용 시 필수 |
| `GEMINI_MODEL` | Gemini 모델 지정 | 선택 |
| `OPENAI_API_KEY` | Gemini 실패 시 대체 호출 | 선택 |
| `OPENAI_MODEL` | OpenAI 모델 지정 | 선택 |

Vercel에서 `Settings → Environment Variables`에 등록하고 Production·Preview·Development에 적용한다.

## 9. 로컬 실행

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
npm install -g vercel
vercel dev
```

로컬 환경 변수는 `.env.local`에 저장하고 GitHub에 커밋하지 않는다.

## 10. 배포 방법

1. Vercel에서 `Add New → Project`를 누른다.
2. `jojunsu98/oiso_changwon` 저장소를 Import한다.
3. Framework Preset은 `Other`로 설정한다.
4. Root Directory는 `.`으로 둔다.
5. 배포 브랜치는 `codyssey-vercel-lite`로 지정한다.
6. 환경 변수를 등록한다.
7. Deploy 후 `/api/chat`, `/api/recommend`, 전체 화면을 테스트한다.

## 11. 실제 테스트 결과

검증일: **2026-10-15**

- 운영 URL 응답: 정상
- 자동·실행 테스트: **17개 중 17개 통과**
- 맞춤 혜택 API 반복 테스트: **3회 연속 성공**
- 정책 판정 결과 수: **24건**
- 기준 입력 판정: 해당 가능 4 / 조건부 해당 가능 13 / 직접 확인 0 / 해당 없음 7
- AI 채팅: 정책·월세·지역말·활동 질문 정상 응답
- 실패 처리: 빈 입력·500자 초과·필수값 누락·나이 범위 오류 정상 차단
- 긴급 경로: 화재 질문에 112·119 안내
- 테스트 응답 내 비밀값 노출 검사: **0건**

자세한 결과는 `submission/codyssey-ai-web-service/03-test-report.md`에서 확인한다.

## 12. 주요 오류와 개선

| 문제 | 원인 | 개선 |
|---|---|---|
| 기존 Streamlit 앱이 과제 구조와 불일치 | 바닐라 프론트·Vercel API 요건 미충족 | 동일 콘셉트로 Lite 버전 재구현 |
| 첫 배포에서 화면 미표시·404 | 잘못된 프리셋 및 `main` 브랜치 배포 | Framework `Other`, 과제 브랜치 Production 지정 |
| API 키를 넣었는데 인식되지 않음 | 변수명 불일치 및 Development에만 적용 | 이름 정리, 세 환경 전체 적용 |
| Gemini 호출 헤더 오류 | 여러 환경 변수 문장이 한 값에 붙여넣어짐 | 비밀값 정규화·한 줄 추출 로직 추가 |
| OpenAI 호출 실패 | API 사용 한도·크레딧 오류 | Gemini 우선 호출 + OpenAI 대체 구조 |
| 오류 원인 파악 어려움 | 사용자 메시지가 지나치게 일반적 | 오류 유형 분류와 서버 로그 분리 |
| 진단 중 비밀값 노출 위험 | 임시 상세 진단 응답 | 진단 제거, 키 재발급 권고, 누출 검사 추가 |

자세한 경과는 `submission/codyssey-ai-web-service/02-error-improvement-report.md`에서 확인한다.

## 13. 보안·개인정보

- API 키는 Vercel 서버 환경 변수에서만 관리한다.
- 브라우저에는 API 키를 전달하지 않는다.
- 실제 비밀값 파일은 `.gitignore`로 제외한다.
- 실명·전화번호·주민등록번호를 입력받지 않는다.
- 입력 길이와 요청 본문 크기를 제한한다.
- 긴급 상황은 AI가 임의 판단하지 않는다.
- 키 노출이 의심되면 파일 삭제로 끝내지 않고 키를 폐기·재발급한다.

## 14. 현재 한계와 개선 방향

- 정책 데이터 확인 기준일은 2026-10-01이며 정기 갱신이 필요하다.
- 실제 지원 자격과 신청 가능 여부는 담당 기관에서 다시 확인해야 한다.
- Lite 버전은 로그인·영구 저장·이메일 알림·캘린더 파일 기능을 제외했다.
- 외부 AI 제공자의 쿼터·요금·장애에 영향을 받을 수 있다.
- 향후 사용자 테스트를 통해 질문 검색 정확도와 모바일 UX를 추가 개선할 수 있다.

## 15. 출처와 기여 범위

기존 오이소창원은 **조준수·이혜경·이미영**이 참여한 팀 프로젝트다. Lite 버전은 팀 프로젝트 전체를 개인 단독 제작물로 표현하지 않는다.

> 본 서비스는 기존 팀 프로젝트 「오이소창원」의 공동 기획·검증 데이터·브랜드 자산을 기반으로 하며, 조준수가 코디세이 개인 미션에서 순수 HTML/CSS/JavaScript 프론트엔드와 Vercel Python Functions 구조로 재구현한 학습용 Lite 버전이다.
