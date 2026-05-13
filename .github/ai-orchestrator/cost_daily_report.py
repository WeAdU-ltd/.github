"""Agrégation quotidienne des logs d'audit orchestrateur (WEA-179)."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, TextIO


REPORT_SCHEMA_VERSION = 1

_LOCAL_PROVIDER = "lm_studio"


@dataclass
class DailyReport:
    date_utc: str
    generated_at_utc: str
    total_ai_calls: int = 0
    calls_by_provider: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    cost_gemini_usd: float = 0.0
    cost_claude_usd: float = 0.0
    cost_local_usd: float = 0.0
    cloud_avoided_via_local_usd: float = 0.0
    estimated_savings_usd: float = 0.0
    duration_sum_by_provider: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    duration_count_by_provider: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    errors_by_provider: dict[str, dict[str, int]] = field(default_factory=dict)
    task_type_cost_usd: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    task_type_cloud_eq_usd: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    source_log_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        avg_ms: dict[str, float | None] = {}
        for prov, cnt in self.duration_count_by_provider.items():
            if cnt > 0:
                avg_ms[prov] = round(self.duration_sum_by_provider[prov] / cnt, 3)
            else:
                avg_ms[prov] = None

        spend = {
            "gemini_flash": round(self.cost_gemini_usd, 8),
            "claude_haiku": round(self.cost_claude_usd, 8),
            "lm_studio": round(self.cost_local_usd, 8),
        }
        most_exp = max(spend, key=lambda k: spend[k])
        if spend[most_exp] == 0.0 and spend["gemini_flash"] == 0.0 and spend["claude_haiku"] == 0.0:
            most_expensive_provider: str | None = None
        else:
            most_expensive_provider = most_exp

        err_flat: dict[str, int] = defaultdict(int)
        for _p, codes in self.errors_by_provider.items():
            for c, n in codes.items():
                err_flat[c] += n
        top_errors = sorted(err_flat.items(), key=lambda x: (-x[1], x[0]))[:12]

        top_tasks = sorted(
            (
                {
                    "task_type": tt,
                    "total_estimated_cost_usd": round(v, 8),
                    "total_cloud_equivalent_usd": round(self.task_type_cloud_eq_usd.get(tt, 0.0), 8),
                }
                for tt, v in self.task_type_cost_usd.items()
            ),
            key=lambda row: (-row["total_estimated_cost_usd"], -row["total_cloud_equivalent_usd"], row["task_type"]),
        )[:15]

        return {
            "report_schema_version": REPORT_SCHEMA_VERSION,
            "date_utc": self.date_utc,
            "generated_at_utc": self.generated_at_utc,
            "total_ai_calls": self.total_ai_calls,
            "calls_by_provider": dict(self.calls_by_provider),
            "cost_totals_usd": {
                "gemini_flash": spend["gemini_flash"],
                "claude_haiku": spend["claude_haiku"],
                "lm_studio": spend["lm_studio"],
                "cloud_avoided_via_local_usd": round(self.cloud_avoided_via_local_usd, 8),
                "estimated_savings_usd": round(self.estimated_savings_usd, 8),
            },
            "avg_duration_ms_by_provider": avg_ms,
            "errors_by_provider": {k: dict(v) for k, v in self.errors_by_provider.items()},
            "top_error_codes": [{"code": c, "count": n} for c, n in top_errors],
            "most_expensive_provider": most_expensive_provider,
            "top_task_types_by_cost": top_tasks,
            "source_log_path": self.source_log_path,
        }


def _parse_date_utc(line: dict[str, Any]) -> str | None:
    d = line.get("date_utc")
    if isinstance(d, str) and len(d) >= 10:
        return d[:10]
    ts = line.get("ts_utc")
    if isinstance(ts, str) and "T" in ts:
        try:
            day = ts.split("T", 1)[0]
            datetime.strptime(day, "%Y-%m-%d")
            return day
        except ValueError:
            return None
    return None


def ingest_line(report: DailyReport, line: dict[str, Any]) -> None:
    prov = str(line.get("provider_used") or "unknown")
    report.calls_by_provider[prov] += 1
    report.total_ai_calls += 1

    cost = float(line["estimated_cost_usd"]) if isinstance(line.get("estimated_cost_usd"), (int, float)) else 0.0
    cloud_eq = line.get("estimated_cloud_equivalent_cost_usd")
    cloud_eq_f = float(cloud_eq) if isinstance(cloud_eq, (int, float)) else None
    savings = line.get("estimated_savings_usd")
    savings_f = float(savings) if isinstance(savings, (int, float)) else None

    outcome = str(line.get("outcome_status") or "")
    is_error = outcome == "error" or (isinstance(line.get("http_status"), int) and line["http_status"] >= 400)

    if prov == "gemini_flash":
        report.cost_gemini_usd += cost
    elif prov == "claude_haiku":
        report.cost_claude_usd += cost
    elif prov == _LOCAL_PROVIDER:
        report.cost_local_usd += cost
        if not is_error and cloud_eq_f is not None:
            report.cloud_avoided_via_local_usd += cloud_eq_f
        if not is_error and savings_f is not None:
            report.estimated_savings_usd += savings_f

    tt = str(line.get("task_type") or "unknown")
    report.task_type_cost_usd[tt] += cost
    if cloud_eq_f is not None:
        report.task_type_cloud_eq_usd[tt] += cloud_eq_f

    dur = line.get("duration_ms")
    if isinstance(dur, (int, float)) and int(dur) >= 0:
        report.duration_sum_by_provider[prov] += int(dur)
        report.duration_count_by_provider[prov] += 1

    if is_error:
        ec = line.get("error_code")
        code = str(ec) if ec else "unknown_error"
        if prov not in report.errors_by_provider:
            report.errors_by_provider[prov] = defaultdict(int)
        report.errors_by_provider[prov][code] += 1


def aggregate_daily(
    log_path: Path,
    *,
    day: date,
) -> DailyReport:
    day_s = day.isoformat()
    report = DailyReport(
        date_utc=day_s,
        generated_at_utc=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        source_log_path=str(log_path.resolve()),
    )
    if not log_path.is_file():
        return report

    with log_path.open(encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue
            if int(obj.get("schema_version", 0) or 0) < 1:
                continue
            if _parse_date_utc(obj) != day_s:
                continue
            ingest_line(report, obj)

    return report


def render_console(report: DailyReport) -> str:
    d = report.to_dict()
    lines = [
        f"WeAdU AI orchestrator — daily cost report ({report.date_utc} UTC)",
        f"Source log: {report.source_log_path}",
        f"Total calls: {report.total_ai_calls}",
        f"Calls by provider: {json.dumps(d['calls_by_provider'], ensure_ascii=False)}",
        f"Cost Gemini (USD): {d['cost_totals_usd']['gemini_flash']}",
        f"Cost Claude (USD): {d['cost_totals_usd']['claude_haiku']}",
        f"Cost local lm_studio (USD): {d['cost_totals_usd']['lm_studio']}",
        f"Cloud avoided via local (USD equiv.): {d['cost_totals_usd']['cloud_avoided_via_local_usd']}",
        f"Estimated savings (USD): {d['cost_totals_usd']['estimated_savings_usd']}",
        f"Avg duration ms by provider: {json.dumps(d['avg_duration_ms_by_provider'], ensure_ascii=False)}",
        f"Errors by provider: {json.dumps(d['errors_by_provider'], ensure_ascii=False)}",
        f"Most expensive provider (actual spend): {d['most_expensive_provider']!r}",
        f"Top error codes: {json.dumps(d['top_error_codes'], ensure_ascii=False)}",
        f"Top task types by cost: {json.dumps(d['top_task_types_by_cost'], ensure_ascii=False)}",
    ]
    return "\n".join(lines) + "\n"


def write_json(report: DailyReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv_summary(report: DailyReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    d = report.to_dict()
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        w.writerow(["date_utc", d["date_utc"]])
        w.writerow(["total_ai_calls", d["total_ai_calls"]])
        w.writerow(["cost_gemini_usd", d["cost_totals_usd"]["gemini_flash"]])
        w.writerow(["cost_claude_usd", d["cost_totals_usd"]["claude_haiku"]])
        w.writerow(["cost_local_usd", d["cost_totals_usd"]["lm_studio"]])
        w.writerow(["cloud_avoided_via_local_usd", d["cost_totals_usd"]["cloud_avoided_via_local_usd"]])
        w.writerow(["estimated_savings_usd", d["cost_totals_usd"]["estimated_savings_usd"]])
        w.writerow(["most_expensive_provider", d["most_expensive_provider"]])
        for prov, n in sorted(d["calls_by_provider"].items()):
            w.writerow([f"calls__{prov}", n])


def write_markdown(report: DailyReport, path: Path) -> None:
    d = report.to_dict()
    lines = [
        f"# Rapport coûts IA — {report.date_utc} (UTC)",
        "",
        f"- Appels totaux : **{d['total_ai_calls']}**",
        f"- Coût Gemini (USD) : **{d['cost_totals_usd']['gemini_flash']}**",
        f"- Coût Claude (USD) : **{d['cost_totals_usd']['claude_haiku']}**",
        f"- Coût local (USD) : **{d['cost_totals_usd']['lm_studio']}**",
        f"- Cloud évité via local (USD équivalent) : **{d['cost_totals_usd']['cloud_avoided_via_local_usd']}**",
        f"- Économie estimée (USD) : **{d['cost_totals_usd']['estimated_savings_usd']}**",
        f"- Provider le plus coûteux (dépense réelle) : **{d['most_expensive_provider']}**",
        "",
        "## Appels par fournisseur",
        "",
        "```json",
        json.dumps(d["calls_by_provider"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Erreurs principales",
        "",
        "```json",
        json.dumps(d["top_error_codes"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Types de tâches (coût)",
        "",
        "```json",
        json.dumps(d["top_task_types_by_cost"], ensure_ascii=False, indent=2),
        "```",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
