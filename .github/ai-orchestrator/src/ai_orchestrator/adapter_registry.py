"""Registre des adaptateurs enregistrés par clé (ex. ``gemini_flash``) — WEA-171 / WEA-173."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai_orchestrator.adapters.base import BaseAdapter

_REGISTRY: dict[str, BaseAdapter] = {}
_INITIALIZED = False


def register_adapter(key: str, adapter: BaseAdapter) -> None:
    """Enregistre ou remplace un adaptateur pour une clé stable."""
    _REGISTRY[key] = adapter


def _ensure_adapters_loaded() -> None:
    global _INITIALIZED
    if _INITIALIZED:
        return
    from ai_orchestrator.adapters.gemini_flash import GeminiFlashAdapter

    register_adapter("gemini_flash", GeminiFlashAdapter())
    _INITIALIZED = True


def get_adapter(key: str) -> BaseAdapter | None:
    """Retourne l'adaptateur pour ``key`` ou ``None`` si non enregistré."""
    _ensure_adapters_loaded()
    return _REGISTRY.get(key)
