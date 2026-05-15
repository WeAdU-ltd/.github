"""
Adaptateur Google Gemini Flash — WEA-173.

- REST ``:generateContent`` (format ``RunRequest`` / ``RunResponse``)
- Clé API via en-tête ``x-goog-api-key`` (jamais dans l'URL ni les messages d'erreur)
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from typing import Any, Callable

from ai_orchestrator.adapters.base import BaseAdapter

# Tarifs indicatifs Gemini 1.5 Flash (USD / million de tokens) — ticket WEA-173
_INPUT_USD_PER_MILLION = 0.075
_OUTPUT_USD_PER_MILLION = 0.30

_DEFAULT_BASE = "https://generativelanguage.googleapis.com"
_DEFAULT_MODEL = "gemini-1.5-flash"

_SYSTEM_INSTRUCTION = (
    "You are running as WeAdU AI orchestrator. Use the provided context and data. "
    "Return a clear structured answer."
)

_TASK_TYPES = frozenset(
    {"classification", "generation", "extraction", "coding", "analysis"}
)
_COMPLEXITIES = frozenset({"low", "medium", "high"})
_PRIVACY = frozenset({"local_only", "standard", "external_allowed"})

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

_urlopen: Callable[..., Any] = urllib.request.urlopen


def _env_api_key() -> str:
    return os.environ.get("GEMINI_API_KEY", "").strip()


def _env_model() -> str:
    raw = os.environ.get("GEMINI_MODEL", "").strip()
    if raw:
        return raw
    legacy = os.environ.get("AI_ORCHESTRATOR_GEMINI_MODEL", "").strip()
    if legacy:
        return legacy
    return _DEFAULT_MODEL


def _env_base_url() -> str:
    raw = os.environ.get("GEMINI_BASE_URL", "").strip()
    if not raw:
        return _DEFAULT_BASE
    return raw.rstrip("/")


def _estimate_cost_usd(input_tokens: int, output_tokens: int) -> float:
    return (
        input_tokens * _INPUT_USD_PER_MILLION / 1_000_000.0
        + output_tokens * _OUTPUT_USD_PER_MILLION / 1_000_000.0
    )


def _build_user_text(inp: dict[str, Any]) -> str:
    prompt = inp.get("prompt") or ""
    ctx = json.dumps(inp.get("context") or {}, ensure_ascii=False, separators=(",", ":"))
    data = json.dumps(inp.get("data") or [], ensure_ascii=False, separators=(",", ":"))
    return f"Prompt:\n{prompt}\n\nContext:\n{ctx}\n\nData:\n{data}"


def _parse_json_body(raw: bytes) -> Any:
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _classify_http_error(status: int) -> tuple[str, bool]:
    if status == 400:
        return "provider_bad_request", False
    if status in (401, 403):
        return "provider_auth_error", False
    if status == 404:
        return "provider_not_found", False
    if status == 429:
        return "provider_rate_limited", True
    if status >= 500:
        return "provider_server_error", True
    return "provider_server_error", True


def _extract_response_text(payload: dict[str, Any]) -> str:
    cands = payload.get("candidates")
    if not isinstance(cands, list) or not cands:
        return ""
    c0 = cands[0]
    if not isinstance(c0, dict):
        return ""
    content = c0.get("content")
    if not isinstance(content, dict):
        return ""
    parts = content.get("parts")
    if not isinstance(parts, list):
        return ""
    chunks: list[str] = []
    for p in parts:
        if isinstance(p, dict) and isinstance(p.get("text"), str):
            chunks.append(p["text"])
    return "".join(chunks)


def _usage_from_metadata(meta: Any) -> tuple[int, int]:
    if not isinstance(meta, dict):
        return 0, 0
    pt = meta.get("promptTokenCount")
    ct = meta.get("candidatesTokenCount")
    inp = int(pt) if isinstance(pt, (int, float)) else 0
    out = int(ct) if isinstance(ct, (int, float)) else 0
    return max(0, inp), max(0, out)


def _routing_reason(req: dict[str, Any]) -> str:
    pm = req.get("preferred_model")
    if isinstance(pm, str) and pm.strip() == "gemini_flash":
        return "user_preferred_gemini_flash"
    if isinstance(pm, str) and pm.strip() == "auto":
        return "auto_routed_gemini_for_medium_complexity"
    return "gemini_flash_execution"


def _validate_run_request(req: dict[str, Any]) -> tuple[bool, str]:
    tid = req.get("task_id")
    if not isinstance(tid, str) or not _UUID_RE.match(tid):
        return False, "task_id must be a UUID string"
    tt = req.get("task_type")
    if tt not in _TASK_TYPES:
        return False, "invalid or missing task_type"
    cx = req.get("complexity")
    if cx not in _COMPLEXITIES:
        return False, "invalid or missing complexity"
    pv = req.get("privacy_level")
    if pv not in _PRIVACY:
        return False, "invalid or missing privacy_level"
    pm = req.get("preferred_model")
    if not isinstance(pm, str) or not pm.strip():
        return False, "preferred_model must be a non-empty string"
    inp = req.get("input")
    if not isinstance(inp, dict):
        return False, "input must be an object"
    if not isinstance(inp.get("prompt"), str):
        return False, "input.prompt must be a string"
    return True, ""


def _http_post_json(
    url: str,
    body: dict[str, Any],
    *,
    api_key: str,
    timeout_sec: float,
) -> tuple[int, bytes]:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-goog-api-key": api_key,
        },
    )
    try:
        with _urlopen(req, timeout=timeout_sec) as resp:  # type: ignore[misc]
            return int(resp.getcode()), resp.read()
    except urllib.error.HTTPError as e:
        return int(e.code), e.read()
    except TimeoutError:
        raise
    except OSError as e:
        raise ConnectionError(str(e)) from e
    except urllib.error.URLError as e:
        reason = e.reason
        if isinstance(reason, TimeoutError):
            raise TimeoutError(str(e)) from e
        if "timed out" in str(e).lower():
            raise TimeoutError(str(e)) from e
        raise ConnectionError(str(e)) from e


def _error_payload(
    task_id: str,
    *,
    code: str,
    message: str,
    retryable: bool,
    model_used: str,
    duration_ms: int = 0,
) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "status": "error",
        "provider_used": "gemini_flash",
        "model_used": model_used,
        "output": {},
        "usage": {
            "input_tokens": 0,
            "output_tokens": 0,
            "estimated_cost_usd": 0.0,
            "duration_ms": duration_ms,
            "estimated_cloud_equivalent_cost_usd": None,
            "estimated_savings_usd": None,
        },
        "routing_reason": "gemini_flash_adapter_error",
        "error": {"code": code, "message": message, "retryable": retryable},
    }


class GeminiFlashAdapter(BaseAdapter):
    """Appels ``generateContent`` vers Gemini Flash (modèle configurable)."""

    @property
    def provider_id(self) -> str:
        return "gemini_flash"

    def run(self, req: dict[str, Any]) -> dict[str, Any]:
        t0 = time.perf_counter()
        task_id = str(req.get("task_id", ""))
        model_cfg = _env_model()

        ok, msg = _validate_run_request(req)
        if not ok:
            return _error_payload(
                task_id or "00000000-0000-4000-8000-000000000000",
                code="validation_error",
                message=msg,
                retryable=False,
                model_used=model_cfg,
                duration_ms=int((time.perf_counter() - t0) * 1000),
            )

        api_key = _env_api_key()
        if not api_key:
            return _error_payload(
                task_id,
                code="provider_config_error",
                message="GEMINI_API_KEY is not configured",
                retryable=False,
                model_used=model_cfg,
                duration_ms=int((time.perf_counter() - t0) * 1000),
            )

        inp = req["input"]
        assert isinstance(inp, dict)
        user_text = _build_user_text(inp)
        options = req.get("options") if isinstance(req.get("options"), dict) else {}
        timeout_ms = int(options["timeout_ms"]) if options.get("timeout_ms") is not None else 30_000
        timeout_ms = max(1000, timeout_ms)
        timeout_sec = timeout_ms / 1000.0

        temperature = float(options["temperature"]) if options.get("temperature") is not None else 0.2
        max_tokens = int(options["max_tokens"]) if options.get("max_tokens") is not None else 1000

        base = _env_base_url()
        # Pas de clé dans l'URL — x-goog-api-key uniquement
        url = f"{base}/v1beta/models/{model_cfg}:generateContent"

        gemini_body: dict[str, Any] = {
            "systemInstruction": {"parts": [{"text": _SYSTEM_INSTRUCTION}]},
            "contents": [{"role": "user", "parts": [{"text": user_text}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        t_call = time.perf_counter()
        try:
            status, raw = _http_post_json(url, gemini_body, api_key=api_key, timeout_sec=timeout_sec)
        except TimeoutError:
            dur = int((time.perf_counter() - t0) * 1000)
            return _error_payload(
                task_id,
                code="provider_timeout",
                message=f"Gemini request exceeded timeout_ms={timeout_ms}",
                retryable=True,
                model_used=model_cfg,
                duration_ms=dur,
            )
        except ConnectionError as e:
            dur = int((time.perf_counter() - t0) * 1000)
            return _error_payload(
                task_id,
                code="provider_unavailable",
                message=f"Gemini endpoint is not reachable: {e}",
                retryable=True,
                model_used=model_cfg,
                duration_ms=dur,
            )

        call_duration_ms = int((time.perf_counter() - t_call) * 1000)
        total_duration_ms = int((time.perf_counter() - t0) * 1000)

        if status != 200:
            code, retry = _classify_http_error(status)
            return _error_payload(
                task_id,
                code=code,
                message=f"Gemini API returned HTTP {status}",
                retryable=retry,
                model_used=model_cfg,
                duration_ms=total_duration_ms,
            )

        payload = _parse_json_body(raw)
        if not isinstance(payload, dict):
            return _error_payload(
                task_id,
                code="provider_invalid_response",
                message="Gemini API returned invalid JSON",
                retryable=True,
                model_used=model_cfg,
                duration_ms=total_duration_ms,
            )

        text_out = _extract_response_text(payload)
        meta = payload.get("usageMetadata")
        in_tok, out_tok = _usage_from_metadata(meta)
        cost = _estimate_cost_usd(in_tok, out_tok)

        return {
            "task_id": task_id,
            "status": "success",
            "provider_used": "gemini_flash",
            "model_used": model_cfg,
            "output": {"text": text_out},
            "usage": {
                "input_tokens": in_tok,
                "output_tokens": out_tok,
                "estimated_cost_usd": cost,
                "duration_ms": call_duration_ms,
                "estimated_cloud_equivalent_cost_usd": None,
                "estimated_savings_usd": None,
            },
            "routing_reason": _routing_reason(req),
            "error": None,
        }
