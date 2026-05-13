"""Point d'entrée FastAPI — wrapper POST /ai/run (WEA-171)."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from lm_studio_adapter.adapter import run as lm_run
from routing import (
    CostCapExceededError,
    PrivacyViolationError,
    enforce_preflight_cost_cap,
    resolve_provider,
)
from schemas import RunRequest

logger = logging.getLogger(__name__)


def _usage_zero() -> dict[str, Any]:
    return {
        "input_tokens": 0,
        "output_tokens": 0,
        "estimated_cost_usd": 0.0,
        "duration_ms": 0,
        "estimated_cloud_equivalent_cost_usd": None,
        "estimated_savings_usd": None,
    }


def _error_envelope(
    task_id: str,
    *,
    code: str,
    message: str,
    provider_used: str = "lm_studio",
    model_used: str = "",
    routing_reason: str = "orchestrator_error",
    retryable: bool = False,
) -> dict[str, Any]:
    """Corps JSON aligné sur RunResponse (api_contract §4) pour les erreurs."""
    return {
        "task_id": task_id,
        "status": "error",
        "provider_used": provider_used,
        "model_used": model_used,
        "output": {},
        "usage": _usage_zero(),
        "routing_reason": routing_reason,
        "error": {"code": code, "message": message, "retryable": retryable},
    }


def _http_status_for_adapter_error(code: str) -> int:
    if code == "validation_error":
        return 422
    if code in ("provider_unavailable", "provider_timeout"):
        return 503
    if code in (
        "provider_bad_request",
        "provider_not_found",
        "provider_auth_error",
        "provider_invalid_response",
    ):
        return 400
    if code == "provider_rate_limited":
        return 429
    if code == "provider_server_error":
        return 502
    return 502


def _request_to_lm_payload(req: RunRequest) -> dict[str, Any]:
    """Sérialise la requête Pydantic pour ``lm_studio_adapter.run`` (dict JSON-like)."""
    data = req.model_dump(mode="python")
    data["task_id"] = str(data["task_id"])
    return data


def create_app() -> FastAPI:
    app = FastAPI(
        title="WeAdU AI Orchestrator",
        version="0.1.0",
        description="POST /ai/run — contrat specs/api_contract.md (WEA-170 / WEA-171).",
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        task_id = "00000000-0000-0000-0000-000000000000"
        try:
            body = await request.json()
            tid = body.get("task_id")
            if isinstance(tid, str) and tid:
                task_id = tid
        except Exception:
            pass
        msg = "; ".join(f"{e.get('loc')}: {e.get('msg')}" for e in exc.errors()[:8])
        payload = _error_envelope(
            task_id,
            code="validation_error",
            message=msg or "request validation failed",
            provider_used="none",
            routing_reason="pydantic_validation",
        )
        return JSONResponse(status_code=422, content=payload)

    @app.post("/ai/run")
    def post_ai_run(req: RunRequest) -> JSONResponse:
        """Exécute une requête IA via le routeur et l'adaptateur LM Studio si requis."""
        tid = str(req.task_id)

        try:
            provider = resolve_provider(req)
            enforce_preflight_cost_cap(req, provider)
        except PrivacyViolationError as e:
            payload = _error_envelope(
                tid,
                code="privacy_violation",
                message=e.message,
                provider_used="none",
                routing_reason="privacy_local_only_blocks_cloud",
            )
            return JSONResponse(status_code=400, content=payload)
        except CostCapExceededError as e:
            payload = _error_envelope(
                tid,
                code="cost_cap_exceeded",
                message=e.message,
                provider_used="none",
                routing_reason="cost_cap_exceeded_preflight",
            )
            return JSONResponse(status_code=400, content=payload)

        if provider != "lm_studio":
            payload = _error_envelope(
                tid,
                code="adapter_not_implemented",
                message=f"Provider {provider} is not available in this version",
                provider_used="none",
                routing_reason=f"routed_to_{provider}_not_implemented",
            )
            return JSONResponse(status_code=503, content=payload)

        payload = _request_to_lm_payload(req)
        try:
            result: dict[str, Any] = lm_run(payload)
        except Exception as e:
            logger.exception("lm_studio_adapter.run raised unexpectedly")
            payload = _error_envelope(
                tid,
                code="internal_error",
                message=str(e),
                provider_used="lm_studio",
                routing_reason="adapter_exception",
            )
            return JSONResponse(status_code=500, content=payload)

        if result.get("status") == "error" and isinstance(result.get("error"), dict):
            code = str(result["error"].get("code") or "error")
            http = _http_status_for_adapter_error(code)
            return JSONResponse(status_code=http, content=result)

        return JSONResponse(status_code=200, content=result)

    return app


app = create_app()
