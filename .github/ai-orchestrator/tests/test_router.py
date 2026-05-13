"""Deterministic routing matrix (WEA-171)."""

from __future__ import annotations

import sys
from pathlib import Path
from uuid import UUID

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from ai_orchestrator.contracts import RunRequest  # noqa: E402
from ai_orchestrator.router import PrivacyViolationError, build_provider_chain  # noqa: E402


def _req(**kwargs: object) -> RunRequest:
    base = {
        "task_id": "550e8400-e29b-41d4-a716-446655440000",
        "task_type": "analysis",
        "complexity": "low",
        "privacy_level": "local_only",
        "preferred_model": "auto",
        "input": {"prompt": "x"},
    }
    base.update(kwargs)
    return RunRequest.model_validate(base)


def test_auto_local_only_always_lm_only() -> None:
    for cx in ("low", "medium", "high"):
        chain = build_provider_chain(_req(privacy_level="local_only", complexity=cx, preferred_model="auto"))
        assert chain == ["lm_studio"]


def test_auto_standard_low_order() -> None:
    assert build_provider_chain(_req(privacy_level="standard", complexity="low", preferred_model="auto")) == [
        "lm_studio",
        "gemini_flash",
        "claude_haiku",
    ]


def test_auto_standard_medium_order() -> None:
    assert build_provider_chain(_req(privacy_level="standard", complexity="medium", preferred_model="auto")) == [
        "gemini_flash",
        "claude_haiku",
        "lm_studio",
    ]


def test_auto_standard_high_order() -> None:
    assert build_provider_chain(_req(privacy_level="standard", complexity="high", preferred_model="auto")) == [
        "claude_haiku",
        "gemini_flash",
    ]


def test_external_allowed_matches_standard_matrix() -> None:
    assert build_provider_chain(
        _req(privacy_level="external_allowed", complexity="medium", preferred_model="auto")
    ) == ["gemini_flash", "claude_haiku", "lm_studio"]


def test_explicit_local_only_lm() -> None:
    assert build_provider_chain(_req(preferred_model="local", privacy_level="standard")) == ["lm_studio"]


def test_explicit_gemini() -> None:
    assert build_provider_chain(_req(preferred_model="gemini_flash", privacy_level="standard")) == [
        "gemini_flash"
    ]


def test_freeform_is_lm_only() -> None:
    assert build_provider_chain(_req(preferred_model="mistral-7b", privacy_level="standard")) == ["lm_studio"]


def test_privacy_violation_gemini_local_only() -> None:
    with pytest.raises(PrivacyViolationError):
        build_provider_chain(_req(preferred_model="gemini_flash", privacy_level="local_only"))


def test_task_id_uuid_object() -> None:
    r = RunRequest.model_validate(
        {
            "task_id": UUID("550e8400-e29b-41d4-a716-446655440000"),
            "task_type": "analysis",
            "complexity": "low",
            "privacy_level": "standard",
            "preferred_model": "auto",
            "input": {"prompt": "a"},
        }
    )
    assert build_provider_chain(r) == ["lm_studio", "gemini_flash", "claude_haiku"]
