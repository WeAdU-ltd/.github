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

**Convention:** put the Linear identifier in the **PR title** (for example `fix: thing (WEA-39)`).
Only the title is scanned by default so issues mentioned in the PR body are not closed by accident.
Set `LINEAR_DONE_SCAN_BODY` to `true` in the workflow step `env` if you need title + body.

**Setup:** add a repository secret `LINEAR_API_KEY` with a Linear API key that can update issues.
If the secret is missing, the job exits successfully and does nothing (safe default).
