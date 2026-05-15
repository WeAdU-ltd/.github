"""Serveur MCP (transport stdio) — proxy vers POST /ai/run du wrapper FastAPI.

Exécution typique depuis Cursor : voir ``ORCHESTRATOR.md`` et le bloc MCP dans
``README.md`` à la racine du dépôt.

Variables d'environnement :

* ``WEADU_ORCHESTRATOR_URL`` — base HTTP du wrapper (défaut ``http://127.0.0.1:8787``).
* ``WEADU_ORCHESTRATOR_TIMEOUT_SEC`` — timeout client HTTP en secondes (défaut ``120``).
"""

from __future__ import annotations

import json
import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("WeAdU AI Orchestrator")


def _orchestrator_base() -> str:
    return os.environ.get("WEADU_ORCHESTRATOR_URL", "http://127.0.0.1:8787").rstrip("/")


def _timeout_sec() -> float:
    raw = os.environ.get("WEADU_ORCHESTRATOR_TIMEOUT_SEC", "120").strip()
    try:
        v = float(raw)
    except ValueError:
        return 120.0
    return max(1.0, v)


@mcp.tool(
    name="ai_run",
    description=(
        "Envoie un corps JSON RunRequest au wrapper WeAdU (POST /ai/run). "
        "Argument run_request_json : chaîne JSON complète du corps "
        "(task_id, task_type, complexity, privacy_level, preferred_model, input, options optionnel)."
    ),
)
async def ai_run(run_request_json: str) -> str:
    try:
        body: Any = json.loads(run_request_json)
    except json.JSONDecodeError as e:
        return json.dumps({"error": "invalid_json", "message": str(e)}, ensure_ascii=False)
    if not isinstance(body, dict):
        return json.dumps(
            {"error": "invalid_body", "message": "La racine JSON doit être un objet"},
            ensure_ascii=False,
        )
    url = f"{_orchestrator_base()}/ai/run"
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                url,
                json=body,
                headers={"Content-Type": "application/json"},
                timeout=_timeout_sec(),
            )
    except httpx.RequestError as e:
        return json.dumps({"error": "request_failed", "message": str(e)}, ensure_ascii=False)
    try:
        payload: Any = r.json()
    except json.JSONDecodeError:
        payload = {"_non_json_body": r.text[:2000]}
    return json.dumps({"http_status": r.status_code, "body": payload}, ensure_ascii=False)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
