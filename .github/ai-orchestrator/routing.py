"""Routage provider v1 — WEA-171 (aligné local_only → LM Studio obligatoire)."""

from __future__ import annotations

import json
import math
from typing import Literal

from schemas import RunRequest, is_cloud_preferred_model_enum

ProviderId = Literal["lm_studio", "gemini_flash", "claude_haiku"]
PrivacyLevel = Literal["local_only", "standard", "external_allowed"]

# Référence coût (USD / million tokens) — alignée adaptateur LM / spec WEA-170
_GEMINI_FLASH_USD_PER_MILLION_TOKENS = 0.075


class PrivacyViolationError(Exception):
    """preferred_model cloud incompatible avec privacy_level local_only."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class CostCapExceededError(Exception):
    """Plafond ``max_cost_usd`` dépassé par l'estimation pré-vol (provider cloud)."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


_ENUM_PM = frozenset({"auto", "local", "gemini_flash", "claude_haiku"})


def cloud_fallback_allowed(privacy_level: PrivacyLevel) -> bool:
    """
    Indique si un repli vers un fournisseur cloud est permis après échec du local.

    Règle produit : interdit sous ``local_only`` ; autorisé pour ``standard`` et
    ``external_allowed`` (sous réserve d'implémentation du chemin de repli).
    """
    return privacy_level != "local_only"


def estimate_preflight_cloud_cost_upper_bound_usd(req: RunRequest) -> float:
    """
    Borne supérieure du coût USD si la charge était facturée au tarif Gemini Flash
    (même agrégation tokens que ``lm_studio_adapter`` WEA-172).
    """
    ctx = json.dumps(req.input.context, ensure_ascii=False, separators=(",", ":"))
    data = json.dumps(req.input.data, ensure_ascii=False, separators=(",", ":"))
    prompt_full = f"Prompt:\n{req.input.prompt}\n\nContext:\n{ctx}\n\nData:\n{data}"
    inp_t = int(math.ceil(len(prompt_full) / 4)) if prompt_full else 0
    out_cap = int(req.options.max_tokens)
    total = inp_t + max(0, out_cap)
    return total * _GEMINI_FLASH_USD_PER_MILLION_TOKENS / 1_000_000.0


def enforce_preflight_cost_cap(req: RunRequest, provider: ProviderId) -> None:
    """
    Applique ``max_cost_usd`` avant tout appel fournisseur cloud.

    Le chemin ``lm_studio`` est traité à coût facturé nul côté orchestrateur ; la
    limite ne s'applique donc pas au blocage local (cf. spec ``estimated_cost_usd`` LM).
    """
    if req.max_cost_usd is None:
        return
    if provider == "lm_studio":
        return
    est = estimate_preflight_cloud_cost_upper_bound_usd(req)
    if est > req.max_cost_usd:
        raise CostCapExceededError(
            f"estimated_preflight_cost_usd {est:.8f} exceeds max_cost_usd {req.max_cost_usd}"
        )


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
