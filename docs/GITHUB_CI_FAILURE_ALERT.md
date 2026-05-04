# Détection rapide des échecs GitHub Actions (`.github`)

Ce dépôt inclut le workflow **[`.github/workflows/ci-failure-alert.yml`](../.github/workflows/ci-failure-alert.yml)** :

1. **`workflow_run`** : dès qu’un workflow **surveillé** se termine en **échec**, un job envoie une alerte **Slack** (si configurée) et ouvre une **issue** sur **ce dépôt** (file de triage), avec lien vers le run et commandes `gh run rerun`.
2. **`schedule` (toutes les 10 min)** : **poll** de secours sur les **15 dernières minutes** pour les mêmes workflows (liste blanche de **noms** de workflows). Couvre les webhooks manqués et, avec un PAT optionnel, une vue **multi-dépôts** org.

## Secrets (optionnels)

| Secret | Rôle |
|--------|------|
| `SLACK_CI_ALERT_WEBHOOK_URL` | URL **Incoming Webhook** Slack — alerte immédiate (voir [WEA-25](./SLACK_APP_AGENTS_WEA25.md)) |
| `GH_ORG_READ_TOKEN` | PAT **fine-grained** : lecture **Actions** + métadonnées sur **tous** les dépôts `WeAdU-ltd` (pour lister les repos à auditer). Sans ce secret, le poll utilise `GITHUB_TOKEN` : liste des repos org si les permissions du token par défaut suffisent, sinon **ce dépôt seulement**. |

Les issues sont créées dans ce dépôt (`GITHUB_FAILURE_TRIAGE_REPO` défaut = repo courant) pour que **`GITHUB_TOKEN`** puisse ouvrir les tickets sans PAT admin sur chaque application.

## Liste blanche des workflows

Les noms (`name:` dans les YAML) sont dupliqués dans **`scripts/github_failure_alert.py`** (`DEFAULT_WATCH_NAMES`). Quand tu ajoutes un workflow critique ailleurs, ajoute son **`name`** à cette liste **et** au tableau `workflows:` dans `ci-failure-alert.yml`.

## Déblocage automatique

Les merges / correctifs **ne sont pas** appliqués sans revue : un agent doit encore **agir** à partir du lien Slack ou de l’issue (alignement sécurité / branch protection).
