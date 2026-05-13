"""FastAPI application — POST /ai/run universal AI wrapper (WEA-171)."""

from __future__ import annotations

import logging
import time
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from ai_orchestrator.adapter_registry import get_adapter_run
from ai_orchestrator.config import load_settings
from ai_orchestrator.contracts import RunRequest
from ai_orchestrator import errors as err
from ai_orchestrator.logging import append_run_log
from ai_orchestrator.router import PrivacyViolationError, build_provider_chain

logger = logging.getLogger(__name__)


def _auth_response(request: Request, settings: Any, task_id: str) -> JSONResponse | None:
    if not settings.api_token:
        return None
    auth = request.headers.get("authorization") or ""
    if not auth.startswith("Bearer "):
        body = err.error_envelope(
            task_id,
            code="invalid_token",
            message="Authorization: Bearer <token> header required",
            routing_reason="api_token_configured",
            provider_used="none",
        )
        return JSONResponse(status_code=401, content=body)
    got = auth.removeprefix("Bearer ").strip()
    if got != settings.api_token:
        body = err.error_envelope(
            task_id,
            code="invalid_token",
            message="Bearer token mismatch",
            routing_reason="api_token_configured",
            provider_used="none",
        )
        return JSONResponse(status_code=401, content=body)
    return None


def _run_orchestration(req: RunRequest, settings: Any) -> tuple[int, dict[str, Any]]:
    tid = str(req.task_id)
    t0 = time.perf_counter()
    try:
        chain = build_provider_chain(req)
    except PrivacyViolationError as e:
        body = err.error_envelope(
            tid,
            code="privacy_violation",
            message=e.message,
            routing_reason="privacy_local_only_blocks_cloud",
            provider_used="none",
        )
        return 400, body

    payload = req.to_adapter_dict()
    last: dict[str, Any] | None = None
    for idx, prov in enumerate(chain):
        try:
            runner = get_adapter_run(prov)
        except KeyError:
            body = err.error_envelope(
                tid,
                code="unknown_provider",
                message=f"Unknown provider id: {prov}",
                routing_reason="adapter_registry",
                provider_used="none",
            )
            return 400, body
        try:
            out = runner(payload)
        except Exception as ex:  # noqa: BLE001
            logger.exception("Adapter %s raised unexpectedly", prov)
            body = err.error_envelope(
                tid,
                code="internal_error",
                message=str(ex),
                routing_reason="adapter_exception",
                provider_used=prov,
            )
            return 500, body

        last = out
        if out.get("status") == "success":
            is_fallback = idx > 0
            base_reason = str(out.get("routing_reason") or "adapter_success")
            rr = f"fallback_after_{chain[idx - 1]}_failed" if is_fallback else base_reason
            norm = err.normalize_adapter_success(
                out,
                is_fallback=is_fallback,
                routing_reason=rr,
            )
            append_run_log(
                settings.log_path,
                task_id=tid,
                status=str(norm.get("status")),
                provider_used=str(norm.get("provider_used")),
                chain=[str(p) for p in chain],
                routing_reason=str(norm.get("routing_reason")),
                duration_ms=int((time.perf_counter() - t0) * 1000),
            )
            return 200, norm

    if not last:
        body = err.error_envelope(
            tid,
            code="internal_error",
            message="no adapter result",
            routing_reason="empty_chain_result",
            provider_used="none",
        )
        return 500, body

    fe = err.finalize_adapter_error_payload(last)
    if isinstance(fe.get("usage"), dict):
        fe["usage"] = err.trim_usage_for_response(fe["usage"])
    ec = fe.get("error") if isinstance(fe.get("error"), dict) else {}
    last_code = str(ec.get("code") or "error")
    http = err.http_for_exhausted_chain(len(chain), last_code)
    append_run_log(
        settings.log_path,
        task_id=tid,
        status="error",
        provider_used=str(fe.get("provider_used") or "none"),
        chain=[str(p) for p in chain],
        routing_reason=str(fe.get("routing_reason") or "all_failed"),
        duration_ms=int((time.perf_counter() - t0) * 1000),
        extra={"error_code": last_code},
    )
    return http, fe


def create_app() -> FastAPI:
    settings = load_settings()
    app = FastAPI(
        title="WeAdU AI Orchestrator",
        version="0.3.0",
        description="POST /ai/run — universal contract (WEA-170 / WEA-171).",
    )

    if settings.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
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
        msg = "; ".join(f"{e.get('loc')}: {e.get('msg')}" for e in exc.errors()[:12])
        payload = err.error_envelope(
            task_id,
            code="validation_error",
            message=msg or "request validation failed",
            routing_reason="pydantic_validation",
            provider_used="none",
        )
        return JSONResponse(status_code=422, content=payload)

    @app.post("/ai/run")
    def post_ai_run(request: Request, req: RunRequest) -> JSONResponse:
        settings = load_settings()
        bad = _auth_response(request, settings, str(req.task_id))
        if bad is not None:
            return bad
        try:
            status, body = _run_orchestration(req, settings)
        except Exception as ex:  # noqa: BLE001
            logger.exception("orchestrator internal failure")
            body = err.error_envelope(
                str(req.task_id),
                code="internal_error",
                message=str(ex),
                routing_reason="orchestrator_unhandled",
                provider_used="none",
            )
            return JSONResponse(status_code=500, content=body)
        return JSONResponse(status_code=status, content=body)

    return app


app = create_app()


def main() -> None:
    import uvicorn

    s = load_settings()
    uvicorn.run(create_app(), host=s.host, port=s.port, log_level="info")


if __name__ == "__main__":
    main()
