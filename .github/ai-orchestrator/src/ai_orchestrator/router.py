"""Deterministic provider routing and fallback chains (WEA-171 matrix v1)."""

from __future__ import annotations

from typing import Literal

from ai_orchestrator.contracts import RunRequest, is_cloud_preferred_model

ProviderId = Literal["lm_studio", "gemini_flash", "claude_haiku"]

_ENUM_PM = frozenset({"auto", "local", "gemini_flash", "claude_haiku"})


class PrivacyViolationError(Exception):
    """Cloud provider requested under ``privacy_level=local_only``."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def _auto_chain(privacy_level: str, complexity: str) -> list[ProviderId]:
    if privacy_level == "local_only":
        return ["lm_studio"]
    if complexity == "low":
        return ["lm_studio", "gemini_flash", "claude_haiku"]
    if complexity == "medium":
        return ["gemini_flash", "claude_haiku", "lm_studio"]
    return ["claude_haiku", "gemini_flash"]


def build_provider_chain(req: RunRequest) -> list[ProviderId]:
    """
    Ordered providers to try. Fallback is orchestrator-only; adapters never
    escalate to cloud themselves.
    """
    pm = req.preferred_model.strip()

    if req.privacy_level == "local_only" and is_cloud_preferred_model(pm):
        raise PrivacyViolationError(
            "preferred_model requests a cloud provider under privacy_level=local_only"
        )

    if pm not in _ENUM_PM:
        return ["lm_studio"]

    if pm == "local":
        return ["lm_studio"]
    if pm == "gemini_flash":
        return ["gemini_flash"]
    if pm == "claude_haiku":
        return ["claude_haiku"]

    # auto
    return list(_auto_chain(req.privacy_level, req.complexity))
