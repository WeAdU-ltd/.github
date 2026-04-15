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
