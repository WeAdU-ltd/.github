"""Tests observabilité / agrégats — WEA-180."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

_ORCH = Path(__file__).resolve().parents[1]
if str(_ORCH) not in sys.path:
    sys.path.insert(0, str(_ORCH))

import observability  # noqa: E402


class TestObservability(unittest.TestCase):
    def tearDown(self) -> None:
        observability.reset_for_tests()
        for key in (
            "AI_ORCHESTRATOR_OBSERVABILITY_LOG",
            "AI_ORCHESTRATOR_OBSERVABILITY_RING_MAX",
        ):
            os.environ.pop(key, None)

    def test_compute_summary_by_provider_and_lm_savings(self) -> None:
        observability.record_orchestrator_run(
            task_id="550e8400-e29b-41d4-a716-446655440000",
            task_type="coding",
            complexity="low",
            privacy_level="local_only",
            preferred_model="local",
            provider_resolved="lm_studio",
            http_status=200,
            response={
                "status": "success",
                "provider_used": "lm_studio",
                "model_used": "gemma-4",
                "usage": {
                    "input_tokens": 1000,
                    "output_tokens": 500,
                    "estimated_cost_usd": 0.0,
                    "duration_ms": 42,
                    "estimated_cloud_equivalent_cost_usd": 0.1125,
                    "estimated_savings_usd": 0.1125,
                },
                "error": None,
            },
            outcome="success",
            duration_wall_ms=50,
        )
        s = observability.compute_summary("month")
        self.assertEqual(s["totals"]["requests"], 1)
        self.assertEqual(s["totals"]["errors"], 0)
        lm = s["by_provider"]["lm_studio"]
        self.assertEqual(lm["calls"], 1)
        self.assertAlmostEqual(lm["total_savings_usd"], 0.1125, places=4)
        self.assertAlmostEqual(lm["total_cloud_equivalent_usd"], 0.1125, places=4)
        self.assertEqual(len(s["by_task_type"]), 1)
        self.assertEqual(s["by_task_type"][0]["task_type"], "coding")

    def test_errors_rollup(self) -> None:
        observability.record_orchestrator_run(
            task_id="550e8400-e29b-41d4-a716-446655440001",
            task_type="analysis",
            complexity="low",
            privacy_level="local_only",
            preferred_model="local",
            provider_resolved="lm_studio",
            http_status=503,
            response={
                "status": "error",
                "provider_used": "lm_studio",
                "model_used": "x",
                "usage": {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "estimated_cost_usd": 0.0,
                    "duration_ms": 0,
                    "estimated_cloud_equivalent_cost_usd": None,
                    "estimated_savings_usd": None,
                },
                "error": {"code": "provider_unavailable", "message": "down", "retryable": True},
            },
            outcome="adapter_error",
            duration_wall_ms=12,
        )
        s = observability.compute_summary("day")
        self.assertEqual(s["totals"]["errors"], 1)
        codes = {e["error_code"]: e["count"] for e in s["errors"]}
        self.assertEqual(codes.get("provider_unavailable"), 1)

    def test_ndjson_file_sink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log_path = os.path.join(tmp, "orch.ndjson")
            os.environ["AI_ORCHESTRATOR_OBSERVABILITY_LOG"] = log_path
            observability.reset_for_tests()
            observability.record_orchestrator_run(
                task_id="550e8400-e29b-41d4-a716-446655440002",
                task_type="classification",
                complexity="high",
                privacy_level="standard",
                preferred_model="auto",
                provider_resolved="gemini_flash",
                http_status=503,
                response={
                    "status": "error",
                    "provider_used": "none",
                    "model_used": "",
                    "usage": {
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "estimated_cost_usd": 0.0,
                        "duration_ms": 0,
                        "estimated_cloud_equivalent_cost_usd": None,
                        "estimated_savings_usd": None,
                    },
                    "error": {
                        "code": "adapter_not_implemented",
                        "message": "x",
                        "retryable": False,
                    },
                },
                outcome="not_implemented",
                duration_wall_ms=3,
            )
            text = Path(log_path).read_text(encoding="utf-8")
            line = text.strip().splitlines()[0]
            row = json.loads(line)
            self.assertEqual(row["schema_version"], "weadu.ai_orchestrator.run_v1")
            self.assertEqual(row["event_type"], "orchestrator.run")
            self.assertEqual(row["outcome"], "not_implemented")


if __name__ == "__main__":
    unittest.main()
