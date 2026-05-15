"""Contrat commun des adaptateurs — WEA-171."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAdapter(ABC):
    """Adaptateur : entrée/sortie JSON alignées sur ``specs/api_contract.md``."""

    @abstractmethod
    def run(self, req: dict[str, Any]) -> dict[str, Any]:
        """Exécute une ``RunRequest`` sérialisée (dict) et renvoie une ``RunResponse`` (dict)."""
