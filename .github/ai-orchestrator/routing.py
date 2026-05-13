"""Routage provider v1 — WEA-171 / WEA-177 (règles data-driven, sans logique dans les adaptateurs)."""

from __future__ import annotations

from orchestrator_config import ProviderId, get_file_backed_config
from schemas import RunRequest, is_cloud_preferred_model_enum


class PrivacyViolationError(Exception):
    """preferred_model cloud incompatible avec privacy_level local_only."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


_ENUM_PM = frozenset({"auto", "local", "gemini_flash", "claude_haiku"})


def resolve_provider(req: RunRequest) -> ProviderId:
    """
    Choisit le provider pour cette requête.

    Les branches « auto » et repli par défaut viennent du fichier JSON
    (``AI_ORCHESTRATOR_CONFIG``) — voir ``ai_orchestrator.config.example.json``.
    """
    rules = get_file_backed_config().routing
    pm = req.preferred_model.strip()

    if req.privacy_level == "local_only":
        if is_cloud_preferred_model_enum(pm):
            raise PrivacyViolationError(
                "preferred_model requests a cloud provider under privacy_level=local_only"
            )
        return "lm_studio"

    if pm not in _ENUM_PM:
        return rules.custom_preferred_model_routes_to

    if pm == "local":
        return "lm_studio"
    if pm == "gemini_flash":
        return "gemini_flash"
    if pm == "claude_haiku":
        return "claude_haiku"

    # auto
    if req.privacy_level in rules.auto_privacy_levels:
        mapped = rules.auto_complexity_to_provider.get(req.complexity)
        if mapped is not None:
            return mapped
    return rules.default_provider
