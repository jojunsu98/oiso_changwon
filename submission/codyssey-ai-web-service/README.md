# 오이소창원 Lite 제출 패키지

코디세이 「AI 웹 개발: 내 아이디어를 현실로, AI 웹 서비스 빌딩」 개인 미션 제출용 GitHub 패키지다.

## 제출 핵심 링크

- **배포 URL:** https://oiso-changwon-lite.vercel.app
- **GitHub 과제 브랜치:** https://github.com/jojunsu98/oiso_changwon/tree/codyssey-vercel-lite
- **GitHub 제출 패키지:** https://github.com/jojunsu98/oiso_changwon/tree/codyssey-vercel-lite/submission/codyssey-ai-web-service
- **Google Drive 제출 폴더:** https://drive.google.com/drive/folders/1fvFPov8IEI4ycado1T78TsZJ3_fvU7w5

## GitHub 문서 구성

| 파일 | 용도 | 상태 |
|---|---|---|
| [`01-service-plan.md`](./01-service-plan.md) | 서비스 목적·타겟·페이지·AI 입출력·실패 처리 | 완료 |
| [`02-error-improvement-report.md`](./02-error-improvement-report.md) | 배포·브랜치·환경 변수·API 오류와 개선 과정 | 완료 |
| [`03-test-report.md`](./03-test-report.md) | 17개 통합 테스트와 반복 호출 결과 | 완료 |
| [`04-submission-checklist.md`](./04-submission-checklist.md) | 과제 요구사항 누락 여부 점검 | 완료 |
| [`05-presentation-script.md`](./05-presentation-script.md) | 5분 내외 발표 대본 | 완료 |
| [`06-evidence-guide.md`](./06-evidence-guide.md) | 증빙 이미지 설명·보안 확인 | 완료 |
| [`07-presentation-slides.md`](./07-presentation-slides.md) | 10장 발표자료 원고·화면 구성 | 완료 |
| [`evidence/`](./evidence) | 데스크톱·모바일·AI·오류 실행 화면 6장 | 완료 |

## 과제 필수 제출물 대응

| 공식 요구사항 | 제출 위치 |
|---|---|
| 배포된 웹서비스 | Vercel URL |
| GitHub 저장소 | `codyssey-vercel-lite` 브랜치 |
| README.md | 저장소 루트 `README.md` |
| 서비스 기획서 | `01-service-plan.md`, `docs/codyssey-service-plan.md` |
| 데스크톱·모바일·AI 동작 증빙 | `evidence/` |
| AI 코딩 도구 사용·오류 개선 증빙 | `02-error-improvement-report.md`, Git 커밋 이력 |
| 발표자료 | `07-presentation-slides.md` |
| 발표대본 | `05-presentation-script.md` |

## 오류 개선 핵심 요약

1. 기존 Streamlit 구조를 HTML/CSS/JavaScript + Vercel Python Functions로 재구현했다.
2. Vercel의 Python 프리셋과 `main` 브랜치 덮어쓰기로 발생한 404를 해결했다.
3. 환경 변수 이름·적용 범위 불일치와 여러 키가 한 값에 들어간 문제를 수정했다.
4. OpenAI API 사용 한도 문제에 대응해 Gemini 우선·OpenAI 대체 호출 구조를 적용했다.
5. 임시 진단 응답의 비밀값 노출 위험을 제거하고 최종 응답 키 패턴 검사 0건을 확인했다.

## 최종 검증

- 실행 테스트: **17/17 통과**
- 맞춤 혜택 반복 호출: **3/3 성공**
- 정책 판정: **24건 정상**
- AI 채팅: 정책·월세·지역말·생활 활동 질문 정상
- 실패 처리: 빈 입력·500자 초과·필수값 누락·나이 범위 오류 정상
- 긴급 처리: 화재 질문 112·119 안내
- 응답 내 비밀값 노출 검사: **0건**

## 외부 제출용 파일 변환

GitHub 문서가 원본이다. 제출처에서 별도 파일 형식을 요구할 경우 아래처럼 변환한다.

- 서비스 기획서: DOCX 또는 PDF
- 오류 개선·테스트 보고서: DOCX 또는 PDF
- 발표자료: PPTX 또는 PDF
- 전체 제출 패키지: ZIP

실제 API 키는 변환 파일·캡처·README에 포함하지 않는다.

## 기여 범위

기존 오이소창원은 **조준수·이혜경·이미영**이 참여한 팀 프로젝트다. Lite 버전은 기존 공동 기획·브랜드·검증 데이터를 기반으로 하며, 이번 개인 미션의 바닐라 프론트엔드, Vercel Python Functions, AI 제공자 대체 구조, 오류 처리, 배포, 테스트, 문서화는 조준수가 수행했다.
