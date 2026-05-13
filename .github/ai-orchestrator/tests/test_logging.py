"""JSONL logging (WEA-171)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from ai_orchestrator.logging import append_run_log  # noqa: E402


def test_append_run_log_writes_jsonl(tmp_path: Path) -> None:
    p = tmp_path / "sub" / "log.jsonl"
    append_run_log(
        p,
        task_id="550e8400-e29b-41d4-a716-446655440000",
        status="success",
        provider_used="lm_studio",
        chain=["lm_studio"],
        routing_reason="test",
        duration_ms=12,
    )
    lines = p.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["task_id"] == "550e8400-e29b-41d4-a716-446655440000"
    assert row["provider_used"] == "lm_studio"
    assert row["chain"] == ["lm_studio"]
