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

## Cursor hooks (commit / agent)

Project file [`.cursor/hooks.json`](.cursor/hooks.json) declares `"version": 1` and an empty
`hooks` map so Cursor validates the file and avoids spurious hook errors (for example
**invalid variable name** when the IDE loads a broken or legacy hook config). To add hooks,
extend `hooks` per [Cursor hooks](https://cursor.com/docs) (do not remove `version`).

**Contournement agent cloud :** si l’erreur « invalid variable name » vient du scanner de secrets
(`pre-commit.cursor`), il faut ignorer les entrées de `CLOUD_AGENT_INJECTED_SECRET_NAMES` qui ne
sont pas des identifiants bash valides avant `${!NAME}` (correctif côté image / hooks Cursor).

## Auto-merge pull requests to `main`

Workflow [`.github/workflows/auto-merge-pr.yml`](.github/workflows/auto-merge-pr.yml) runs on
each PR update and calls `gh pr merge --auto --merge` so GitHub **queues the merge** when branch
protection allows it (same pattern as other WeAdU repos such as NEG). After **CI** and any other
required checks go green, the merge completes without a human clicking Merge. Ensure **Allow
auto-merge** is enabled on the repository and that **required status checks** include the jobs you
care about (here: `actionlint` from [`ci.yml`](.github/workflows/ci.yml)).

## This repository — Linear Done on merge

When a pull request is **merged into the default branch** (`main`), the workflow
[`.github/workflows/linear-done-on-merge.yml`](.github/workflows/linear-done-on-merge.yml)
runs [`scripts/linear_mark_done_on_merge.py`](scripts/linear_mark_done_on_merge.py) and
moves matching Linear issues to the team **completed** (Done) state when policy allows it.

**WEA-*** tickets (WeAdU team key `WEA`): the script **does not** mark Done unless the merged PR
description contains a Markdown section **`## Critères de fait`** whose bullet lines each show an
explicit completed checkbox (`[x]`). Copy the checklist from Linear into the PR body and tick each
line when the criterion is actually satisfied; otherwise the automation posts an **Écart** comment
on the issue and leaves it open (no false Done). Other team keys are unchanged (no checklist gate).

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
