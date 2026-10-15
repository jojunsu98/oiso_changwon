"""AI text provider helper for Vercel Python Functions.

Gemini is used first when GEMINI_API_KEY exists. OpenAI is used as a fallback.
No secret value is returned to the browser or written to logs.
"""

from __future__ import annotations

import json
import os
from urllib import error, request


class AIProviderError(Exception):
    """Raised when every configured AI provider fails."""


def _gemini_models() -> list[str]:
    configured = os.getenv("GEMINI_MODEL", "").strip()
    candidates = [
        configured,
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash",
        "gemini-2.5-flash",
    ]
    unique: list[str] = []
    for model in candidates:
        if model and model not in unique:
            unique.append(model)
    return unique


def _generate_with_gemini(
    *,
    api_key: str,
    instructions: str,
    input_text: str,
    max_output_tokens: int,
) -> str:
    prompt = f"{instructions}\n\n[사용자 입력]\n{input_text}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": max_output_tokens,
        },
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    failures: list[str] = []

    for model in _gemini_models():
        endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent"
        )
        req = request.Request(
            endpoint,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "x-goog-api-key": api_key,
            },
        )
        try:
            with request.urlopen(req, timeout=18) as response:
                result = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            status = ""
            try:
                error_payload = json.loads(exc.read().decode("utf-8"))
                status = str((error_payload.get("error") or {}).get("status") or "")
            except Exception:
                status = ""
            suffix = f":{status}" if status else ""
            failures.append(f"{model}:HTTP{exc.code}{suffix}")
            continue
        except (error.URLError, TimeoutError, OSError) as exc:
            failures.append(f"{model}:{type(exc).__name__}")
            continue

        candidates = result.get("candidates") or []
        if not candidates:
            failures.append(f"{model}:empty_candidates")
            continue
        parts = ((candidates[0].get("content") or {}).get("parts") or [])
        text = "\n".join(
            str(part.get("text", "")).strip()
            for part in parts
            if isinstance(part, dict) and part.get("text")
        ).strip()
        if text:
            return text
        failures.append(f"{model}:empty_text")

    raise AIProviderError("Gemini 호출 실패: " + ", ".join(failures))


def _generate_with_openai(
    *,
    api_key: str,
    instructions: str,
    input_text: str,
    max_output_tokens: int,
) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=api_key, timeout=18.0, max_retries=0)
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        instructions=instructions,
        input=input_text,
        max_output_tokens=max_output_tokens,
    )
    text = (response.output_text or "").strip()
    if not text:
        raise AIProviderError("OpenAI 응답 본문이 비어 있습니다.")
    return text


def generate_text(
    *,
    instructions: str,
    input_text: str,
    max_output_tokens: int,
) -> str:
    """Generate text with Gemini first and OpenAI as a fallback."""

    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    openai_key = (
        os.getenv("OPENAI_API_KEY")
        or os.getenv("CODEX_API_KEY")
        or ""
    ).strip()
    failures: list[str] = []

    if gemini_key:
        try:
            return _generate_with_gemini(
                api_key=gemini_key,
                instructions=instructions,
                input_text=input_text,
                max_output_tokens=max_output_tokens,
            )
        except Exception as exc:
            failures.append(f"Gemini:{str(exc)}")

    if openai_key:
        try:
            return _generate_with_openai(
                api_key=openai_key,
                instructions=instructions,
                input_text=input_text,
                max_output_tokens=max_output_tokens,
            )
        except Exception as exc:
            failures.append(f"OpenAI:{type(exc).__name__}")

    if not failures:
        raise AIProviderError("사용 가능한 AI API 키가 설정되지 않았습니다.")
    raise AIProviderError("모든 AI 제공자 호출 실패: " + " | ".join(failures))
