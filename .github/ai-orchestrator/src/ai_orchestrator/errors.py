"""HTTP + JSON envelopes for orchestrator errors (WEA-170 / WEA-171)."""

from __future__ import annotations

from typing import Any

_REFERENCE_PROVIDER = "gemini_flash"
_REFERENCE_PRICE_PER_1M = 0.075


def usage_zeros(duration_ms: int = 0) -> dict[str, Any]:
    return {
        "input_tokens": 0,
        "output_tokens": 0,
        "estimated_cost_usd": 0.0,
        "duration_ms": duration_ms,
    }


def cost_block_from_usage(usage: dict[str, Any]) -> dict[str, Any]:
    """Top-level `cost` object required by WEA-171 for success paths."""
    cloud = usage.get("estimated_cloud_equivalent_cost_usd")
    sav = usage.get("estimated_savings_usd")
    if cloud is None:
        cloud = 0.0
    if sav is None:
        sav = 0.0
    return {
        "estimated_cloud_equivalent_cost_usd": float(cloud),
        "estimated_savings_usd": float(sav),
        "reference_provider": _REFERENCE_PROVIDER,
        "reference_price_usd_per_1m_tokens": _REFERENCE_PRICE_PER_1M,
    }


def trim_usage_for_response(usage: dict[str, Any]) -> dict[str, Any]:
    """WEA-171 usage block (four numeric fields only in public contract)."""
    return {
        "input_tokens": int(usage.get("input_tokens") or 0),
        "output_tokens": int(usage.get("output_tokens") or 0),
        "estimated_cost_usd": float(usage.get("estimated_cost_usd") or 0.0),
        "duration_ms": int(usage.get("duration_ms") or 0),
    }


def normalize_adapter_success(
    body: dict[str, Any],
    *,
    is_fallback: bool,
    routing_reason: str,
) -> dict[str, Any]:
    """Attach `cost`, trim `usage`, ensure `error` null, set status for fallback."""
    out = dict(body)
    u = out.get("usage") if isinstance(out.get("usage"), dict) else {}
    out["usage"] = trim_usage_for_response(u)
    out["cost"] = cost_block_from_usage(u)
    out["routing_reason"] = routing_reason
    out["error"] = None
    if is_fallback:
        out["status"] = "fallback"
    return out


def finalize_adapter_error_payload(body: dict[str, Any]) -> dict[str, Any]:
    """Align adapter error dicts with WEA-171 (``output`` / ``cost`` / ``model_used``)."""
    b = dict(body)
    out = b.get("output")
    if out in ({}, [], None):
        b["output"] = None
    if "cost" not in b or b.get("cost") is None:
        b["cost"] = None
    mu = b.get("model_used")
    if mu == "":
        b["model_used"] = None
    return b


def error_envelope(
    task_id: str,
    *,
    code: str,
    message: str,
    routing_reason: str,
    provider_used: str = "none",
    model_used: str | None = None,
    retryable: bool = False,
    duration_ms: int = 0,
) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "status": "error",
        "provider_used": provider_used,
        "model_used": model_used,
        "output": None,
        "usage": usage_zeros(duration_ms=duration_ms),
        "cost": None,
        "routing_reason": routing_reason,
        "error": {"code": code, "message": message, "retryable": retryable},
    }


def http_status_for_adapter_error(code: str) -> int:
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
    if code == "adapter_misconfigured":
        return 503
    return 502


def http_for_exhausted_chain(chain_len: int, last_code: str) -> int:
    """After trying every provider: 502 if multiple candidates, else map last error."""
    if chain_len > 1:
        return 502
    return http_status_for_adapter_error(last_code)
