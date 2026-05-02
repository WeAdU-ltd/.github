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

## This repository — Linear Done on merge

When a pull request is **merged into the default branch** (`main`), the workflow
[`.github/workflows/linear-done-on-merge.yml`](.github/workflows/linear-done-on-merge.yml)
runs [`scripts/linear_mark_done_on_merge.py`](scripts/linear_mark_done_on_merge.py) and
moves matching Linear issues to the team **completed** (Done) state.

**How tickets are found (no manual PR title needed):** the script looks for identifiers like
`WEA-39` in the **head branch name** and in the **PR title** (case-insensitive, e.g. `wea-39` in
`jeff/wea-39-short-title` or `cursor/wea-39-foo-d965`). That matches typical Linear / agent branch
names. Optional: set `LINEAR_DONE_SCAN_BODY` to `true` on the workflow step to also scan the PR
body (use only if you accept the risk of closing tickets that are only mentioned in prose).

**Secrets:** if `LINEAR_API_KEY` is an **organization** secret, ensure this repository is in the
secret’s access list so the workflow receives it. Repository-level secrets with the same name also
work. If the key is missing from the job, the script exits successfully and does nothing.

**About “merge the PR”:** this automation runs **after** a merge. It does not replace whoever or
whatever merges the pull request (human, Cursor, or another bot). If merges are already automated
elsewhere, you do not need to merge by hand; this job only updates Linear once the merge exists.
