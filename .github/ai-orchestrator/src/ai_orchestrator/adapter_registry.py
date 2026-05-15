"""Registre des adaptateurs par identifiant provider — WEA-171 / WEA-173 / WEA-174."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from ai_orchestrator.adapters.claude_haiku import ClaudeHaikuAdapter

if TYPE_CHECKING:
    from ai_orchestrator.adapters.base import BaseAdapter

_claude_haiku = ClaudeHaikuAdapter()

adapter_registry: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "claude_haiku": _claude_haiku.run,
}

_GEMINI_REGISTRY: dict[str, BaseAdapter] = {}
_GEMINI_INITIALIZED = False


def _ensure_gemini_loaded() -> None:
    global _GEMINI_INITIALIZED
    if _GEMINI_INITIALIZED:
        return
    from ai_orchestrator.adapters.gemini_flash import GeminiFlashAdapter

    _GEMINI_REGISTRY["gemini_flash"] = GeminiFlashAdapter()
    _GEMINI_INITIALIZED = True


def get_adapter(key: str) -> BaseAdapter | None:
    """Retourne l'adaptateur cloud enregistré pour ``key`` (ex. ``gemini_flash``)."""
    _ensure_gemini_loaded()
    return _GEMINI_REGISTRY.get(key)
