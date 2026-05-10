"""Adaptateur LM Studio (API OpenAI-compatible) pour l’orchestrateur WeAdU — ticket WEA-172."""

from .adapter import check_availability, run

__all__ = ["check_availability", "run"]
