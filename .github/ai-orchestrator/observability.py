"""Structured run logs and dashboard aggregates — WEA-180.

Emits one JSON object per line (NDJSON) for external systems (e.g. Larridin)
when ``AI_ORCHESTRATOR_OBSERVABILITY_LOG`` is set, and retains a bounded in-memory
ring for the built-in ``/ops`` dashboard.
"""

from __future__ import annotations

import json
import os
import threading
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Literal

Period = Literal["day", "week", "month"]

_SCHEMA_VERSION = "weadu.ai_orchestrator.run_v1"
_SERVICE = "weadu-ai-orchestrator"

_lock = threading.Lock()
_ring: list[dict[str, Any]] = []
_ring_max = 8000
_log_path: str | None = None


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if raw.isdigit():
        return max(100, int(raw))
    return default


def _refresh_config() -> None:
    global _ring_max, _log_path
    _ring_max = _env_int("AI_ORCHESTRATOR_OBSERVABILITY_RING_MAX", 8000)
    p = os.environ.get("AI_ORCHESTRATOR_OBSERVABILITY_LOG", "").strip()
    _log_path = p if p else None


def reset_for_tests() -> None:
    """Clear in-memory ring (unit tests only)."""
    with _lock:
        _ring.clear()
    _refresh_config()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _append_ring(event: dict[str, Any]) -> None:
    _refresh_config()
    with _lock:
        _ring.append(event)
        overflow = len(_ring) - _ring_max
        if overflow > 0:
            del _ring[0:overflow]


def _append_file(event: dict[str, Any]) -> None:
    _refresh_config()
    if not _log_path:
        return
    line = json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"
    path = Path(_log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        with path.open("a", encoding="utf-8") as f:
            f.write(line)


def _usage_from_response(response: dict[str, Any] | None) -> dict[str, Any]:
    if not response or not isinstance(response.get("usage"), dict):
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "estimated_cost_usd": 0.0,
            "duration_ms": 0,
            "estimated_cloud_equivalent_cost_usd": None,
            "estimated_savings_usd": None,
        }
    u = response["usage"]
    assert isinstance(u, dict)

    def _f(key: str) -> float:
        v = u.get(key)
        if isinstance(v, (int, float)):
            return float(v)
        return 0.0

    def _opt_f(key: str) -> float | None:
        v = u.get(key)
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        return None

    def _i(key: str) -> int:
        v = u.get(key)
        if isinstance(v, int):
            return v
        if isinstance(v, float):
            return int(v)
        return 0

    return {
        "input_tokens": _i("input_tokens"),
        "output_tokens": _i("output_tokens"),
        "estimated_cost_usd": _f("estimated_cost_usd"),
        "duration_ms": _i("duration_ms"),
        "estimated_cloud_equivalent_cost_usd": _opt_f("estimated_cloud_equivalent_cost_usd"),
        "estimated_savings_usd": _opt_f("estimated_savings_usd"),
    }


def _error_from_response(response: dict[str, Any] | None) -> tuple[str | None, bool | None]:
    if not response or not isinstance(response.get("error"), dict):
        return None, None
    e = response["error"]
    code = e.get("code")
    retry = e.get("retryable")
    c = str(code) if code is not None else None
    r: bool | None
    if isinstance(retry, bool):
        r = retry
    else:
        r = None
    return c, r


def record_orchestrator_run(
    *,
    task_id: str,
    task_type: str | None,
    complexity: str | None,
    privacy_level: str | None,
    preferred_model: str | None,
    provider_resolved: str,
    http_status: int,
    response: dict[str, Any] | None,
    outcome: str,
    duration_wall_ms: int,
) -> None:
    """Append one observability event (memory + optional NDJSON file)."""
    usage = _usage_from_response(response)
    err_code, err_retry = _error_from_response(response)
    status = None
    provider_used = None
    model_used = None
    routing_reason = None
    if response:
        st = response.get("status")
        status = str(st) if st is not None else None
        pu = response.get("provider_used")
        provider_used = str(pu) if pu is not None else None
        mu = response.get("model_used")
        model_used = str(mu) if isinstance(mu, str) else None
        rr = response.get("routing_reason")
        routing_reason = str(rr) if isinstance(rr, str) else None

    event: dict[str, Any] = {
        "schema_version": _SCHEMA_VERSION,
        "ts": _utc_now_iso(),
        "service": _SERVICE,
        "event_type": "orchestrator.run",
        "outcome": outcome,
        "task_id": task_id,
        "task_type": task_type,
        "complexity": complexity,
        "privacy_level": privacy_level,
        "preferred_model": preferred_model,
        "provider_resolved": provider_resolved,
        "http_status": http_status,
        "status": status,
        "provider_used": provider_used,
        "model_used": model_used,
        "routing_reason": routing_reason,
        "duration_wall_ms": int(duration_wall_ms),
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
        "estimated_cost_usd": usage["estimated_cost_usd"],
        "usage_duration_ms": usage["duration_ms"],
        "estimated_cloud_equivalent_cost_usd": usage["estimated_cloud_equivalent_cost_usd"],
        "estimated_savings_usd": usage["estimated_savings_usd"],
        "error_code": err_code,
        "error_retryable": err_retry,
    }
    _append_ring(event)
    try:
        _append_file(event)
    except OSError:
        # Never block the request path on log IO failures
        pass


def _parse_ts(ts: str) -> datetime | None:
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def window_start_utc(period: Period) -> datetime:
    now = datetime.now(timezone.utc)
    if period == "day":
        return now - timedelta(days=1)
    if period == "week":
        return now - timedelta(days=7)
    return now - timedelta(days=30)


def list_events_for_period(period: Period) -> list[dict[str, Any]]:
    cutoff = window_start_utc(period)
    with _lock:
        snap = list(_ring)
    out: list[dict[str, Any]] = []
    for ev in snap:
        ts = ev.get("ts")
        if not isinstance(ts, str):
            continue
        dt = _parse_ts(ts)
        if dt is None or dt < cutoff:
            continue
        out.append(ev)
    return out


def compute_summary(period: Period) -> dict[str, Any]:
    events = list_events_for_period(period)
    now = datetime.now(timezone.utc)
    cutoff = window_start_utc(period)

    totals = {
        "requests": len(events),
        "errors": 0,
        "total_estimated_cost_usd": 0.0,
        "total_cloud_equivalent_usd": 0.0,
        "total_savings_usd": 0.0,
    }

    by_provider: dict[str, dict[str, Any]] = {}
    err_counter: Counter[str] = Counter()
    task_spend: list[dict[str, Any]] = []
    by_task_type: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "calls": 0,
            "total_cloud_equivalent_usd": 0.0,
            "total_savings_usd": 0.0,
            "total_latency_ms": 0,
        }
    )

    for ev in events:
        st = ev.get("status")
        ec = ev.get("error_code")
        if st == "error" or ec:
            totals["errors"] += 1
        if isinstance(ec, str) and ec:
            err_counter[ec] += 1

        prov = str(ev.get("provider_used") or ev.get("provider_resolved") or "unknown")
        if prov not in by_provider:
            by_provider[prov] = {
                "calls": 0,
                "total_estimated_cost_usd": 0.0,
                "total_cloud_equivalent_usd": 0.0,
                "total_savings_usd": 0.0,
                "total_latency_ms": 0,
            }
        bp = by_provider[prov]
        bp["calls"] += 1
        bp["total_estimated_cost_usd"] += float(ev.get("estimated_cost_usd") or 0.0)
        ce = ev.get("estimated_cloud_equivalent_cost_usd")
        if isinstance(ce, (int, float)):
            bp["total_cloud_equivalent_usd"] += float(ce)
            totals["total_cloud_equivalent_usd"] += float(ce)
        sv = ev.get("estimated_savings_usd")
        if isinstance(sv, (int, float)):
            bp["total_savings_usd"] += float(sv)
            totals["total_savings_usd"] += float(sv)
        lat = int(ev.get("duration_wall_ms") or 0)
        bp["total_latency_ms"] += lat

        totals["total_estimated_cost_usd"] += float(ev.get("estimated_cost_usd") or 0.0)

        tt = str(ev.get("task_type") or "unknown")
        bt = by_task_type[tt]
        bt["calls"] += 1
        if isinstance(ce, (int, float)):
            bt["total_cloud_equivalent_usd"] += float(ce)
        if isinstance(sv, (int, float)):
            bt["total_savings_usd"] += float(sv)
        bt["total_latency_ms"] += lat

        ce_f = float(ce) if isinstance(ce, (int, float)) else 0.0
        task_spend.append(
            {
                "task_id": ev.get("task_id"),
                "task_type": tt,
                "provider_used": prov,
                "estimated_cloud_equivalent_cost_usd": ce_f,
                "estimated_savings_usd": float(sv) if isinstance(sv, (int, float)) else None,
                "duration_wall_ms": lat,
                "status": st,
                "error_code": ec,
            }
        )

    for prov, bp in by_provider.items():
        c = max(1, int(bp["calls"]))
        bp["avg_latency_ms"] = round(bp["total_latency_ms"] / c, 2)

    for tt, bt in by_task_type.items():
        c = max(1, int(bt["calls"]))
        bt["avg_latency_ms"] = round(bt["total_latency_ms"] / c, 2)

    task_spend.sort(key=lambda x: x["estimated_cloud_equivalent_cost_usd"], reverse=True)
    errors_list = [{"error_code": k, "count": v} for k, v in err_counter.most_common()]

    task_type_rollup = [
        {
            "task_type": tt,
            "calls": int(v["calls"]),
            "total_cloud_equivalent_usd": round(v["total_cloud_equivalent_usd"], 6),
            "total_savings_usd": round(v["total_savings_usd"], 6),
            "avg_latency_ms": v["avg_latency_ms"],
        }
        for tt, v in sorted(
            by_task_type.items(),
            key=lambda kv: kv[1]["total_cloud_equivalent_usd"],
            reverse=True,
        )
    ]

    return {
        "period": period,
        "window_start": cutoff.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        "window_end": now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        "totals": {
            "requests": totals["requests"],
            "errors": totals["errors"],
            "total_estimated_cost_usd": round(totals["total_estimated_cost_usd"], 6),
            "total_cloud_equivalent_usd": round(totals["total_cloud_equivalent_usd"], 6),
            "total_savings_usd": round(totals["total_savings_usd"], 6),
        },
        "by_provider": by_provider,
        "by_task_type": task_type_rollup,
        "errors": errors_list,
        "top_tasks_by_cloud_equivalent": task_spend[:25],
    }


def dashboard_html() -> str:
    path = Path(__file__).resolve().parent / "static" / "dashboard.html"
    return path.read_text(encoding="utf-8")
