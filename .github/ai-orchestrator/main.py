"""Point d'entrée FastAPI — wrapper POST /ai/run (WEA-171 / WEA-175)."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

_ORCH_ROOT = Path(__file__).resolve().parent
_SRC = _ORCH_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ai_orchestrator.adapter_registry import adapter_registry, get_adapter

from lm_studio_adapter.adapter import run as lm_run
from router import PrivacyViolationError, select_provider
from schemas import RunRequest

logger = logging.getLogger(__name__)

# Adapters déployés sur cette instance (WEA-175) — aligné avec les modules présents.
ORCHESTRATOR_AVAILABLE_ADAPTERS: list[str] = [
    "lm_studio",
    "gemini_flash",
    "claude_haiku",
]


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
    if code in ("provider_unavailable", "provider_timeout", "provider_config_error"):
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
    if code == "provider_overloaded":
        return 503
    if code == "provider_server_error":
        return 502
    return 502


def _request_to_lm_payload(req: RunRequest) -> dict[str, Any]:
    """Sérialise la requête Pydantic pour ``lm_studio_adapter.run`` (dict JSON-like)."""
    data = req.model_dump(mode="python")
    data["task_id"] = str(data["task_id"])
    return data


def _adapter_json_response(
    tid: str,
    decision_rr: str,
    result: dict[str, Any],
) -> JSONResponse:
    if result.get("status") == "error" and isinstance(result.get("error"), dict):
        code = str(result["error"].get("code") or "error")
        http = _http_status_for_adapter_error(code)
        rr = result.get("routing_reason") or decision_rr
        if isinstance(rr, str) and decision_rr not in rr:
            rr = f"{decision_rr}; {rr}"
        merged = {**result, "routing_reason": rr}
        return JSONResponse(status_code=http, content=merged)

    rr_out = result.get("routing_reason")
    if isinstance(rr_out, str) and rr_out.strip():
        merged_rr = f"{decision_rr}; {rr_out}"
    else:
        merged_rr = decision_rr
    return JSONResponse(status_code=200, content={**result, "routing_reason": merged_rr})


def create_app() -> FastAPI:
    app = FastAPI(
        title="WeAdU AI Orchestrator",
        version="0.1.0",
        description="POST /ai/run — contrat specs/api_contract.md (WEA-170 / WEA-171 / WEA-175).",
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
        """Exécute une requête IA via le routeur intelligent puis les adaptateurs disponibles."""
        tid = str(req.task_id)

        try:
            decision = select_provider(req, ORCHESTRATOR_AVAILABLE_ADAPTERS)
        except PrivacyViolationError as e:
            payload = _error_envelope(
                tid,
                code="privacy_violation",
                message=e.message,
                provider_used="none",
                routing_reason="privacy_violation",
            )
            return JSONResponse(status_code=400, content=payload)

        if decision.provider == "none":
            payload = _error_envelope(
                tid,
                code="routing_blocked",
                message="no runnable provider under current constraints",
                provider_used="none",
                routing_reason=decision.routing_reason,
            )
            return JSONResponse(status_code=422, content=payload)

        chain = [decision.provider, *decision.fallback_chain]
        tried_cloud: list[str] = []
        avail = set(ORCHESTRATOR_AVAILABLE_ADAPTERS)

        for prov in chain:
            if prov not in avail:
                tried_cloud.append(prov)
                continue

            payload_d = _request_to_lm_payload(req)

            if prov == "lm_studio":
                try:
                    result: dict[str, Any] = lm_run(payload_d)
                except Exception as e:
                    logger.exception("lm_studio_adapter.run raised unexpectedly")
                    return JSONResponse(
                        status_code=500,
                        content=_error_envelope(
                            tid,
                            code="internal_error",
                            message=str(e),
                            provider_used="lm_studio",
                            routing_reason=f"{decision.routing_reason}; adapter_exception",
                        ),
                    )
                return _adapter_json_response(tid, decision.routing_reason, result)

            if prov == "gemini_flash":
                adapter = get_adapter("gemini_flash")
                if adapter is None:
                    tried_cloud.append(prov)
                    continue
                try:
                    result = adapter.run(payload_d)
                except Exception as e:
                    logger.exception("gemini_flash adapter.run raised unexpectedly")
                    return JSONResponse(
                        status_code=500,
                        content=_error_envelope(
                            tid,
                            code="internal_error",
                            message=str(e),
                            provider_used="gemini_flash",
                            routing_reason=f"{decision.routing_reason}; adapter_exception",
                        ),
                    )
                return _adapter_json_response(tid, decision.routing_reason, result)

            if prov == "claude_haiku":
                try:
                    result = adapter_registry["claude_haiku"](payload_d)
                except Exception as e:
                    logger.exception("claude_haiku adapter raised unexpectedly")
                    return JSONResponse(
                        status_code=500,
                        content=_error_envelope(
                            tid,
                            code="internal_error",
                            message=str(e),
                            provider_used="claude_haiku",
                            routing_reason=f"{decision.routing_reason}; adapter_exception",
                        ),
                    )
                return _adapter_json_response(tid, decision.routing_reason, result)

            tried_cloud.append(prov)

        first = tried_cloud[0] if tried_cloud else decision.provider
        return JSONResponse(
            status_code=503,
            content=_error_envelope(
                tid,
                code="adapter_not_implemented",
                message=f"Provider {first} is not available in this version",
                provider_used="none",
                routing_reason=f"{decision.routing_reason}; routed_to_{first}_not_implemented",
            ),
        )

    return app


app = create_app()
