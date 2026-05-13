"""Registre des adaptateurs par identifiant provider — WEA-171 / WEA-174."""

from __future__ import annotations

from typing import Any, Callable

from ai_orchestrator.adapters.claude_haiku import ClaudeHaikuAdapter

_claude_haiku = ClaudeHaikuAdapter()

adapter_registry: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "claude_haiku": _claude_haiku.run,
}
