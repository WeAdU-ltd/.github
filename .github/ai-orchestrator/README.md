# Orchestrateur IA WeAdU (WEA-171)

Point d’entrée HTTP unique pour les appels modèles : **POST `/ai/run`**. Le code vit sous **`.github/ai-orchestrator/`** dans le dépôt `WeAdU-ltd/.github`.

## Structure

- `src/ai_orchestrator/` — package Python (`server`, `contracts`, `router`, `adapter_registry`, `logging`, `errors`, `config`, `adapters/`)
- `tests/` — `pytest`
- `specs/api_contract.md` — contrat entrée/sortie (WEA-170)

## Installation

```bash
pip install -r .github/ai-orchestrator/requirements.txt
```

## Exécution locale

Depuis la racine du clone (avec `PYTHONPATH` pointant vers `src/` et la racine orchestrateur pour les imports) :

```bash
export LC_ALL=C.UTF-8
export PYTHONPATH=".github/ai-orchestrator/src:.github/ai-orchestrator"
python3 -m uvicorn ai_orchestrator.server:app --host 127.0.0.1 --port 8787
```

Équivalent :

```bash
cd .github/ai-orchestrator
export LC_ALL=C.UTF-8
export PYTHONPATH=src:.
python3 -m ai_orchestrator.server
```

Par défaut l’écoute est **127.0.0.1:8787** (pas `0.0.0.0`). CORS désactivé sauf configuration contraire.

## Variables d’environnement

| Variable | Défaut | Rôle |
|----------|--------|------|
| `AI_ORCHESTRATOR_HOST` | `127.0.0.1` | Bind HTTP |
| `AI_ORCHESTRATOR_PORT` | `8787` | Port |
| `AI_ORCHESTRATOR_LOG_PATH` | `logs/ai_orchestrator.jsonl` (sous `.github/ai-orchestrator/`) | Journal JSONL (sans prompt) |
| `AI_ORCHESTRATOR_API_TOKEN` | vide | Si défini : header `Authorization: Bearer …` obligatoire sur `POST /ai/run` |
| `AI_ORCHESTRATOR_ENABLE_CORS` | `false` | `true` / `1` pour activer CORS large (dev) |
| `LM_STUDIO_BASE_URL` | `http://localhost:1234` | Base OpenAI-compatible LM Studio |
| `GEMINI_API_KEY` | — | Appels adaptateur Gemini (optionnel si non utilisé) |
| `ANTHROPIC_API_KEY` | — | Appels adaptateur Claude Haiku (optionnel si non utilisé) |

## Tests

```bash
export LC_ALL=C.UTF-8
python3 -m pip install -r .github/ai-orchestrator/requirements.txt
PYTHONPATH=.github/ai-orchestrator/src:.github/ai-orchestrator python3 -m pytest -q .github/ai-orchestrator/tests
```

Les adaptateurs cloud et LM Studio sont couverts avec **mocks** (pas d’appels réseau obligatoires).

## Contrat et routage

Voir `specs/api_contract.md` (WEA-170) et le ticket Linear **WEA-171** pour la matrice de routage `auto` / `local_only` / modèles explicites et les codes HTTP (`200`, `400`, `401`, `422`, `502`, `503`, `500`).
