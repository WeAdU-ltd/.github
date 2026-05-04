# Cartographie des secrets (WEA-14)

Document d’ancrage pour le ticket [WEA-14](https://linear.app/weadu/issue/WEA-14/secrets-cartographie-1password-github-cursor-regle-chercher-avant-de). Il complète l’inventaire GitHub ↔ Linear ([WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces), voir [`GITHUB_LINEAR_INVENTORY_WEA12.md`](./GITHUB_LINEAR_INVENTORY_WEA12.md)). Le **socle secrets** (noms canoniques, org/environments, finance-RH, Cursor) est décrit dans [`SECRETS_SOCLE_WEA15.md`](./SECRETS_SOCLE_WEA15.md) ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)).

---

## Règle agents : chercher avant de demander

Avant de solliciter un humain pour un mot de passe, une clé API ou un jeton :

1. **Inventaires et docs du dépôt** : `README`, `docs/`, scripts d’inventaire (ex. `scripts/linear_github_inventory_wea12.py`), fichiers `CONTRIBUTING` / runbooks s’ils existent.
2. **Cartographie des noms** : [`SECRETS_SOCLE_WEA15.md`](./SECRETS_SOCLE_WEA15.md) (nom GitHub **canonique** vs libellé éventuel dans un coffre).
3. **Secrets « d’app »** : coffres ou secrets attachés à l’outil qui exécute le travail (GitHub Actions, environnement CI, variables du runner, secrets du dépôt appelant) plutôt qu’un coffre personnel générique.
4. **GitHub** : secrets et variables au niveau **organisation**, **dépôt** et **environnement** (`Settings` → `Secrets and variables` → `Actions` / `Dependabot` si utilisé). Pour les workflows réutilisables, les secrets passent depuis le workflow appelant (voir ci-dessous).
5. **Cursor** : secrets fournis dans l’UI ou la config cloud du workspace (pas dans le chat). Ne pas demander à l’humain une valeur déjà injectée côté agent si elle est documentée comme disponible dans ce canal.
6. **1Password** (vault équipe) quand l’intégration est disponible : **rechercher un jeton existant** (souvent un PAT GitHub sous un **autre titre** : « GitHub PAT », « gh », etc.) **avant** de proposer d’en créer un nouveau. Vérifier que les **portées** couvrent le besoin ; réutiliser la **même valeur** dans le secret GitHub org attendu plutôt que dupliquer les PAT inutilement. **Ne jamais** coller un secret dans Linear ou le chat ; une seule lecture structurée plutôt qu’une rafale (rate limits).

Si, après ces étapes, l’information manque encore : le noter sur le ticket Linear (écart par rapport aux critères de fait / [règle avant Done](https://linear.app/weadu/document/regle-agents-criteres-de-fait-avant-done-tous-projets-2b32aec9e234)) plutôt que d’inventer une valeur.

---

## 1Password — réutilisation et prudence

- **Réutilisation** : pour un besoin « nouveau » côté GitHub (`secrets.FOO`), chercher d’abord si un **PAT ou jeton équivalent** existe déjà dans le vault sous un **autre nom** ; aligner la valeur **sans recréer** si les portées suffisent (section *Alias* dans [`SECRETS_SOCLE_WEA15.md`](./SECRETS_SOCLE_WEA15.md)).
- **Débit** : les intégrations CLI / Connect / SDK peuvent être **limitées** ; éviter les boucles de recherche ; une consultation ciblée vaut mieux que dix requêtes vagues.
- Quand 1Password est nécessaire : cibler un **item / vault** connu, documenté pour l’équipe, plutôt qu’une recherche large et répétée.

---

## Tableau : outil → type de secret → comment chercher

| Outil / lieu | Types de secrets typiques | Comment les agents doivent chercher |
|--------------|---------------------------|--------------------------------------|
| **GitHub — dépôt** | PAT dédiés (si stockés en secret), clés de déploiement, tokens de packages, `ACTIONS_*` personnalisés | Onglet du dépôt → *Settings* → *Secrets and variables* → *Actions*. Lire aussi `.github/workflows/` pour les noms attendus (`secrets.NOM`). |
| **GitHub — environnement** | Secrets par `environment` (ex. `production`, `staging`) | *Settings* → *Environments* → nom d’env → *Environment secrets*. Aligné avec les workflows qui déclarent `environment:`. |
| **GitHub — organisation** | Secrets partagés entre dépôts, OIDC, policies | *Organization settings* → *Secrets and variables* → *Actions*. Croiser avec [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces) / `GITHUB_LINEAR_INVENTORY_WEA12.md`. |
| **GitHub — workflow réutilisable** (ex. ce dépôt `WeAdU-ltd/.github`) | Secrets **passés par l’appelant** : ne sont pas définis dans le dépôt `.github` lui-même | Lire l’appel `workflow_call` / `uses:` dans le dépôt **application** ; les valeurs vivent dans les secrets du dépôt appelant. Exemple : [`auto-deploy.yml`](../.github/workflows/auto-deploy.yml) attend `env_file`, `ssh_private_key`, `ssh_known_hosts`. |
| **Cursor Cloud Agents** | `OP_SERVICE_ACCOUNT_TOKEN` | Same token as SDK ; CLI `op` optional via devcontainer — [`ONEPASSWORD_AGENTS.md`](./ONEPASSWORD_AGENTS.md) |
| **1Password** (vault équipe) | Mots de passe, clés, certificats, « Service Account » | Doc interne du vault / convention de nommage ; **une** consultation planifiée ; éviter boucles de recherche. |
| **Autres fournisseurs** | OAuth client secrets, clés cloud (GCP, AWS…), webhooks | Runbooks du dépôt ([`GOOGLE_OAUTH_WEA20.md`](./GOOGLE_OAUTH_WEA20.md)), *Secrets Manager* du cloud, tickets Linear liés (ex. chaîne Google [WEA-20](https://linear.app/weadu/issue/WEA-20/google-passe-oauth-gmail-drive-docs-sheets-ads-analytics)). |
| **n8n** (Cloud ou self-hosted) | URL de base, clé API, auth éventuelle ; SMTP / digest humain | Conventions [WEA-26](https://linear.app/weadu/issue/WEA-26/n8n-hebergement-20-euromois-cloud-vs-vps-mise-en-service) : [`WEA-26-n8n-hebergement.md`](./WEA-26-n8n-hebergement.md). Politique d’envoi humain (UK) [WEA-19](https://linear.app/weadu/issue/WEA-19/notifications-e-mail-prioritaire-5h-23h-uk-slack-calme-20h-7h-urgence) : [`NOTIFICATIONS_EMAIL_SLACK_WEA19.md`](./NOTIFICATIONS_EMAIL_SLACK_WEA19.md). Workflow + noms SMTP / mail [WEA-31](https://linear.app/weadu/issue/WEA-31/n8n-files-e-mail-humain-etalement-5h-23h-uk-integrations) : [`WEA-31-n8n-human-email-queue.md`](./WEA-31-n8n-human-email-queue.md). |
| **Interactive Brokers (UK)** | Identifiants portail, certificats Client Portal Gateway si utilisés, paramètres connexion API (hôte/port hors Git uniquement via env) | Isolation **finance-RH** ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)) ; procédure API / smoke dans [`INTERACTIVE_BROKERS_UK_WEA30.md`](./INTERACTIVE_BROKERS_UK_WEA30.md) ([WEA-30](https://linear.app/weadu/issue/WEA-30/interactive-brokers-uk-api-et-ordres-autonomes)). |
| **Slack — app agents** | Bot token `xoxb-…` (nom canonique `SLACK_BOT_TOKEN`) | Org ou dépôt GitHub / socle [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh) ; procédure et règles anti-notification dans [`SLACK_APP_AGENTS_WEA25.md`](./SLACK_APP_AGENTS_WEA25.md) ([WEA-25](https://linear.app/weadu/issue/WEA-25/slack-app-agents-regles-anti-notification)). |
| **Brave Search API** | Clé API recherche web (`X-Subscription-Token`) | Doc [`BRAVE_SEARCH_API_WEA22.md`](./BRAVE_SEARCH_API_WEA22.md), ticket [WEA-22](https://linear.app/weadu/issue/WEA-22/brave-search-api-cles-et-quotas-pour-agents) ; variable **`BRAVE_SEARCH_API_KEY`**. |
| **Gmail (agents)** | Client OAuth, secret, refresh token (compte ou identité dédiée agents) | Runbook [`GMAIL_AGENTS_WEA24.md`](./GMAIL_AGENTS_WEA24.md) ([WEA-24](https://linear.app/weadu/issue/WEA-24/gmail-acces-agents-lecture-envoi)) ; noms **`GMAIL_OAUTH_CLIENT_ID`**, **`GMAIL_OAUTH_CLIENT_SECRET`**, **`GMAIL_OAUTH_REFRESH_TOKEN`** ; OAuth client selon [WEA-20](./GOOGLE_OAUTH_WEA20.md). |
| **WeAdU-ltd/.github — alertes CI** | `SLACK_CI_ALERT_WEBHOOK_URL` (Incoming Webhook Slack) | Secret **dépôt** ou org — [`GITHUB_CI_FAILURE_ALERT.md`](./GITHUB_CI_FAILURE_ALERT.md) |
| **WeAdU-ltd/.github — poll org (optionnel)** | `GH_ORG_READ_TOKEN` (PAT fine-grained, lecture Actions) | Même doc ; accès read aux runs de tous les dépôts de l’org |

---

## Référence : déploiement via workflow réutilisable

Les dépôts applicatifs qui consomment `WeAdU-ltd/.github/.github/workflows/auto-deploy.yml` doivent déclarer les secrets **dans le dépôt appelant** (voir [README principal](../README.md)). Les agents cherchent donc d’abord le workflow appelant et les secrets nommés là, pas uniquement le dépôt `.github`.

---

_Document statique ; mise à jour lorsque le [socle secrets (WEA-15)](./SECRETS_SOCLE_WEA15.md) ou les conventions d’équipe évoluent._
