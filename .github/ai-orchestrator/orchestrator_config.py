"""
Configuration centralisée — WEA-177.

Secrets : uniquement via variables d’environnement (ou injecteur externe qui
exporte ces variables). Aucune valeur secrète dans les fichiers JSON d’exemple.

Routage, seuils de coût de référence, fallback et chemins de logs : JSON
optionnel pointé par ``AI_ORCHESTRATOR_CONFIG`` (voir ``ai_orchestrator.config.example.json``).

Les paramètres LM Studio lus depuis l’environnement sont exposés par des
fonctions : chaque appel relit ``os.environ`` pour rester compatible avec les
tests qui utilisent ``patch.dict``.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Mapping

logger = logging.getLogger(__name__)

ProviderId = Literal["lm_studio", "gemini_flash", "claude_haiku"]

_DEFAULT_LM_BASE = "http://localhost:1234"
_DEFAULT_LM_MODEL = "gemma-4"
_DEFAULT_LM_TIMEOUT_MS = 30_000
_LM_CHAT_TIMEOUT_MS_MIN = 30_000
_LM_HTTP_MODELS_TIMEOUT_SEC = 30.0
_DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"
_DEFAULT_CLAUDE_MODEL = "claude-3-5-haiku-20241022"
_DEFAULT_COST_REF = 0.075

# JSON par défaut (identique au comportement historique du routeur v1)
_DEFAULT_FILE_CONFIG: dict[str, Any] = {
    "version": 1,
    "routing": {
        "auto_privacy_levels": ["standard", "external_allowed"],
        "auto_complexity_to_provider": {
            "low": "lm_studio",
            "medium": "gemini_flash",
            "high": "claude_haiku",
        },
        "custom_preferred_model_routes_to": "lm_studio",
        "default_provider": "lm_studio",
    },
    "cost": {
        "gemini_flash_reference_usd_per_million_tokens": _DEFAULT_COST_REF,
    },
    "fallback": {
        "enabled": False,
        "order_after_local_failure": ["gemini_flash", "claude_haiku"],
    },
    "logging": {
        "file_path": None,
        "level": "INFO",
    },
}


@dataclass(frozen=True)
class RoutingRules:
    """Règles data-driven consommées par ``routing.resolve_provider``."""

    auto_privacy_levels: frozenset[str]
    auto_complexity_to_provider: Mapping[str, ProviderId]
    custom_preferred_model_routes_to: ProviderId
    default_provider: ProviderId


@dataclass(frozen=True)
class FallbackRules:
    enabled: bool
    order_after_local_failure: tuple[ProviderId, ...]


@dataclass(frozen=True)
class LoggingRules:
    file_path: str | None
    level: str


@dataclass(frozen=True)
class FileBackedConfig:
    routing: RoutingRules
    cost_gemini_flash_reference_usd_per_million_tokens: float
    fallback: FallbackRules
    logging: LoggingRules


_merged_file_config: dict[str, Any] | None = None
_config_path_used: str | None = None


def reset_orchestrator_config_cache() -> None:
    """Réinitialise le cache JSON (tests uniquement)."""
    global _merged_file_config, _config_path_used
    _merged_file_config = None
    _config_path_used = None


def _deep_merge_defaults(user: dict[str, Any]) -> dict[str, Any]:
    out = json.loads(json.dumps(_DEFAULT_FILE_CONFIG))

    def merge(dst: dict[str, Any], src: Mapping[str, Any]) -> None:
        for k, v in src.items():
            if isinstance(v, dict) and isinstance(dst.get(k), dict):
                merge(dst[k], v)  # type: ignore[arg-type]
            else:
                dst[k] = v  # type: ignore[index]

    merge(out, user)
    return out


def _load_json_file(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("AI_ORCHESTRATOR_CONFIG root must be a JSON object")
    return data


def _get_merged_file_dict() -> dict[str, Any]:
    global _merged_file_config, _config_path_used
    path_raw = os.environ.get("AI_ORCHESTRATOR_CONFIG", "").strip()
    if not path_raw:
        if _merged_file_config is None or _config_path_used != "":
            _merged_file_config = json.loads(json.dumps(_DEFAULT_FILE_CONFIG))
            _config_path_used = ""
        return _merged_file_config

    if _merged_file_config is not None and _config_path_used == path_raw:
        return _merged_file_config

    path = Path(path_raw).expanduser()
    if not path.is_file():
        raise FileNotFoundError(
            f"AI_ORCHESTRATOR_CONFIG points to missing file: {path_raw}"
        )
    user = _load_json_file(path)
    merged = _deep_merge_defaults(user)
    _merged_file_config = merged
    _config_path_used = path_raw
    logger.info("Loaded AI orchestrator config from %s", path)
    return _merged_file_config


def get_file_backed_config() -> FileBackedConfig:
    """Config non-secrets (routage, coût de référence, fallback, logs)."""
    d = _get_merged_file_dict()
    r = d["routing"]
    auto_priv = r.get("auto_privacy_levels") or []
    if not isinstance(auto_priv, list):
        raise ValueError("routing.auto_privacy_levels must be a list")
    ac = r.get("auto_complexity_to_provider") or {}
    if not isinstance(ac, dict):
        raise ValueError("routing.auto_complexity_to_provider must be an object")
    allowed: frozenset[str] = frozenset({"lm_studio", "gemini_flash", "claude_haiku"})
    auto_map: dict[str, ProviderId] = {}
    for ck, pv in ac.items():
        if ck not in ("low", "medium", "high"):
            continue
        if not isinstance(pv, str) or pv not in allowed:
            raise ValueError(
                f"routing.auto_complexity_to_provider.{ck} must be one of {sorted(allowed)}"
            )
        auto_map[str(ck)] = pv  # type: ignore[assignment]

    cust = r.get("custom_preferred_model_routes_to", "lm_studio")
    if not isinstance(cust, str) or cust not in allowed:
        raise ValueError("routing.custom_preferred_model_routes_to invalid")

    dprov = r.get("default_provider", "lm_studio")
    if not isinstance(dprov, str) or dprov not in allowed:
        raise ValueError("routing.default_provider invalid")

    cost_block = d.get("cost") or {}
    rate = cost_block.get("gemini_flash_reference_usd_per_million_tokens", _DEFAULT_COST_REF)
    if isinstance(rate, (int, float)) and float(rate) >= 0:
        cost_rate = float(rate)
    else:
        raise ValueError("cost.gemini_flash_reference_usd_per_million_tokens must be a number >= 0")

    fb = d.get("fallback") or {}
    fb_enabled = bool(fb.get("enabled", False))
    order_raw = fb.get("order_after_local_failure") or []
    order: list[ProviderId] = []
    if isinstance(order_raw, list):
        for item in order_raw:
            if isinstance(item, str) and item in allowed and item != "lm_studio":
                order.append(item)  # type: ignore[arg-type]

    log_block = d.get("logging") or {}
    log_path = log_block.get("file_path")
    log_path_s = str(log_path).strip() if isinstance(log_path, str) and log_path.strip() else None
    lvl = log_block.get("level", "INFO")
    level_s = str(lvl).upper() if isinstance(lvl, str) else "INFO"

    return FileBackedConfig(
        routing=RoutingRules(
            auto_privacy_levels=frozenset(str(x) for x in auto_priv),
            auto_complexity_to_provider=auto_map,
            custom_preferred_model_routes_to=cust,  # type: ignore[arg-type]
            default_provider=dprov,  # type: ignore[arg-type]
        ),
        cost_gemini_flash_reference_usd_per_million_tokens=cost_rate,
        fallback=FallbackRules(enabled=fb_enabled, order_after_local_failure=tuple(order)),
        logging=LoggingRules(file_path=log_path_s, level=level_s),
    )


def orchestrator_debug_enabled() -> bool:
    v = os.environ.get("AI_ORCHESTRATOR_DEBUG", "").strip().lower()
    if v in ("1", "true", "yes", "on"):
        return True
    if v in ("0", "false", "no", "off", ""):
        return False
    return bool(v)


def cloud_cost_reference_usd_per_million_tokens() -> float:
    """Tarif de référence pour l’estimation « équivalent cloud » (non facturé LM)."""
    env_raw = os.environ.get(
        "CLOUD_COST_REFERENCE_GEMINI_FLASH_USD_PER_MILLION_TOKENS", ""
    ).strip()
    if env_raw:
        try:
            v = float(env_raw)
            if v >= 0:
                return v
        except ValueError:
            pass
    return get_file_backed_config().cost_gemini_flash_reference_usd_per_million_tokens


def lm_studio_base_url() -> str:
    raw = os.environ.get("LM_STUDIO_BASE_URL", "").strip()
    if not raw:
        return _DEFAULT_LM_BASE
    return raw.rstrip("/")


def lm_studio_model_low() -> str:
    return os.environ.get("LM_STUDIO_MODEL_LOW", "").strip() or _DEFAULT_LM_MODEL


def lm_studio_model_default() -> str:
    return os.environ.get("LM_STUDIO_MODEL_DEFAULT", "").strip() or _DEFAULT_LM_MODEL


def lm_studio_timeout_ms() -> int:
    raw = os.environ.get("LM_STUDIO_TIMEOUT_MS", "").strip()
    if raw.isdigit():
        return max(_LM_CHAT_TIMEOUT_MS_MIN, int(raw))
    return _LM_CHAT_TIMEOUT_MS_MIN


def lm_studio_api_key() -> str:
    return os.environ.get("LM_STUDIO_API_KEY", "").strip()


def lm_http_models_timeout_sec() -> float:
    raw = os.environ.get("LM_STUDIO_HTTP_MODELS_TIMEOUT_SEC", "").strip()
    if raw:
        try:
            v = float(raw)
            if v > 0:
                return v
        except ValueError:
            pass
    return _LM_HTTP_MODELS_TIMEOUT_SEC


def lm_chat_timeout_ms_min() -> int:
    return _LM_CHAT_TIMEOUT_MS_MIN


def gemini_api_key() -> str:
    return os.environ.get("GEMINI_API_KEY", "").strip()


def anthropic_api_key() -> str:
    return os.environ.get("ANTHROPIC_API_KEY", "").strip()


def gemini_active_model_id() -> str:
    return os.environ.get("GEMINI_MODEL", "").strip() or _DEFAULT_GEMINI_MODEL


def claude_active_model_id() -> str:
    return os.environ.get("CLAUDE_MODEL", "").strip() or _DEFAULT_CLAUDE_MODEL


def default_max_cost_usd() -> float | None:
    """Plafond coût par défaut (requête) si ``AI_ORCHESTRATOR_DEFAULT_MAX_COST_USD`` défini."""
    raw = os.environ.get("AI_ORCHESTRATOR_DEFAULT_MAX_COST_USD", "").strip()
    if not raw:
        return None
    try:
        v = float(raw)
        return v if v >= 0 else None
    except ValueError:
        return None


def missing_required_cloud_secret(provider: ProviderId) -> str | None:
    """
    Si le provider cloud est ciblé mais la clé canonique manque, retourne le nom
    de variable attendu ; sinon ``None``.
    """
    if provider == "gemini_flash":
        return "GEMINI_API_KEY" if not gemini_api_key() else None
    if provider == "claude_haiku":
        return "ANTHROPIC_API_KEY" if not anthropic_api_key() else None
    return None
