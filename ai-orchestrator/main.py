"""
Orchestrateur IA WeAdU — point d'entrée FastAPI.

POST /ai/run valide la requête, route vers LM Studio lorsque c'est le provider
cible, et appelle l'API OpenAI-compatible de LM Studio (GET /v1/models,
POST /v1/chat/completions) sans maquette.

Exécution depuis ce dossier :
  pip install -r requirements.txt
  uvicorn main:app --host 127.0.0.1 --port 8787

Variables d'environnement (LM Studio) :
  LM_STUDIO_BASE_URL   (défaut http://localhost:1234)
  LM_STUDIO_API_KEY    (optionnel, header Bearer)
  LM_STUDIO_MODEL_LOW  (défaut gemma-4)
  LM_STUDIO_MODEL_DEFAULT (défaut gemma-4)
  LM_STUDIO_TIMEOUT_MS (défaut 30000, plancher 30000 pour le POST)
"""

from __future__ import annotations

import json
import math
import os
import time
from typing import Any, Literal
from uuid import UUID

import httpx
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# Constantes LM Studio
# ---------------------------------------------------------------------------

_GEMINI_FLASH_USD_PER_1M = 0.075
_DEFAULT_MODEL = "gemma-4"
_MODELS_TIMEOUT_SEC = 30.0
_CHAT_TIMEOUT_MS_MIN = 30_000

_LM_ENV_ROUTED = frozenset({"local", "auto"})
_CLOUD_ENUM = frozenset({"gemini_flash", "claude_haiku"})

_SYSTEM_MESSAGE = (
    "You are running as WeAdU local AI orchestrator. Use the provided context and data. "
    "Return a clear structured answer."
)


def _env_base_url() -> str:
    raw = os.environ.get("LM_STUDIO_BASE_URL", "http://localhost:1234").strip()
    return raw.rstrip("/") or "http://localhost:1234"


def _env_model_low() -> str:
    return os.environ.get("LM_STUDIO_MODEL_LOW", "").strip() or _DEFAULT_MODEL


def _env_model_default() -> str:
    return os.environ.get("LM_STUDIO_MODEL_DEFAULT", "").strip() or _DEFAULT_MODEL


def _env_api_key() -> str:
    return os.environ.get("LM_STUDIO_API_KEY", "").strip()


def _lm_headers() -> dict[str, str]:
    h = {"Accept": "application/json", "Content-Type": "application/json"}
    key = _env_api_key()
    if key:
        h["Authorization"] = f"Bearer {key}"
    return h


# ---------------------------------------------------------------------------
# Schémas Pydantic (alignés specs/api_contract.md)
# ---------------------------------------------------------------------------

TaskType = Literal["classification", "generation", "extraction", "coding", "analysis"]
Complexity = Literal["low", "medium", "high"]
PrivacyLevel = Literal["local_only", "standard", "external_allowed"]


class RunInput(BaseModel):
    model_config = ConfigDict(extra="allow")

    prompt: str = Field(..., min_length=1)
    context: dict[str, Any] = Field(default_factory=dict)
    data: list[Any] = Field(default_factory=list)


class RunOptions(BaseModel):
    model_config = ConfigDict(extra="allow")

    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, gt=0)
    timeout_ms: int = Field(default=30000, ge=1000)


class RunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: UUID
    task_type: TaskType
    complexity: Complexity
    privacy_level: PrivacyLevel
    preferred_model: str = Field(..., min_length=1)
    max_cost_usd: float | None = None
    input: RunInput
    options: RunOptions = Field(default_factory=RunOptions)

    @field_validator("preferred_model")
    @classmethod
    def strip_pm(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("preferred_model must be non-empty")
        return s

    @field_validator("max_cost_usd")
    @classmethod
    def max_cost(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("max_cost_usd must be >= 0")
        return v


# ---------------------------------------------------------------------------
# Routage provider (v1 — seul LM implémenté dans ce dépôt)
# ---------------------------------------------------------------------------

class PrivacyViolation(Exception):
    """preferred_model cloud sous local_only."""

    def __init__(self, message: str) -> None:
        self.message = message


def resolve_provider(req: RunRequest) -> Literal["lm_studio", "gemini_flash", "claude_haiku"]:
    pm = req.preferred_model.strip()
    if req.privacy_level == "local_only":
        if pm in _CLOUD_ENUM:
            raise PrivacyViolation(
                "preferred_model requests a cloud provider under privacy_level=local_only"
            )
        return "lm_studio"
    if pm not in (*_LM_ENV_ROUTED, *_CLOUD_ENUM):
        return "lm_studio"
    if pm == "local":
        return "lm_studio"
    if pm == "gemini_flash":
        return "gemini_flash"
    if pm == "claude_haiku":
        return "claude_haiku"
    if req.privacy_level in ("standard", "external_allowed"):
        if req.complexity == "low":
            return "lm_studio"
        if req.complexity == "medium":
            return "gemini_flash"
        return "claude_haiku"
    return "lm_studio"


def _resolve_model_id(complexity: str) -> str:
    return _env_model_low() if complexity == "low" else _env_model_default()


def _resolve_lm_model_name(req: RunRequest) -> tuple[str, bool]:
    """(model_id, uses_env) — uses_env True si local|auto."""
    pm = req.preferred_model.strip()
    if pm in _LM_ENV_ROUTED:
        return _resolve_model_id(req.complexity), True
    return pm, False


def _routing_reason(complexity: str, model_id: str, uses_env: bool) -> str:
    if not uses_env:
        return f"local execution with explicit model from preferred_model ({model_id})"
    if complexity == "low":
        return "local execution selected for low complexity task"
    return "local execution with LM_STUDIO_MODEL_DEFAULT for non-low complexity"


def _build_user_content(inp: RunInput) -> str:
    ctx = json.dumps(inp.context, ensure_ascii=False, separators=(",", ":"))
    data = json.dumps(inp.data, ensure_ascii=False, separators=(",", ":"))
    return f"Prompt:\n{inp.prompt}\n\nContext:\n{ctx}\n\nData:\n{data}"


def _usage_zero() -> dict[str, Any]:
    return {
        "input_tokens": 0,
        "output_tokens": 0,
        "estimated_cost_usd": 0.0,
        "duration_ms": 0,
        "estimated_cloud_equivalent_cost_usd": None,
        "estimated_savings_usd": None,
    }


def _error_body(
    task_id: str,
    *,
    code: str,
    message: str,
    provider_used: str = "none",
    model_used: str = "",
    routing_reason: str = "orchestrator_error",
    retryable: bool = False,
    duration_ms: int | None = None,
) -> dict[str, Any]:
    usage = _usage_zero()
    if duration_ms is not None:
        usage["duration_ms"] = duration_ms
    return {
        "task_id": task_id,
        "status": "error",
        "provider_used": provider_used,
        "model_used": model_used,
        "output": {},
        "usage": usage,
        "routing_reason": routing_reason,
        "error": {"code": code, "message": message, "retryable": retryable},
    }


def _http_status_for_lm_error(code: str) -> int:
    if code == "validation_error":
        return 422
    if code in ("provider_unavailable", "provider_timeout"):
        return 503
    if code in ("provider_bad_request", "provider_auth_error", "provider_not_found", "provider_invalid_response"):
        return 400
    if code == "provider_rate_limited":
        return 429
    if code == "provider_server_error":
        return 502
    return 502


def _list_model_ids(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return []
    data = payload.get("data")
    if not isinstance(data, list):
        return []
    out: list[str] = []
    for item in data:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            out.append(item["id"])
    return out


def _economy_usage(inp_tokens: int, out_tokens: int, duration_ms: int) -> dict[str, Any]:
    total = inp_tokens + out_tokens
    cloud_eq = total * _GEMINI_FLASH_USD_PER_1M / 1_000_000.0
    return {
        "input_tokens": inp_tokens,
        "output_tokens": out_tokens,
        "estimated_cost_usd": 0.0,
        "duration_ms": duration_ms,
        "estimated_cloud_equivalent_cost_usd": cloud_eq,
        "estimated_savings_usd": cloud_eq,
    }


def _estimate_tokens(prompt_full: str, response_text: str) -> tuple[int, int]:
    inp_t = int(math.ceil(len(prompt_full) / 4)) if prompt_full else 0
    out_t = int(math.ceil(len(response_text) / 4)) if response_text else 0
    return inp_t, out_t


async def _lm_studio_run(req: RunRequest) -> dict[str, Any]:
    """
    Appels HTTP réels vers LM Studio : GET /v1/models puis POST /v1/chat/completions.
    Retourne un dict RunResponse (success ou error).
    """
    t0 = time.perf_counter()
    tid = str(req.task_id)

    pm = req.preferred_model.strip()
    if pm in _CLOUD_ENUM:
        return _error_body(
            tid,
            code="validation_error",
            message="preferred_model requests a cloud provider; lm_studio endpoint cannot fulfill",
            provider_used="lm_studio",
        )

    model_id, uses_env = _resolve_lm_model_name(req)
    base = _env_base_url()
    models_url = f"{base}/v1/models"
    chat_url = f"{base}/v1/chat/completions"

    timeout_ms = max(_CHAT_TIMEOUT_MS_MIN, req.options.timeout_ms)
    post_timeout = httpx.Timeout(timeout_ms / 1000.0, connect=30.0)

    headers = _lm_headers()

    connect_timeout = httpx.Timeout(_MODELS_TIMEOUT_SEC, connect=30.0)
    async with httpx.AsyncClient(timeout=connect_timeout) as client:
        try:
            mresp = await client.get(models_url, headers=headers, timeout=_MODELS_TIMEOUT_SEC)
        except httpx.TimeoutException:
            return _error_body(
                tid,
                code="provider_timeout",
                message="LM Studio GET /v1/models timed out",
                provider_used="lm_studio",
                routing_reason="lm_studio_adapter_error",
                retryable=True,
                duration_ms=int((time.perf_counter() - t0) * 1000),
            )
        except httpx.RequestError as e:
            return _error_body(
                tid,
                code="provider_unavailable",
                message=f"LM Studio unreachable at {base}: {e}",
                provider_used="lm_studio",
                routing_reason="lm_studio_adapter_error",
                retryable=True,
                duration_ms=int((time.perf_counter() - t0) * 1000),
            )

        if mresp.status_code != 200:
            code = "provider_server_error" if mresp.status_code >= 500 else "provider_bad_request"
            return _error_body(
                tid,
                code=code,
                message=f"GET /v1/models HTTP {mresp.status_code}",
                provider_used="lm_studio",
                routing_reason="lm_studio_adapter_error",
                retryable=mresp.status_code >= 500 or mresp.status_code == 429,
                duration_ms=int((time.perf_counter() - t0) * 1000),
            )

        try:
            models_payload = mresp.json()
        except json.JSONDecodeError:
            return _error_body(
                tid,
                code="provider_invalid_response",
                message="GET /v1/models invalid JSON",
                provider_used="lm_studio",
                routing_reason="lm_studio_adapter_error",
                retryable=True,
                duration_ms=int((time.perf_counter() - t0) * 1000),
            )

        ids = _list_model_ids(models_payload)
        if model_id not in ids:
            return _error_body(
                tid,
                code="provider_not_found",
                message=f"Configured LM Studio model not found in /v1/models: {model_id}",
                provider_used="lm_studio",
                model_used=model_id,
                routing_reason="lm_studio_adapter_error",
                retryable=False,
                duration_ms=int((time.perf_counter() - t0) * 1000),
            )

    user_content = _build_user_content(req.input)
    body = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": _SYSTEM_MESSAGE},
            {"role": "user", "content": user_content},
        ],
        "temperature": req.options.temperature,
        "max_tokens": req.options.max_tokens,
    }

    t_chat = time.perf_counter()
    async with httpx.AsyncClient(timeout=post_timeout) as client:
        try:
            cresp = await client.post(
                chat_url,
                headers=headers,
                json=body,
                timeout=timeout_ms / 1000.0,
            )
        except httpx.TimeoutException:
            return _error_body(
                tid,
                code="provider_timeout",
                message=f"POST /v1/chat/completions exceeded timeout_ms={timeout_ms}",
                provider_used="lm_studio",
                model_used=model_id,
                routing_reason="lm_studio_adapter_error",
                retryable=True,
                duration_ms=int((time.perf_counter() - t0) * 1000),
            )
        except httpx.RequestError as e:
            return _error_body(
                tid,
                code="provider_unavailable",
                message=f"LM Studio unreachable at {base}: {e}",
                provider_used="lm_studio",
                model_used=model_id,
                routing_reason="lm_studio_adapter_error",
                retryable=True,
                duration_ms=int((time.perf_counter() - t0) * 1000),
            )

    chat_ms = int((time.perf_counter() - t_chat) * 1000)
    total_ms = int((time.perf_counter() - t0) * 1000)

    if cresp.status_code == 401 or cresp.status_code == 403:
        return _error_body(
            tid,
            code="provider_auth_error",
            message="LM Studio authentication failed",
            provider_used="lm_studio",
            model_used=model_id,
            routing_reason="lm_studio_adapter_error",
            retryable=False,
            duration_ms=total_ms,
        )
    if cresp.status_code == 404:
        return _error_body(
            tid,
            code="provider_not_found",
            message="POST /v1/chat/completions HTTP 404",
            provider_used="lm_studio",
            model_used=model_id,
            routing_reason="lm_studio_adapter_error",
            retryable=False,
            duration_ms=total_ms,
        )
    if cresp.status_code == 429:
        return _error_body(
            tid,
            code="provider_rate_limited",
            message="LM Studio rate limited",
            provider_used="lm_studio",
            model_used=model_id,
            routing_reason="lm_studio_adapter_error",
            retryable=True,
            duration_ms=total_ms,
        )
    if cresp.status_code >= 500:
        return _error_body(
            tid,
            code="provider_server_error",
            message=f"POST /v1/chat/completions HTTP {cresp.status_code}",
            provider_used="lm_studio",
            model_used=model_id,
            routing_reason="lm_studio_adapter_error",
            retryable=True,
            duration_ms=total_ms,
        )
    if cresp.status_code != 200:
        return _error_body(
            tid,
            code="provider_bad_request",
            message=f"POST /v1/chat/completions HTTP {cresp.status_code}",
            provider_used="lm_studio",
            model_used=model_id,
            routing_reason="lm_studio_adapter_error",
            retryable=False,
            duration_ms=total_ms,
        )

    try:
        chat_payload = cresp.json()
    except json.JSONDecodeError:
        return _error_body(
            tid,
            code="provider_invalid_response",
            message="POST /v1/chat/completions invalid JSON",
            provider_used="lm_studio",
            model_used=model_id,
            routing_reason="lm_studio_adapter_error",
            retryable=True,
            duration_ms=total_ms,
        )

    choices = chat_payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return _error_body(
            tid,
            code="provider_invalid_response",
            message="chat completion missing choices",
            provider_used="lm_studio",
            model_used=model_id,
            routing_reason="lm_studio_adapter_error",
            retryable=True,
            duration_ms=total_ms,
        )
    msg0 = choices[0]
    if not isinstance(msg0, dict):
        return _error_body(
            tid,
            code="provider_invalid_response",
            message="invalid choice",
            provider_used="lm_studio",
            model_used=model_id,
            routing_reason="lm_studio_adapter_error",
            retryable=True,
            duration_ms=total_ms,
        )
    message_obj = msg0.get("message")
    if not isinstance(message_obj, dict):
        return _error_body(
            tid,
            code="provider_invalid_response",
            message="missing message",
            provider_used="lm_studio",
            model_used=model_id,
            routing_reason="lm_studio_adapter_error",
            retryable=True,
            duration_ms=total_ms,
        )
    content = message_obj.get("content")
    text_out = content if isinstance(content, str) else ""

    model_used = chat_payload.get("model")
    if not isinstance(model_used, str) or not model_used:
        model_used = model_id

    usage_block = chat_payload.get("usage")
    in_t = out_t = 0
    if isinstance(usage_block, dict):
        pt, ct = usage_block.get("prompt_tokens"), usage_block.get("completion_tokens")
        if isinstance(pt, (int, float)):
            in_t = int(pt)
        if isinstance(ct, (int, float)):
            out_t = int(ct)
    if in_t == 0 and out_t == 0:
        in_t, out_t = _estimate_tokens(user_content, text_out)

    usage = _economy_usage(in_t, out_t, chat_ms)

    return {
        "task_id": tid,
        "status": "success",
        "provider_used": "lm_studio",
        "model_used": model_used,
        "output": {"text": text_out},
        "usage": usage,
        "routing_reason": _routing_reason(req.complexity, model_id, uses_env),
        "error": None,
    }


def create_app() -> FastAPI:
    app = FastAPI(
        title="WeAdU AI Orchestrator",
        version="0.2.0",
        description="POST /ai/run — appels HTTP réels vers LM Studio (API OpenAI-compatible).",
    )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        task_id = "00000000-0000-0000-0000-000000000000"
        try:
            body = await request.json()
            tid = body.get("task_id")
            if isinstance(tid, str) and tid:
                task_id = tid
        except Exception:
            pass
        msg = "; ".join(f"{e.get('loc')}: {e.get('msg')}" for e in exc.errors()[:8])
        body = _error_body(
            task_id,
            code="validation_error",
            message=msg or "request validation failed",
            provider_used="none",
            routing_reason="pydantic_validation",
        )
        return JSONResponse(status_code=422, content=body)

    @app.post("/ai/run")
    async def post_ai_run(req: RunRequest) -> JSONResponse:
        tid = str(req.task_id)
        try:
            provider = resolve_provider(req)
        except PrivacyViolation as e:
            body = _error_body(
                tid,
                code="privacy_violation",
                message=e.message,
                provider_used="none",
                routing_reason="privacy_local_only_blocks_cloud",
            )
            return JSONResponse(status_code=400, content=body)

        if provider != "lm_studio":
            body = _error_body(
                tid,
                code="adapter_not_implemented",
                message=f"Provider {provider} is not implemented in this deployment",
                provider_used="none",
                routing_reason=f"routed_to_{provider}_not_implemented",
            )
            return JSONResponse(status_code=503, content=body)

        result = await _lm_studio_run(req)
        if result.get("status") == "error" and isinstance(result.get("error"), dict):
            code = str(result["error"].get("code") or "error")
            return JSONResponse(status_code=_http_status_for_lm_error(code), content=result)
        return JSONResponse(status_code=200, content=result)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8787, reload=False)
