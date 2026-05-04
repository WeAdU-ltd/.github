# Détection rapide des échecs GitHub Actions (`.github`)

## Où part l’alerte ?

| Canal | Quand |
|-------|--------|
| **Issue GitHub** sur **`WeAdU-ltd/.github`** | **Toujours** (sauf si tu désactives les issues via `GITHUB_FAILURE_SKIP_ISSUE=1` dans le workflow). C’est la **notification principale** : titre, lien vers le run en échec, commandes `gh run rerun`. |
| **Slack** | **Uniquement** si le secret `SLACK_CI_ALERT_WEBHOOK_URL` est défini. **Sans ce secret, aucun message Slack** — tu peux ignorer Slack entièrement. |
| **E-mail GitHub** | Si ton compte **watch** ce dépôt ou si tu as activé les notifs **Actions** / nouvelles issues, tu reçois un mail **sans** Slack (réglages compte GitHub). |

Ce dépôt inclut le workflow **[`.github/workflows/ci-failure-alert.yml`](../.github/workflows/ci-failure-alert.yml)** :

1. **`workflow_run`** : dès qu’un workflow **surveillé** se termine en **échec**, un job ouvre une **issue** sur **ce dépôt** ; Slack **seulement** si le webhook est configuré.
2. **`schedule` (toutes les 10 min)** : **poll** de secours sur les **15 dernières minutes** (même liste blanche de noms de workflows).

## Secrets (optionnels)

| Secret | Rôle |
|--------|------|
| `SLACK_CI_ALERT_WEBHOOK_URL` | *(Optionnel)* URL **Incoming Webhook** Slack — à **omettre** si tu ne veux pas Slack [WEA-25](./SLACK_APP_AGENTS_WEA25.md) |
| `GH_ORG_READ_TOKEN` | *(Optionnel)* PAT **fine-grained** : lecture **Actions** sur les dépôts à auditer + liste des repos org. **Ce nom n’apparaît nulle part ailleurs dans ce dépôt** — ce n’est pas un doublon d’un secret déjà documenté sous un autre libellé. Les scripts locaux ([WEA-12](./GITHUB_LINEAR_INVENTORY_WEA12.md)) utilisent plutôt la variable d’environnement **`GITHUB_TOKEN`** (PAT perso) : si tu as **un** PAT lecture org dans 1Password, tu peux **réutiliser la même valeur** ici en la copiant dans le secret **`GH_ORG_READ_TOKEN`** du dépôt (un jeton, deux usages), ou créer un PAT dédié « poll CI » pour limiter le blast radius. |

Sans `GH_ORG_READ_TOKEN`, le poll utilise le **`GITHUB_TOKEN`** du workflow : il peut lister l’org **si** les permissions du token Actions le permettent ; sinon le poll ne couvre que **ce dépôt**.

**1Password :** ce dépôt ne contient pas de référence `op://` vers un PAT GitHub pour ce rôle. Les agents ne peuvent pas lire ton coffre depuis cet environnement ; vérifie dans ton vault un item du type « GitHub PAT org » et, le cas échéant, réutilise-le comme valeur du secret **`GH_ORG_READ_TOKEN`** sur GitHub.

Les issues sont créées dans ce dépôt (`GITHUB_FAILURE_TRIAGE_REPO` défaut = repo courant) pour que **`GITHUB_TOKEN`** puisse ouvrir les tickets sans PAT admin sur chaque application.

## Liste blanche des workflows

Les noms (`name:` dans les YAML) sont dupliqués dans **`scripts/github_failure_alert.py`** (`DEFAULT_WATCH_NAMES`). Quand tu ajoutes un workflow critique ailleurs, ajoute son **`name`** à cette liste **et** au tableau `workflows:` dans `ci-failure-alert.yml`.

## Déblocage automatique

Les merges / correctifs **ne sont pas** appliqués sans revue : un agent doit encore **agir** à partir du lien dans **l’issue** (ou Slack si tu l’as activé).
