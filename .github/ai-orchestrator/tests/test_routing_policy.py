"""Routage data-driven (WEA-177) — patch de la config fichier sans JSON réel."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock
from uuid import UUID

import orchestrator_config as oc  # noqa: E402
import routing  # noqa: E402
from orchestrator_config import (  # noqa: E402
    FallbackRules,
    FileBackedConfig,
    LoggingRules,
    RoutingRules,
)
from routing import resolve_provider  # noqa: E402
from schemas import RunRequest  # noqa: E402


def _fake_file_config(
    *,
    auto_map: dict[str, oc.ProviderId] | None = None,
) -> FileBackedConfig:
    am: dict[str, oc.ProviderId] = auto_map or {
        "low": "lm_studio",
        "medium": "gemini_flash",
        "high": "claude_haiku",
    }
    return FileBackedConfig(
        routing=RoutingRules(
            auto_privacy_levels=frozenset({"standard", "external_allowed"}),
            auto_complexity_to_provider=am,
            custom_preferred_model_routes_to="lm_studio",
            default_provider="lm_studio",
        ),
        cost_gemini_flash_reference_usd_per_million_tokens=0.075,
        fallback=FallbackRules(False, ()),
        logging=LoggingRules(None, "INFO"),
    )


class TestRoutingPolicy(unittest.TestCase):
    def tearDown(self) -> None:
        oc.reset_orchestrator_config_cache()

    def test_auto_medium_respects_config_matrix(self) -> None:
        fake = _fake_file_config(
            auto_map={
                "low": "lm_studio",
                "medium": "lm_studio",
                "high": "claude_haiku",
            },
        )
        req = RunRequest(
            task_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            task_type="analysis",
            complexity="medium",
            privacy_level="standard",
            preferred_model="auto",
            input={"prompt": "x"},
        )
        with mock.patch.object(routing, "get_file_backed_config", return_value=fake):
            self.assertEqual(resolve_provider(req), "lm_studio")

    def test_default_provider_when_auto_privacy_not_matched(self) -> None:
        fake = FileBackedConfig(
            routing=RoutingRules(
                auto_privacy_levels=frozenset({"external_allowed"}),
                auto_complexity_to_provider={
                    "low": "lm_studio",
                    "medium": "gemini_flash",
                    "high": "claude_haiku",
                },
                custom_preferred_model_routes_to="lm_studio",
                default_provider="lm_studio",
            ),
            cost_gemini_flash_reference_usd_per_million_tokens=0.075,
            fallback=FallbackRules(False, ()),
            logging=LoggingRules(None, "INFO"),
        )
        req = RunRequest(
            task_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            task_type="analysis",
            complexity="medium",
            privacy_level="standard",
            preferred_model="auto",
            input={"prompt": "x"},
        )
        with mock.patch.object(routing, "get_file_backed_config", return_value=fake):
            self.assertEqual(resolve_provider(req), "lm_studio")
