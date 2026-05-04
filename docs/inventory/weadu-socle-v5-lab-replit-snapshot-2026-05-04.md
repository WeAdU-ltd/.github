# Project Snapshot — Weadu-Socle-V5-Lab
**Repl courant — export structuré, aucune valeur de secret**
**Produit le :** 2026-05-04
**Source :** lecture directe des fichiers + variables d'environnement live

---

## 1. Stack

| Champ | Valeur |
|---|---|
| **Langage** | Python 3.11 |
| **Framework web** | FastAPI 0.135+ + Uvicorn |
| **Gestionnaire de paquets** | `uv` via `pyproject.toml` |
| **Port exposé** | 5000 (mappé → port externe 80) |
| **Runtime Nix** | `stable-25_05`, paquet système `libxcrypt` |

### Dépendances principales (`pyproject.toml`)

| Package | Usage |
|---|---|
| `fastapi`, `uvicorn` | Framework web + serveur ASGI |
| `pydantic` | Validation des modèles |
| `sqlmodel` | ORM Ideas Dashboard |
| `psycopg2-binary` | Driver PostgreSQL |
| `sqlalchemy` | Engine bas niveau (pg.py) |
| `anthropic` | Client Claude API (Haiku + Sonnet) |
| `onepassword-sdk` | Chargement secrets 1Password |
| `slack-sdk` | Web API + Socket Mode (AI Council) |
| `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2` | Google OAuth + Sheets/Drive/Ads |
| `boto3` | AWS DynamoDB (Portfolio Manager) + push secrets EC2 |
| `httpx` | Client HTTP async |
| `openpyxl` | Export Excel (onboarding sheet) |

### Fichiers d'entrée et de configuration

| Fichier | Rôle |
|---|---|
| `main.py` | Point d'entrée FastAPI — 2 300 lignes, tous les endpoints |
| `pyproject.toml` | Dépendances et métadonnées (Python ≥ 3.11) |
| `.replit` | `entrypoint = "main.py"`, `deploymentTarget = "vm"`, ports, workflows |
| `app/core/config.py` | Configuration non-secrète (IDs Google Sheets, paramètres Google Ads) |
| `config/infra_projects.json` | Registre des 20 projets surveillés |
| `config/governance.md` | Règles R1-R15 (ne jamais modifier sans accord) |

---

## 2. Run local — commandes exactes

```bash
# Lancement complet (identique au workflow Replit et au déploiement prod)
bash tools/setup_ssh.sh && python main.py

# Vérifier que l'app répond
curl https://$REPLIT_DEV_DOMAIN/health

# Vérifier la synchro AWS
curl https://$REPLIT_DEV_DOMAIN/aws/status

# Consulter Claude (économique)
python3 tools/ask_claude.py "ta question" --model haiku

# Consulter Claude avec contexte projet complet
python3 tools/ask_claude.py "ta question" --model haiku --context

# Valider le kit 1Password + Claude + Slack
python3 kit/validate_kit.py
```

> `tools/setup_ssh.sh` reconstruit la clé SSH AWS (`~/.ssh/id_ed25519_aws`) depuis
> le secret `AWS_SSH_KEY_B64` — obligatoire à chaque démarrage car le container
> Replit est éphémère.

---

## 3. Git

| Champ | Valeur |
|---|---|
| **Branche par défaut** | `main` |
| **Remote GitHub** | **Aucun** — pas de remote GitHub/GitLab configuré |
| **Remote interne Replit** | `gitsafe-backup` → `git://gitsafe:5418/backup.git` (backup auto Replit) |
| **Remotes subrepl** | 6 remotes `subrepl-*` → `git+ssh://git@ssh.picard.replit.dev:/home/runner/workspace` (workspaces agent internes) |
| **Branches locales** | `main`, `replit-agent`, `subrepl-8mpebpbn`, `subrepl-9uh4oiiv`, `subrepl-a7lltuam`, `subrepl-d01ofgx9`, `subrepl-fkorz7yh`, `subrepl-v1wpi1y5` |

### Derniers commits (HEAD → main)

| Hash | Message |
|---|---|
| `2eba5bf` | Add an inventory of all existing projects and their details |
| `e2cb017` | Fix issues preventing the AI council from responding to debate messages |
| `4aa3db6` | Update AI Council to use dedicated log channel for debates |
| `483e252` | Add channel IDs to vault loader and improve error handling |
| `b76995f` | Add structured debate protocol and improve channel resolution |

> **Note** : `github_repo` n'est renseigné dans aucun projet de `config/infra_projects.json`.
> L'audit profond quotidien (`GITHUB_TOKEN` dans 1Password) ne s'exécute donc sur aucun repo pour l'instant.

---

## 4. Secrets — noms de variables uniquement

### 4a. Replit Secrets (injectés directement dans l'environnement au démarrage du container)

| Variable | Usage |
|---|---|
| `OP_SERVICE_ACCOUNT_TOKEN` | Bootstrap 1Password — seule clé stockée dans Replit Secrets (toutes les autres viennent de 1Password via ce token) |
| `SESSION_SECRET` | Secret de session FastAPI |
| `SOCLE_SLACK_BOT_TOKEN` | Bot token Slack direct (redondance avec `SLACK_BOT_TOKEN` chargé via 1Password) |
| `SMTP_USER` | Adresse email expéditeur SMTP (valeur non-secrète visible dans `.replit` `[userenv.shared]`) |

> Les variables `DATABASE_URL`, `PGHOST`, `PGDATABASE`, `PGPORT`, `PGUSER`
> sont **injectées automatiquement par Replit** lors du provisionnement PostgreSQL —
> elles ne sont pas gérées manuellement dans Replit Secrets.

### 4b. Chargées depuis 1Password vault `Replit` au démarrage (`vault_loader.py`)

| Variable | Requis | Usage |
|---|---|---|
| `ANTHROPIC_API_KEY` | **Oui** | Claude API — tous les appels IA |
| `SLACK_BOT_TOKEN` | Non | Slack Web API (xoxb-) — alertes, AI Council |
| `SLACK_APP_TOKEN` | Non | Socket Mode (xapp-) — écoute temps réel `#ai-council-log` |
| `SLACK_WEBHOOK_URL` | Non | Webhook alertes canal principal |
| `SLACK_WEBHOOK_JEFF` | Non | Webhook DM Jeff |
| `SLACK_USER_ID` | Non | ID Slack de Jeff (détection pause AI Council) |
| `SLACK_COUNCIL_CHANNEL_ID` | Non | ID canal `#ai-council` |
| `SLACK_LOG_CHANNEL_ID` | Non | ID canal `#ai-council-log` |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Non | Service account Google (Sheets, Drive, Docs) |
| `NOTION_TOKEN` | Non | Notion API — création/lecture tâches |
| `GITHUB_TOKEN` | Non | Audit profond quotidien — lecture repos |
| `AWS_SSH_KEY_B64` | Non | Clé SSH EC2 en base64 — reconstituée dans `~/.ssh/id_ed25519_aws` |
| `AWS_ACCESS_KEY_ID` | Non | IAM AWS — DynamoDB Portfolio Manager |
| `AWS_SECRET_ACCESS_KEY` | Non | IAM AWS — DynamoDB Portfolio Manager |

**Total secrets gérés : 4 Replit Secrets + 14 via 1Password = 18 variables**

---

## 5. Base de données Replit

**PostgreSQL Replit managé : Oui**

| Table | Description | Schéma clé |
|---|---|---|
| `kv_state` | Clé-valeur générique JSONB — état persistant du système | `key TEXT PK`, `value JSONB`, `updated_at TIMESTAMPTZ` |
| `ideas` | Ideas Dashboard — toutes les idées (CRUD + IA) | `id`, `title`, `description`, `status`, `deadline`, `progress_log`, `possible_duplicate_of`, `duplicate_dismissed` |

### Clés actives dans `kv_state`

| Clé | Contenu |
|---|---|
| `council_state` | État paused/active du AI Council + timestamps |
| `debate_threads` | Threads de débat en cours dans `#ai-council-log` |
| `nudged_projects` | Projets déjà relancés (circuit breaker portfolio) |
| `questionnaire_cos_notified` | Flag notification questionnaire envoyé |

### DynamoDB AWS (eu-west-2) — Portfolio Manager Phase 1b

| Table | Usage |
|---|---|
| `PortfolioRegistry-prod` | Registre autoritatif des 20+ projets |
| `PortfolioHeartbeats-prod` | Dernier heartbeat par projet (TTL 7 jours) |
| `PortfolioContextEvents-prod` | Historique complet des événements projet |
| `ClientRegistry-prod` | Noms canoniques des clients avec aliases |

> Fallback automatique vers fichier local `.local/portfolio_state.json` si
> `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` sont absents.

---

## 6. Déploiement

| Champ | Valeur |
|---|---|
| **URL `.replit.app`** | `https://weadu-socle-v-5-lab.replit.app` (confirmé dans `app/core/config.py` → `IDEAS_BASE_URL`) |
| **Type de déploiement** | `deploymentTarget = "vm"` (Reserved VM — ligne dans `.replit`) |
| **Always On** | Non confirmé — le CSV équipe du 17/03/2026 indiquait "not deployed" ; le type VM dans `.replit` est configuré mais l'état actuel du déploiement prod n'est pas vérifié depuis ce workspace |
| **Workflow dev** | `bash tools/setup_ssh.sh && python main.py` (identique prod et dev) |
| **Charge** | Production active : AI Council en Socket Mode (temps réel), watcher COS toutes les 10 min, audit profond quotidien 7h Paris, cross-reviewer 23h Paris, rapports Slack quotidiens |
| **Distinction prod/dev** | `IS_PROD = os.environ.get("REPLIT_DEPLOYMENT", "") == "1"` — en dev : `push_cos_config()` ignoré, heartbeats prod non envoyés |

---

## 7. Services externes

### AWS Lightsail (EC2)

| Champ | Valeur |
|---|---|
| **IP** | `52.56.83.170` |
| **Région** | `eu-west-2a` |
| **OS** | Windows Server 2022 |
| **Utilisateur SSH** | `Administrator` (jamais `ubuntu`) |
| **Clé SSH** | Ed25519, reconstruite depuis `AWS_SSH_KEY_B64`, chemin `~/.ssh/id_ed25519_aws` |
| **Alias SSH Replit** | `aws-stocks` |
| **Ce que Socle fait sur EC2** | (1) Push 14 secrets vers `C:\ProgramData\.secret_cache\` au démarrage ; (2) Push config COS vers `C:\Scripts\weadu\cos\aws_secrets.env` (prod uniquement) ; (3) Health check COS `localhost:5050` via SSH toutes les 10 min ; (4) Déploiement COS via `tools/deploy_to_ec2.py` |

### AWS DynamoDB

| Champ | Valeur |
|---|---|
| **Région** | `eu-west-2` |
| **Auth** | `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` (IAM, via 1Password) |
| **Tables** | `PortfolioRegistry-prod`, `PortfolioHeartbeats-prod`, `PortfolioContextEvents-prod`, `ClientRegistry-prod` |
| **Infra as code** | `infrastructure/portfolio-manager/dynamodb-tables.yaml` (CloudFormation) |

### Slack

| Champ | Valeur |
|---|---|
| **Bot token** | `SLACK_BOT_TOKEN` (xoxb-) — Web API |
| **App token** | `SLACK_APP_TOKEN` (xapp-) — Socket Mode (WebSocket sortant, pas de HTTP entrant) |
| **Webhooks** | `SLACK_WEBHOOK_URL` (canal principal), `SLACK_WEBHOOK_JEFF` (DM Jeff) |
| **Canaux actifs** | `#ai-council` (lecture seule pour Socle v2), `#ai-council-log` (Socle répond dans les threads COS) |
| **Bot Socle** | `bot_id=B0AL0J7NLJZ` |

### Anthropic Claude

| Champ | Valeur |
|---|---|
| **Clé** | `ANTHROPIC_API_KEY` (via 1Password) |
| **Modèle principal** | `claude-sonnet-4-20250514` |
| **Modèle économique** | `claude-haiku-3-5` |
| **Usages** | AI Council (débats), duplicate detection Ideas, cross-reviewer 23h, deep audit 7h, génération briefs |
| **Journal** | `output/claude_calls.jsonl` (cappé 10 000 entrées) |

### Google

| Service | Usage | Auth |
|---|---|---|
| **Google Sheets** | Lecture/écriture feuille famille (`AF_SPREADSHEET_ID`) + Execution Log dashboards | Service Account JSON |
| **Google Drive / Docs / Tasks / Gmail / Apps Script / Analytics** | OAuth 2.0, scopes configurés | `GOOGLE_OAUTH_CLIENT_ID` + `GOOGLE_OAUTH_CLIENT_SECRET` (1Password) |
| **Google Ads API** | Périmètre MCC `635-111-4788` uniquement (R11 governance) | `GOOGLE_ADS_DEVELOPER_TOKEN`, `GOOGLE_ADS_MCC_CUSTOMER_ID`, `GOOGLE_ADS_REFRESH_TOKEN` (pushés vers COS) |
| **Tokens stockés** | `config/google_tokens.json` (gitignored) | — |

### OAuth Google — Redirect URIs enregistrées dans Google Cloud Console

```
https://3194f6df-244f-4f58-84f3-868f0387782b-00-8ykz5nzxp7d7.picard.replit.dev/auth/google/callback
```
> URI workspace dev (éphémère). L'URI prod `.replit.app/auth/google/callback` n'est pas confirmée comme enregistrée.

### Notion

| Champ | Valeur |
|---|---|
| **Token** | `NOTION_TOKEN` (via 1Password) |
| **Usage** | Lecture/création tâches Notion via `/notion/tasks` et `/notion/clients` |

### 1Password SDK

| Champ | Valeur |
|---|---|
| **SDK** | `onepassword-sdk>=0.4.0` |
| **Vault principal** | `Replit` |
| **Vault secondaire** | `Tech` |
| **Bootstrap token** | `OP_SERVICE_ACCOUNT_TOKEN` (seul secret stocké dans Replit Secrets) |
| **Cache local** | `/tmp/.secret_cache.json` (TTL 4h) |

### AWS SNS (récepteur webhook)

| Champ | Valeur |
|---|---|
| **Endpoint** | `POST /alerts/sns` (alias legacy : `/alerts/cos`) |
| **Usage** | Récepteur HTTPS générique pour topics SNS — auto-confirme, forward vers Slack `#ai-council` |

---

## Résumé "ne pas coller dans Linear"

Les éléments suivants **ne doivent pas apparaître dans un ticket Linear** :
- Les valeurs des variables d'environnement (même tronquées)
- Le contenu de `config/google_tokens.json`
- Le contenu de `/tmp/.secret_cache.json`
- L'IP AWS `52.56.83.170` combinée avec des clés ou credentials
- Tout log contenant des tokens Slack (`xoxb-`, `xapp-`)

**Ce document lui-même est safe** — aucune valeur de secret, uniquement des noms de variables et des métadonnées techniques.
