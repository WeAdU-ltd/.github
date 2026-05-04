# .github

Shared GitHub Actions assets for the WeAdU organization.

## Reusable workflows

### `auto-deploy.yml`

Reusable deployment workflow intended to be called from application repositories.

Features:

- checks out either the triggering SHA or an explicit ref
- supports optional setup and build commands before deployment
- writes a multiline `.env`-style secret to disk when needed
- configures SSH credentials for deployments that need them
- serializes deployments per repository/environment with GitHub concurrency

Example caller workflow:

```yaml
name: Deploy production

on:
  push:
    branches:
      - main

jobs:
  deploy:
    uses: WeAdU-ltd/.github/.github/workflows/auto-deploy.yml@main
    with:
      environment: production
      setup_command: npm ci
      build_command: npm run build
      deploy_command: |
        rsync -az --delete ./ deploy@example.com:/srv/my-app/
        ssh deploy@example.com 'cd /srv/my-app && docker compose up -d --build'
    secrets:
      env_file: ${{ secrets.PRODUCTION_ENV_FILE }}
      ssh_private_key: ${{ secrets.PRODUCTION_SSH_PRIVATE_KEY }}
      ssh_known_hosts: ${{ secrets.PRODUCTION_SSH_KNOWN_HOSTS }}
```

Caller repositories can omit the SSH and env-file secrets if their deploy command
does not need them.

## Documentation (WeAdU / Linear)

Anchors in [`docs/`](docs/):

- [Google OAuth (WEA-20)](docs/GOOGLE_OAUTH_WEA20.md) — scopes, redirect URIs, écran de consentement.
- [GitHub ↔ Linear inventory (WEA-12)](docs/GITHUB_LINEAR_INVENTORY_WEA12.md)
- [Branch protection + anti-secrets (WEA-32)](docs/GITHUB_BRANCH_PROTECTION_WEA32.md) — règles `main`, audit API, Gitleaks CI / pre-commit.
- [Secrets cartographie (WEA-14)](docs/SECRETS_CARTOGRAPHIE_WEA14.md) — où chercher avant de demander une valeur.
- [LLM routing, cost, budget (WEA-18)](docs/WEA-18-llm-routing-cost.md)
- **Inventaires cloud** (régénérables par script, secrets hors repo) :
  - [GCP (WEA-27)](docs/inventory/WEA-27-google-cloud.md)
  - [OVH (WEA-28)](docs/inventory/WEA-28-ovh-duplicates.md)
  - [AWS EC2 (WEA-29)](docs/inventory/WEA-29-aws-ec2-inventory.md)

## n8n hosting (budget < 20 €/mois)

Décision documentée et checklist : [`docs/WEA-26-n8n-hebergement.md`](docs/WEA-26-n8n-hebergement.md) ([WEA-26](https://linear.app/weadu/issue/WEA-26/n8n-hebergement-20-euromois-cloud-vs-vps-mise-en-service)). Les valeurs secrètes restent dans le socle secrets ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)), pas dans ce dépôt.

## Brave Search API (agents)

Convention secrets + smoke test : [`docs/BRAVE_SEARCH_API_WEA22.md`](docs/BRAVE_SEARCH_API_WEA22.md) ([WEA-22](https://linear.app/weadu/issue/WEA-22/brave-search-api-cles-et-quotas-pour-agents)).

## Cursor hooks (commit / agent)

Project file [`.cursor/hooks.json`](.cursor/hooks.json) declares `"version": 1` and an empty
`hooks` map so Cursor validates the file and avoids spurious hook errors (for example
**invalid variable name** when the IDE loads a broken or legacy hook config). To add hooks,
extend `hooks` per [Cursor hooks](https://cursor.com/docs) (do not remove `version`).

**Contournement agent cloud :** si l’erreur « invalid variable name » vient du scanner de secrets
(`pre-commit.cursor`), il faut ignorer les entrées de `CLOUD_AGENT_INJECTED_SECRET_NAMES` qui ne
sont pas des identifiants bash valides avant `${!NAME}` (correctif côté image / hooks Cursor).

## Scraping (Decodo, ScraperAPI, Zyte)

Convention de **clés** (variables d’environnement) et **matrice cas → fournisseur** pour les agents : [`docs/SCRAPING_DECODO_SCRAPERAPI_ZYTE_WEA23.md`](docs/SCRAPING_DECODO_SCRAPERAPI_ZYTE_WEA23.md) ([WEA-23](https://linear.app/weadu/issue/WEA-23/scraping-decodo-scraperapi-zyte-cles-routage)). Le stockage effectif des secrets suit le socle [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh).

## Interactive Brokers (UK) — API (WEA-30)

Guide agents : chemins API (Web / TWS), cadre ordres autonomes, risque courtage, smoke script — [`docs/INTERACTIVE_BROKERS_UK_WEA30.md`](docs/INTERACTIVE_BROKERS_UK_WEA30.md) ([Linear WEA-30](https://linear.app/weadu/issue/WEA-30/interactive-brokers-uk-api-et-ordres-autonomes)).

## Slack (agents / automation)

Pour l’app Slack, le jeton bot (`SLACK_BOT_TOKEN`) et les règles anti-notification (canaux dédiés, fils, pas de `@here` / `@channel` ; alignement [WEA-19](https://linear.app/weadu/issue/WEA-19/notifications-e-mail-prioritaire-5h-23h-uk-slack-calme-20h-7h-urgence)), voir [`docs/SLACK_APP_AGENTS_WEA25.md`](docs/SLACK_APP_AGENTS_WEA25.md).

## Auto-merge pull requests to `main`

Workflow [`.github/workflows/auto-merge-pr.yml`](.github/workflows/auto-merge-pr.yml) runs on
each PR update and calls `gh pr merge --auto --merge` so GitHub **queues the merge** when branch
protection allows it (same pattern as other WeAdU repos such as NEG). After **CI** and any other
required checks go green, the merge completes without a human clicking Merge. Ensure **Allow
auto-merge** is enabled on the repository and that **required status checks** include the jobs you
care about (here: `actionlint` and `gitleaks` from [`ci.yml`](.github/workflows/ci.yml)).

## Linear — sync checklist into the PR (WEA-*)

Workflow [`.github/workflows/linear-sync-pr-criteria.yml`](.github/workflows/linear-sync-pr-criteria.yml)
runs when a PR is opened or updated. If the branch or title contains a **WEA-*** id and the Linear
issue has a `## Critères de fait` section, that block is **appended to the PR body** automatically
(you do not need to copy-paste from Linear). Tick `[x]` on the ticket or in the PR when each
criterion is satisfied.

## This repository — Linear Done on merge

When a pull request is **merged into the default branch** (`main`), the workflow
[`.github/workflows/linear-done-on-merge.yml`](.github/workflows/linear-done-on-merge.yml)
runs [`scripts/linear_mark_done_on_merge.py`](scripts/linear_mark_done_on_merge.py) and
moves matching Linear issues to the team **completed** (Done) state when policy allows it.

**WEA-*** tickets (WeAdU team key `WEA`): the script moves the issue to **Done** only if every
bullet under `## Critères de fait` has an explicit `[x]`, using **first** the merged PR body (if
that section has checklist bullets), **else** the same section on the **Linear issue description**.
If not met, an **Écart** comment is posted and the issue stays open (no false Done). Other team keys
are unchanged (no checklist gate).

**How tickets are found (no manual PR title needed):** the script looks for identifiers like
`WEA-39` in the **head branch name** and in the **PR title** (case-insensitive, e.g. `wea-39` in
`jeff/wea-39-short-title` or `cursor/wea-39-foo-d965`). That matches typical Linear / agent branch
names. Optional: set `LINEAR_DONE_SCAN_BODY` to `true` on the workflow step to also scan the PR
body (use only if you accept the risk of closing tickets that are only mentioned in prose).

**Secrets:** if `LINEAR_API_KEY` is an **organization** secret, ensure this repository is in the
secret’s access list so the workflow receives it. Repository-level secrets with the same name also
work. If the key is missing from the job, the script exits successfully and does nothing. For the
full org convention (shared secrets, new internal repos, finance-RH isolation), see
[`docs/SECRETS_SOCLE_WEA15.md`](docs/SECRETS_SOCLE_WEA15.md).

**About “merge the PR”:** [auto-merge](#auto-merge-pull-requests-to-main) handles queuing the
merge when checks pass; this Linear job runs **after** the merge exists and updates issues
according to the rules above.
