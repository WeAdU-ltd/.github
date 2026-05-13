# WEA-177 — Configuration centralisée de l’orchestrateur IA (`.github/ai-orchestrator/`)

Document d’ancrage pour [WEA-177](https://linear.app/weadu/issue/WEA-177/centraliser-la-configuration-providers-secrets-et-regles-de-routage). Complète le contrat [`.github/ai-orchestrator/specs/api_contract.md`](../.github/ai-orchestrator/specs/api_contract.md) et la note coûts [WEA-18](./WEA-18-llm-routing-cost.md).

## Objectif

Une seule couche de configuration : **secrets** via variables d’environnement (ou magasin qui les exporte en env) ; **routage, seuils de coût de référence, fallback documenté, logs** via un fichier JSON optionnel. Les adaptateurs (ex. `lm_studio_adapter`) ne contiennent pas de règles métier de routage.

## Nouveau poste de travail

1. Aller dans le dossier orchestrateur du clone du dépôt `WeAdU-ltd/.github` :

   `cd .github/ai-orchestrator`

2. Installer les dépendances :

   `python3 -m pip install -r requirements.txt`

3. Copier les exemples (noms ASCII sûrs, sans valeurs secrètes) :

   - `cp env.ai-orchestrator.example .env.ai-orchestrator` puis éditer **hors Git** les variables nécessaires ; **ou** exporter les mêmes noms dans le shell / GitHub Actions / Cursor.

   - Optionnel : `cp ai_orchestrator.config.example.json ./ai_orchestrator.local.json` et pointer `AI_ORCHESTRATOR_CONFIG` vers le chemin **absolu** de ce fichier pour modifier la matrice `auto_complexity_to_provider` sans toucher au code.

4. Démarrer l’API :

   `uvicorn main:app --host 127.0.0.1 --port 8787`

Si `AI_ORCHESTRATOR_CONFIG` pointe vers un fichier absent ou un JSON invalide, le chargement de l’application échoue au démarrage avec un message explicite. Si une requête est routée vers un provider cloud et que la clé canonique manque, la réponse HTTP est **503** avec `error.code: configuration_error` et le nom de variable attendu (ex. `GEMINI_API_KEY`).

## Fichiers de référence

| Fichier | Rôle |
|--------|------|
| [`.github/ai-orchestrator/orchestrator_config.py`](../.github/ai-orchestrator/orchestrator_config.py) | Lecture env + fusion JSON ; point d’entrée unique côté code |
| [`.github/ai-orchestrator/env.ai-orchestrator.example`](../.github/ai-orchestrator/env.ai-orchestrator.example) | Liste des variables d’environnement |
| [`.github/ai-orchestrator/ai_orchestrator.config.example.json`](../.github/ai-orchestrator/ai_orchestrator.config.example.json) | Exemple de règles versionnable (sans secrets) |

## Secrets (noms canoniques)

| Variable | Obligatoire |
|----------|-------------|
| `GEMINI_API_KEY` | Oui si le routage cible `gemini_flash` |
| `ANTHROPIC_API_KEY` | Oui si le routage cible `claude_haiku` |
| `LM_STUDIO_API_KEY` | Non (Bearer optionnel) |

Les **valeurs** ne sont pas dans ce dépôt ; alignement socle : [WEA-15](./SECRETS_SOCLE_WEA15.md), [WEA-14](./SECRETS_CARTOGRAPHIE_WEA14.md).

## Règles de fallback

Le bloc `fallback` du JSON décrit l’ordre envisagé après échec local ; l’exécution automatique dans les adaptateurs pourra s’y brancher dans une version ultérieure. La présence dans le fichier satisfait le critère « modifiable sans toucher aux adaptateurs ».
