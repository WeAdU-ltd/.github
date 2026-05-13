"""Smoke MCP — trois outils sans erreur (WEA-176)."""

from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

_SRC = Path(__file__).resolve().parents[1] / "src"
_ORCH = Path(__file__).resolve().parents[1]
for _p in (_SRC, _ORCH):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


from ai_orchestrator import mcp_server as mcp_mod  # noqa: E402


class TestMcpSmoke(unittest.TestCase):
    def test_ai_route_preview_local_only(self) -> None:
        out = mcp_mod._ai_route_preview_impl("low", "local_only", "local")
        self.assertEqual(out["provider"], "lm_studio")
        self.assertEqual(out["routing_reason"], "local_only enforced")
        self.assertEqual(out["fallback_chain"], [])

    def test_ai_route_preview_privacy_violation(self) -> None:
        out = mcp_mod._ai_route_preview_impl("low", "local_only", "gemini_flash")
        self.assertIsNone(out["provider"])
        self.assertIn("privacy_violation", out["routing_reason"])

    def test_ai_cost_summary_aggregates(self) -> None:
        log = Path(self.id())  # unique name base
        # use temp under tmp - self.id() is test name string
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "orch.jsonl"
            now = datetime.now(timezone.utc).isoformat()
            log_path.write_text(
                json.dumps(
                    {
                        "ts": now,
                        "status": "success",
                        "provider_used": "lm_studio",
                        "estimated_cost_usd": 0.0,
                        "estimated_savings_usd": 0.5,
                    }
                )
                + "\n"
                + json.dumps(
                    {
                        "ts": now,
                        "status": "error",
                        "provider_used": "lm_studio",
                        "estimated_cost_usd": 0.0,
                        "estimated_savings_usd": None,
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            fake_settings = mock.Mock(log_path=log_path)
            with mock.patch.object(mcp_mod, "orch_log_settings", fake_settings):
                out = mcp_mod._ai_cost_summary_impl("last_7_days")
        self.assertEqual(out["total_calls"], 2)
        self.assertEqual(out["error_count"], 1)
        self.assertGreaterEqual(out["lm_studio_estimated_savings_usd"], 0.5)

    def test_ai_run_returns_wrapper_json(self) -> None:
        fake = {
            "task_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "success",
            "provider_used": "lm_studio",
            "model_used": "gemma-4",
            "output": {"text": "ok"},
            "usage": {
                "input_tokens": 1,
                "output_tokens": 1,
                "estimated_cost_usd": 0.0,
                "duration_ms": 1,
                "estimated_cloud_equivalent_cost_usd": None,
                "estimated_savings_usd": None,
            },
            "routing_reason": "test",
            "error": None,
        }
        mock_resp = mock.Mock()
        mock_resp.json.return_value = fake
        mock_client = mock.Mock()
        mock_client.__enter__ = mock.Mock(return_value=mock_client)
        mock_client.__exit__ = mock.Mock(return_value=False)
        mock_client.post.return_value = mock_resp
        with mock.patch.object(mcp_mod.httpx, "Client", return_value=mock_client):
            out = mcp_mod._ai_run_impl(
                "analysis",
                "low",
                "local_only",
                "hello",
                {},
                "local",
            )
        self.assertEqual(out["status"], "success")
        self.assertEqual(out["provider_used"], "lm_studio")


if __name__ == "__main__":
    unittest.main()
