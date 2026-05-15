"""Politiques de routage IA v1 — modifiables sans toucher à ``router.py`` (WEA-175)."""

from __future__ import annotations

from typing import Final

# Fournisseurs considérés comme cloud (interdits en ``local_only``).
ROUTING_CLOUD_PROVIDER_IDS: Final[frozenset[str]] = frozenset({"gemini_flash", "claude_haiku"})

# Identifiants d’adaptateurs reconnus par le routeur (ordre sans effet ici).
DEFAULT_ROUTING_ADAPTER_IDS: Final[tuple[str, ...]] = (
    "lm_studio",
    "gemini_flash",
    "claude_haiku",
)

# Pire cas coût USD par appel routé (borne conservative pour ``max_cost_usd``).
# Ajustable sans modifier le moteur.
WORST_CASE_ROUTING_COST_USD: Final[dict[str, float]] = {
    "lm_studio": 0.0,
    "gemini_flash": 0.002,
    "claude_haiku": 0.02,
}

# Matrice v1 : (privacy_level, complexity) -> ordre préféré (primaire puis fallbacks).
# « aucun » = pas d’entrée supplémentaire dans le tuple.
ROUTING_MATRIX_V1: Final[dict[tuple[str, str], tuple[str, ...]]] = {
    ("local_only", "low"): ("lm_studio",),
    ("local_only", "medium"): ("lm_studio",),
    ("local_only", "high"): ("lm_studio",),
    ("standard", "low"): ("lm_studio", "gemini_flash", "claude_haiku"),
    ("standard", "medium"): ("gemini_flash", "claude_haiku", "lm_studio"),
    ("standard", "high"): ("claude_haiku", "gemini_flash"),
    ("external_allowed", "low"): ("lm_studio", "gemini_flash", "claude_haiku"),
    ("external_allowed", "medium"): ("gemini_flash", "claude_haiku", "lm_studio"),
    ("external_allowed", "high"): ("claude_haiku", "gemini_flash"),
}
