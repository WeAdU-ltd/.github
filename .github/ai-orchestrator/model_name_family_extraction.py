"""WEA-182 — extraction ``model_name`` / ``model_family`` via ``POST /ai/run``.

Référence métier recommandée par le ticket : même rôle que l'extraction dans le
pipeline Negative Terms (module applicatif ``ta_ga_product_title_cache`` — hors
de ce dépôt ; noter le fichier et la ligne exacts sur le ticket Linear WEA-182
lors de l'intégration dans l'app).

- ``USE_ORCHESTRATOR=true`` (défaut) : HTTP ``POST {AI_ORCHESTRATOR_URL}/ai/run`` uniquement ;
  aucune clé fournisseur locale, pas de calcul de coût côté appelant (usage dans la réponse).
- ``USE_ORCHESTRATOR=false`` : rollback — appel **in-process** à
  ``lm_studio_adapter.adapter.run`` (équivalent local sans hop HTTP ; en prod
  Negative Terms ce drapeau rétablit l'appel direct historique au cloud).

La logique métier (prompt + parsing JSON) reste dans ce module, pas dans le routeur FastAPI.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from typing import Any

import httpx

_EXTRACTION_INSTRUCTIONS = (
    "You extract product model identifiers from a Google Shopping style title. "
    'Reply with a single JSON object only, keys "model_name" and "model_family" '
    "(strings, use empty string if unknown). No markdown, no commentary."
)


def build_extraction_prompt(product_title: str) -> str:
    title = (product_title or "").strip()
    return f"{_EXTRACTION_INSTRUCTIONS}\n\nTitle:\n{title}\n"


def parse_model_name_family_from_llm_text(raw: str) -> dict[str, str | None]:
    """Parse structured fields from model output (tolerant of fences / noise)."""
    text = (raw or "").strip()
    if "```" in text:
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if m:
            text = m.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return {"model_name": None, "model_family": None}
    try:
        obj = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {"model_name": None, "model_family": None}
    if not isinstance(obj, dict):
        return {"model_name": None, "model_family": None}
    mn = obj.get("model_name")
    mf = obj.get("model_family")
    return {
        "model_name": mn if isinstance(mn, str) else None,
        "model_family": mf if isinstance(mf, str) else None,
    }


def _use_orchestrator() -> bool:
    v = os.environ.get("USE_ORCHESTRATOR", "true").strip().lower()
    return v in ("1", "true", "yes", "on")


def _orchestrator_base_url() -> str:
    return os.environ.get("AI_ORCHESTRATOR_URL", "http://127.0.0.1:8787").strip().rstrip("/")


def _run_request_payload(product_title: str, task_id: uuid.UUID) -> dict[str, Any]:
    return {
        "task_id": str(task_id),
        "task_type": "extraction",
        "complexity": "low",
        "privacy_level": "local_only",
        "preferred_model": "local",
        "input": {
            "prompt": build_extraction_prompt(product_title),
            "context": {"migration": "WEA-182", "caller": "model_name_family_extraction"},
            "data": [],
        },
        "options": {"temperature": 0.1, "max_tokens": 256, "timeout_ms": 60_000},
    }


def _via_orchestrator_http(product_title: str) -> dict[str, Any]:
    tid = uuid.uuid4()
    url = f"{_orchestrator_base_url()}/ai/run"
    payload = _run_request_payload(product_title, tid)
    headers: dict[str, str] = {"Content-Type": "application/json", "Accept": "application/json"}
    key = os.environ.get("AI_ORCHESTRATOR_API_KEY", "").strip()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    timeout = httpx.Timeout(120.0, connect=30.0)
    with httpx.Client(timeout=timeout) as client:
        r = client.post(url, json=payload, headers=headers)
    try:
        body = r.json()
    except json.JSONDecodeError:
        return {
            "ok": False,
            "error": f"orchestrator_non_json_http_{r.status_code}",
            "model_name": None,
            "model_family": None,
            "raw_text": "",
        }
    if r.status_code != 200 or body.get("status") != "success":
        err = body.get("error") if isinstance(body.get("error"), dict) else {}
        code = err.get("code") if isinstance(err, dict) else None
        return {
            "ok": False,
            "error": str(code or f"http_{r.status_code}"),
            "model_name": None,
            "model_family": None,
            "raw_text": "",
            "orchestrator_body": body,
        }
    out = body.get("output") if isinstance(body.get("output"), dict) else {}
    text = out.get("text") if isinstance(out.get("text"), str) else ""
    parsed = parse_model_name_family_from_llm_text(text)
    return {
        "ok": True,
        "error": None,
        "model_name": parsed["model_name"],
        "model_family": parsed["model_family"],
        "raw_text": text,
        "orchestrator_body": body,
    }


def _legacy_inprocess_lm_adapter(product_title: str) -> dict[str, Any]:
    """Rollback: bypass HTTP orchestrator; same prompt/parse path (LM Studio in CI)."""
    from lm_studio_adapter.adapter import run as lm_run

    tid = uuid.uuid4()
    payload = _run_request_payload(product_title, tid)
    result: dict[str, Any] = lm_run(payload)
    if result.get("status") != "success":
        err = result.get("error") if isinstance(result.get("error"), dict) else {}
        code = err.get("code") if isinstance(err, dict) else None
        return {
            "ok": False,
            "error": str(code or "lm_adapter_error"),
            "model_name": None,
            "model_family": None,
            "raw_text": "",
            "orchestrator_body": None,
        }
    out = result.get("output") if isinstance(result.get("output"), dict) else {}
    text = out.get("text") if isinstance(out.get("text"), str) else ""
    parsed = parse_model_name_family_from_llm_text(text)
    return {
        "ok": True,
        "error": None,
        "model_name": parsed["model_name"],
        "model_family": parsed["model_family"],
        "raw_text": text,
        "orchestrator_body": result,
    }


def extract_model_name_family_from_product_title(product_title: str) -> dict[str, Any]:
    """
    Extraction structurée pour titres produit (équivalent métier WEA-182).

    Environnement :
      ``USE_ORCHESTRATOR`` — ``true``/``false`` (défaut ``true``).
      ``AI_ORCHESTRATOR_URL`` — base HTTP de l'orchestrateur (défaut ``http://127.0.0.1:8787``).
      ``AI_ORCHESTRATOR_API_KEY`` — optionnel, header Bearer.
    """
    if _use_orchestrator():
        return _via_orchestrator_http(product_title)
    return _legacy_inprocess_lm_adapter(product_title)
