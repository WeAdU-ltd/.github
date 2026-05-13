"""Pydantic contract validation (WEA-171)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from ai_orchestrator.contracts import RunRequest  # noqa: E402


def _base() -> dict:
    return {
        "task_id": "550e8400-e29b-41d4-a716-446655440000",
        "task_type": "analysis",
        "complexity": "low",
        "privacy_level": "standard",
        "preferred_model": "auto",
        "input": {"prompt": "hello"},
    }


def test_negative_max_cost_usd() -> None:
    b = _base()
    b["max_cost_usd"] = -0.01
    with pytest.raises(ValidationError):
        RunRequest.model_validate(b)


def test_temperature_above_two() -> None:
    b = _base()
    b["options"] = {"temperature": 2.1}
    with pytest.raises(ValidationError):
        RunRequest.model_validate(b)


def test_max_tokens_zero_invalid() -> None:
    b = _base()
    b["options"] = {"max_tokens": 0}
    with pytest.raises(ValidationError):
        RunRequest.model_validate(b)


def test_timeout_ms_below_1000() -> None:
    b = _base()
    b["options"] = {"timeout_ms": 500}
    with pytest.raises(ValidationError):
        RunRequest.model_validate(b)


def test_options_defaults_merged() -> None:
    r = RunRequest.model_validate({**_base(), "options": {"temperature": 0.5}})
    assert r.options is not None
    assert r.options.temperature == 0.5
    assert r.options.max_tokens == 1000
    assert r.options.timeout_ms == 30000


def test_empty_prompt_rejected() -> None:
    b = _base()
    b["input"] = {"prompt": "   "}
    with pytest.raises(ValidationError):
        RunRequest.model_validate(b)
