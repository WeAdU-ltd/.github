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

### `auto-merge-enable.yml`

Reusable workflow: enables **GitHub auto-merge** on a PR number (`gh pr merge --auto --merge`).
Use from **any** repo in the org so every project gets the same behavior as this `.github` repo.

```yaml
on:
  pull_request:
    types: [opened, reopened, synchronize, ready_for_review]

jobs:
  enable-auto-merge:
    if: github.event.pull_request.draft == false
    uses: WeAdU-ltd/.github/.github/workflows/auto-merge-enable.yml@main
    permissions:
      contents: write
      pull-requests: write
    with:
      pr_number: ${{ github.event.pull_request.number }}
```

Tighten the `if:` (default branch, same-repo forks only) to match [`.github/workflows/auto-merge-pr.yml`](.github/workflows/auto-merge-pr.yml) if you fork or use unusual bases.

## Documentation (WeAdU / Linear)

Anchors in [`docs/`](docs/):

- [Google OAuth (WEA-20)](docs/GOOGLE_OAUTH_WEA20.md) — scopes, redirect URIs, écran de consentement.
- [Gmail agents — lecture + envoi (WEA-24)](docs/GMAIL_AGENTS_WEA24.md) — secrets nommés, conventions, smoke script.
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

**Contournement agent cloud (commit / push) :** si le hook `pre-commit.cursor` échoue avec **invalid variable name** (souvent à cause d’une entrée mal formée dans `CLOUD_AGENT_INJECTED_SECRET_NAMES` côté image Cursor), exécuter `git commit --no-verify` pour ce dépôt ; la **CI** sur GitHub exécute actionlint et les smokes dry-run. Le correctif durable est côté **Cursor** (filtrer les noms d’environnement non valides pour bash avant `${!NAME}`) — voir le paragraphe ci-dessus.

## Scraping (Decodo, ScraperAPI, Zyte)

Convention de **clés** (variables d’environnement) et **matrice cas → fournisseur** pour les agents : [`docs/SCRAPING_DECODO_SCRAPERAPI_ZYTE_WEA23.md`](docs/SCRAPING_DECODO_SCRAPERAPI_ZYTE_WEA23.md) ([WEA-23](https://linear.app/weadu/issue/WEA-23/scraping-decodo-scraperapi-zyte-cles-routage)). Le stockage effectif des secrets suit le socle [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh).

## Interactive Brokers (UK) — API (WEA-30)

Guide agents : chemins API (Web / TWS), cadre ordres autonomes, risque courtage, smoke script — [`docs/INTERACTIVE_BROKERS_UK_WEA30.md`](docs/INTERACTIVE_BROKERS_UK_WEA30.md) ([Linear WEA-30](https://linear.app/weadu/issue/WEA-30/interactive-brokers-uk-api-et-ordres-autonomes)).

## Slack (agents / automation)

Pour l’app Slack, le jeton bot (`SLACK_BOT_TOKEN`) et les règles anti-notification (canaux dédiés, fils, pas de `@here` / `@channel` ; alignement [WEA-19](https://linear.app/weadu/issue/WEA-19/notifications-e-mail-prioritaire-5h-23h-uk-slack-calme-20h-7h-urgence)), voir [`docs/SLACK_APP_AGENTS_WEA25.md`](docs/SLACK_APP_AGENTS_WEA25.md).

## Gmail (agents — lecture + envoi)

OAuth refresh token + smoke (profil Gmail, envoi test **vers soi** avec `--send`) : [`docs/GMAIL_AGENTS_WEA24.md`](docs/GMAIL_AGENTS_WEA24.md) ([WEA-24](https://linear.app/weadu/issue/WEA-24/gmail-acces-agents-lecture-envoi)). Les valeurs secrètes suivent le socle [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh). Vérification **sans terminal** : workflow manuel [`.github/workflows/gmail-smoke-wea24.yml`](.github/workflows/gmail-smoke-wea24.yml) (GitHub → Actions → **Gmail smoke (WEA-24)** → Run workflow).

## Auto-merge pull requests to `main`

Workflow [`.github/workflows/auto-merge-pr.yml`](.github/workflows/auto-merge-pr.yml) calls the reusable [`auto-merge-enable.yml`](.github/workflows/auto-merge-enable.yml) so GitHub **queues the merge** when branch protection allows it (same pattern as other WeAdU repos such as NEG). After **CI** and any other required checks go green, the merge completes without a human clicking Merge.

**Repository setting — enable once per repo (or for the whole org):** GitHub requires **Allow auto-merge** on the repository. To turn it on for **every** repo under `WeAdU-ltd` in one shot (uses your local `gh` login, no token in the repo):

```bash
gh auth login   # if needed
python3 scripts/github_enable_auto_merge_org.py --org WeAdU-ltd
```

Use `--dry-run` first to see which repos would be updated.

**Org-wide for PRs:** copy the caller snippet under [`auto-merge-enable.yml`](#auto-merge-enableyml) into each application repo (or add it via a codemod / template). Until that workflow exists in a repo, only manual Merge remains there — **auto-merge is not a GitHub org-wide toggle for PRs**.

**Checks:** ensure **required status checks** list the jobs you care about. On this repository the **`actionlint`** job from [`ci.yml`](.github/workflows/ci.yml) also runs **gitleaks** (do not add a second required check for gitleaks unless you split jobs).

**Security note:** auto-merge merges when **required** checks pass; it does **not** bypass branch protection or reviews if your rules require them. A PAT does not replace these rules.

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
