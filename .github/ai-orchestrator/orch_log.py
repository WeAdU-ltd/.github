"""Journal JSONL des exécutions orchestrateur — agrégation coûts (WEA-176)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent


class Settings:
    """Chemins configurables pour les outils MCP et le wrapper HTTP."""

    def __init__(self) -> None:
        raw = os.environ.get("AI_ORCHESTRATOR_LOG_PATH", "").strip()
        self.log_path = Path(raw) if raw else _ROOT / "ai_orchestrator.jsonl"


settings = Settings()


def append_run_line(record: dict[str, Any]) -> None:
    """Ajoute une ligne JSON (UTF-8) au fichier de log ; ignore les erreurs disque."""
    rec = dict(record)
    rec.setdefault("ts", datetime.now(timezone.utc).isoformat())
    path = settings.log_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
