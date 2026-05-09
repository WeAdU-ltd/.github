"""
Adaptateur LM Studio — WEA-172.

- API exclusive : POST /v1/chat/completions, GET /v1/models
- Contrat d’entrée / sortie aligné sur specs/api_contract.md (WEA-170)
- Pas de logique métier ; pas de secrets en dur ; pas de fallback cloud

Résolution du champ ``preferred_model`` (contrat universel, aligné sur
``specs/api_contract.md``) :

- **``local`` ou ``auto``** : l’identifiant LM Studio pour le JSON ``model`` est
  résolu via les variables d’environnement ``LM_STUDIO_MODEL_LOW`` si
  ``complexity`` vaut ``low``, sinon ``LM_STUDIO_MODEL_DEFAULT`` (repli
  ``gemma-4`` si absentes). Ces deux tokens sont les **seuls** qui déclenchent
  cette résolution pilotée par l’environnement.
- **Toute autre chaîne non vide** : envoyée **telle quelle** (après ``strip()``)
  comme champ ``model`` vers LM Studio — nom exact côté serveur LM ; doit
  apparaître dans ``GET /v1/models``.
- **``gemini_flash`` / ``claude_haiku``** : refusées dans cet adaptateur (ce ne
  sont pas des ids LM Studio ; le routeur ne doit pas les envoyer ici).
"""

from __future__ import annotations

import json
import math
import os
import re
import time
import urllib.error
import urllib.request
from typing import Any, Callable

# Référence coût équivalent cloud (USD / million de tokens) — spec WEA-172
_GEMINI_FLASH_USD_PER_MILLION_TOKENS = 0.075

_DEFAULT_BASE = "http://localhost:1234"
_DEFAULT_MODEL = "gemma-4"
_SYSTEM_MESSAGE = (
    "You are running as WeAdU local AI orchestrator. Use the provided context and data. "
    "Return a clear structured answer."
)

_TASK_TYPES = frozenset(
    {"classification", "generation", "extraction", "coding", "analysis"}
)
_COMPLEXITIES = frozenset({"low", "medium", "high"})
_PRIVACY = frozenset({"local_only", "standard", "external_allowed"})
# Résolution LM via variables d'environnement (LOW / DEFAULT) — api_contract §2.4
_LM_ENV_ROUTED = frozenset({"local", "auto"})
# Enums « cloud » du contrat : interdites dans l'adaptateur LM uniquement
_CLOUD_PROVIDER_ENUM = frozenset({"gemini_flash", "claude_haiku"})

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

# Injection de tests uniquement (même signature que urllib.request.urlopen)
_urlopen: Callable[..., Any] = urllib.request.urlopen


def _env_base_url() -> str:
    raw = os.environ.get("LM_STUDIO_BASE_URL", "").strip()
    if not raw:
        return _DEFAULT_BASE
    return raw.rstrip("/")


def _env_model_low() -> str:
    return os.environ.get("LM_STUDIO_MODEL_LOW", "").strip() or _DEFAULT_MODEL


def _env_model_default() -> str:
    return os.environ.get("LM_STUDIO_MODEL_DEFAULT", "").strip() or _DEFAULT_MODEL


def _env_timeout_ms() -> int:
    raw = os.environ.get("LM_STUDIO_TIMEOUT_MS", "").strip()
    if raw.isdigit():
        return int(raw)
    return 30000


def _env_api_key() -> str:
    return os.environ.get("LM_STUDIO_API_KEY", "").strip()


def _headers() -> dict[str, str]:
    h = {"Content-Type": "application/json", "Accept": "application/json"}
    key = _env_api_key()
    if key:
        h["Authorization"] = f"Bearer {key}"
    return h


def _http_json(
    method: str,
    url: str,
    *,
    body: dict[str, Any] | None,
    timeout_sec: float,
) -> tuple[int, bytes]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=_headers())
    try:
        with _urlopen(req, timeout=timeout_sec) as resp:  # type: ignore[misc]
            code = resp.getcode()
            raw = resp.read()
            return int(code), raw
    except urllib.error.HTTPError as e:
        return int(e.code), e.read()
    except TimeoutError:
        raise
    except OSError as e:
        # connexion refusée, reset peer, etc.
        raise ConnectionError(str(e)) from e
    except urllib.error.URLError as e:
        reason = e.reason
        if isinstance(reason, TimeoutError):
            raise TimeoutError(str(e)) from e
        if "timed out" in str(e).lower():
            raise TimeoutError(str(e)) from e
        raise ConnectionError(str(e)) from e


def _parse_json_body(raw: bytes) -> Any:
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _list_model_ids(models_payload: Any) -> list[str]:
    if not isinstance(models_payload, dict):
        return []
    data = models_payload.get("data")
    if not isinstance(data, list):
        return []
    ids: list[str] = []
    for item in data:
        if isinstance(item, dict) and "id" in item and isinstance(item["id"], str):
            ids.append(item["id"])
    return ids


def _build_user_content(inp: dict[str, Any]) -> str:
    prompt = inp.get("prompt") or ""
    ctx = json.dumps(inp.get("context") or {}, ensure_ascii=False, separators=(",", ":"))
    data = json.dumps(inp.get("data") or [], ensure_ascii=False, separators=(",", ":"))
    return f"Prompt:\n{prompt}\n\nContext:\n{ctx}\n\nData:\n{data}"


def _resolve_model_id(complexity: str) -> str:
    if complexity == "low":
        return _env_model_low()
    return _env_model_default()


def _preferred_model_value(req: dict[str, Any]) -> tuple[bool, str]:
    pm = req.get("preferred_model")
    if not isinstance(pm, str):
        return False, "preferred_model must be a string"
    s = pm.strip()
    if not s:
        return False, "preferred_model must be a non-empty string"
    return True, s


def _resolve_lm_model_id(req: dict[str, Any]) -> tuple[str, bool]:
    """Choisit l’identifiant LM Studio pour le corps ``model`` du POST.

    Retourne ``(model_id, uses_env_resolution)`` où ``uses_env_resolution`` est
    True uniquement pour ``preferred_model`` ∈ {``local``, ``auto``} ; sinon
    ``model_id`` est la chaîne telle quelle (nom de modèle LM custom).
    """
    ok, pm = _preferred_model_value(req)
    if not ok:
        raise ValueError(pm)
    complexity = str(req["complexity"])
    if pm in _LM_ENV_ROUTED:
        return _resolve_model_id(complexity), True
    return pm, False


def _routing_reason(complexity: str, model_id: str, uses_env_resolution: bool) -> str:
    if not uses_env_resolution:
        return f"local execution with explicit model from preferred_model ({model_id})"
    if complexity == "low":
        return "local execution selected for low complexity task"
    return "local execution with LM_STUDIO_MODEL_DEFAULT for non-low complexity"


def _estimate_tokens_from_chars(prompt_full: str, response_text: str) -> tuple[int, int]:
    """Formule WEA-172 : ceil(len / 4) par côté."""
    inp_t = int(math.ceil(len(prompt_full) / 4)) if prompt_full else 0
    out_t = int(math.ceil(len(response_text) / 4)) if response_text else 0
    return inp_t, out_t


def _economy_usage(
    input_tokens: int,
    output_tokens: int,
    duration_ms: int,
) -> dict[str, Any]:
    total = input_tokens + output_tokens
    cloud_eq = total * _GEMINI_FLASH_USD_PER_MILLION_TOKENS / 1_000_000.0
    savings = cloud_eq  # estimated_cost_usd toujours 0 pour LM Studio
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": 0.0,
        "duration_ms": duration_ms,
        "estimated_cloud_equivalent_cost_usd": cloud_eq,
        "estimated_savings_usd": savings,
    }


def _error_payload(
    task_id: str,
    *,
    code: str,
    message: str,
    retryable: bool,
    duration_ms: int = 0,
) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "status": "error",
        "provider_used": "lm_studio",
        "model_used": _env_model_low(),
        "output": {},
        "usage": {
            "input_tokens": 0,
            "output_tokens": 0,
            "estimated_cost_usd": 0.0,
            "duration_ms": duration_ms,
            "estimated_cloud_equivalent_cost_usd": None,
            "estimated_savings_usd": None,
        },
        "routing_reason": "lm_studio_adapter_error",
        "error": {"code": code, "message": message, "retryable": retryable},
    }


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


def check_availability() -> bool:
    """
    GET /v1/models avec timeout 2 s.
    Succès : HTTP 200, JSON valide, liste `data` non vide si exposée.
    """
    base = _env_base_url()
    url = f"{base}/v1/models"
    try:
        code, raw = _http_json("GET", url, body=None, timeout_sec=2.0)
    except (TimeoutError, ConnectionError):
        return False
    if code != 200:
        return False
    payload = _parse_json_body(raw)
    ids = _list_model_ids(payload)
    return len(ids) > 0


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
    ok_pm, pm_msg = _preferred_model_value(req)
    if not ok_pm:
        return False, pm_msg
    # Cet adaptateur ne sert que LM Studio : enums cloud explicites = erreur d'usage
    if pm_msg in _CLOUD_PROVIDER_ENUM:
        return False, "preferred_model requests a cloud provider; lm_studio_adapter cannot fulfill"
    inp = req.get("input")
    if not isinstance(inp, dict):
        return False, "input must be an object"
    if not isinstance(inp.get("prompt"), str):
        return False, "input.prompt must be a string"
    return True, ""


def run(req: dict[str, Any]) -> dict[str, Any]:
    """
    Exécute une requête au format universel (WEA-170) via LM Studio.

    Étapes : validation → GET /v1/models (vérif modèle) → POST /v1/chat/completions
    """
    t0 = time.perf_counter()
    task_id = str(req.get("task_id", ""))

    ok, msg = _validate_run_request(req)
    if not ok:
        return _error_payload(
            task_id or "00000000-0000-0000-0000-000000000000",
            code="validation_error",
            message=msg,
            retryable=False,
            duration_ms=int((time.perf_counter() - t0) * 1000),
        )

    complexity = str(req["complexity"])
    model_id, uses_env_resolution = _resolve_lm_model_id(req)
    base = _env_base_url()
    models_url = f"{base}/v1/models"
    chat_url = f"{base}/v1/chat/completions"

    # 1) Vérifier présence du modèle configuré
    try:
        mcode, mraw = _http_json("GET", models_url, body=None, timeout_sec=2.0)
    except TimeoutError:
        dur = int((time.perf_counter() - t0) * 1000)
        return _error_payload(
            task_id,
            code="provider_timeout",
            message="LM Studio /v1/models request timed out",
            retryable=True,
            duration_ms=dur,
        )
    except ConnectionError as e:
        dur = int((time.perf_counter() - t0) * 1000)
        return _error_payload(
            task_id,
            code="provider_unavailable",
            message=f"LM Studio is not reachable at {base}: {e}",
            retryable=True,
            duration_ms=dur,
        )

    if mcode != 200:
        code, retry = _classify_http_error(mcode)
        dur = int((time.perf_counter() - t0) * 1000)
        return _error_payload(
            task_id,
            code=code,
            message=f"GET /v1/models returned HTTP {mcode}",
            retryable=retry,
            duration_ms=dur,
        )

    models_payload = _parse_json_body(mraw)
    if models_payload is None:
        dur = int((time.perf_counter() - t0) * 1000)
        return _error_payload(
            task_id,
            code="provider_invalid_response",
            message="GET /v1/models returned invalid JSON",
            retryable=True,
            duration_ms=dur,
        )

    ids = _list_model_ids(models_payload)
    if model_id not in ids:
        dur = int((time.perf_counter() - t0) * 1000)
        return _error_payload(
            task_id,
            code="provider_not_found",
            message=f"Configured LM Studio model not found in /v1/models: {model_id}",
            retryable=False,
            duration_ms=dur,
        )

    inp = req["input"]
    assert isinstance(inp, dict)
    user_content = _build_user_content(inp)
    options = req.get("options") if isinstance(req.get("options"), dict) else {}
    timeout_ms = int(options["timeout_ms"]) if options.get("timeout_ms") is not None else _env_timeout_ms()
    timeout_sec = max(0.001, timeout_ms / 1000.0)

    temperature = float(options["temperature"]) if options.get("temperature") is not None else 0.2
    max_tokens = int(options["max_tokens"]) if options.get("max_tokens") is not None else 1000

    # ``model_id`` : si ``preferred_model`` ∈ {local, auto} → LOW/DEFAULT ; sinon
    # chaîne personnalisée envoyée telle quelle à LM Studio.
    body = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": _SYSTEM_MESSAGE},
            {"role": "user", "content": user_content},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    t_chat = time.perf_counter()
    try:
        ccode, craw = _http_json("POST", chat_url, body=body, timeout_sec=timeout_sec)
    except TimeoutError:
        dur = int((time.perf_counter() - t0) * 1000)
        return _error_payload(
            task_id,
            code="provider_timeout",
            message=f"POST /v1/chat/completions exceeded timeout_ms={timeout_ms}",
            retryable=True,
            duration_ms=dur,
        )
    except ConnectionError as e:
        dur = int((time.perf_counter() - t0) * 1000)
        return _error_payload(
            task_id,
            code="provider_unavailable",
            message=f"LM Studio is not reachable at {base}: {e}",
            retryable=True,
            duration_ms=dur,
        )

    chat_duration_ms = int((time.perf_counter() - t_chat) * 1000)
    total_duration_ms = int((time.perf_counter() - t0) * 1000)

    if ccode != 200:
        code, retry = _classify_http_error(ccode)
        return _error_payload(
            task_id,
            code=code,
            message=f"POST /v1/chat/completions returned HTTP {ccode}",
            retryable=retry,
            duration_ms=total_duration_ms,
        )

    chat_payload = _parse_json_body(craw)
    if not isinstance(chat_payload, dict):
        return _error_payload(
            task_id,
            code="provider_invalid_response",
            message="POST /v1/chat/completions returned invalid JSON",
            retryable=True,
            duration_ms=total_duration_ms,
        )

    choices = chat_payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return _error_payload(
            task_id,
            code="provider_invalid_response",
            message="chat completion missing choices",
            retryable=True,
            duration_ms=total_duration_ms,
        )
    msg0 = choices[0]
    if not isinstance(msg0, dict):
        return _error_payload(
            task_id,
            code="provider_invalid_response",
            message="chat completion choice malformed",
            retryable=True,
            duration_ms=total_duration_ms,
        )
    message_obj = msg0.get("message")
    if not isinstance(message_obj, dict):
        return _error_payload(
            task_id,
            code="provider_invalid_response",
            message="chat completion missing message",
            retryable=True,
            duration_ms=total_duration_ms,
        )
    content = message_obj.get("content")
    text_out = content if isinstance(content, str) else ""

    model_used = chat_payload.get("model")
    if not isinstance(model_used, str) or not model_used:
        model_used = model_id

    usage_block = chat_payload.get("usage")
    input_tokens = 0
    output_tokens = 0
    if isinstance(usage_block, dict):
        pt = usage_block.get("prompt_tokens")
        ct = usage_block.get("completion_tokens")
        if isinstance(pt, int):
            input_tokens = pt
        elif isinstance(pt, float):
            input_tokens = int(pt)
        if isinstance(ct, int):
            output_tokens = ct
        elif isinstance(ct, float):
            output_tokens = int(ct)

    if input_tokens == 0 and output_tokens == 0 and not usage_block:
        input_tokens, output_tokens = _estimate_tokens_from_chars(user_content, text_out)

    usage = _economy_usage(input_tokens, output_tokens, chat_duration_ms)

    return {
        "task_id": task_id,
        "status": "success",
        "provider_used": "lm_studio",
        "model_used": model_used,
        "output": {"text": text_out},
        "usage": usage,
        "routing_reason": _routing_reason(complexity, model_id, uses_env_resolution),
        "error": None,
    }
