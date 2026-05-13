> **Ingestion dépôt `WeAdU-ltd/.github` — 2026-05-12** : texte fourni par le référent (chat). L’en-tête du document source cite **Wellbots**, **Socle V5.1 / After Framfield** et la date **2026-03-28** ; le référent confirme la correspondance avec le Repl **Max Conv Val Budget Mngt** (WEA-33 ligne **#7**) et le nom de dépôt **`WeAdU-ltd/max-conv-val-budget-mngt`**. En cas d’écart, reproduire l’export depuis le bon workspace Replit. **Aucune valeur de secret** dans ce fichier ; **pas d’IPv4 publique** (alignement [WEA-29](./WEA-29-aws-ec2-inventory.md)).

---

Wellbots — Architecture & Référence Technique
Généré le 2026-03-28 — Socle V5.1 / After Framfield

## 1. Stack

### Couche Replit — FastAPI (orchestration & monitoring)

| Élément | Valeur |
|---------|--------|
| Langage | Python 3.11 |
| Framework | FastAPI + Uvicorn |
| Gestionnaire de paquets | uv (`pyproject.toml`) |
| Point d’entrée | `main.py` |
| Config projet (non-secrets) | `app/core/config.py` |
| Chargement secrets | `app/utils/vault_loader.py` → 1Password SDK |

Dépendances principales : `fastapi`, `uvicorn`, `pydantic`, `anthropic`, `onepassword-sdk`, `google-api-python-client`, `google-auth-oauthlib`, `slack-sdk`

### Couche Lambda — Wellbots Budget Script

| Élément | Valeur |
|---------|--------|
| Langage | TypeScript (compilé ES2022 → CommonJS) |
| Runtime | Node.js 20 |
| Gestionnaire de paquets | npm (`package.json`) |
| Point d’entrée | `wellbots/lambda/src/handler.ts` → `dist/handler.js` |
| Config métier | `wellbots/lambda/src/config.ts` |
| Logique ROAS | `wellbots/lambda/src/logic/roas.ts` |
| Infra CDK | `wellbots/lambda/infra/stack.ts` |
| SAM template | `wellbots/lambda/template.yaml` |

Dépendances principales : `google-ads-api` (gRPC), `googleapis` (Sheets), `@aws-sdk/client-ses`, `@aws-sdk/client-secrets-manager`

## 2. Run local

### FastAPI (Replit)

```bash
# Démarrage standard (workflow Replit)
bash tools/setup_ssh.sh && python main.py
# → Démarre sur le port 5000
```

### Lambda — Tests

```bash
cd wellbots/lambda
npm test                   # 151 tests Jest
npm run test:watch         # mode watch
```

### Lambda — Dry-run local (nécessite les secrets OAuth)

```bash
cd wellbots/lambda
GOOGLE_ADS_MCC_CUSTOMER_ID=8129743980 \
GOOGLE_ADS_LOGIN_CUSTOMER_ID=6351114788 \
GOOGLE_ADS_DEVELOPER_TOKEN=<depuis 1Password> \
GOOGLE_OAUTH_CLIENT_ID=<depuis 1Password> \
GOOGLE_OAUTH_CLIENT_SECRET=<depuis 1Password> \
GOOGLE_ADS_REFRESH_TOKEN=<depuis 1Password> \
WELLBOTS_DRY_RUN=true \
npx ts-node --transpile-only src/dry-run.ts
```

### Lambda — Build & packaging manuel (contournement SAM timeout)

```bash
cd wellbots/lambda
npm run build              # esbuild → dist/handler.js
# Packaging zip + update code (bypass S3 upload timeout)
python3 -c "
import zipfile, os
with zipfile.ZipFile('/tmp/wellbots.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    z.write('dist/handler.js', 'handler.js')
"
aws lambda update-function-code \
  --function-name wellbots-budget-lambda-prod \
  --zip-file fileb:///tmp/wellbots.zip \
  --region us-east-1
```

### Lambda — Restauration des env vars depuis SSM (fix quoting CF)

Utiliser boto3 directement — **jamais** via `--parameter-overrides` shell (le JSON du service account contient des guillemets qui cassent le quoting).

```bash
python3 wellbots/lambda/tools/restore_lambda_env.py   # si créé
# ou : boto3 ssm.get_parameter + lambda.update_function_configuration
```

### Outils de validation Preview vs Lambda

```bash
cd wellbots/lambda
npm run parse-preview -- preview-raw.txt preview-parsed.json
npm run compare -- preview-parsed.json dry-run-output.json
```

## 3. Git

| Élément | Valeur |
|---------|--------|
| Remote principal | `gitsafe-backup` → `git://gitsafe:5418/backup.git` |
| Remote Replit (interne) | `subrepl-*` (SSH interne Replit — ne pas utiliser manuellement) |
| Branche par défaut | `main` |
| Dernier commit | `ced68c6` — Restore service account credentials to prevent crashes |
| Branches actives | `main`, `replit-agent` |

## 4. Secrets

### Replit Secrets (1 seul — bootstrap uniquement)

| Variable | Rôle |
|----------|------|
| `OP_SERVICE_ACCOUNT_TOKEN` | Token Service Account 1Password — déverrouille tous les autres secrets |

### Secrets chargés depuis 1Password vault Replit au démarrage

| Variable | Utilisé par |
|----------|-------------|
| `AWS_SSH_KEY_B64` | FastAPI — connexion SSH vers Lightsail |
| `ANTHROPIC_API_KEY` | FastAPI — Claude API (multi-agent) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | FastAPI + Lambda — Google Sheets (service account) |
| `GOOGLE_OAUTH_CLIENT_ID` | FastAPI + Lambda — OAuth Google Ads |
| `GOOGLE_OAUTH_CLIENT_SECRET` | FastAPI + Lambda — OAuth Google Ads |
| `GOOGLE_ADS_REFRESH_TOKEN` | Lambda — refresh token OAuth Ads |
| `GOOGLE_ADS_DEVELOPER_TOKEN` | Lambda — accès Google Ads API |
| `SLACK_BOT_TOKEN` | FastAPI — Slack SDK |
| `SLACK_WEBHOOK_URL` | FastAPI — alertes Slack |
| `SLACK_WEBHOOK_JEFF` | FastAPI — canal Jeff |
| `SLACK_SIGNING_SECRET` | FastAPI — validation webhooks Slack |
| `NOTION_TOKEN` | FastAPI — Notion API |

### Secrets Lambda en production (AWS SSM Parameter Store — `/wellbots/prod/`)

| Paramètre SSM | Env var Lambda correspondante |
|---------------|-------------------------------|
| `/wellbots/prod/GOOGLE_OAUTH_CLIENT_ID` | `GOOGLE_OAUTH_CLIENT_ID` |
| `/wellbots/prod/GOOGLE_OAUTH_CLIENT_SECRET` | `GOOGLE_OAUTH_CLIENT_SECRET` |
| `/wellbots/prod/GOOGLE_ADS_REFRESH_TOKEN` | `GOOGLE_ADS_REFRESH_TOKEN` |
| `/wellbots/prod/GOOGLE_ADS_DEVELOPER_TOKEN` | `GOOGLE_ADS_DEVELOPER_TOKEN` |
| `/wellbots/prod/GOOGLE_SERVICE_ACCOUNT_JSON` | `GOOGLE_SERVICE_ACCOUNT_JSON` |
| `/wellbots/prod/GOOGLE_ADS_MCC_CUSTOMER_ID` | `GOOGLE_ADS_MCC_CUSTOMER_ID` |

### Variables d'environnement Lambda (non-secrets, dans `template.yaml`)

| Variable | Valeur / Rôle |
|----------|----------------|
| `WELLBOTS_DRY_RUN` | `false` en prod — passer `true` pour dry-run |
| `WELLBOTS_BATCH_SIZE` | `5` — campagnes traitées en parallèle |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | `6351114788` — WeAdU MCC (propriétaire du dev token) |
| `LOG_LEVEL` | `INFO` |

## 5. Base Replit

| Élément | Statut |
|---------|--------|
| Projet Replit actif | Oui — **Weadu-Socle-V5-Lab** (selon document source) |
| Replit DB (KV) | Présente (`REPLIT_DB_URL` détecté) — non utilisée activement dans le code actuel |
| Modules Nix | `python-3.11`, `nodejs-20` (channel `stable-25_05`) |
| Rôle de Replit | Orchestration, monitoring AWS, push secrets, watcher COS, FastAPI endpoints, OAuth flow |

## 6. Déploiement

### Replit (FastAPI)

| Élément | Valeur |
|---------|--------|
| Target | cloudrun (Google Cloud Run, géré par Replit) |
| URL de dev | `https://<repl-id>.picard.replit.dev` (éphémère) |
| URL de prod publiée | `https://<slug>.replit.app` (si deployed) |
| Mode | Non déployé en production actuellement — usage développement / orchestration |
| Entrée workflow | `bash tools/setup_ssh.sh && python main.py` (port 5000) |

### AWS Lambda (Wellbots Budget Script)

| Élément | Valeur |
|---------|--------|
| Fonction | `wellbots-budget-lambda-prod` |
| Région | `us-east-1` |
| Runtime | `nodejs20.x` |
| Mémoire | 512 MB |
| Timeout | 300 s |
| Stack CloudFormation | `wellbots-budget-lambda` |
| Déclencheur | EventBridge — `cron(0 12 * * ? *)` → 12:00 UTC tous les jours |
| Règle EventBridge | `wellbots-daily-trigger-prod` |
| Bucket SAM | `wellbots-sam-artifacts-prod` (`us-east-1`) |
| Mode prod | Live (`WELLBOTS_DRY_RUN=false`) — ajuste réellement les budgets |
| Déploiement CF | `deploy.sh prod` (bug quoting JSON — utiliser boto3 pour les env vars) |
| Déploiement code only | `aws lambda update-function-code` via zip (bypass timeout SAM) |

## 7. Services externes

### AWS

| Service | Usage | Détail |
|---------|-------|--------|
| Lambda | Exécution Wellbots Budget Script | `us-east-1`, `nodejs20.x`, 512MB |
| EventBridge | Déclencheur quotidien | `cron(0 12 * * ? *)` |
| SES | Emails de résumé et alertes | `@aws-sdk/client-ses` |
| SSM Parameter Store | Stockage secrets Lambda prod | `/wellbots/prod/*` (SecureString) |
| CloudWatch Logs | Logs Lambda | `/aws/lambda/wellbots-budget-lambda-prod` |
| Lightsail | Serveur Windows (WeAdU COS + Wellbots V5.1) | `stocks-monitor`, `eu-west-2a`, **IPv4 non reproduite ici** — voir [WEA-29](./WEA-29-aws-ec2-inventory.md), Windows Server 2022 |
| S3 | Artifacts SAM deploy | `wellbots-sam-artifacts-prod` |
| CDK | Infrastructure as code | `wellbots/lambda/infra/stack.ts` |

### Google

| Service | Usage | Auth |
|---------|-------|------|
| Google Ads API | Lecture ROAS, campagnes, budgets — écriture budgets | OAuth 2.0 (refresh token) via `google-ads-api` (gRPC) |
| Google Sheets API | Log ajustements, daily tracker, accounts list | Service Account JSON |
| Google OAuth 2.0 | Génération/refresh tokens Ads | Client ID/Secret + refresh token |
| MCC Wellbots | `8129743980` — compte MCC à opérer | |
| MCC WeAdU (LOGIN) | `6351114788` — propriétaire du developer token | |

### Autres

| Service | Usage | SDK / méthode |
|---------|-------|---------------|
| 1Password | Source de vérité des secrets | `onepassword-sdk` (Python) + CLI `op` (si dispo) |
| Anthropic Claude | Multi-agent debate pattern | `anthropic` Python SDK |
| Slack | Alertes opérationnelles, watcher COS | `slack-sdk` + webhooks |
| Notion | Intégration workspace | `notion_client.py` |

### Note deploy critique

Le `deploy.sh` actuel passe `GOOGLE_SERVICE_ACCOUNT_JSON` via `--parameter-overrides` shell, ce qui tronque la valeur au premier `"` du JSON. Workaround testé : restaurer les env vars Lambda directement via `boto3` `lambda.update_function_configuration` après chaque `sam deploy` (les 6 credentials depuis SSM).
