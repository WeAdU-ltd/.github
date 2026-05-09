"""Tests unitaires HTTP mockés pour lm_studio_adapter — WEA-172."""

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

# Import package depuis la racine ai-orchestrator
_ORCH_ROOT = Path(__file__).resolve().parents[1]
if str(_ORCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_ORCH_ROOT))

from lm_studio_adapter import adapter as ad  # noqa: E402


def _uuid() -> str:
    return "550e8400-e29b-41d4-a716-446655440000"


def _base_req(**kwargs: object) -> dict:
    r: dict = {
        "task_id": _uuid(),
        "task_type": "analysis",
        "complexity": "low",
        "privacy_level": "local_only",
        "preferred_model": "local",
        "input": {"prompt": "Analyse ce contenu", "context": {}, "data": []},
        "options": {"temperature": 0.2, "max_tokens": 1000, "timeout_ms": 30000},
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


class TestLmStudioAdapter(unittest.TestCase):
    def setUp(self) -> None:
        self.env = mock.patch.dict(
            os.environ,
            {
                "LM_STUDIO_BASE_URL": "http://localhost:1234",
                "LM_STUDIO_MODEL_LOW": "gemma-4",
                "LM_STUDIO_MODEL_DEFAULT": "gemma-4",
                "LM_STUDIO_TIMEOUT_MS": "30000",
                "LM_STUDIO_API_KEY": "",
            },
            clear=False,
        )
        self.env.start()

    def tearDown(self) -> None:
        self.env.stop()

    def test_post_success_with_usage(self) -> None:
        models = {"data": [{"id": "gemma-4"}]}
        chat = {
            "id": "x",
            "object": "chat.completion",
            "model": "gemma-4",
            "choices": [{"message": {"role": "assistant", "content": "Résultat généré"}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
        }
        calls: list[tuple] = []

        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            calls.append((req.full_url, req.method, timeout))
            if req.method == "GET":
                return _RespCM(200, json.dumps(models).encode())
            if req.method == "POST":
                body = json.loads(req.data.decode())
                self.assertEqual(body["model"], "gemma-4")
                self.assertEqual(body["messages"][0]["role"], "system")
                self.assertIn("Prompt:", body["messages"][1]["content"])
                return _RespCM(200, json.dumps(chat).encode())
            raise AssertionError(req.method)

        with mock.patch.object(ad, "_urlopen", side_effect=fake_open):
            out = ad.run(_base_req())
        self.assertEqual(out["status"], "success")
        self.assertEqual(out["provider_used"], "lm_studio")
        self.assertEqual(out["output"]["text"], "Résultat généré")
        self.assertEqual(out["usage"]["input_tokens"], 100)
        self.assertEqual(out["usage"]["output_tokens"], 50)
        self.assertEqual(out["usage"]["estimated_cost_usd"], 0.0)
        exp = 150 * 0.075 / 1_000_000.0
        self.assertAlmostEqual(out["usage"]["estimated_cloud_equivalent_cost_usd"], exp, places=10)
        self.assertAlmostEqual(out["usage"]["estimated_savings_usd"], exp, places=10)
        self.assertEqual(len(calls), 2)

    def test_post_success_without_usage_estimates_tokens(self) -> None:
        models = {"data": [{"id": "gemma-4"}]}
        chat = {
            "model": "gemma-4",
            "choices": [{"message": {"content": "abcd"}}],
        }
        req = _base_req()

        def fake_open(r: urllib.request.Request, timeout: object = None) -> _RespCM:
            if r.method == "GET":
                return _RespCM(200, json.dumps(models).encode())
            return _RespCM(200, json.dumps(chat).encode())

        with mock.patch.object(ad, "_urlopen", side_effect=fake_open):
            out = ad.run(req)
        self.assertEqual(out["status"], "success")
        import math

        uc_len = len(ad._build_user_content(req["input"]))  # type: ignore[attr-defined]
        exp_in = int(math.ceil(uc_len / 4))
        exp_out = int(math.ceil(4 / 4))  # "abcd"
        self.assertEqual(out["usage"]["input_tokens"], exp_in)
        self.assertEqual(out["usage"]["output_tokens"], exp_out)

    def test_model_absent_provider_not_found(self) -> None:
        models = {"data": [{"id": "other-model"}]}

        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            return _RespCM(200, json.dumps(models).encode())

        with mock.patch.object(ad, "_urlopen", side_effect=fake_open):
            out = ad.run(_base_req())
        self.assertEqual(out["status"], "error")
        self.assertEqual(out["error"]["code"], "provider_not_found")
        self.assertFalse(out["error"]["retryable"])
        self.assertIn("gemma-4", out["error"]["message"])

    def test_connection_refused(self) -> None:
        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            raise ConnectionError("Connection refused")

        with mock.patch.object(ad, "_urlopen", side_effect=fake_open):
            out = ad.run(_base_req())
        self.assertEqual(out["error"]["code"], "provider_unavailable")
        self.assertTrue(out["error"]["retryable"])

    def test_models_get_timeout(self) -> None:
        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            raise TimeoutError("timed out")

        with mock.patch.object(ad, "_urlopen", side_effect=fake_open):
            out = ad.run(_base_req())
        self.assertEqual(out["error"]["code"], "provider_timeout")

    def test_chat_timeout(self) -> None:
        models = {"data": [{"id": "gemma-4"}]}
        stage = {"n": 0}

        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            if req.method == "GET":
                return _RespCM(200, json.dumps(models).encode())
            stage["n"] += 1
            raise TimeoutError("chat timed out")

        with mock.patch.object(ad, "_urlopen", side_effect=fake_open):
            out = ad.run(_base_req())
        self.assertEqual(out["error"]["code"], "provider_timeout")

    def test_http_400_on_chat(self) -> None:
        models = {"data": [{"id": "gemma-4"}]}

        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            if req.method == "GET":
                return _RespCM(200, json.dumps(models).encode())
            raise urllib.error.HTTPError(req.full_url, 400, "bad", {}, BytesIO(b"{}"))

        with mock.patch.object(ad, "_urlopen", side_effect=fake_open):
            out = ad.run(_base_req())
        self.assertEqual(out["error"]["code"], "provider_bad_request")

    def test_http_401_on_chat(self) -> None:
        models = {"data": [{"id": "gemma-4"}]}

        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            if req.method == "GET":
                return _RespCM(200, json.dumps(models).encode())
            raise urllib.error.HTTPError(req.full_url, 401, "auth", {}, BytesIO(b"{}"))

        with mock.patch.object(ad, "_urlopen", side_effect=fake_open):
            out = ad.run(_base_req())
        self.assertEqual(out["error"]["code"], "provider_auth_error")

    def test_http_404_on_chat(self) -> None:
        models = {"data": [{"id": "gemma-4"}]}

        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            if req.method == "GET":
                return _RespCM(200, json.dumps(models).encode())
            raise urllib.error.HTTPError(req.full_url, 404, "nf", {}, BytesIO(b"{}"))

        with mock.patch.object(ad, "_urlopen", side_effect=fake_open):
            out = ad.run(_base_req())
        self.assertEqual(out["error"]["code"], "provider_not_found")

    def test_http_500_on_chat(self) -> None:
        models = {"data": [{"id": "gemma-4"}]}

        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            if req.method == "GET":
                return _RespCM(200, json.dumps(models).encode())
            raise urllib.error.HTTPError(req.full_url, 500, "srv", {}, BytesIO(b"{}"))

        with mock.patch.object(ad, "_urlopen", side_effect=fake_open):
            out = ad.run(_base_req())
        self.assertEqual(out["error"]["code"], "provider_server_error")
        self.assertTrue(out["error"]["retryable"])

    def test_invalid_json_chat(self) -> None:
        models = {"data": [{"id": "gemma-4"}]}

        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            if req.method == "GET":
                return _RespCM(200, json.dumps(models).encode())
            return _RespCM(200, b"not-json")

        with mock.patch.object(ad, "_urlopen", side_effect=fake_open):
            out = ad.run(_base_req())
        self.assertEqual(out["error"]["code"], "provider_invalid_response")

    def test_empty_choices(self) -> None:
        models = {"data": [{"id": "gemma-4"}]}
        chat = {"choices": [], "model": "gemma-4"}

        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            if req.method == "GET":
                return _RespCM(200, json.dumps(models).encode())
            return _RespCM(200, json.dumps(chat).encode())

        with mock.patch.object(ad, "_urlopen", side_effect=fake_open):
            out = ad.run(_base_req())
        self.assertEqual(out["error"]["code"], "provider_invalid_response")

    def test_preferred_gemini_validation(self) -> None:
        with mock.patch.object(ad, "_urlopen") as m:
            out = ad.run(_base_req(preferred_model="gemini_flash"))
        m.assert_not_called()
        self.assertEqual(out["status"], "error")
        self.assertEqual(out["error"]["code"], "validation_error")

    def test_explicit_freeform_overrides_medium_default_env(self) -> None:
        """Chaîne libre prime sur LM_STUDIO_MODEL_DEFAULT lorsque complexity=medium."""
        req = _base_req(complexity="medium", preferred_model="custom-med")
        models = {"data": [{"id": "gemma-4"}, {"id": "only-default"}, {"id": "custom-med"}]}
        chat = {
            "model": "custom-med",
            "choices": [{"message": {"content": "x"}}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        }

        def fake_open(r: urllib.request.Request, timeout: object = None) -> _RespCM:
            if r.method == "GET":
                return _RespCM(200, json.dumps(models).encode())
            body = json.loads(r.data.decode())
            self.assertEqual(
                body["model"],
                "custom-med",
                "POST model doit reprendre preferred_model personnalisé, pas LM_STUDIO_MODEL_DEFAULT",
            )
            return _RespCM(200, json.dumps(chat).encode())

        with mock.patch.dict(os.environ, {"LM_STUDIO_MODEL_DEFAULT": "only-default"}):
            with mock.patch.object(ad, "_urlopen", side_effect=fake_open):
                out = ad.run(req)
        self.assertEqual(out["status"], "success")
        self.assertEqual(out["model_used"], "custom-med")

    def test_explicit_freeform_model_overrides_low_default(self) -> None:
        """Chaîne libre = id LM Studio ; prime sur LM_STUDIO_MODEL_LOW."""
        req = _base_req(complexity="low", preferred_model="mistral-local")
        models = {"data": [{"id": "gemma-4"}, {"id": "mistral-local"}]}
        chat = {
            "model": "mistral-local",
            "choices": [{"message": {"content": "ok"}}],
            "usage": {"prompt_tokens": 2, "completion_tokens": 1},
        }

        def fake_open(r: urllib.request.Request, timeout: object = None) -> _RespCM:
            if r.method == "GET":
                return _RespCM(200, json.dumps(models).encode())
            body = json.loads(r.data.decode())
            self.assertEqual(body["model"], "mistral-local")
            return _RespCM(200, json.dumps(chat).encode())

        with mock.patch.object(ad, "_urlopen", side_effect=fake_open):
            out = ad.run(req)
        self.assertEqual(out["status"], "success")
        self.assertIn("explicit model from preferred_model", out["routing_reason"])
        self.assertIn("mistral-local", out["routing_reason"])

    def test_preferred_model_empty_string_validation(self) -> None:
        with mock.patch.object(ad, "_urlopen") as m:
            out = ad.run(_base_req(preferred_model="   "))
        m.assert_not_called()
        self.assertEqual(out["error"]["code"], "validation_error")

    def test_preferred_model_non_string_validation(self) -> None:
        r = _base_req()
        r["preferred_model"] = None
        with mock.patch.object(ad, "_urlopen") as m:
            out = ad.run(r)
        m.assert_not_called()
        self.assertEqual(out["error"]["code"], "validation_error")

    def test_medium_uses_model_default_env(self) -> None:
        models = {"data": [{"id": "gemma-4"}, {"id": "custom-default"}]}
        chat = {
            "model": "custom-default",
            "choices": [{"message": {"content": "ok"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 2},
        }

        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            if req.method == "GET":
                return _RespCM(200, json.dumps(models).encode())
            body = json.loads(req.data.decode())
            self.assertEqual(body["model"], "custom-default")
            return _RespCM(200, json.dumps(chat).encode())

        with mock.patch.dict(os.environ, {"LM_STUDIO_MODEL_DEFAULT": "custom-default"}):
            with mock.patch.object(ad, "_urlopen", side_effect=fake_open):
                out = ad.run(_base_req(complexity="medium"))
        self.assertEqual(out["status"], "success")
        self.assertEqual(out["model_used"], "custom-default")

    def test_check_availability_true(self) -> None:
        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            self.assertIn("/v1/models", req.full_url)
            self.assertEqual(timeout, 2.0)
            return _RespCM(200, json.dumps({"data": [{"id": "gemma-4"}]}).encode())

        with mock.patch.object(ad, "_urlopen", side_effect=fake_open):
            self.assertTrue(ad.check_availability())

    def test_check_availability_false_on_timeout(self) -> None:
        def fake_open(req: urllib.request.Request, timeout: object = None) -> _RespCM:
            raise TimeoutError()

        with mock.patch.object(ad, "_urlopen", side_effect=fake_open):
            self.assertFalse(ad.check_availability())

    def test_bearer_when_api_key_set(self) -> None:
        models = {"data": [{"id": "gemma-4"}]}
        chat = {
            "model": "gemma-4",
            "choices": [{"message": {"content": "x"}}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        }
        auths: list[str | None] = []

        class _Capturing:
            def __init__(self, inner: _RespCM) -> None:
                self._inner = inner

            def __enter__(self) -> _RespCM:
                return self._inner

            def __exit__(self, *a: object) -> bool:
                return False

        def fake_open(req: urllib.request.Request, timeout: object = None) -> _Capturing:
            auths.append(req.get_header("Authorization"))
            if req.method == "GET":
                return _Capturing(_RespCM(200, json.dumps(models).encode()))
            return _Capturing(_RespCM(200, json.dumps(chat).encode()))

        with mock.patch.dict(os.environ, {"LM_STUDIO_API_KEY": "secret-token"}):
            with mock.patch.object(ad, "_urlopen", side_effect=fake_open):
                ad.run(_base_req())
        self.assertTrue(any(h == "Bearer secret-token" for h in auths if h))


@unittest.skipUnless(os.environ.get("RUN_LM_STUDIO_SMOKE_TEST") == "1", "set RUN_LM_STUDIO_SMOKE_TEST=1")
class TestLmStudioSmokeOptional(unittest.TestCase):
    def test_live_smoke(self) -> None:
        if not ad.check_availability():
            self.skipTest("LM Studio not reachable")
        out = ad.run(_base_req())
        self.assertIn(out["status"], ("success", "error"))


if __name__ == "__main__":
    unittest.main()
