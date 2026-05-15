"""
Adaptateur Anthropic Claude Haiku — WEA-174.

Messages API ``POST /v1/messages`` ; coût estimé depuis ``usage`` ; erreurs
429 / 529 / timeout ``retryable: true`` ; 401 ``retryable: false``.
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

# Tarifs indicatifs Claude Haiku (USD / million de tokens) — ticket WEA-174
_INPUT_USD_PER_MILLION = 0.80
_OUTPUT_USD_PER_MILLION = 4.00

_DEFAULT_MODEL = "claude-haiku-4-5"
_DEFAULT_BASE_URL = "https://api.anthropic.com"
_ANTHROPIC_VERSION = "2023-06-01"

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
    return os.environ.get("ANTHROPIC_API_KEY", "").strip()


def _env_model() -> str:
    raw = os.environ.get("ANTHROPIC_MODEL", "").strip()
    if raw:
        return raw
    legacy = os.environ.get("AI_ORCHESTRATOR_CLAUDE_MODEL", "").strip()
    return legacy or _DEFAULT_MODEL


def _env_base_url() -> str:
    raw = os.environ.get("ANTHROPIC_BASE_URL", "").strip()
    if not raw:
        return _DEFAULT_BASE_URL
    return raw.rstrip("/")


def _redact_secret(message: str, secret: str) -> str:
    if not secret or len(secret) < 8:
        return message
    if secret in message:
        return message.replace(secret, "[REDACTED]")
    return message


def _build_user_content(inp: dict[str, Any]) -> str:
    prompt = inp.get("prompt") or ""
    ctx_raw = inp.get("context") or {}
    ctx: dict[str, Any] = dict(ctx_raw) if isinstance(ctx_raw, dict) else {}
    ctx.pop("system", None)
    ctx_s = json.dumps(ctx, ensure_ascii=False, separators=(",", ":"))
    data = json.dumps(inp.get("data") or [], ensure_ascii=False, separators=(",", ":"))
    return f"Prompt:\n{prompt}\n\nContext:\n{ctx_s}\n\nData:\n{data}"


def _extract_system(inp: dict[str, Any]) -> str | None:
    ctx = inp.get("context")
    if not isinstance(ctx, dict):
        return None
    s = ctx.get("system")
    if isinstance(s, str) and s.strip():
        return s.strip()
    return None


def _estimate_cost_usd(input_tokens: int, output_tokens: int) -> float:
    return (
        input_tokens * _INPUT_USD_PER_MILLION + output_tokens * _OUTPUT_USD_PER_MILLION
    ) / 1_000_000.0


def _parse_json_body(raw: bytes) -> Any:
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _http_json(
    url: str,
    body: dict[str, Any],
    *,
    api_key: str,
    timeout_sec: float,
) -> tuple[int, bytes]:
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": api_key,
            "anthropic-version": _ANTHROPIC_VERSION,
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
    secret: str = "",
) -> dict[str, Any]:
    safe_msg = _redact_secret(message, secret)
    return {
        "task_id": task_id,
        "status": "error",
        "provider_used": "claude_haiku",
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
        "routing_reason": "claude_haiku_adapter_error",
        "error": {"code": code, "message": safe_msg, "retryable": retryable},
    }


def _classify_http_error(status: int) -> tuple[str, bool]:
    if status == 400:
        return "provider_bad_request", False
    if status == 401:
        return "provider_auth_error", False
    if status == 403:
        return "provider_auth_error", False
    if status == 404:
        return "provider_not_found", False
    if status == 429:
        return "provider_rate_limited", True
    if status == 529:
        return "provider_overloaded", True
    if status >= 500:
        return "provider_server_error", True
    return "provider_server_error", True


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


def _assistant_text(payload: dict[str, Any]) -> str:
    parts: list[str] = []
    content = payload.get("content")
    if isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text" and isinstance(block.get("text"), str):
                parts.append(block["text"])
    return "".join(parts)


def _read_usage_tokens(usage: Any) -> tuple[int, int]:
    if not isinstance(usage, dict):
        return 0, 0
    inp = usage.get("input_tokens")
    out = usage.get("output_tokens")
    it = int(inp) if isinstance(inp, (int, float)) else 0
    ot = int(out) if isinstance(out, (int, float)) else 0
    return it, ot


class ClaudeHaikuAdapter(BaseAdapter):
    """Appels Anthropic Messages API (Haiku / modèle ``ANTHROPIC_MODEL``)."""

    def run(self, req: dict[str, Any]) -> dict[str, Any]:
        t0 = time.perf_counter()
        task_id = str(req.get("task_id", ""))
        model_cfg = _env_model()
        secret = _env_api_key()

        ok, msg = _validate_run_request(req)
        if not ok:
            return _error_payload(
                task_id or "00000000-0000-0000-0000-000000000000",
                code="validation_error",
                message=msg,
                retryable=False,
                model_used=model_cfg,
                duration_ms=int((time.perf_counter() - t0) * 1000),
                secret=secret,
            )

        if not secret:
            return _error_payload(
                task_id,
                code="provider_auth_error",
                message="ANTHROPIC_API_KEY is not configured",
                retryable=False,
                model_used=model_cfg,
                duration_ms=int((time.perf_counter() - t0) * 1000),
                secret=secret,
            )

        inp = req["input"]
        assert isinstance(inp, dict)
        user_content = _build_user_content(inp)
        system = _extract_system(inp)

        options = req.get("options") if isinstance(req.get("options"), dict) else {}
        timeout_ms = int(options["timeout_ms"]) if options.get("timeout_ms") is not None else 30_000
        timeout_ms = max(1000, timeout_ms)
        timeout_sec = timeout_ms / 1000.0

        temperature = float(options["temperature"]) if options.get("temperature") is not None else 0.2
        max_tokens = int(options["max_tokens"]) if options.get("max_tokens") is not None else 1000

        body: dict[str, Any] = {
            "model": model_cfg,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": user_content}],
            "temperature": temperature,
        }
        if system:
            body["system"] = system

        base = _env_base_url()
        url = f"{base}/v1/messages"

        t_http = time.perf_counter()
        try:
            code, raw = _http_json(url, body, api_key=secret, timeout_sec=timeout_sec)
        except TimeoutError:
            dur = int((time.perf_counter() - t0) * 1000)
            return _error_payload(
                task_id,
                code="provider_timeout",
                message=f"POST /v1/messages exceeded timeout_ms={timeout_ms}",
                retryable=True,
                model_used=model_cfg,
                duration_ms=dur,
                secret=secret,
            )
        except ConnectionError as e:
            dur = int((time.perf_counter() - t0) * 1000)
            safe_e = _redact_secret(str(e), secret)
            return _error_payload(
                task_id,
                code="provider_unavailable",
                message=f"Anthropic API is not reachable: {safe_e}",
                retryable=True,
                model_used=model_cfg,
                duration_ms=dur,
                secret=secret,
            )

        duration_ms = int((time.perf_counter() - t_http) * 1000)
        total_duration_ms = int((time.perf_counter() - t0) * 1000)

        if code != 200:
            err_code, retry = _classify_http_error(code)
            parsed = _parse_json_body(raw)
            detail = ""
            if isinstance(parsed, dict):
                em = parsed.get("error")
                if isinstance(em, dict) and isinstance(em.get("message"), str):
                    detail = em["message"]
                elif isinstance(em, str):
                    detail = em
            base_msg = f"POST /v1/messages returned HTTP {code}"
            message = f"{base_msg}: {detail}" if detail else base_msg
            message = _redact_secret(message, secret)
            return _error_payload(
                task_id,
                code=err_code,
                message=message,
                retryable=retry,
                model_used=model_cfg,
                duration_ms=total_duration_ms,
                secret=secret,
            )

        payload = _parse_json_body(raw)
        if not isinstance(payload, dict):
            return _error_payload(
                task_id,
                code="provider_invalid_response",
                message="POST /v1/messages returned invalid JSON",
                retryable=True,
                model_used=model_cfg,
                duration_ms=total_duration_ms,
                secret=secret,
            )

        text_out = _assistant_text(payload)
        model_used = payload.get("model")
        if not isinstance(model_used, str) or not model_used:
            model_used = model_cfg

        usage_raw = payload.get("usage")
        in_tok, out_tok = _read_usage_tokens(usage_raw)
        est_cost = _estimate_cost_usd(in_tok, out_tok)

        return {
            "task_id": task_id,
            "status": "success",
            "provider_used": "claude_haiku",
            "model_used": model_used,
            "output": {"text": text_out},
            "usage": {
                "input_tokens": in_tok,
                "output_tokens": out_tok,
                "estimated_cost_usd": est_cost,
                "duration_ms": duration_ms,
                "estimated_cloud_equivalent_cost_usd": None,
                "estimated_savings_usd": None,
            },
            "routing_reason": "cloud execution via Anthropic Claude Haiku",
            "error": None,
        }
