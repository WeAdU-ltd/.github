"""Serveur MCP — expose l'orchestrateur IA aux agents (WEA-176)."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

import httpx
from mcp.server.fastmcp import FastMCP

_ORCH_ROOT = Path(__file__).resolve().parents[2]
if str(_ORCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_ORCH_ROOT))

from orch_log import settings as orch_log_settings  # noqa: E402
from routing import select_provider_chain  # noqa: E402
from schemas import RunRequest, RunInput, RunOptions  # noqa: E402

TaskType = Literal["analysis", "generation", "extraction", "coding", "classification"]
Complexity = Literal["low", "medium", "high"]
PrivacyLevel = Literal["local_only", "standard", "external_allowed"]
PreferredModel = Literal["auto", "local", "gemini_flash", "claude_haiku"]
CostPeriod = Literal["today", "last_7_days", "last_30_days"]

_MCP_HOST = os.environ.get("AI_ORCHESTRATOR_MCP_HOST", "127.0.0.1").strip() or "127.0.0.1"
_MCP_PORT = int(os.environ.get("AI_ORCHESTRATOR_MCP_PORT", "8788").strip() or "8788")

mcp = FastMCP(
    "weadu-ai",
    instructions="WeAdU AI orchestrator MCP — proxy HTTP vers POST /ai/run, prévisualisation route, coûts JSONL.",
    host=_MCP_HOST,
    port=_MCP_PORT,
)


def _api_base_url() -> str:
    host = os.environ.get("AI_ORCHESTRATOR_HOST", "127.0.0.1").strip() or "127.0.0.1"
    port = os.environ.get("AI_ORCHESTRATOR_PORT", "8787").strip() or "8787"
    return f"http://{host}:{port}".rstrip("/")


def _api_headers() -> dict[str, str]:
    token = os.environ.get("AI_ORCHESTRATOR_API_TOKEN", "").strip()
    h = {"Accept": "application/json", "Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _parse_ts(ts: str) -> datetime | None:
    try:
        s = ts.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _window_start(period: CostPeriod) -> datetime:
    now = datetime.now(timezone.utc)
    if period == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == "last_7_days":
        return now - timedelta(days=7)
    return now - timedelta(days=30)


def _ai_cost_summary_impl(period: CostPeriod) -> dict[str, Any]:
    path = orch_log_settings.log_path
    start = _window_start(period)
    by_provider: dict[str, dict[str, float | int]] = {}
    total_calls = 0
    error_calls = 0
    lm_savings = 0.0

    if not path.is_file():
        return {
            "period": period,
            "total_calls": 0,
            "error_count": 0,
            "error_rate": 0.0,
            "totals_by_provider": {},
            "lm_studio_estimated_savings_usd": 0.0,
            "log_path": str(path),
        }

    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts_raw = row.get("ts")
            if not isinstance(ts_raw, str):
                continue
            ts = _parse_ts(ts_raw)
            if ts is None or ts < start:
                continue

            total_calls += 1
            status = row.get("status")
            if status == "error":
                error_calls += 1

            prov = str(row.get("provider_used") or "unknown")
            bucket = by_provider.setdefault(
                prov,
                {"calls": 0, "estimated_cost_usd": 0.0, "errors": 0},
            )
            bucket["calls"] = int(bucket["calls"]) + 1
            cost = row.get("estimated_cost_usd")
            if isinstance(cost, (int, float)):
                bucket["estimated_cost_usd"] = float(bucket["estimated_cost_usd"]) + float(cost)
            if status == "error":
                bucket["errors"] = int(bucket["errors"]) + 1

            if prov == "lm_studio":
                sav = row.get("estimated_savings_usd")
                if isinstance(sav, (int, float)):
                    lm_savings += float(sav)

    err_rate = (error_calls / total_calls) if total_calls else 0.0
    return {
        "period": period,
        "total_calls": total_calls,
        "error_count": error_calls,
        "error_rate": round(err_rate, 6),
        "totals_by_provider": by_provider,
        "lm_studio_estimated_savings_usd": round(lm_savings, 6),
        "log_path": str(path),
    }


def _preview_request(
    complexity: Complexity,
    privacy_level: PrivacyLevel,
    preferred_model: PreferredModel | str,
) -> RunRequest:
    return RunRequest(
        task_id=uuid4(),
        task_type="analysis",
        complexity=complexity,
        privacy_level=privacy_level,
        preferred_model=preferred_model,
        input=RunInput(prompt="mcp_route_preview", context={}, data=[]),
        options=RunOptions(),
    )


def _ai_route_preview_impl(
    complexity: Complexity,
    privacy_level: PrivacyLevel,
    preferred_model: PreferredModel | str,
) -> dict[str, Any]:
    req = _preview_request(complexity, privacy_level, preferred_model)
    return select_provider_chain(req)


def _usage_zero() -> dict[str, Any]:
    return {
        "input_tokens": 0,
        "output_tokens": 0,
        "estimated_cost_usd": 0.0,
        "duration_ms": 0,
        "estimated_cloud_equivalent_cost_usd": None,
        "estimated_savings_usd": None,
    }


def _transport_error_response(task_id: str, message: str) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "status": "error",
        "provider_used": "none",
        "model_used": "",
        "output": {},
        "usage": _usage_zero(),
        "routing_reason": "mcp_transport_error",
        "error": {"code": "mcp_request_error", "message": message, "retryable": True},
    }


def _ai_run_impl(
    task_type: TaskType,
    complexity: Complexity,
    privacy_level: PrivacyLevel,
    prompt: str,
    context: dict[str, Any],
    preferred_model: PreferredModel | str,
) -> dict[str, Any]:
    tid = str(uuid4())
    body: dict[str, Any] = {
        "task_id": tid,
        "task_type": task_type,
        "complexity": complexity,
        "privacy_level": privacy_level,
        "preferred_model": preferred_model,
        "input": {"prompt": prompt, "context": context or {}, "data": []},
        "options": {
            "temperature": 0.2,
            "max_tokens": 1000,
            "timeout_ms": 30000,
        },
    }
    url = f"{_api_base_url()}/ai/run"
    try:
        with httpx.Client(timeout=120.0) as client:
            r = client.post(url, json=body, headers=_api_headers())
    except httpx.RequestError as e:
        return _transport_error_response(tid, str(e))
    try:
        payload: dict[str, Any] = r.json()
    except json.JSONDecodeError:
        return {
            "task_id": tid,
            "status": "error",
            "provider_used": "none",
            "model_used": "",
            "output": {},
            "usage": _usage_zero(),
            "routing_reason": "mcp_invalid_json_response",
            "error": {
                "code": "mcp_invalid_json",
                "message": r.text[:2000],
                "retryable": False,
            },
        }
    if not isinstance(payload, dict):
        return _transport_error_response(tid, "orchestrator returned non-object JSON")
    if "task_id" not in payload:
        payload = {**payload, "task_id": tid}
    return payload


@mcp.tool(name="ai_run")
def ai_run(
    task_type: TaskType,
    complexity: Complexity,
    privacy_level: PrivacyLevel,
    prompt: str,
    context: dict[str, Any] | None = None,
    preferred_model: PreferredModel | str = "auto",
) -> dict[str, Any]:
    """Exécute une tâche via POST /ai/run (orchestrateur local) ; retourne status HTTP + corps JSON."""
    return _ai_run_impl(
        task_type,
        complexity,
        privacy_level,
        prompt,
        context or {},
        preferred_model,
    )


@mcp.tool(name="ai_route_preview")
def ai_route_preview(
    complexity: Complexity,
    privacy_level: PrivacyLevel,
    preferred_model: PreferredModel | str,
) -> dict[str, Any]:
    """Indique le provider cible et la raison de routage sans exécuter l'adaptateur."""
    return _ai_route_preview_impl(complexity, privacy_level, preferred_model)


@mcp.tool(name="ai_cost_summary")
def ai_cost_summary(period: CostPeriod) -> dict[str, Any]:
    """Agrège coûts, appels et taux d'erreur depuis le fichier JSONL de l'orchestrateur."""
    return _ai_cost_summary_impl(period)


def main() -> None:
    raw = os.environ.get("AI_ORCHESTRATOR_MCP_TRANSPORT", "stdio").strip().lower()
    if raw in ("http", "sse"):
        transport: Literal["stdio", "sse", "streamable-http"] = "sse"
    elif raw in ("streamable-http", "streamable_http"):
        transport = "streamable-http"
    else:
        transport = "stdio"
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
