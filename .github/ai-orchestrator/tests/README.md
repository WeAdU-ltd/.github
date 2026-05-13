# Tests orchestrateur IA (`.github/ai-orchestrator`)

## Exécution locale

Depuis la racine du dépôt :

```bash
cd .github/ai-orchestrator
python3 -m pip install -r requirements.txt pytest httpx
python3 -m pytest tests/ -q
```

Ou avec chemin absolu (session shell vide) :

```bash
python3 -m pip install -r /chemin/vers/clone/.github/ai-orchestrator/requirements.txt pytest httpx
python3 -m pytest /chemin/vers/clone/.github/ai-orchestrator/tests/ -q
```

## WEA-181 — non-régression routage

Le fichier `tests/test_routing_regression_wea181.py` verrouille :

- `local_only` → provider `lm_studio` (y compris `preferred_model=auto`).
- `standard` + `auto` + complexité `low` / `medium` / `high` → LM Studio / Gemini Flash / Claude Haiku.
- `preferred_model` cloud explicite refusé sous `local_only` (`PrivacyViolationError`).
- Politique de repli cloud : `cloud_fallback_allowed` est faux pour `local_only`, vrai pour `standard` et `external_allowed`.
- Plafond `max_cost_usd` : `enforce_preflight_cost_cap` bloque les chemins cloud si la borne supérieure pré-vol (tarif de référence Gemini Flash, alignée sur l’adaptateur LM) dépasse le budget ; le chemin `lm_studio` n’est pas bloqué par ce plafond (coût facturé orchestrateur nul en local).

Les tests HTTP mockés existants (`test_lm_studio_adapter.py`, `test_api_integration.py`) complètent la couverture adaptateur et endpoint `POST /ai/run`.
