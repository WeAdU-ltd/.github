"""Tests d'intégration FastAPI — POST /ai/run (WEA-171)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

from fastapi.testclient import TestClient

_ORCH = Path(__file__).resolve().parents[1]
if str(_ORCH) not in sys.path:
    sys.path.insert(0, str(_ORCH))

import main  # noqa: E402


def _valid_uuid() -> str:
    return "550e8400-e29b-41d4-a716-446655440000"


def _minimal_body(**overrides: object) -> dict:
    b: dict = {
        "task_id": _valid_uuid(),
        "task_type": "analysis",
        "complexity": "low",
        "privacy_level": "local_only",
        "preferred_model": "local",
        "input": {"prompt": "hello"},
    }
    b.update(overrides)
    return b


class TestAiRunIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(main.app)

    def test_post_ai_run_success_calls_lm_adapter(self) -> None:
        fake = {
            "task_id": _valid_uuid(),
            "status": "success",
            "provider_used": "lm_studio",
            "model_used": "gemma-4",
            "output": {"text": "ok"},
            "usage": {
                "input_tokens": 1,
                "output_tokens": 1,
                "estimated_cost_usd": 0.0,
                "duration_ms": 5,
                "estimated_cloud_equivalent_cost_usd": 0.1,
                "estimated_savings_usd": 0.1,
            },
            "routing_reason": "test",
            "error": None,
        }
        with mock.patch("main.lm_run", return_value=fake) as m:
            r = self.client.post("/ai/run", json=_minimal_body())
        self.assertEqual(r.status_code, 200, r.text)
        m.assert_called_once()
        args, _ = m.call_args
        self.assertEqual(args[0]["privacy_level"], "local_only")
        self.assertEqual(args[0]["preferred_model"], "local")
        data = r.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["output"]["text"], "ok")

    def test_local_only_privacy_violation_returns_400(self) -> None:
        with mock.patch("main.lm_run") as m:
            r = self.client.post(
                "/ai/run",
                json=_minimal_body(privacy_level="local_only", preferred_model="gemini_flash"),
            )
        self.assertEqual(r.status_code, 400)
        m.assert_not_called()
        data = r.json()
        self.assertEqual(data["error"]["code"], "privacy_violation")
        self.assertEqual(data["provider_used"], "none")

    def test_standard_medium_auto_routes_gemini_returns_503(self) -> None:
        with mock.patch("main.lm_run") as m:
            r = self.client.post(
                "/ai/run",
                json=_minimal_body(
                    privacy_level="standard",
                    complexity="medium",
                    preferred_model="auto",
                    max_cost_usd=1.0,
                ),
            )
        self.assertEqual(r.status_code, 503)
        m.assert_not_called()
        data = r.json()
        self.assertEqual(data["error"]["code"], "adapter_not_implemented")

    def test_cost_cap_exceeded_returns_400_before_adapter(self) -> None:
        with mock.patch("main.lm_run") as m:
            r = self.client.post(
                "/ai/run",
                json=_minimal_body(
                    privacy_level="standard",
                    complexity="medium",
                    preferred_model="auto",
                    max_cost_usd=0.0,
                ),
            )
        self.assertEqual(r.status_code, 400)
        m.assert_not_called()
        data = r.json()
        self.assertEqual(data["error"]["code"], "cost_cap_exceeded")
        self.assertEqual(data["routing_reason"], "cost_cap_exceeded_preflight")

    def test_local_only_zero_max_cost_still_hits_lm_adapter(self) -> None:
        fake = {
            "task_id": _valid_uuid(),
            "status": "success",
            "provider_used": "lm_studio",
            "model_used": "gemma-4",
            "output": {"text": "ok"},
            "usage": {
                "input_tokens": 1,
                "output_tokens": 1,
                "estimated_cost_usd": 0.0,
                "duration_ms": 5,
                "estimated_cloud_equivalent_cost_usd": None,
                "estimated_savings_usd": None,
            },
            "routing_reason": "test",
            "error": None,
        }
        with mock.patch("main.lm_run", return_value=fake) as m:
            r = self.client.post(
                "/ai/run",
                json=_minimal_body(
                    privacy_level="local_only",
                    max_cost_usd=0.0,
                ),
            )
        self.assertEqual(r.status_code, 200, r.text)
        m.assert_called_once()

    def test_adapter_error_passed_through_with_http_mapping(self) -> None:
        err_body = {
            "task_id": _valid_uuid(),
            "status": "error",
            "provider_used": "lm_studio",
            "model_used": "gemma-4",
            "output": {},
            "usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "estimated_cost_usd": 0.0,
                "duration_ms": 0,
                "estimated_cloud_equivalent_cost_usd": None,
                "estimated_savings_usd": None,
            },
            "routing_reason": "x",
            "error": {"code": "provider_unavailable", "message": "down", "retryable": True},
        }
        with mock.patch("main.lm_run", return_value=err_body):
            r = self.client.post("/ai/run", json=_minimal_body())
        self.assertEqual(r.status_code, 503)
        self.assertEqual(r.json()["error"]["code"], "provider_unavailable")

    def test_validation_error_returns_422_envelope(self) -> None:
        bad = _minimal_body()
        bad["task_type"] = "invalid_task"
        r = self.client.post("/ai/run", json=bad)
        self.assertEqual(r.status_code, 422)
        data = r.json()
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["error"]["code"], "validation_error")


if __name__ == "__main__":
    unittest.main()
