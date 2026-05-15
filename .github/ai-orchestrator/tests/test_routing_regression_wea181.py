"""
Non-régression routage / confidentialité / coût — Linear WEA-181.

Ces tests ciblent ``routing.resolve_provider`` et les garde-fous associés
(``cloud_fallback_allowed``, ``enforce_preflight_cost_cap``) sans appel réseau.
"""

from __future__ import annotations

import sys
import unittest
from uuid import UUID

from pathlib import Path

_ORCH_ROOT = Path(__file__).resolve().parents[1]
if str(_ORCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_ORCH_ROOT))

from routing import (  # noqa: E402
    CostCapExceededError,
    PrivacyViolationError,
    cloud_fallback_allowed,
    enforce_preflight_cost_cap,
    estimate_preflight_cloud_cost_upper_bound_usd,
    resolve_provider,
)
from schemas import RunInput, RunOptions, RunRequest  # noqa: E402

_TID = UUID("550e8400-e29b-41d4-a716-446655440000")


def _mk(
    *,
    task_type: str = "analysis",
    complexity: str = "low",
    privacy_level: str = "local_only",
    preferred_model: str = "auto",
    prompt: str = "hello",
    max_cost_usd: float | None = None,
    max_tokens: int = 1000,
) -> RunRequest:
    return RunRequest(
        task_id=_TID,
        task_type=task_type,  # type: ignore[arg-type]
        complexity=complexity,  # type: ignore[arg-type]
        privacy_level=privacy_level,  # type: ignore[arg-type]
        preferred_model=preferred_model,
        max_cost_usd=max_cost_usd,
        input=RunInput(prompt=prompt),
        options=RunOptions(max_tokens=max_tokens),
    )


class TestResolveProviderRegression(unittest.TestCase):
    def test_local_only_always_lm_studio_auto(self) -> None:
        r = _mk(privacy_level="local_only", preferred_model="auto", complexity="high")
        self.assertEqual(resolve_provider(r), "lm_studio")

    def test_local_only_always_lm_studio_free_model_id(self) -> None:
        r = _mk(privacy_level="local_only", preferred_model="my-local-model-id")
        self.assertEqual(resolve_provider(r), "lm_studio")

    def test_low_complexity_standard_auto_uses_lm_studio(self) -> None:
        r = _mk(
            privacy_level="standard",
            complexity="low",
            preferred_model="auto",
        )
        self.assertEqual(resolve_provider(r), "lm_studio")

    def test_medium_complexity_standard_auto_uses_gemini_flash(self) -> None:
        r = _mk(
            privacy_level="standard",
            complexity="medium",
            preferred_model="auto",
        )
        self.assertEqual(resolve_provider(r), "gemini_flash")

    def test_high_complexity_standard_auto_uses_claude_haiku(self) -> None:
        r = _mk(
            privacy_level="standard",
            complexity="high",
            preferred_model="auto",
        )
        self.assertEqual(resolve_provider(r), "claude_haiku")

    def test_external_allowed_matches_standard_auto_matrix(self) -> None:
        self.assertEqual(
            resolve_provider(
                _mk(
                    privacy_level="external_allowed",
                    complexity="medium",
                    preferred_model="auto",
                )
            ),
            "gemini_flash",
        )

    def test_forced_gemini_respected_when_standard(self) -> None:
        r = _mk(privacy_level="standard", preferred_model="gemini_flash")
        self.assertEqual(resolve_provider(r), "gemini_flash")

    def test_forced_claude_respected_when_standard(self) -> None:
        r = _mk(privacy_level="standard", preferred_model="claude_haiku")
        self.assertEqual(resolve_provider(r), "claude_haiku")

    def test_forced_local_respected(self) -> None:
        r = _mk(
            privacy_level="standard",
            complexity="high",
            preferred_model="local",
        )
        self.assertEqual(resolve_provider(r), "lm_studio")

    def test_forced_cloud_rejected_under_local_only_gemini(self) -> None:
        with self.assertRaises(PrivacyViolationError):
            resolve_provider(_mk(privacy_level="local_only", preferred_model="gemini_flash"))

    def test_forced_cloud_rejected_under_local_only_claude(self) -> None:
        with self.assertRaises(PrivacyViolationError):
            resolve_provider(_mk(privacy_level="local_only", preferred_model="claude_haiku"))


class TestCloudFallbackPolicy(unittest.TestCase):
    def test_fallback_cloud_forbidden_local_only(self) -> None:
        self.assertFalse(cloud_fallback_allowed("local_only"))

    def test_fallback_cloud_allowed_standard(self) -> None:
        self.assertTrue(cloud_fallback_allowed("standard"))

    def test_fallback_cloud_allowed_external_allowed(self) -> None:
        self.assertTrue(cloud_fallback_allowed("external_allowed"))


class TestPreflightCostCap(unittest.TestCase):
    def test_lm_path_never_raises_cap_even_with_zero_budget(self) -> None:
        r = _mk(
            privacy_level="standard",
            complexity="low",
            preferred_model="auto",
            max_cost_usd=0.0,
            max_tokens=1_000_000,
        )
        enforce_preflight_cost_cap(r, "lm_studio")

    def test_cloud_path_raises_when_budget_below_estimate(self) -> None:
        r = _mk(
            privacy_level="standard",
            complexity="medium",
            preferred_model="auto",
            max_cost_usd=0.0,
        )
        with self.assertRaises(CostCapExceededError):
            enforce_preflight_cost_cap(r, "gemini_flash")

    def test_cloud_path_allowed_when_budget_covers_upper_bound(self) -> None:
        r = _mk(
            privacy_level="standard",
            complexity="medium",
            preferred_model="auto",
            max_cost_usd=1.0,
            prompt="hi",
            max_tokens=1000,
        )
        est = estimate_preflight_cloud_cost_upper_bound_usd(r)
        self.assertLess(est, r.max_cost_usd)
        enforce_preflight_cost_cap(r, "gemini_flash")


if __name__ == "__main__":
    unittest.main()
