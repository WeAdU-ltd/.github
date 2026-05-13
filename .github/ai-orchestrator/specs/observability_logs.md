# Logs structurés orchestrateur — WEA-180

**Objectif :** une ligne JSON par exécution (`POST /ai/run` ou erreur de validation), consommable par **Larridin**, un SIEM, ou tout outil NDJSON, **sans** dépendre d’une intégration propriétaire côté orchestrateur.

La documentation publique Larridin ne fixe pas un schéma d’ingestion détaillé au moment de l’écriture ; ce dépôt définit un contrat **stable** (`schema_version`) extensible.

## Fichier NDJSON (optionnel)

| Variable | Description |
|----------|-------------|
| `AI_ORCHESTRATOR_OBSERVABILITY_LOG` | Chemin absolu ou relatif d’un fichier **append-only** ; chaque ligne est un objet JSON UTF-8. |
| `AI_ORCHESTRATOR_OBSERVABILITY_RING_MAX` | Taille max du tampon mémoire pour `/ops/summary` (défaut `8000`). |

Si la variable fichier n’est pas définie, seuls le tampon mémoire et le dashboard intégré reçoivent les événements.

## Schéma `weadu.ai_orchestrator.run_v1`

Champs obligatoires recommandés pour l’ingestion :

| Champ | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Toujours `weadu.ai_orchestrator.run_v1`. |
| `ts` | string | Horodatage UTC ISO 8601 avec suffixe `Z`. |
| `service` | string | `weadu-ai-orchestrator`. |
| `event_type` | string | `orchestrator.run`. |
| `outcome` | string | `success`, `adapter_error`, `validation_error`, `privacy_violation`, `not_implemented`, `internal_error`. |
| `task_id` | string | UUID de la requête. |
| `task_type` | string \| null | Enum métier si connue. |
| `complexity` | string \| null | `low` / `medium` / `high`. |
| `privacy_level` | string \| null | Niveau de confidentialité demandé. |
| `preferred_model` | string \| null | Valeur telle qu’envoyée par l’appelant. |
| `provider_resolved` | string | Décision routeur ou `none` si bloqué avant appel. |
| `http_status` | int | Code HTTP renvoyé au client. |
| `status` | string \| null | `success` / `error` / `fallback` depuis l’enveloppe réponse. |
| `provider_used` | string \| null | Fournisseur réellement utilisé dans la réponse. |
| `model_used` | string \| null | Identifiant modèle si présent. |
| `routing_reason` | string \| null | Raison textuelle / code métier. |
| `duration_wall_ms` | int | Durée murale handler côté API. |
| `input_tokens` | int | Jetons entrée (usage). |
| `output_tokens` | int | Jetons sortie (usage). |
| `estimated_cost_usd` | number | Coût direct facturé (souvent `0` pour LM Studio). |
| `usage_duration_ms` | int | Durée retournée dans le bloc `usage` (ex. durée chat). |
| `estimated_cloud_equivalent_cost_usd` | number \| null | Contrefactuel cloud (ex. équivalent Gemini Flash côté adaptateur LM). |
| `estimated_savings_usd` | number \| null | Économies estimées quand le run est local. |
| `error_code` | string \| null | Code machine si erreur. |
| `error_retryable` | bool \| null | Indication retry. |

**Remarque Larridin :** mapper `ts` vers le champ date attendu par le produit ; `schema_version` + `event_type` permettent de filtrer la source.

## Dashboard alternatif

- Page HTML : `GET /ops/dashboard`
- JSON agrégé (fenêtre glissante **jour / semaine / mois** côté serveur) : `GET /ops/summary?period=day|week|month`

Les agrégats sont calculés sur le **tampon du processus** ; pour historique long terme, indexer le fichier NDJSON ou un bus d’événements.

---

*Ticket : [WEA-180](https://linear.app/weadu/issue/WEA-180/connecter-les-logs-de-lorchestrateur-a-larridin-ou-dashboard-equivalent).*
