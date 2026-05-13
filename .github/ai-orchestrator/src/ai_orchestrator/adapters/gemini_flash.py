"""Google Gemini Flash adapter — HTTP only, no cloud fallback (WEA-171)."""

from __future__ import annotations

import json
import math
import os
import time
from typing import Any

import httpx

_GEMINI_FLASH_REF_USD_PER_1M = 0.075
_DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash").strip() or "gemini-2.0-flash"


def _http_post(
    url: str,
    *,
    headers: dict[str, str],
    json_body: dict[str, Any],
    timeout_sec: float,
    params: dict[str, str] | None = None,
) -> httpx.Response:
    with httpx.Client(timeout=timeout_sec) as client:
        return client.post(url, headers=headers, json=json_body, params=params)


def _build_prompt(req: dict[str, Any]) -> str:
    inp = req.get("input") or {}
    if not isinstance(inp, dict):
        return ""
    prompt = inp.get("prompt") or ""
    ctx = json.dumps(inp.get("context") or {}, ensure_ascii=False, separators=(",", ":"))
    data = json.dumps(inp.get("data") or [], ensure_ascii=False, separators=(",", ":"))
    return f"Prompt:\n{prompt}\n\nContext:\n{ctx}\n\nData:\n{data}"


def _usage(inp_t: int, out_t: int, dur_ms: int, est_cost: float) -> dict[str, Any]:
    total = inp_t + out_t
    ref = total * _GEMINI_FLASH_REF_USD_PER_1M / 1_000_000.0
    return {
        "input_tokens": inp_t,
        "output_tokens": out_t,
        "estimated_cost_usd": float(est_cost),
        "duration_ms": dur_ms,
        "estimated_cloud_equivalent_cost_usd": ref,
        "estimated_savings_usd": max(0.0, ref - float(est_cost)),
    }


def _err(
    task_id: str,
    *,
    code: str,
    message: str,
    retryable: bool,
    duration_ms: int,
) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "status": "error",
        "provider_used": "gemini_flash",
        "model_used": None,
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


def run(req: dict[str, Any]) -> dict[str, Any]:
    t0 = time.perf_counter()
    task_id = str(req.get("task_id", ""))
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return _err(
            task_id,
            code="adapter_misconfigured",
            message="GEMINI_API_KEY is not set",
            retryable=False,
            duration_ms=int((time.perf_counter() - t0) * 1000),
        )

    opts = req.get("options") if isinstance(req.get("options"), dict) else {}
    timeout_ms = int(opts.get("timeout_ms") or 30000)
    timeout_sec = max(1.0, timeout_ms / 1000.0)
    temperature = float(opts.get("temperature") if opts.get("temperature") is not None else 0.2)
    max_tokens = int(opts.get("max_tokens") or 1000)

    model = _DEFAULT_MODEL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    user_text = _build_prompt(req)
    body: dict[str, Any] = {
        "contents": [{"parts": [{"text": user_text}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }
    try:
        resp = _http_post(
            url,
            headers={"Content-Type": "application/json"},
            json_body=body,
            timeout_sec=timeout_sec,
            params={"key": api_key},
        )
    except httpx.TimeoutException:
        return _err(
            task_id,
            code="provider_timeout",
            message="Gemini request timed out",
            retryable=True,
            duration_ms=int((time.perf_counter() - t0) * 1000),
        )
    except httpx.RequestError as e:
        return _err(
            task_id,
            code="provider_unavailable",
            message=f"Gemini unreachable: {e}",
            retryable=True,
            duration_ms=int((time.perf_counter() - t0) * 1000),
        )

    dur = int((time.perf_counter() - t0) * 1000)
    if resp.status_code != 200:
        code = "provider_server_error" if resp.status_code >= 500 else "provider_bad_request"
        if resp.status_code in (401, 403):
            code = "provider_auth_error"
        return _err(
            task_id,
            code=code,
            message=f"Gemini HTTP {resp.status_code}",
            retryable=resp.status_code >= 500,
            duration_ms=dur,
        )

    try:
        payload = resp.json()
    except json.JSONDecodeError:
        return _err(
            task_id,
            code="provider_invalid_response",
            message="Gemini returned invalid JSON",
            retryable=True,
            duration_ms=dur,
        )

    text = ""
    if isinstance(payload, dict):
        cands = payload.get("candidates")
        if isinstance(cands, list) and cands:
            c0 = cands[0]
            if isinstance(c0, dict):
                content = c0.get("content")
                if isinstance(content, dict):
                    parts = content.get("parts")
                    if isinstance(parts, list) and parts and isinstance(parts[0], dict):
                        t = parts[0].get("text")
                        if isinstance(t, str):
                            text = t

    inp_t = out_t = 0
    meta = payload.get("usageMetadata") if isinstance(payload, dict) else None
    if isinstance(meta, dict):
        pt = meta.get("promptTokenCount")
        ct = meta.get("candidatesTokenCount")
        if isinstance(pt, int):
            inp_t = pt
        if isinstance(ct, int):
            out_t = ct
    if inp_t == 0 and out_t == 0:
        inp_t = int(math.ceil(len(user_text) / 4)) if user_text else 0
        out_t = int(math.ceil(len(text) / 4)) if text else 0

    total = inp_t + out_t
    est_cost = total * _GEMINI_FLASH_REF_USD_PER_1M / 1_000_000.0

    return {
        "task_id": task_id,
        "status": "success",
        "provider_used": "gemini_flash",
        "model_used": model,
        "output": {"text": text},
        "usage": _usage(inp_t, out_t, dur, est_cost),
        "routing_reason": "gemini_flash_completion",
        "error": None,
    }
