"""Map provider id → adapter ``run(req: dict) -> dict`` (WEA-171)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

AdapterRun = Callable[[dict[str, Any]], dict[str, Any]]


def get_adapter_run(provider: str) -> AdapterRun:
    if provider == "lm_studio":
        from ai_orchestrator.adapters.lm_studio import run

        return run
    if provider == "gemini_flash":
        from ai_orchestrator.adapters.gemini_flash import run

        return run
    if provider == "claude_haiku":
        from ai_orchestrator.adapters.claude_haiku import run

        return run
    raise KeyError(f"unknown provider: {provider}")
