"""Classe de base des adaptateurs — contrat WEA-171 (dict in / dict out)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAdapter(ABC):
    """Adaptateur : requête universelle ``dict`` → ``RunResponse`` sérialisé en ``dict``."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Valeur ``provider_used`` (ex. ``gemini_flash``)."""

    @abstractmethod
    def run(self, req: dict[str, Any]) -> dict[str, Any]:
        """Exécute une ``RunRequest`` JSON-like ; retourne un ``RunResponse`` dict."""
