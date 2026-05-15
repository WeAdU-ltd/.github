"""Moteur de routage intelligent v1 — WEA-175."""

from __future__ import annotations

from dataclasses import dataclass

import config as orch_config
from schemas import RunRequest, is_cloud_preferred_model_enum


class PrivacyViolationError(Exception):
    """``preferred_model`` cloud incompatible avec ``privacy_level=local_only``."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


@dataclass(frozen=True)
class ProviderDecision:
    """Décision de routage : premier provider à tenter + chaîne de repli."""

    provider: str
    fallback_chain: tuple[str, ...]
    routing_reason: str
    privacy_enforced: bool


_ENUM_PREFERRED: frozenset[str] = frozenset({"auto", "local", "gemini_flash", "claude_haiku"})


def _matrix_chain(privacy_level: str, complexity: str) -> tuple[str, ...]:
    key = (privacy_level, complexity)
    try:
        return orch_config.ROUTING_MATRIX_V1[key]
    except KeyError as e:
        raise KeyError(f"unknown routing matrix cell: {key!r}") from e


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in items:
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


def _explicit_preferred_chain(pm: str, matrix_row: tuple[str, ...]) -> list[str]:
    row = list(matrix_row)
    if pm == "auto":
        return row
    if pm == "local":
        return ["lm_studio"]
    if pm == "gemini_flash":
        anchor = "gemini_flash"
    elif pm == "claude_haiku":
        anchor = "claude_haiku"
    else:
        tail = [p for p in row if p != "lm_studio"]
        return _dedupe_preserve_order(["lm_studio", *tail])

    return _dedupe_preserve_order([anchor, *[p for p in row if p != anchor]])


def _strip_cloud(chain: list[str]) -> tuple[list[str], bool]:
    cloud = orch_config.ROUTING_CLOUD_PROVIDER_IDS
    stripped = [p for p in chain if p not in cloud]
    removed = len(stripped) != len(chain)
    return stripped, removed


def _apply_max_cost(chain: list[str], max_cost_usd: float | None) -> tuple[list[str], list[str]]:
    """Retourne (chaîne filtrée, segments de raison coût)."""
    if max_cost_usd is None:
        return chain, []
    costs = orch_config.WORST_CASE_ROUTING_COST_USD
    notes: list[str] = []
    out: list[str] = []
    for p in chain:
        c = costs.get(p, float("inf"))
        if c <= max_cost_usd:
            out.append(p)
        else:
            notes.append(f"{p} excluded by max_cost_usd (worst_case {c} USD)")
    return out, notes


def _pick_available(chain: list[str], available: set[str]) -> list[str]:
    return [p for p in chain if p in available]


def select_provider(request: RunRequest, available_adapters: list[str]) -> ProviderDecision:
    """
    Sélection déterministe du provider et de la chaîne de repli.

    Politiques : module ``config`` (``ROUTING_MATRIX_V1``, coûts, nuage).
    """
    pm = request.preferred_model.strip()
    privacy = request.privacy_level
    complexity = request.complexity

    if privacy == "local_only" and is_cloud_preferred_model_enum(pm):
        raise PrivacyViolationError(
            "preferred_model requests a cloud provider under privacy_level=local_only"
        )

    matrix_row = _matrix_chain(privacy, complexity)
    logical = _explicit_preferred_chain(pm, matrix_row)

    reasons: list[str] = []
    privacy_enforced = privacy == "local_only" or pm == "local"

    if privacy == "local_only":
        logical, stripped = _strip_cloud(logical)
        if stripped:
            reasons.append("local_only enforced (cloud fallbacks removed)")
        if not logical:
            logical = ["lm_studio"]
            reasons.append("local_only default to lm_studio")

    logical = _dedupe_preserve_order(logical)

    logical, cost_notes = _apply_max_cost(logical, request.max_cost_usd)
    reasons.extend(cost_notes)

    avail_set = set(available_adapters)
    picked = _pick_available(logical, avail_set)

    if not picked:
        tail = [r for r in reasons if r]
        rr = "; ".join(_dedupe_preserve_order([*tail, "no provider available under constraints"]))
        return ProviderDecision(
            provider="none",
            fallback_chain=(),
            routing_reason=rr,
            privacy_enforced=privacy_enforced,
        )

    primary = picked[0]
    fallbacks = tuple(picked[1:])

    if pm == "auto":
        if privacy == "local_only":
            base = f"local_only / {complexity} (auto) → {primary}"
        elif complexity == "low" and primary == "lm_studio":
            base = "low complexity → lm_studio"
        else:
            base = f"{privacy} / {complexity} (auto) → {primary}"
    elif pm in _ENUM_PREFERRED and pm != "auto":
        base = f"preferred_model={pm} overrides matrix; primary {primary}"
    else:
        base = f"free-form model id → lm_studio primary ({complexity})"

    first_blocked = next((p for p in logical if p not in avail_set), None)
    if first_blocked is not None and first_blocked != primary:
        reasons.insert(0, f"{first_blocked} unavailable, fallback {primary}")

    routing_reason = "; ".join(_dedupe_preserve_order([base, *reasons])) or base
    if not routing_reason.strip():
        routing_reason = "routing decision"

    return ProviderDecision(
        provider=primary,
        fallback_chain=fallbacks,
        routing_reason=routing_reason,
        privacy_enforced=privacy_enforced,
    )
