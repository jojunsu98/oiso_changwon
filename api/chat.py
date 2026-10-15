"""Vercel Python Function: 검증된 정책·생활·민원·지역말 자료를 검색해 AI 답변을 만든다."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import date
from functools import lru_cache
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
MAX_BODY_BYTES = 20_000
MAX_MESSAGE_LENGTH = 500

DATA_FILES = {
    "policies": "policies_mvp.json",
    "complaints": "complaint_channels.json",
    "dialects": "dialects_core30.json",
    "activities": "activities_mvp.json",
}

STOPWORDS = {
    "창원", "창원시", "알려줘", "궁금해", "어떻게", "어디", "무슨", "있어", "있나요",
    "하는", "대한", "관련", "그냥", "제가", "나는", "저는", "거야", "인가요", "해줘",
}

CRISIS_PATTERNS = ("죽고 싶", "자살", "자해", "목숨을", "살기 싫", "사라지고 싶")
EMERGENCY_PATTERNS = ("화재", "불이 났", "사고 났", "위협받", "폭행당", "응급", "119", "112")


@lru_cache(maxsize=None)
def _load_dataset(name: str) -> dict[str, Any]:
    path = DATA_DIR / DATA_FILES[name]
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().lower()


def _tokens(question: str) -> set[str]:
    values = re.findall(r"[가-힣A-Za-z0-9]{2,}", question.lower())
    return {value for value in values if value not in STOPWORDS}


def _safe_url(value: Any) -> str | None:
    if not value:
        return None
    match = re.search(r"https://[^\s;)]+", str(value))
    return match.group(0) if match else None


def _item_text(item: dict[str, Any], fields: tuple[str, ...]) -> str:
    return " ".join(_normalize(item.get(field)) for field in fields)


def _score(tokens: set[str], title: str, body: str, phrase: str) -> int:
    score = 0
    if phrase and phrase in title:
        score += 10
    for token in tokens:
        if token in title:
            score += 5
        elif token in body:
            score += 2
    return score


def _retrieve_policies(question: str, tokens: set[str], limit: int = 4) -> list[dict[str, Any]]:
    dataset = _load_dataset("policies")
    intent_boost = any(word in question for word in ("지원", "혜택", "정책", "월세", "취업", "전입", "교통", "청년", "주거"))
    ranked = []
    for item in dataset.get("items", []):
        title = _normalize(item.get("사업명"))
        body = _item_text(
            item,
            (
                "분야", "대상 요약", "거주 요건", "취업 상태", "기타 조건", "지원 내용",
                "상태(9/30 기준)", "신청 방법", "신청 기간(2026)", "MVP 선정 이유",
            ),
        )
        score = _score(tokens, title, body, _normalize(question))
        if intent_boost and any(token in (title + " " + body) for token in tokens):
            score += 2
        if score > 0:
            ranked.append((score, item))

    ranked.sort(key=lambda pair: (-pair[0], pair[1].get("ID", "")))
    return [item for _, item in ranked[:limit]]


def _retrieve_complaints(question: str, tokens: set[str], limit: int = 3) -> list[dict[str, Any]]:
    dataset = _load_dataset("complaints")
    intent_boost = any(word in question for word in ("민원", "불편", "고장", "신고", "접수", "상담", "외로", "우울"))
    ranked = []
    for item in dataset.get("items", []):
        title = _normalize(item.get("단계"))
        body = _item_text(item, ("예시", "안내", "연락처"))
        score = _score(tokens, title, body, _normalize(question))
        if intent_boost and score:
            score += 3
        if score > 0:
            ranked.append((score, item))
    ranked.sort(key=lambda pair: -pair[0])
    return [item for _, item in ranked[:limit]]


def _retrieve_dialects(question: str, tokens: set[str], limit: int = 3) -> list[dict[str, Any]]:
    dataset = _load_dataset("dialects")
    compact_question = re.sub(r"\s+", "", question.lower())
    intent_boost = any(word in question for word in ("사투리", "지역말", "뜻", "무슨 말", "경상도"))
    ranked = []
    for item in dataset.get("items", []):
        expression = _normalize(item.get("표현"))
        compact_expression = re.sub(r"\s+", "", expression)
        body = _item_text(item, ("표준어 뜻", "사용 상황", "DB 표제어"))
        score = _score(tokens, expression, body, _normalize(question))
        if compact_expression and compact_expression in compact_question:
            score += 14
        if intent_boost and score:
            score += 3
        if score > 0:
            ranked.append((score, item))
    ranked.sort(key=lambda pair: -pair[0])
    return [item for _, item in ranked[:limit]]


def _activity_is_current(item: dict[str, Any]) -> bool:
    end = item.get("종료일")
    if not end:
        return True
    try:
        return date.fromisoformat(str(end)) >= date.today()
    except ValueError:
        return True


def _retrieve_activities(question: str, tokens: set[str], limit: int = 4) -> list[dict[str, Any]]:
    dataset = _load_dataset("activities")
    intent_boost = any(
        word in question
        for word in ("갈 곳", "뭐 하지", "놀", "축제", "행사", "문화", "운동", "전시", "주말", "데이트", "맛집", "카페")
    )
    ranked = []
    for item in dataset.get("items", []):
        if not _activity_is_current(item):
            continue
        title = _normalize(item.get("이름"))
        body = _item_text(
            item,
            (
                "유형(행사/모임/기관/공간)", "생활권(구)", "관심사 태그", "대상", "참여 방법",
                "일정·운영시간", "대분류", "MVP 그룹", "실내·실외", "메모",
            ),
        )
        score = _score(tokens, title, body, _normalize(question))
        if intent_boost:
            score += 2
        if score > 0:
            ranked.append((score, item))
    ranked.sort(key=lambda pair: (-pair[0], pair[1].get("ID", "")))
    return [item for _, item in ranked[:limit]]


def _compact_policy(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "자료유형": "정책",
        "정책명": item.get("사업명"),
        "분야": item.get("분야"),
        "대상": item.get("대상 요약"),
        "지원내용": item.get("지원 내용"),
        "신청기간": item.get("신청 기간(2026)"),
        "모집상태": item.get("상태(9/30 기준)"),
        "신청방법": item.get("신청 방법"),
        "추가조건": item.get("기타 조건"),
        "최종확인일": item.get("최종 확인일"),
        "공식확인": item.get("link") or item.get("공식 URL (원문 직접 확인)"),
    }


def _compact_complaint(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "자료유형": "불편사항 접수",
        "단계": item.get("단계"),
        "예시": item.get("예시"),
        "안내": item.get("안내"),
        "연락처": item.get("연락처"),
    }


def _compact_dialect(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "자료유형": "지역말",
        "표현": item.get("표현"),
        "표준어뜻": item.get("표준어 뜻"),
        "사용상황": item.get("사용 상황"),
        "검수상태": item.get("뉘앙스"),
        "출처": item.get("출처"),
    }


def _compact_activity(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "자료유형": "생활·활동",
        "이름": item.get("이름"),
        "지역": item.get("생활권(구)"),
        "태그": item.get("관심사 태그"),
        "대상": item.get("대상"),
        "참여방법": item.get("참여 방법"),
        "일정운영시간": item.get("일정·운영시간"),
        "연락처": item.get("연락처"),
        "최종확인일": item.get("최종 확인일"),
        "공식확인": item.get("공식 URL"),
    }


def _source_cards(
    policies: list[dict[str, Any]],
    complaints: list[dict[str, Any]],
    dialects: list[dict[str, Any]],
    activities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    for item in policies:
        sources.append(
            {
                "type": "정책",
                "title": item.get("사업명", "정책 자료"),
                "url": _safe_url(item.get("link") or item.get("공식 URL (원문 직접 확인)")),
                "checked": item.get("최종 확인일"),
            }
        )
    for item in complaints:
        sources.append({"type": "민원", "title": f"{item.get('단계', '')} 상황 안내", "url": None})
    for item in dialects:
        sources.append({"type": "지역말", "title": item.get("표현", "지역말 자료"), "url": _safe_url(item.get("출처"))})
    for item in activities:
        sources.append(
            {
                "type": "생활",
                "title": item.get("이름", "생활 정보"),
                "url": _safe_url(item.get("공식 URL")),
                "checked": item.get("최종 확인일"),
            }
        )

    unique: list[dict[str, Any]] = []
    seen = set()
    for source in sources:
        key = (source.get("type"), source.get("title"), source.get("url"))
        if key not in seen:
            seen.add(key)
            unique.append(source)
    return unique[:7]


def _fixed_safety_answer(message: str) -> tuple[str, list[dict[str, Any]]] | None:
    normalized = _normalize(message)
    if any(pattern in normalized for pattern in CRISIS_PATTERNS):
        answer = (
            "지금은 AI 안내보다 사람과 즉시 연결하는 것이 우선입니다. "
            "자살예방상담전화 109는 24시간 이용할 수 있고, 당장 위험하거나 다친 사람이 있으면 119에 연락하세요. "
            "가능하면 혼자 있지 말고 가까운 사람에게 현재 상황을 바로 알려 주세요."
        )
        return answer, [{"type": "위기", "title": "자살예방상담전화 109·119", "url": "https://www.129.go.kr/109"}]
    if any(pattern in normalized for pattern in EMERGENCY_PATTERNS):
        answer = "화재·사고·폭력·즉각적인 위협 상황이면 AI 답변을 기다리지 말고 경찰 112 또는 소방·구급 119에 바로 신고하세요."
        return answer, [{"type": "긴급", "title": "경찰 112·소방/구급 119", "url": None}]
    return None


def _profile_context(profile: Any) -> dict[str, Any] | None:
    if not isinstance(profile, dict):
        return None
    allowed = ("age", "move_in_date", "job_type", "employed_in_changwon", "previous_residence_years", "vehicle")
    return {key: profile.get(key) for key in allowed if key in profile}


def _generate_answer(message: str, context: dict[str, Any], profile: dict[str, Any] | None) -> str:
    api_key = (os.getenv("OPENAI_API_KEY") or os.getenv("CODEX_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다.")

    instructions = """
당신은 '오이소창원'의 창원 정착 코디네이터다. 제공된 검증 자료만 사용해 한국어로 답한다.

필수 규칙:
1. 자료에 없는 사실·금액·날짜·연락처·자격 조건을 만들지 않는다.
2. 정책은 '해당 가능성이 있다', '조건 확인이 필요하다'처럼 설명하고 최종 자격을 확정하지 않는다.
3. 모집 종료·확인 필요 상태를 현재 신청 가능하다고 바꾸지 않는다.
4. 지역말 자료의 검수 상태가 '사람 검수 필요'라면 그 한계를 짧게 밝힌다.
5. 행사·운영시간은 자료의 최종 확인일 기준이며 최신 여부를 공식 경로에서 재확인하라고 말한다.
6. 질문과 관련된 핵심 답을 먼저 말하고, 다음 행동을 1~3개로 정리한다.
7. 자료가 충분하지 않으면 추측하지 말고 '현재 확인된 자료만으로는 답하기 어렵다'고 말한다.
8. 개인정보를 추가로 요구하지 않는다.
9. 답변은 보통 4~8문장으로 간결하게 작성한다.
""".strip()

    from openai import OpenAI

    client = OpenAI(api_key=api_key, timeout=28.0, max_retries=1)
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        instructions=instructions,
        input=json.dumps(
            {
                "현재 날짜": date.today().isoformat(),
                "사용자 질문": message,
                "선택 입력 조건": profile,
                "검색된 검증 자료": context,
            },
            ensure_ascii=False,
        ),
        max_output_tokens=750,
    )
    answer = (response.output_text or "").strip()
    if not answer:
        raise RuntimeError("AI 응답 본문이 비어 있습니다.")
    return answer


class handler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Allow", "POST, OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        self._send_json(200, {"ok": True, "endpoint": "chat", "message": "POST 요청으로 질문을 보내 주세요."})

    def do_POST(self) -> None:  # noqa: N802
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0:
                self._send_json(400, {"message": "질문을 입력해 주세요."})
                return
            if content_length > MAX_BODY_BYTES:
                self._send_json(413, {"message": "입력값이 너무 큽니다."})
                return

            try:
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._send_json(400, {"message": "요청 형식이 올바르지 않습니다."})
                return
            if not isinstance(payload, dict):
                self._send_json(400, {"message": "요청 본문은 객체 형식이어야 합니다."})
                return

            message = str(payload.get("message", "")).strip()
            if not message:
                self._send_json(400, {"message": "질문을 입력해 주세요."})
                return
            if len(message) > MAX_MESSAGE_LENGTH:
                self._send_json(400, {"message": f"질문은 {MAX_MESSAGE_LENGTH}자 이내로 입력해 주세요."})
                return

            safety = _fixed_safety_answer(message)
            if safety:
                answer, sources = safety
                self._send_json(200, {"ok": True, "answer": answer, "sources": sources, "mode": "safety"})
                return

            tokens = _tokens(message)
            policies = _retrieve_policies(message, tokens)
            complaints = _retrieve_complaints(message, tokens)
            dialects = _retrieve_dialects(message, tokens)
            activities = _retrieve_activities(message, tokens)

            context = {
                "정책": [_compact_policy(item) for item in policies],
                "불편사항": [_compact_complaint(item) for item in complaints],
                "지역말": [_compact_dialect(item) for item in dialects],
                "생활·활동": [_compact_activity(item) for item in activities],
                "데이터 확인일": {
                    name: _load_dataset(name).get("checked_at")
                    for name in DATA_FILES
                },
            }
            sources = _source_cards(policies, complaints, dialects, activities)

            if not any((policies, complaints, dialects, activities)):
                self._send_json(
                    200,
                    {
                        "ok": True,
                        "answer": (
                            "현재 오이소창원이 확인한 정책·생활·민원·지역말 자료에서는 질문과 직접 연결되는 근거를 찾지 못했습니다. "
                            "창원 청년 정책, 전입 지원, 생활 불편 접수, 지역 활동 또는 경상도 표현처럼 범위를 조금 더 구체적으로 적어 주세요."
                        ),
                        "sources": [],
                        "mode": "no-context",
                    },
                )
                return

            try:
                answer = _generate_answer(message, context, _profile_context(payload.get("profile")))
            except RuntimeError as exc:
                if "OPENAI_API_KEY" in str(exc):
                    self._send_json(503, {"message": "AI 기능을 사용하려면 배포 환경에 OPENAI_API_KEY를 설정해야 합니다."})
                    return
                raise
            except Exception as exc:
                print(f"[chat] OpenAI call failed: {type(exc).__name__}: {exc}", file=sys.stderr)
                self._send_json(502, {"message": "AI 응답을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요."})
                return

            self._send_json(200, {"ok": True, "answer": answer, "sources": sources, "mode": "grounded-ai"})
        except Exception as exc:
            print(f"[chat] unexpected error: {type(exc).__name__}: {exc}", file=sys.stderr)
            self._send_json(500, {"message": "서버에서 답변을 만들지 못했습니다. 잠시 후 다시 시도해 주세요."})
