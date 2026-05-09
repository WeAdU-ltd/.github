"""Routage provider v1 — WEA-171 (aligné local_only → LM Studio obligatoire)."""

from __future__ import annotations

from typing import Literal

from schemas import RunRequest, is_cloud_preferred_model_enum

ProviderId = Literal["lm_studio", "gemini_flash", "claude_haiku"]


class PrivacyViolationError(Exception):
    """preferred_model cloud incompatible avec privacy_level local_only."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


_ENUM_PM = frozenset({"auto", "local", "gemini_flash", "claude_haiku"})


def resolve_provider(req: RunRequest) -> ProviderId:
    """
    Choisit le provider pour cette requête.

    Règles v1 :
    - ``local_only`` : toujours ``lm_studio`` ; enums cloud en preferred_model
      → :exc:`PrivacyViolationError`.
    - Chaîne ``preferred_model`` hors les quatre enums : considérée comme id de
      modèle LM Studio → ``lm_studio`` (wrapper v1).
    - ``local`` → ``lm_studio``.
    - ``gemini_flash`` / ``claude_haiku`` → provider correspondant si privacy
      non ``local_only``.
    - ``auto`` + ``standard`` / ``external_allowed`` : matrice complexité
      (medium → Gemini, high → Claude, low → LM).
    """
    pm = req.preferred_model.strip()

    if req.privacy_level == "local_only":
        if is_cloud_preferred_model_enum(pm):
            raise PrivacyViolationError(
                "preferred_model requests a cloud provider under privacy_level=local_only"
            )
        return "lm_studio"

    if pm not in _ENUM_PM:
        return "lm_studio"

    if pm == "local":
        return "lm_studio"
    if pm == "gemini_flash":
        return "gemini_flash"
    if pm == "claude_haiku":
        return "claude_haiku"

    # auto
    if req.privacy_level in ("standard", "external_allowed"):
        if req.complexity == "low":
            return "lm_studio"
        if req.complexity == "medium":
            return "gemini_flash"
        return "claude_haiku"

    return "lm_studio"
