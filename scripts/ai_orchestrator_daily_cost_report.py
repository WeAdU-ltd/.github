#!/usr/bin/env python3
"""Rapport quotidien des coûts IA et économies locales (WEA-179).

Lit un fichier NDJSON produit par l'orchestrateur (``audit_log``) et écrit
console + JSON/CSV/Markdown optionnels.

Session vide (exemple) :

  export LC_ALL=C.UTF-8
  python3 /workspace/scripts/ai_orchestrator_daily_cost_report.py \\
    --date 2026-05-13 \\
    --log /workspace/.github/ai-orchestrator/var/ai_orchestrator_calls.jsonl \\
    --json-out /tmp/weadu_ai_report.json \\
    --csv-out /tmp/weadu_ai_report.csv \\
    --md-out /tmp/weadu_ai_report.md
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timezone
from pathlib import Path


def _orch_dir() -> Path:
    return Path(__file__).resolve().parents[1] / ".github" / "ai-orchestrator"


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    p = argparse.ArgumentParser(description="Daily AI cost / savings report (WEA-179).")
    p.add_argument(
        "--date",
        help="UTC calendar day YYYY-MM-DD (default: today UTC).",
    )
    p.add_argument(
        "--log",
        help="Path to ai_orchestrator_calls.jsonl (default: AI_ORCHESTRATOR_AUDIT_LOG_PATH or orchestrator var/).",
    )
    p.add_argument("--json-out", type=Path, help="Write full report JSON to this path.")
    p.add_argument("--csv-out", type=Path, help="Write summary CSV to this path.")
    p.add_argument("--md-out", type=Path, help="Write Markdown report to this path.")
    p.add_argument("--quiet-console", action="store_true", help="Skip printing report to stdout.")
    args = p.parse_args(argv)

    orch = _orch_dir()
    sys.path.insert(0, str(orch))
    from cost_daily_report import (  # noqa: PLC0415 — after sys.path
        aggregate_daily,
        render_console,
        write_csv_summary,
        write_json,
        write_markdown,
    )

    if args.date:
        try:
            day = date.fromisoformat(args.date)
        except ValueError:
            print(f"Invalid --date {args.date!r}, expected YYYY-MM-DD", file=sys.stderr)
            return 2
    else:
        day = datetime.now(timezone.utc).date()

    if args.log:
        log_path = Path(args.log)
    else:
        import os

        raw = os.environ.get("AI_ORCHESTRATOR_AUDIT_LOG_PATH", "").strip()
        log_path = Path(raw) if raw else orch / "var" / "ai_orchestrator_calls.jsonl"

    report = aggregate_daily(log_path, day=day)
    text = render_console(report)
    if not args.quiet_console:
        sys.stdout.write(text)

    if args.json_out:
        write_json(report, args.json_out)
    if args.csv_out:
        write_csv_summary(report, args.csv_out)
    if args.md_out:
        write_markdown(report, args.md_out)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
