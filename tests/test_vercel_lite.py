"""오이소창원 Lite의 배포 전 핵심 로직 회귀 테스트."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"모듈을 불러올 수 없습니다: {relative_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


recommend = load_module("vercel_lite_recommend", "api/recommend.py")
chat = load_module("vercel_lite_chat", "api/chat.py")


class RecommendTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "age": 28,
            "move_in_date": "2026-09-20",
            "job_type": "직장인",
            "employed_in_changwon": True,
            "previous_residence_years": 3,
            "vehicle": "없음",
        }

    def test_profile_parsing(self):
        profile = recommend._parse_profile(self.payload)
        self.assertEqual(profile["age"], 28)
        self.assertEqual(profile["move_in_date"], date(2026, 9, 20))
        self.assertTrue(profile["employed_in_changwon"])

    def test_missing_input_is_rejected(self):
        invalid = dict(self.payload)
        invalid["job_type"] = ""
        with self.assertRaises(ValueError):
            recommend._parse_profile(invalid)

    def test_existing_policy_engine_is_reused(self):
        profile = recommend._parse_profile(self.payload)
        results = recommend.match_policies(profile, today=date(2026, 10, 15))
        self.assertEqual(len(results), 24)
        self.assertIn(results[0]["level"], recommend.LEVELS)
        self.assertTrue(any(item["id"] == "P01" for item in results))


class ChatRetrievalTests(unittest.TestCase):
    def test_dialect_retrieval(self):
        question = "욕봤데이는 무슨 뜻이야?"
        results = chat._retrieve_dialects(question, chat._tokens(question))
        self.assertTrue(results)
        self.assertEqual(results[0]["표현"], "욕봤데이")

    def test_complaint_retrieval(self):
        question = "가로등이 고장 났는데 어디에 신고해?"
        results = chat._retrieve_complaints(question, chat._tokens(question))
        self.assertTrue(results)
        self.assertTrue(any("가로등" in item.get("예시", "") for item in results))

    def test_policy_retrieval(self):
        question = "창원 전입 직장인 지원금이 있어?"
        results = chat._retrieve_policies(question, chat._tokens(question))
        self.assertTrue(results)
        self.assertTrue(any("전입" in item.get("사업명", "") for item in results))

    def test_safety_route_does_not_call_ai(self):
        fixed = chat._fixed_safety_answer("죽고 싶다는 생각이 들어")
        self.assertIsNotNone(fixed)
        answer, sources = fixed
        self.assertIn("109", answer)
        self.assertTrue(sources)


if __name__ == "__main__":
    unittest.main()
