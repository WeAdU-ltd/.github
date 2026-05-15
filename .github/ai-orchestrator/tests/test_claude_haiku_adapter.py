"""Tests unitaires mockés pour l'adaptateur Claude Haiku — WEA-174."""

from __future__ import annotations

import json
import os
import sys
import unittest
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path
from unittest import mock

_ORCH_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ORCH_ROOT / "src"
for _p in (_SRC, _ORCH_ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from ai_orchestrator.adapters import claude_haiku as ch  # noqa: E402


def _uuid() -> str:
    return "550e8400-e29b-41d4-a716-446655440000"


def _base_req(**kwargs: object) -> dict:
    r: dict = {
        "task_id": _uuid(),
        "task_type": "analysis",
        "complexity": "high",
        "privacy_level": "external_allowed",
        "preferred_model": "claude_haiku",
        "input": {"prompt": "Explain briefly", "context": {}, "data": []},
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


class TestClaudeHaikuAdapter(unittest.TestCase):
    def setUp(self) -> None:
        self.env = mock.patch.dict(
            os.environ,
            {
                "ANTHROPIC_API_KEY": "sk-ant-api03-testkeyvalue123456789",
                "ANTHROPIC_MODEL": "claude-haiku-4-5",
                "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
            },
            clear=False,
        )
        self.env.start()

    def tearDown(self) -> None:
        self.env.stop()

    def test_success_usage_and_cost(self) -> None:
        api_resp = {
            "id": "msg_1",
            "type": "message",
            "role": "assistant",
            "model": "claude-haiku-4-5",
            "content": [{"type": "text", "text": "Hello from Haiku"}],
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 1_000_000, "output_tokens": 500_000},
        }
        calls: list[tuple] = []

        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            calls.append((req.full_url, req.method, timeout))
            self.assertIn("/v1/messages", req.full_url)
            self.assertEqual(timeout, 5.0)
            hdrs = {k.lower(): v for k, v in req.header_items()}
            self.assertEqual(hdrs.get("x-api-key"), "sk-ant-api03-testkeyvalue123456789")
            body = json.loads(req.data.decode())
            self.assertEqual(body["model"], "claude-haiku-4-5")
            self.assertEqual(body["messages"][0]["role"], "user")
            self.assertIn("Prompt:", body["messages"][0]["content"])
            return _RespCM(200, json.dumps(api_resp).encode())

        with mock.patch.object(ch, "_urlopen", side_effect=fake_open):
            out = ch.ClaudeHaikuAdapter().run(_base_req())
        self.assertEqual(out["status"], "success")
        self.assertEqual(out["provider_used"], "claude_haiku")
        self.assertEqual(out["output"]["text"], "Hello from Haiku")
        self.assertEqual(out["usage"]["input_tokens"], 1_000_000)
        self.assertEqual(out["usage"]["output_tokens"], 500_000)
        exp_cost = 1_000_000 * 0.80 / 1_000_000.0 + 500_000 * 4.00 / 1_000_000.0
        self.assertAlmostEqual(out["usage"]["estimated_cost_usd"], exp_cost, places=6)
        self.assertEqual(len(calls), 1)

    def test_http_529_overload_retryable(self) -> None:
        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            raise urllib.error.HTTPError(
                req.full_url, 529, "overload", {}, BytesIO(b'{"error":{"type":"overloaded"}}')
            )

        with mock.patch.object(ch, "_urlopen", side_effect=fake_open):
            out = ch.ClaudeHaikuAdapter().run(_base_req())
        self.assertEqual(out["status"], "error")
        self.assertEqual(out["error"]["code"], "provider_overloaded")
        self.assertTrue(out["error"]["retryable"])

    def test_http_401_invalid_key_not_retryable(self) -> None:
        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            raise urllib.error.HTTPError(req.full_url, 401, "auth", {}, BytesIO(b"{}"))

        with mock.patch.object(ch, "_urlopen", side_effect=fake_open):
            out = ch.ClaudeHaikuAdapter().run(_base_req())
        self.assertEqual(out["error"]["code"], "provider_auth_error")
        self.assertFalse(out["error"]["retryable"])

    def test_timeout_retryable(self) -> None:
        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            raise TimeoutError("socket timeout")

        with mock.patch.object(ch, "_urlopen", side_effect=fake_open):
            out = ch.ClaudeHaikuAdapter().run(
                _base_req(options={"temperature": 0.2, "max_tokens": 100, "timeout_ms": 2000})
            )
        self.assertEqual(out["error"]["code"], "provider_timeout")
        self.assertTrue(out["error"]["retryable"])
        self.assertIn("timeout_ms=2000", out["error"]["message"])

    def test_http_429_rate_limit_retryable(self) -> None:
        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            raise urllib.error.HTTPError(req.full_url, 429, "rate", {}, BytesIO(b"{}"))

        with mock.patch.object(ch, "_urlopen", side_effect=fake_open):
            out = ch.ClaudeHaikuAdapter().run(_base_req())
        self.assertEqual(out["error"]["code"], "provider_rate_limited")
        self.assertTrue(out["error"]["retryable"])

    def test_error_body_does_not_echo_api_key(self) -> None:
        key = "sk-ant-api03-testkeyvalue123456789"
        err_json = json.dumps({"error": {"message": f"invalid {key} in request"}})

        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            raise urllib.error.HTTPError(req.full_url, 400, "bad", {}, BytesIO(err_json.encode()))

        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": key}, clear=False):
            with mock.patch.object(ch, "_urlopen", side_effect=fake_open):
                out = ch.ClaudeHaikuAdapter().run(_base_req())
        self.assertNotIn(key, out["error"]["message"])
        self.assertIn("[REDACTED]", out["error"]["message"])

    def test_context_system_sent_as_top_level(self) -> None:
        api_resp = {
            "model": "claude-haiku-4-5",
            "content": [{"type": "text", "text": "ok"}],
            "usage": {"input_tokens": 10, "output_tokens": 2},
        }

        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            body = json.loads(req.data.decode())
            self.assertEqual(body.get("system"), "Be concise.")
            self.assertNotIn("Be concise", body["messages"][0]["content"])
            return _RespCM(200, json.dumps(api_resp).encode())

        inp = {
            "prompt": "Hi",
            "context": {"system": "Be concise.", "x": 1},
            "data": [],
        }
        with mock.patch.object(ch, "_urlopen", side_effect=fake_open):
            out = ch.ClaudeHaikuAdapter().run(_base_req(input=inp))
        self.assertEqual(out["status"], "success")

    def test_missing_api_key(self) -> None:
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}, clear=False):
            out = ch.ClaudeHaikuAdapter().run(_base_req())
        self.assertEqual(out["error"]["code"], "provider_auth_error")
        self.assertFalse(out["error"]["retryable"])


class TestAdapterRegistry(unittest.TestCase):
    def test_claude_haiku_registered(self) -> None:
        from ai_orchestrator.adapter_registry import adapter_registry  # noqa: PLC0415

        self.assertIn("claude_haiku", adapter_registry)
        self.assertTrue(callable(adapter_registry["claude_haiku"]))


if __name__ == "__main__":
    unittest.main()
