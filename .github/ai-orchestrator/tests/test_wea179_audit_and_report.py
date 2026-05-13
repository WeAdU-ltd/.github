"""WEA-179 — journal NDJSON et rapport quotidien."""

from __future__ import annotations

import json
import os
import sys
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

_ORCH = Path(__file__).resolve().parents[1]
if str(_ORCH) not in sys.path:
    sys.path.insert(0, str(_ORCH))

import audit_log  # noqa: E402
import cost_daily_report  # noqa: E402
import main  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from schemas import RunRequest  # noqa: E402


def _uuid() -> str:
    return "550e8400-e29b-41d4-a716-446655440000"


def _minimal_body(**overrides: object) -> dict:
    b: dict = {
        "task_id": _uuid(),
        "task_type": "analysis",
        "complexity": "low",
        "privacy_level": "local_only",
        "preferred_model": "local",
        "input": {"prompt": "hello"},
    }
    b.update(overrides)
    return b


class TestAuditLog(unittest.TestCase):
    def test_build_record_from_run_maps_usage(self) -> None:
        req = RunRequest.model_validate(_minimal_body())
        body = {
            "task_id": _uuid(),
            "status": "success",
            "provider_used": "lm_studio",
            "model_used": "gemma-4",
            "output": {"text": "x"},
            "usage": {
                "input_tokens": 10,
                "output_tokens": 20,
                "estimated_cost_usd": 0.0,
                "duration_ms": 42,
                "estimated_cloud_equivalent_cost_usd": 0.05,
                "estimated_savings_usd": 0.05,
            },
            "routing_reason": "test",
            "error": None,
        }
        rec = audit_log.build_record_from_run(req, body, http_status=200)
        self.assertEqual(rec["schema_version"], 1)
        self.assertEqual(rec["provider_used"], "lm_studio")
        self.assertEqual(rec["estimated_cloud_equivalent_cost_usd"], 0.05)
        self.assertEqual(rec["outcome_status"], "success")


class TestDailyReport(unittest.TestCase):
    def test_aggregate_counts_and_savings(self) -> None:
        log = Path(self.id())
        lines = [
            {
                "schema_version": 1,
                "date_utc": "2030-01-15",
                "outcome_status": "success",
                "provider_used": "lm_studio",
                "task_type": "analysis",
                "estimated_cost_usd": 0.0,
                "estimated_cloud_equivalent_cost_usd": 1.0,
                "estimated_savings_usd": 1.0,
                "duration_ms": 100,
                "http_status": 200,
            },
            {
                "schema_version": 1,
                "date_utc": "2030-01-15",
                "outcome_status": "error",
                "provider_used": "lm_studio",
                "task_type": "analysis",
                "estimated_cost_usd": 0.0,
                "estimated_cloud_equivalent_cost_usd": None,
                "estimated_savings_usd": None,
                "duration_ms": 50,
                "http_status": 503,
                "error_code": "provider_unavailable",
            },
            {
                "schema_version": 1,
                "date_utc": "2030-01-15",
                "outcome_status": "success",
                "provider_used": "gemini_flash",
                "task_type": "coding",
                "estimated_cost_usd": 0.02,
                "estimated_cloud_equivalent_cost_usd": 0.02,
                "estimated_savings_usd": 0.0,
                "duration_ms": 200,
                "http_status": 200,
            },
        ]
        log.write_text(
            "\n".join(json.dumps(x, separators=(",", ":")) for x in lines) + "\n",
            encoding="utf-8",
        )
        try:
            r = cost_daily_report.aggregate_daily(log, day=date(2030, 1, 15))
        finally:
            log.unlink(missing_ok=True)
        self.assertEqual(r.total_ai_calls, 3)
        self.assertAlmostEqual(r.cloud_avoided_via_local_usd, 1.0)
        self.assertAlmostEqual(r.estimated_savings_usd, 1.0)
        self.assertAlmostEqual(r.cost_gemini_usd, 0.02)
        d = r.to_dict()
        self.assertEqual(d["most_expensive_provider"], "gemini_flash")
        codes = {x["code"]: x["count"] for x in d["top_error_codes"]}
        self.assertEqual(codes.get("provider_unavailable"), 1)


class TestIntegrationAuditAppend(unittest.TestCase):
    def setUp(self) -> None:
        self.log = Path(os.environ.get("TMPDIR", "/tmp")) / f"wea179_test_{os.getpid()}.jsonl"
        if self.log.exists():
            self.log.unlink()

    def tearDown(self) -> None:
        if self.log.exists():
            self.log.unlink()

    def test_post_ai_run_appends_line(self) -> None:
        fake = {
            "task_id": _uuid(),
            "status": "success",
            "provider_used": "lm_studio",
            "model_used": "gemma-4",
            "output": {"text": "ok"},
            "usage": {
                "input_tokens": 1,
                "output_tokens": 1,
                "estimated_cost_usd": 0.0,
                "duration_ms": 5,
                "estimated_cloud_equivalent_cost_usd": 0.1,
                "estimated_savings_usd": 0.1,
            },
            "routing_reason": "test",
            "error": None,
        }
        env = {
            "AI_ORCHESTRATOR_AUDIT_LOG_PATH": str(self.log),
            "AI_ORCHESTRATOR_AUDIT_LOG_DISABLED": "",
        }
        with mock.patch.dict(os.environ, env, clear=False):
            with mock.patch("main.lm_run", return_value=fake):
                client = TestClient(main.create_app())
                r = client.post("/ai/run", json=_minimal_body())
        self.assertEqual(r.status_code, 200)
        raw = self.log.read_text(encoding="utf-8").strip()
        self.assertTrue(raw)
        row = json.loads(raw.splitlines()[0])
        self.assertEqual(row["provider_used"], "lm_studio")
        self.assertEqual(row["task_type"], "analysis")


if __name__ == "__main__":
    unittest.main()
