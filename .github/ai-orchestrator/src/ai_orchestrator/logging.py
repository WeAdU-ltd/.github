"""JSONL call logging for cost / ROI tracking (WEA-171)."""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any

_lock = threading.Lock()


def _utc_ts() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def append_run_log(
    log_path: Path,
    *,
    task_id: str,
    status: str,
    provider_used: str,
    chain: list[str],
    routing_reason: str,
    duration_ms: int,
    extra: dict[str, Any] | None = None,
) -> None:
    """Append one JSON line; never logs prompt text."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    row: dict[str, Any] = {
        "ts": _utc_ts(),
        "task_id": task_id,
        "status": status,
        "provider_used": provider_used,
        "chain": chain,
        "routing_reason": routing_reason,
        "duration_ms": duration_ms,
    }
    if extra:
        row.update(extra)
    line = json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
    with _lock:
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(line)
