"""Tests du moteur de routage intelligent (WEA-175)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import cast
from unittest import mock
from uuid import uuid4

_ORCH = Path(__file__).resolve().parents[1]
if str(_ORCH) not in sys.path:
    sys.path.insert(0, str(_ORCH))

import config  # noqa: E402
from router import PrivacyViolationError, ProviderDecision, select_provider  # noqa: E402
from schemas import Complexity, PrivacyLevel, RunInput, RunRequest  # noqa: E402


def _req(
    *,
    privacy: str = "standard",
    complexity: str = "low",
    preferred: str = "auto",
    max_cost: float | None = None,
) -> RunRequest:
    return RunRequest(
        task_id=uuid4(),
        task_type="analysis",
        complexity=cast(Complexity, complexity),
        privacy_level=cast(PrivacyLevel, privacy),
        preferred_model=preferred,
        max_cost_usd=max_cost,
        input=RunInput(prompt="ping"),
    )


_ALL = ["lm_studio", "gemini_flash", "claude_haiku"]
_LM_ONLY = ["lm_studio"]


class TestRoutingMatrix(unittest.TestCase):
    """9 combinaisons privacy × complexity (preferred_model=auto, tous adapters)."""

    def test_local_only_rows(self) -> None:
        for c in ("low", "medium", "high"):
            with self.subTest(complexity=c):
                d = select_provider(_req(privacy="local_only", complexity=cast(Complexity, c)), _ALL)
                self.assertEqual(d.provider, "lm_studio")
                self.assertEqual(d.fallback_chain, ())
                self.assertTrue(d.privacy_enforced)
                self.assertTrue(d.routing_reason)

    def test_standard_low(self) -> None:
        d = select_provider(_req(privacy="standard", complexity="low"), _ALL)
        self.assertEqual(d.provider, "lm_studio")
        self.assertEqual(d.fallback_chain, ("gemini_flash", "claude_haiku"))
        self.assertIn("low complexity → lm_studio", d.routing_reason)

    def test_standard_medium(self) -> None:
        d = select_provider(_req(privacy="standard", complexity="medium"), _ALL)
        self.assertEqual(d.provider, "gemini_flash")
        self.assertEqual(d.fallback_chain, ("claude_haiku", "lm_studio"))

    def test_standard_high(self) -> None:
        d = select_provider(_req(privacy="standard", complexity="high"), _ALL)
        self.assertEqual(d.provider, "claude_haiku")
        self.assertEqual(d.fallback_chain, ("gemini_flash",))

    def test_external_allowed_matches_standard(self) -> None:
        for c in ("low", "medium", "high"):
            std = select_provider(_req(privacy="standard", complexity=cast(Complexity, c)), _ALL)
            ext = select_provider(_req(privacy="external_allowed", complexity=cast(Complexity, c)), _ALL)
            with self.subTest(complexity=c):
                self.assertEqual(std.provider, ext.provider)
                self.assertEqual(std.fallback_chain, ext.fallback_chain)


class TestPreferredModel(unittest.TestCase):
    def test_explicit_gemini_overrides_standard_low_matrix(self) -> None:
        d = select_provider(_req(privacy="standard", complexity="low", preferred="gemini_flash"), _ALL)
        self.assertEqual(d.provider, "gemini_flash")
        self.assertIn("preferred_model=gemini_flash", d.routing_reason)

    def test_explicit_claude_reorders_standard_low(self) -> None:
        d = select_provider(_req(privacy="standard", complexity="low", preferred="claude_haiku"), _ALL)
        self.assertEqual(d.provider, "claude_haiku")
        self.assertEqual(
            d.fallback_chain,
            ("lm_studio", "gemini_flash"),
        )

    def test_local_only_gemini_raises(self) -> None:
        with self.assertRaises(PrivacyViolationError):
            select_provider(_req(privacy="local_only", preferred="gemini_flash"), _ALL)

    def test_preferred_local_no_cloud_fallback_in_chain(self) -> None:
        d = select_provider(_req(privacy="standard", complexity="medium", preferred="local"), _ALL)
        self.assertEqual(d.provider, "lm_studio")
        self.assertEqual(d.fallback_chain, ())
        self.assertTrue(d.privacy_enforced)


class TestLocalOnlyNoCloudFallback(unittest.TestCase):
    def test_strip_cloud_even_if_matrix_would_include_cloud(self) -> None:
        # Cas artificiel : matrice « standard » injectée alors que privacy est local_only —
        # le moteur doit quand même retirer le cloud (monkeypatch config).
        fake_matrix = {
            ("local_only", "low"): ("lm_studio", "gemini_flash", "claude_haiku"),
        }
        with mock.patch.dict(config.ROUTING_MATRIX_V1, fake_matrix, clear=False):
            d = select_provider(_req(privacy="local_only", complexity="low"), _ALL)
        self.assertEqual(d.provider, "lm_studio")
        self.assertEqual(d.fallback_chain, ())
        self.assertIn("local_only enforced", d.routing_reason)


class TestAvailabilityAndCost(unittest.TestCase):
    def test_fallback_when_primary_cloud_not_deployed(self) -> None:
        d = select_provider(_req(privacy="standard", complexity="medium"), _LM_ONLY)
        self.assertEqual(d.provider, "lm_studio")
        self.assertEqual(d.fallback_chain, ())
        self.assertIn("gemini_flash unavailable", d.routing_reason)

    def test_max_cost_excludes_cloud_keeps_lm(self) -> None:
        d = select_provider(
            _req(privacy="standard", complexity="low", max_cost=0.0),
            _ALL,
        )
        self.assertEqual(d.provider, "lm_studio")
        self.assertIn("excluded by max_cost_usd", d.routing_reason)

    def test_no_adapter_matches_returns_none(self) -> None:
        d = select_provider(_req(), [])
        self.assertEqual(d.provider, "none")
        self.assertEqual(d.fallback_chain, ())
        self.assertTrue(d.routing_reason)


class TestDeterminism(unittest.TestCase):
    def test_same_input_same_output(self) -> None:
        r = _req(privacy="external_allowed", complexity="high")
        a = select_provider(r, _ALL)
        b = select_provider(r, _ALL)
        self.assertEqual(a, b)
        self.assertIsInstance(a, ProviderDecision)
