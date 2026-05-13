"""Append-only audit lines for POST /ai/run (WEA-178) — ``ai_orchestrator.jsonl``."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def _jsonl_path() -> str | None:
    """Audit JSONL is opt-in: set ``AI_ORCHESTRATOR_JSONL`` to a file path (ex. ``ai_orchestrator.jsonl``)."""
    if "AI_ORCHESTRATOR_JSONL" not in os.environ:
        return None
    raw = os.environ["AI_ORCHESTRATOR_JSONL"].strip()
    if not raw or raw.lower() in ("0", "false", "off"):
        return None
    return raw


def append_ai_run_audit(record: dict[str, Any]) -> None:
    """Write one UTF-8 JSON line; never raises (logging only)."""
    path = _jsonl_path()
    if not path:
        return
    try:
        line = json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError:
        logger.warning("ai_orchestrator jsonl append failed", exc_info=True)


def build_audit_record_from_run_response(body: dict[str, Any]) -> dict[str, Any]:
    """Minimal stable fields for operators (no full prompt)."""
    usage = body.get("usage") if isinstance(body.get("usage"), dict) else {}
    return {
        "task_id": body.get("task_id"),
        "status": body.get("status"),
        "provider_used": body.get("provider_used"),
        "model_used": body.get("model_used"),
        "routing_reason": body.get("routing_reason"),
        "estimated_cost_usd": usage.get("estimated_cost_usd"),
        "estimated_cloud_equivalent_cost_usd": usage.get("estimated_cloud_equivalent_cost_usd"),
        "estimated_savings_usd": usage.get("estimated_savings_usd"),
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "duration_ms": usage.get("duration_ms"),
        "error_code": (body.get("error") or {}).get("code") if isinstance(body.get("error"), dict) else None,
    }
