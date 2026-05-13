"""FastAPI POST /ai/run — integration tests with mocked adapters (WEA-171)."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest import mock

import pytest
from fastapi.testclient import TestClient

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from ai_orchestrator.server import create_app  # noqa: E402


def _uuid() -> str:
    return "550e8400-e29b-41d4-a716-446655440000"


def _minimal(**overrides: object) -> dict:
    b: dict = {
        "task_id": _uuid(),
        "task_type": "analysis",
        "complexity": "low",
        "privacy_level": "local_only",
        "input": {"prompt": "hello"},
    }
    b.update(overrides)
    return b


def _lm_success(text: str = "ok") -> dict:
    return {
        "task_id": _uuid(),
        "status": "success",
        "provider_used": "lm_studio",
        "model_used": "gemma-4",
        "output": {"text": text},
        "usage": {
            "input_tokens": 1,
            "output_tokens": 1,
            "estimated_cost_usd": 0.0,
            "duration_ms": 5,
            "estimated_cloud_equivalent_cost_usd": 0.1,
            "estimated_savings_usd": 0.1,
        },
        "routing_reason": "lm_ok",
        "error": None,
    }


def _prov_err(provider: str, code: str = "provider_unavailable") -> dict:
    return {
        "task_id": _uuid(),
        "status": "error",
        "provider_used": provider,
        "model_used": "",
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
        "error": {"code": code, "message": "down", "retryable": True},
    }


@pytest.fixture()
def client_no_auth(tmp_path: Path) -> TestClient:
    log = tmp_path / "t.jsonl"
    env = {
        "AI_ORCHESTRATOR_API_TOKEN": "",
        "AI_ORCHESTRATOR_ENABLE_CORS": "false",
        "AI_ORCHESTRATOR_LOG_PATH": str(log),
    }
    with mock.patch.dict(os.environ, env, clear=False):
        yield TestClient(create_app())


def test_post_ai_run_success_local(client_no_auth: TestClient) -> None:
    with mock.patch(
        "ai_orchestrator.server.get_adapter_run",
        return_value=lambda req: _lm_success(),
    ) as m:
        r = client_no_auth.post("/ai/run", json=_minimal(preferred_model="local"))
    m.assert_called()
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert data["output"]["text"] == "ok"
    assert "cost" in data and data["cost"]["reference_provider"] == "gemini_flash"


def test_local_only_privacy_violation(client_no_auth: TestClient) -> None:
    with mock.patch("ai_orchestrator.server.get_adapter_run") as m:
        r = client_no_auth.post(
            "/ai/run",
            json=_minimal(privacy_level="local_only", preferred_model="gemini_flash"),
        )
    m.assert_not_called()
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "privacy_violation"


def test_standard_medium_auto_fallback_chain(client_no_auth: TestClient) -> None:
    """Gemini fails → Claude fails → LM succeeds → 200 fallback."""

    def fake_get(provider: str):
        def run(req: dict) -> dict:  # noqa: ARG001
            if provider == "gemini_flash":
                return _prov_err("gemini_flash")
            if provider == "claude_haiku":
                return _prov_err("claude_haiku")
            return _lm_success("from-lm")

        return run

    with mock.patch("ai_orchestrator.server.get_adapter_run", side_effect=fake_get):
        r = client_no_auth.post(
            "/ai/run",
            json=_minimal(
                privacy_level="standard",
                complexity="medium",
                preferred_model="auto",
            ),
        )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "fallback"
    assert body["provider_used"] == "lm_studio"
    assert body["output"]["text"] == "from-lm"


def test_all_cloud_fail_single_local_candidate_502(client_no_auth: TestClient) -> None:
    def fake_get(provider: str):
        return lambda req: _prov_err(provider, "provider_server_error")

    with mock.patch("ai_orchestrator.server.get_adapter_run", side_effect=fake_get):
        r = client_no_auth.post(
            "/ai/run",
            json=_minimal(
                privacy_level="standard",
                complexity="medium",
                preferred_model="auto",
            ),
        )
    assert r.status_code == 502


def test_single_provider_chain_uses_adapter_http_mapping(client_no_auth: TestClient) -> None:
    with mock.patch(
        "ai_orchestrator.server.get_adapter_run",
        return_value=lambda req: _prov_err("lm_studio", "provider_unavailable"),
    ):
        r = client_no_auth.post("/ai/run", json=_minimal(preferred_model="local"))
    assert r.status_code == 503


def test_validation_error_envelope(client_no_auth: TestClient) -> None:
    bad = _minimal()
    bad["task_type"] = "invalid_task"
    r = client_no_auth.post("/ai/run", json=bad)
    assert r.status_code == 422
    data = r.json()
    assert data["status"] == "error"
    assert data["error"]["code"] == "validation_error"


def test_bearer_required_401(tmp_path: Path) -> None:
    log = tmp_path / "t.jsonl"
    with mock.patch.dict(
        os.environ,
        {
            "AI_ORCHESTRATOR_API_TOKEN": "secret",
            "AI_ORCHESTRATOR_LOG_PATH": str(log),
        },
        clear=False,
    ):
        c = TestClient(create_app())
        r = c.post("/ai/run", json=_minimal(preferred_model="local"))
    assert r.status_code == 401


def test_bearer_ok(tmp_path: Path) -> None:
    log = tmp_path / "t.jsonl"
    with mock.patch.dict(
        os.environ,
        {
            "AI_ORCHESTRATOR_API_TOKEN": "secret",
            "AI_ORCHESTRATOR_LOG_PATH": str(log),
        },
        clear=False,
    ):
        c = TestClient(create_app())
        with mock.patch(
            "ai_orchestrator.server.get_adapter_run",
            return_value=lambda req: _lm_success(),
        ):
            r = c.post(
                "/ai/run",
                json=_minimal(preferred_model="local"),
                headers={"Authorization": "Bearer secret"},
            )
    assert r.status_code == 200


def test_preferred_model_defaults_to_auto(client_no_auth: TestClient) -> None:
    """Omit preferred_model → auto; standard + low → LM first in chain."""

    seen: list[str] = []

    def fake_get(provider: str):
        def run(req: dict) -> dict:  # noqa: ARG001
            seen.append(provider)
            if provider == "lm_studio":
                return _lm_success()
            return _prov_err(provider)

        return run

    with mock.patch("ai_orchestrator.server.get_adapter_run", side_effect=fake_get):
        body = _minimal(privacy_level="standard", complexity="low")
        body.pop("preferred_model", None)
        r = client_no_auth.post("/ai/run", json=body)
    assert r.status_code == 200
    assert seen[0] == "lm_studio"
