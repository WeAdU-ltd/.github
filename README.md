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

### `flip-flop-deploy.yml`

Zero-downtime deployment workflow using the flip-flop pattern. Each deploy lands
in a timestamped release directory on the remote server, and the live symlink is
atomically swapped to the new release only after the transfer completes.

Features:

- zero-downtime deploys via atomic symlink swap (`ln -sfn`)
- timestamped release directories (`<unix_time>-<short_sha>`)
- optional setup and build commands run locally before rsync
- rsync-based file transfer to the remote server
- optional post-activation command (e.g. restart services, run migrations)
- automatic cleanup of old releases (configurable retention count)
- env file materialization (included in rsync transfer)
- SSH credential management
- concurrency serialization per repository/environment

Example caller workflow:

```yaml
name: Deploy production

on:
  push:
    branches:
      - main

jobs:
  deploy:
    uses: WeAdU-ltd/.github/.github/workflows/flip-flop-deploy.yml@main
    with:
      environment: production
      ssh_connection: deploy@example.com
      remote_base_dir: /srv/my-app
      remote_public_dir: /srv/my-app/current
      setup_command: npm ci
      build_command: npm run build
      post_activate_command: docker compose up -d --build
      keep_releases: 5
    secrets:
      env_file: ${{ secrets.PRODUCTION_ENV_FILE }}
      ssh_private_key: ${{ secrets.PRODUCTION_SSH_PRIVATE_KEY }}
      ssh_known_hosts: ${{ secrets.PRODUCTION_SSH_KNOWN_HOSTS }}
```

The `env_file` secret is optional. All other secrets are required since this
workflow always connects to a remote server over SSH.
