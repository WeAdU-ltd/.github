"""Environment-driven settings for the AI orchestrator (WEA-171)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _orch_root() -> Path:
    """`.github/ai-orchestrator/` root (parent of `src/`)."""
    return Path(__file__).resolve().parents[2]


def _truthy(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw in ("1", "true", "yes", "on")


@dataclass(frozen=True, slots=True)
class Settings:
    host: str
    port: int
    log_path: Path
    api_token: str
    enable_cors: bool
    lm_studio_base_url: str


def load_settings() -> Settings:
    root = _orch_root()
    default_log = root / "logs" / "ai_orchestrator.jsonl"
    log_raw = os.environ.get("AI_ORCHESTRATOR_LOG_PATH", "").strip()
    log_path = Path(log_raw) if log_raw else default_log
    if not log_path.is_absolute():
        log_path = (root / log_path).resolve()

    host = os.environ.get("AI_ORCHESTRATOR_HOST", "127.0.0.1").strip() or "127.0.0.1"
    port_s = os.environ.get("AI_ORCHESTRATOR_PORT", "8787").strip()
    try:
        port = int(port_s)
    except ValueError:
        port = 8787

    return Settings(
        host=host,
        port=port,
        log_path=log_path,
        api_token=os.environ.get("AI_ORCHESTRATOR_API_TOKEN", "").strip(),
        enable_cors=_truthy("AI_ORCHESTRATOR_ENABLE_CORS", False),
        lm_studio_base_url=os.environ.get("LM_STUDIO_BASE_URL", "http://localhost:1234")
        .strip()
        .rstrip("/")
        or "http://localhost:1234",
    )


def get_api_token() -> str:
    """Bearer token for POST /ai/run when configured (empty = no auth)."""
    return os.environ.get("AI_ORCHESTRATOR_API_TOKEN", "").strip()
