"""Tests WEA-182 — extraction model_name / model_family (orchestrateur vs rollback)."""

from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

_ORCH = Path(__file__).resolve().parents[1]
if str(_ORCH) not in sys.path:
    sys.path.insert(0, str(_ORCH))

import model_name_family_extraction as m  # noqa: E402


class TestParseModelNameFamily(unittest.TestCase):
    def test_plain_json(self) -> None:
        raw = '{"model_name": "Pixel 8", "model_family": "Pixel"}'
        out = m.parse_model_name_family_from_llm_text(raw)
        self.assertEqual(out["model_name"], "Pixel 8")
        self.assertEqual(out["model_family"], "Pixel")

    def test_json_in_fence(self) -> None:
        raw = 'Here:\n```json\n{"model_name": "X", "model_family": "Y"}\n```'
        out = m.parse_model_name_family_from_llm_text(raw)
        self.assertEqual(out["model_name"], "X")
        self.assertEqual(out["model_family"], "Y")

    def test_invalid_returns_none(self) -> None:
        out = m.parse_model_name_family_from_llm_text("no json")
        self.assertIsNone(out["model_name"])
        self.assertIsNone(out["model_family"])


class TestOrchestratorVsLegacyEquivalence(unittest.TestCase):
    """Same ``output.text`` → même parsing (N exemples synthétiques)."""

    def _success_body(self, text: str) -> dict:
        return {
            "task_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "success",
            "provider_used": "lm_studio",
            "model_used": "gemma-4",
            "output": {"text": text},
            "usage": {
                "input_tokens": 10,
                "output_tokens": 10,
                "estimated_cost_usd": 0.0,
                "duration_ms": 1,
                "estimated_cloud_equivalent_cost_usd": 0.0015,
                "estimated_savings_usd": 0.0015,
            },
            "routing_reason": "test",
            "error": None,
        }

    def test_three_titles_equivalent_paths(self) -> None:
        samples = [
            '{"model_name": "A14", "model_family": "Galaxy"}',
            '{"model_name": "", "model_family": "iPhone"}',
            '{"model_name": "Z", "model_family": ""}',
        ]
        for text in samples:
            with mock.patch.dict(os.environ, {"USE_ORCHESTRATOR": "true"}, clear=False):
                with mock.patch("model_name_family_extraction.httpx.Client") as Client:
                    inst = Client.return_value.__enter__.return_value
                    resp = mock.Mock()
                    resp.status_code = 200
                    resp.json.return_value = self._success_body(text)
                    inst.post.return_value = resp
                    orch = m.extract_model_name_family_from_product_title("dummy title")

            with mock.patch.dict(os.environ, {"USE_ORCHESTRATOR": "false"}, clear=False):
                with mock.patch("lm_studio_adapter.adapter.run", return_value=self._success_body(text)):
                    leg = m.extract_model_name_family_from_product_title("dummy title")

            self.assertTrue(orch["ok"], orch)
            self.assertTrue(leg["ok"], leg)
            self.assertEqual(orch["model_name"], leg["model_name"])
            self.assertEqual(orch["model_family"], leg["model_family"])
            self.assertEqual(orch["raw_text"], leg["raw_text"])

    def test_orchestrator_http_error_surfaces(self) -> None:
        with mock.patch.dict(os.environ, {"USE_ORCHESTRATOR": "true"}, clear=False):
            with mock.patch("model_name_family_extraction.httpx.Client") as Client:
                inst = Client.return_value.__enter__.return_value
                resp = mock.Mock()
                resp.status_code = 503
                resp.json.return_value = {"status": "error", "error": {"code": "down"}}
                inst.post.return_value = resp
                out = m.extract_model_name_family_from_product_title("t")
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "down")


if __name__ == "__main__":
    unittest.main()
