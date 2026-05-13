"""Tests unitaires mockés pour l'adaptateur Gemini Flash — WEA-173."""

from __future__ import annotations

import json
import os
import sys
import unittest
import urllib.request
from io import BytesIO
from pathlib import Path
from unittest import mock

_ORCH_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ORCH_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from ai_orchestrator.adapter_registry import get_adapter  # noqa: E402
from ai_orchestrator.adapters import gemini_flash as gf  # noqa: E402


def _uuid() -> str:
    return "550e8400-e29b-41d4-a716-446655440000"


def _base_req(**kwargs: object) -> dict:
    r: dict = {
        "task_id": _uuid(),
        "task_type": "analysis",
        "complexity": "medium",
        "privacy_level": "standard",
        "preferred_model": "gemini_flash",
        "input": {"prompt": "Résumé", "context": {"k": 1}, "data": []},
        "options": {"temperature": 0.2, "max_tokens": 500, "timeout_ms": 5000},
    }
    r.update(kwargs)
    return r


class _RespCM:
    __slots__ = ("_code", "_body")

    def __init__(self, code: int, body: bytes) -> None:
        self._code = code
        self._body = body

    def __enter__(self) -> _RespCM:
        return self

    def __exit__(self, *args: object) -> bool:
        return False

    def read(self) -> bytes:
        return self._body

    def getcode(self) -> int:
        return self._code


class TestGeminiFlashAdapter(unittest.TestCase):
    def setUp(self) -> None:
        self.env = mock.patch.dict(
            os.environ,
            {
                "GEMINI_API_KEY": "test-key-not-real",
                "GEMINI_MODEL": "gemini-1.5-flash",
                "GEMINI_BASE_URL": "https://generativelanguage.googleapis.com",
            },
            clear=False,
        )
        self.env.start()

    def tearDown(self) -> None:
        self.env.stop()

    def test_registry_exposes_gemini_flash(self) -> None:
        ad = get_adapter("gemini_flash")
        self.assertIsNotNone(ad)
        self.assertEqual(ad.provider_id, "gemini_flash")

    def test_success_usage_and_cost(self) -> None:
        body = {
            "candidates": [
                {
                    "content": {
                        "role": "model",
                        "parts": [{"text": "Réponse courte"}],
                    }
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 1000,
                "candidatesTokenCount": 500,
                "totalTokenCount": 1500,
            },
        }
        calls: list[tuple] = []

        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            calls.append((req.full_url, req.method, timeout))
            self.assertNotIn("test-key-not-real", req.full_url)
            hdrs = {k.lower(): v for k, v in req.header_items()}
            self.assertEqual(hdrs.get("x-goog-api-key"), "test-key-not-real")
            self.assertAlmostEqual(float(timeout), 5.0)
            posted = json.loads(req.data.decode())
            self.assertIn("generationConfig", posted)
            self.assertEqual(posted["generationConfig"]["maxOutputTokens"], 500)
            return _RespCM(200, json.dumps(body).encode())

        with mock.patch.object(gf, "_urlopen", side_effect=fake_open):
            out = gf.GeminiFlashAdapter().run(_base_req())

        self.assertEqual(out["status"], "success")
        self.assertEqual(out["provider_used"], "gemini_flash")
        self.assertEqual(out["output"]["text"], "Réponse courte")
        self.assertEqual(out["usage"]["input_tokens"], 1000)
        self.assertEqual(out["usage"]["output_tokens"], 500)
        expected_cost = 1000 * 0.075 / 1_000_000 + 500 * 0.30 / 1_000_000
        self.assertAlmostEqual(out["usage"]["estimated_cost_usd"], expected_cost, places=10)
        self.assertEqual(len(calls), 1)

    def test_quota_429_retryable(self) -> None:
        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            return _RespCM(429, b'{"error":{"message":"quota"}}')

        with mock.patch.object(gf, "_urlopen", side_effect=fake_open):
            out = gf.GeminiFlashAdapter().run(_base_req())

        self.assertEqual(out["status"], "error")
        err = out["error"]
        assert isinstance(err, dict)
        self.assertEqual(err["code"], "provider_rate_limited")
        self.assertTrue(err["retryable"])
        self.assertNotIn("test-key-not-real", err["message"])
        self.assertNotIn("test-key-not-real", json.dumps(out))

    def test_invalid_key_401_not_retryable(self) -> None:
        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            return _RespCM(401, b'{"error":{"message":"API key not valid"}}')

        with mock.patch.object(gf, "_urlopen", side_effect=fake_open):
            out = gf.GeminiFlashAdapter().run(_base_req())

        err = out["error"]
        assert isinstance(err, dict)
        self.assertEqual(err["code"], "provider_auth_error")
        self.assertFalse(err["retryable"])
        self.assertNotIn("test-key-not-real", err["message"])

    def test_forbidden_403_not_retryable(self) -> None:
        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            return _RespCM(403, b"{}")

        with mock.patch.object(gf, "_urlopen", side_effect=fake_open):
            out = gf.GeminiFlashAdapter().run(_base_req())

        err = out["error"]
        assert isinstance(err, dict)
        self.assertEqual(err["code"], "provider_auth_error")
        self.assertFalse(err["retryable"])

    def test_server_503_retryable(self) -> None:
        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            return _RespCM(503, b"{}")

        with mock.patch.object(gf, "_urlopen", side_effect=fake_open):
            out = gf.GeminiFlashAdapter().run(_base_req())

        err = out["error"]
        assert isinstance(err, dict)
        self.assertEqual(err["code"], "provider_server_error")
        self.assertTrue(err["retryable"])

    def test_timeout_respected(self) -> None:
        req = _base_req()
        req["options"] = {**req["options"], "timeout_ms": 12000}

        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            self.assertEqual(timeout, 12.0)
            raise TimeoutError("simulated")

        with mock.patch.object(gf, "_urlopen", side_effect=fake_open):
            out = gf.GeminiFlashAdapter().run(req)

        err = out["error"]
        assert isinstance(err, dict)
        self.assertEqual(err["code"], "provider_timeout")
        self.assertTrue(err["retryable"])
        self.assertIn("timeout_ms=12000", err["message"])

    def test_missing_api_key_no_http_call(self) -> None:
        def boom(*_a: object, **_k: object) -> None:
            raise AssertionError("urlopen must not be called without API key")

        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=False):
            with mock.patch.object(gf, "_urlopen", side_effect=boom):
                out = gf.GeminiFlashAdapter().run(_base_req())

        err = out["error"]
        assert isinstance(err, dict)
        self.assertEqual(err["code"], "provider_config_error")
        self.assertFalse(err["retryable"])

    def test_cost_formula_helper(self) -> None:
        self.assertAlmostEqual(
            gf._estimate_cost_usd(1_000_000, 1_000_000),
            0.075 + 0.30,
            places=6,
        )


if __name__ == "__main__":
    unittest.main()
