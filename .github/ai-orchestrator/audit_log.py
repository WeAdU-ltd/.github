"""Journal d'audit NDJSON des appels POST /ai/run (WEA-179, Larridin-ready)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from schemas import RunRequest

AUDIT_SCHEMA_VERSION = 1

_DEFAULT_LOG_PATH = Path(__file__).resolve().parent / "var" / "ai_orchestrator_calls.jsonl"
_MAX_ERR_MSG = 500


def _audit_log_path() -> Path:
    raw = os.environ.get("AI_ORCHESTRATOR_AUDIT_LOG_PATH", "").strip()
    return Path(raw) if raw else _DEFAULT_LOG_PATH


def audit_logging_enabled() -> bool:
    return os.environ.get("AI_ORCHESTRATOR_AUDIT_LOG_DISABLED", "").strip().lower() not in (
        "1",
        "true",
        "yes",
    )


def append_audit_line(record: dict[str, Any]) -> None:
    if not audit_logging_enabled():
        return
    path = _audit_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
    with path.open("a", encoding="utf-8") as f:
        f.write(line)


def _usage_numbers(payload: dict[str, Any]) -> dict[str, Any]:
    usage = payload.get("usage") if isinstance(payload.get("usage"), dict) else {}
    u_in = usage.get("input_tokens")
    u_out = usage.get("output_tokens")
    dur = usage.get("duration_ms")
    cost = usage.get("estimated_cost_usd")
    cloud_eq = usage.get("estimated_cloud_equivalent_cost_usd")
    savings = usage.get("estimated_savings_usd")
    return {
        "input_tokens": int(u_in) if isinstance(u_in, (int, float)) else 0,
        "output_tokens": int(u_out) if isinstance(u_out, (int, float)) else 0,
        "duration_ms": int(dur) if isinstance(dur, (int, float)) else 0,
        "estimated_cost_usd": float(cost) if isinstance(cost, (int, float)) else 0.0,
        "estimated_cloud_equivalent_cost_usd": float(cloud_eq)
        if isinstance(cloud_eq, (int, float))
        else None,
        "estimated_savings_usd": float(savings) if isinstance(savings, (int, float)) else None,
    }


def _truncate_msg(msg: str) -> str:
    if len(msg) <= _MAX_ERR_MSG:
        return msg
    return msg[: _MAX_ERR_MSG - 3] + "..."


def build_record_from_run(
    req: RunRequest,
    response_body: dict[str, Any],
    *,
    http_status: int,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    err = response_body.get("error") if isinstance(response_body.get("error"), dict) else None
    err_code = str(err.get("code") or "") if err else ""
    err_msg = str(err.get("message") or "") if err else ""
    if err_msg:
        err_msg = _truncate_msg(err_msg)
    status = str(response_body.get("status") or "")
    u = _usage_numbers(response_body)
    return {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "ts_utc": now.isoformat().replace("+00:00", "Z"),
        "date_utc": now.date().isoformat(),
        "task_id": str(response_body.get("task_id") or str(req.task_id)),
        "task_type": str(req.task_type),
        "complexity": str(req.complexity),
        "privacy_level": str(req.privacy_level),
        "preferred_model": str(req.preferred_model),
        "http_status": int(http_status),
        "outcome_status": status,
        "provider_used": str(response_body.get("provider_used") or ""),
        "model_used": str(response_body.get("model_used") or ""),
        "routing_reason": str(response_body.get("routing_reason") or ""),
        "error_code": err_code or None,
        "error_message": err_msg or None,
        **u,
    }


def build_record_from_validation_failure(
    *,
    task_id: str,
    http_status: int,
    error_code: str,
    message: str,
    body_hint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    hint = body_hint or {}
    tt = hint.get("task_type")
    task_type = str(tt) if isinstance(tt, str) else "unknown"
    pm = hint.get("preferred_model")
    preferred = str(pm) if isinstance(pm, str) else ""
    return {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "ts_utc": now.isoformat().replace("+00:00", "Z"),
        "date_utc": now.date().isoformat(),
        "task_id": task_id,
        "task_type": task_type,
        "complexity": str(hint.get("complexity") or ""),
        "privacy_level": str(hint.get("privacy_level") or ""),
        "preferred_model": preferred,
        "http_status": int(http_status),
        "outcome_status": "error",
        "provider_used": "none",
        "model_used": "",
        "routing_reason": "request_validation_failed",
        "error_code": error_code,
        "error_message": _truncate_msg(message),
        "input_tokens": 0,
        "output_tokens": 0,
        "duration_ms": 0,
        "estimated_cost_usd": 0.0,
        "estimated_cloud_equivalent_cost_usd": None,
        "estimated_savings_usd": None,
    }
