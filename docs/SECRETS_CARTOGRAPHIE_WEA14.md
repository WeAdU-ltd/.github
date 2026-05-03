# Cartographie des secrets (WEA-14)

Document d’ancrage pour le ticket [WEA-14](https://linear.app/weadu/issue/WEA-14/secrets-cartographie-1password-github-cursor-regle-chercher-avant-de). Il complète l’inventaire GitHub ↔ Linear ([WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces), voir [`GITHUB_LINEAR_INVENTORY_WEA12.md`](./GITHUB_LINEAR_INVENTORY_WEA12.md)). Le **socle secrets** (noms canoniques, org/environments, finance-RH, Cursor) est décrit dans [`SECRETS_SOCLE_WEA15.md`](./SECRETS_SOCLE_WEA15.md) ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)).

---

## Règle agents : chercher avant de demander

Avant de solliciter un humain pour un mot de passe, une clé API ou un jeton :

1. **Inventaires et docs du dépôt** : `README`, `docs/`, scripts d’inventaire (ex. `scripts/linear_github_inventory_wea12.py`), fichiers `CONTRIBUTING` / runbooks s’ils existent.
2. **Secrets « d’app »** : coffres ou secrets attachés à l’outil qui exécute le travail (GitHub Actions, environnement CI, variables du runner, secrets du dépôt appelant) plutôt qu’un coffre personnel générique.
3. **GitHub** : secrets et variables au niveau **organisation**, **dépôt** et **environnement** (`Settings` → `Secrets and variables` → `Actions` / `Dependabot` si utilisé). Pour les workflows réutilisables, les secrets passent depuis le workflow appelant (voir ci-dessous).
4. **Cursor** : secrets fournis dans l’UI ou la config cloud du workspace (pas dans le chat). Ne pas demander à l’humain une valeur déjà injectée côté agent si elle est documentée comme disponible dans ce canal.
5. **1Password** (ou équivalent) : **en dernier recours** si rien d’autre ne suffit, et en **évitant les appels répétés ou en rafale** (rate limits, quotas). Une seule lecture structurée vaut mieux que plusieurs requêtes fragmentées.

Si, après ces étapes, l’information manque encore : le noter sur le ticket Linear (écart par rapport aux critères de fait / [règle avant Done](https://linear.app/weadu/document/regle-agents-criteres-de-fait-avant-done-tous-projets-2b32aec9e234)) plutôt que d’inventer une valeur.

---

## 1Password — usage prudent

- Les intégrations CLI / Connect / SDK peuvent être **limitées en débit** ; privilégier les **secrets d’application** (GitHub Encrypted Secrets, secrets du fournisseur cloud, variables d’environnement du job) déjà prévus pour l’automation.
- Quand 1Password est nécessaire : cibler un **item / vault** connu, documenté pour l’équipe, plutôt qu’une recherche large et répétée.

---

## Tableau : outil → type de secret → comment chercher

| Outil / lieu | Types de secrets typiques | Comment les agents doivent chercher |
|--------------|---------------------------|--------------------------------------|
| **GitHub — dépôt** | PAT dédiés (si stockés en secret), clés de déploiement, tokens de packages, `ACTIONS_*` personnalisés | Onglet du dépôt → *Settings* → *Secrets and variables* → *Actions*. Lire aussi `.github/workflows/` pour les noms attendus (`secrets.NOM`). |
| **GitHub — environnement** | Secrets par `environment` (ex. `production`, `staging`) | *Settings* → *Environments* → nom d’env → *Environment secrets*. Aligné avec les workflows qui déclarent `environment:`. |
| **GitHub — organisation** | Secrets partagés entre dépôts, OIDC, policies | *Organization settings* → *Secrets and variables* → *Actions*. Croiser avec [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces) / `GITHUB_LINEAR_INVENTORY_WEA12.md`. |
| **GitHub — workflow réutilisable** (ex. ce dépôt `WeAdU-ltd/.github`) | Secrets **passés par l’appelant** : ne sont pas définis dans le dépôt `.github` lui-même | Lire l’appel `workflow_call` / `uses:` dans le dépôt **application** ; les valeurs vivent dans les secrets du dépôt appelant. Exemple : [`auto-deploy.yml`](../.github/workflows/auto-deploy.yml) attend `env_file`, `ssh_private_key`, `ssh_known_hosts`. |
| **Cursor Cloud / Desktop** | Clés API configurées pour l’agent, intégrations MCP | Paramètres du workspace / règles projet ; ne pas supposer que les secrets du poste local existent dans le cloud. |
| **1Password** (vault équipe) | Mots de passe, clés, certificats, « Service Account » | Doc interne du vault / convention de nommage ; **une** consultation planifiée ; éviter boucles de recherche. |
| **Autres fournisseurs** | OAuth client secrets, clés cloud (GCP, AWS…), webhooks | Runbooks du dépôt ([`GOOGLE_OAUTH_WEA20.md`](./GOOGLE_OAUTH_WEA20.md)), *Secrets Manager* du cloud, tickets Linear liés (ex. chaîne Google [WEA-20](https://linear.app/weadu/issue/WEA-20/google-passe-oauth-gmail-drive-docs-sheets-ads-analytics)). |
| **Interactive Brokers (UK)** | Identifiants portail, certificats Client Portal Gateway si utilisés, paramètres connexion API (hôte/port hors Git uniquement via env) | Isolation **finance-RH** ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)) ; procédure API / smoke dans [`INTERACTIVE_BROKERS_UK_WEA30.md`](./INTERACTIVE_BROKERS_UK_WEA30.md) ([WEA-30](https://linear.app/weadu/issue/WEA-30/interactive-brokers-uk-api-et-ordres-autonomes)). |
| **Slack — app agents** | Bot token `xoxb-…` (nom canonique `SLACK_BOT_TOKEN`) | Org ou dépôt GitHub / socle [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh) ; procédure et règles anti-notification dans [`SLACK_APP_AGENTS_WEA25.md`](./SLACK_APP_AGENTS_WEA25.md) ([WEA-25](https://linear.app/weadu/issue/WEA-25/slack-app-agents-regles-anti-notification)). |
| **Brave Search API** | Clé API recherche web (`X-Subscription-Token`) | Doc [`BRAVE_SEARCH_API_WEA22.md`](./BRAVE_SEARCH_API_WEA22.md), ticket [WEA-22](https://linear.app/weadu/issue/WEA-22/brave-search-api-cles-et-quotas-pour-agents) ; variable **`BRAVE_SEARCH_API_KEY`**. |
| **Web scraping** (Decodo, ScraperAPI, Zyte) | Clés API, paires user/mot de passe (Decodo Basic) | Inventaire + routage : [`SCRAPING_DECODO_SCRAPERAPI_ZYTE_WEA23.md`](./SCRAPING_DECODO_SCRAPERAPI_ZYTE_WEA23.md) ([WEA-23](https://linear.app/weadu/issue/WEA-23/scraping-decodo-scraperapi-zyte-cles-routage)) ; emplacement des valeurs selon [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh). |

---

## Référence : déploiement via workflow réutilisable

Les dépôts applicatifs qui consomment `WeAdU-ltd/.github/.github/workflows/auto-deploy.yml` doivent déclarer les secrets **dans le dépôt appelant** (voir [README principal](../README.md)). Les agents cherchent donc d’abord le workflow appelant et les secrets nommés là, pas uniquement le dépôt `.github`.

---

_Document statique ; mise à jour lorsque le [socle secrets (WEA-15)](./SECRETS_SOCLE_WEA15.md) ou les conventions d’équipe évoluent._
