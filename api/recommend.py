"""Vercel Python Function: 사용자 조건을 정책 DB와 비교하고 AI 요약을 반환한다."""

from __future__ import annotations

import json
import os
import sys
from datetime import date
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
DATA_FILE = ROOT / "data" / "policies_mvp.json"

# 기존 오이소창원의 검증된 규칙 판정 모듈을 그대로 재사용한다.
sys.path.insert(0, str(SRC_DIR))
from policy_matcher import LEVELS, match_policies  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _ai_provider import generate_text  # noqa: E402

MAX_BODY_BYTES = 12_000
ALLOWED_JOB_TYPES = {"직장인", "구직자", "학생", "자영업", "기타"}
ALLOWED_VEHICLE_VALUES = {"있음", "없음"}


def _json_default(value: Any) -> str:
    if isinstance(value, (date, Path)):
        return value.isoformat() if isinstance(value, date) else str(value)
    return str(value)


def _policy_version() -> str | None:
    try:
        payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return payload.get("checked_at")
    except (OSError, json.JSONDecodeError):
        return None


def _parse_profile(payload: dict[str, Any]) -> dict[str, Any]:
    required = (
        "age",
        "move_in_date",
        "job_type",
        "employed_in_changwon",
        "previous_residence_years",
        "vehicle",
    )
    missing = [field for field in required if field not in payload or payload[field] in (None, "")]
    if missing:
        raise ValueError("필수값이 누락되었습니다: " + ", ".join(missing))

    try:
        age = int(payload["age"])
    except (TypeError, ValueError) as exc:
        raise ValueError("만 나이는 숫자로 입력해 주세요.") from exc
    if age < 18 or age > 100:
        raise ValueError("만 나이는 18세부터 100세 사이로 입력해 주세요.")

    try:
        move_in_date = date.fromisoformat(str(payload["move_in_date"]))
    except ValueError as exc:
        raise ValueError("전입일 형식이 올바르지 않습니다.") from exc

    job_type = str(payload["job_type"]).strip()
    if job_type not in ALLOWED_JOB_TYPES:
        raise ValueError("현재 하는 일의 선택값이 올바르지 않습니다.")

    employed = payload["employed_in_changwon"]
    if not isinstance(employed, bool):
        raise ValueError("창원 사업장 재직 여부를 선택해 주세요.")

    try:
        previous_residence_years = float(payload["previous_residence_years"])
    except (TypeError, ValueError) as exc:
        raise ValueError("전입 전 거주 기간을 선택해 주세요.") from exc
    if previous_residence_years < 0 or previous_residence_years > 100:
        raise ValueError("전입 전 거주 기간의 값이 올바르지 않습니다.")

    vehicle = str(payload["vehicle"]).strip()
    if vehicle not in ALLOWED_VEHICLE_VALUES:
        raise ValueError("차량 보유 여부를 선택해 주세요.")

    return {
        "age": age,
        "move_in_date": move_in_date,
        "job_type": job_type,
        "employed_in_changwon": employed,
        "previous_residence_years": previous_residence_years,
        "vehicle": vehicle,
    }


def _compact_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """브라우저와 AI에 필요한 필드만 반환해 응답 크기와 과다 노출을 줄인다."""
    allowed_fields = (
        "id",
        "name",
        "category",
        "level",
        "message",
        "reasons",
        "support",
        "how_to_apply",
        "status",
        "schedule",
        "link",
        "checked",
        "core",
        "priority",
        "eligible_date",
    )
    return [{key: result.get(key) for key in allowed_fields} for result in results]


def _build_ai_summary(profile: dict[str, Any], results: list[dict[str, Any]]) -> dict[str, Any]:
    configured = any(
        (os.getenv("GEMINI_API_KEY"), os.getenv("OPENAI_API_KEY"), os.getenv("CODEX_API_KEY"))
    )
    if not configured:
        return {
  "available": False,
  "summary": "AI 환경 변수가 아직 설정되지 않아 규칙 기반 판정 결과만 표시합니다.",
  "message": "AI API 키 미설정",
        }

    candidates = [result for result in results if result.get("level") != "해당 없음"][:7]
    ai_context = [
        {
  "정책명": item.get("name"),
  "판정": item.get("level"),
  "이유": item.get("reasons"),
  "지원내용": item.get("support"),
  "일정": item.get("schedule"),
  "모집상태": item.get("status"),
        }
        for item in candidates
    ]
    profile_for_ai = {
        "나이": profile["age"],
        "전입일": profile["move_in_date"].isoformat(),
        "하는 일": profile["job_type"],
        "창원 사업장 재직": profile["employed_in_changwon"],
        "전입 전 타지역 거주기간": profile["previous_residence_years"],
        "차량": profile["vehicle"],
    }

    instructions = """
당신은 '오이소창원'의 창원 정착 코디네이터다.
아래 규칙 기반 판정 결과만 사용해 한국어로 4~6문장의 짧은 정착 브리핑을 작성한다.
- 정책 자격을 확정하거나 '무조건 받을 수 있다'고 말하지 않는다.
- '해당 가능', '조건부 해당 가능', '직접 확인'이라는 판정 표현을 유지한다.
- 우선 확인할 정책 2~3개와 다음 행동 또는 확인 시점을 구체적으로 말한다.
- 입력·판정 자료에 없는 조건, 금액, 날짜, 연락처를 만들어내지 않는다.
- 마지막 문장은 '최종 자격과 최신 모집 일정은 공식 기관에서 다시 확인해 주세요.'로 끝낸다.
""".strip()

    try:
        summary = generate_text(
  instructions=instructions,
  input_text=json.dumps(
      {"사용자 조건": profile_for_ai, "규칙 기반 판정": ai_context},
      ensure_ascii=False,
      default=_json_default,
  ),
  max_output_tokens=550,
        )
        return {"available": True, "summary": summary, "message": "정상 생성"}
    except Exception as exc:
        print(f"[recommend] AI summary failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return {
  "available": False,
  "summary": "정책 판정은 완료했지만 AI 요약을 불러오지 못했습니다. 아래 구조화된 결과를 확인해 주세요.",
  "message": "AI API 오류",
        }

class handler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=_json_default).encode("utf-8")
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
        self._send_json(
            200,
            {
                "ok": True,
                "endpoint": "recommend",
                "message": "POST 요청으로 사용자 조건을 보내 주세요.",
                "data_checked_at": _policy_version(),
            },
        )

    def do_POST(self) -> None:  # noqa: N802
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0:
                self._send_json(400, {"message": "입력값이 비어 있습니다."})
                return
            if content_length > MAX_BODY_BYTES:
                self._send_json(413, {"message": "입력값이 너무 큽니다."})
                return

            raw_body = self.rfile.read(content_length)
            try:
                payload = json.loads(raw_body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._send_json(400, {"message": "요청 형식이 올바르지 않습니다."})
                return
            if not isinstance(payload, dict):
                self._send_json(400, {"message": "요청 본문은 객체 형식이어야 합니다."})
                return

            try:
                profile = _parse_profile(payload)
            except ValueError as exc:
                self._send_json(400, {"message": str(exc)})
                return

            results = _compact_results(match_policies(profile))
            counts = {level: sum(item["level"] == level for item in results) for level in LEVELS}
            ai = _build_ai_summary(profile, results)

            self._send_json(
                200,
                {
                    "ok": True,
                    "counts": counts,
                    "results": results,
                    "ai": ai,
                    "data_checked_at": _policy_version(),
                    "disclaimer": "참고용 판정이며 최종 자격과 최신 일정은 담당 기관 확인이 필요합니다.",
                },
            )
        except Exception as exc:
            print(f"[recommend] unexpected error: {type(exc).__name__}: {exc}", file=sys.stderr)
            self._send_json(500, {"message": "서버에서 결과를 만들지 못했습니다. 잠시 후 다시 시도해 주세요."})
