"""Routage provider v1 — WEA-171 (aligné local_only → LM Studio obligatoire)."""

from __future__ import annotations

from typing import Any, Literal

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


def _routing_reason(req: RunRequest, primary: ProviderId) -> str:
    """Libellé stable pour prévisualisation MCP (sans exécution)."""
    pm = req.preferred_model.strip()
    if req.privacy_level == "local_only":
        return "local_only enforced"
    if pm not in _ENUM_PM:
        return "preferred_model_non_enum_maps_to_lm_studio"
    if pm == "local":
        return "preferred_model_local"
    if pm == "gemini_flash":
        return "preferred_model_gemini_flash"
    if pm == "claude_haiku":
        return "preferred_model_claude_haiku"
    if req.privacy_level in ("standard", "external_allowed"):
        if req.complexity == "low":
            return "auto_complexity_low_routes_lm_studio"
        if req.complexity == "medium":
            return "auto_complexity_medium_routes_gemini_flash"
        return "auto_complexity_high_routes_claude_haiku"
    return "default_lm_studio"


def select_provider_chain(req: RunRequest) -> dict[str, Any]:
    """
    Prévisualise le provider sans appeler d'adaptateur.

    Retourne ``provider`` (ou ``null`` si violation de confidentialité),
    ``routing_reason`` et ``fallback_chain`` (vide en v1).
    """
    try:
        primary = resolve_provider(req)
    except PrivacyViolationError as e:
        return {
            "provider": None,
            "routing_reason": f"privacy_violation: {e.message}",
            "fallback_chain": [],
        }
    return {
        "provider": primary,
        "routing_reason": _routing_reason(req, primary),
        "fallback_chain": [],
    }
