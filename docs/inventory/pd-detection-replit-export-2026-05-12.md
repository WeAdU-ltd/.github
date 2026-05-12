# PD Detection — Export structuré du projet

_Généré le 2026-05-12. Aucune valeur de secret incluse._  
_Miroir dépôt : aligné [runbook pd-detection §2](./pd-detection-replit-migration-WEA-128.md) et ticket [WEA-128](https://linear.app/weadu/issue/WEA-128/pd-detection-brief-agent-replit-infos-migration)._

---

## Stack

| Couche | Détail |
|--------|--------|
| **Langage** | Python 3.11 (Replit) / Python 3.14 (AWS production) |
| **Framework web** | FastAPI 0.115+ + uvicorn[standard] |
| **Runtime additionnel** | Node.js 20 (mockup sandbox canvas uniquement) |
| **Base de données** | PostgreSQL 16 (Replit — non utilisé, 0 tables) |
| **Data / ML** | pandas 3.0+, numpy 2.4+, yfinance, scikit-learn (implicite) |
| **Trading** | ib_insync (IBKR TWS API, port 4001) |
| **Secrets** | onepassword-sdk 0.4+ (1Password service account) |
| **Cloud AWS** | boto3 1.42+ |
| **AI** | anthropic 0.86+ |
| **HTTP / Scraping** | requests, beautifulsoup4, google-auth, google-auth-oauthlib |
| **Ads** | google-ads, google-api-python-client |

**Fichiers d'entrée principaux :**

| Fichier | Rôle |
|---------|------|
| `main.py` | Point d'entrée FastAPI (Replit) |
| `pyproject.toml` | Dépendances Python (uv/pip) |
| `requirements.txt` | Dépendances legacy AWS/compat |
| `.replit` | Config workflows Replit |
| `app/core/config.py` | Config projet (IDs, URLs — pas de secrets) |
| `app/utils/vault_loader.py` | Chargement secrets 1Password au démarrage |
| `tools/daily_monitor.py` | Orchestrateur principal (AWS uniquement) |
| `tools/stocks_api.py` | API publique (AWS, `stocks.generads.com`) |

---

## Run local

```bash
# 1. Restaurer la clé SSH AWS + synchroniser les données depuis AWS
bash tools/setup_ssh.sh && python3 tools/sync_aws.py pull
# 2. Lancer le serveur FastAPI (dev, port 8000)
uvicorn main:app --host 0.0.0.0 --port 8000
# 3. Run complet monitoring (AWS uniquement — ne pas lancer sur Replit)
python3 tools/daily_monitor.py          # full run (LP + News scraping)
python3 tools/daily_monitor.py --fast   # skip scraping, market signals only
```

`OP_SERVICE_ACCOUNT_TOKEN` doit être dans l'environnement avant le démarrage pour que `vault_loader` charge les secrets 1Password. En cas de rate-limit 1Password, les secrets critiques (`PD_API_KEY`, `OVH_*`) sont disponibles via Replit Secrets directs.

---

## Git

| Champ | Valeur |
|-------|--------|
| Remote principal | `https://github.com/JeffWeadu/pd-detection` |
| Remote backup | `git://gitsafe:5418/backup.git` (Replit interne) |
| Branche par défaut | `migration-replit-v5` |
| Dernier commit | `5bbe7b3` — Add trading reports for stock actions and stop-loss events |

---

## Secrets Replit (noms uniquement)

Injectés directement comme Replit Secrets (disponibles sans 1Password) :

| Variable | Usage |
|----------|-------|
| `PD_API_KEY` | Auth API stocks.generads.com |
| `AWS_SSH_KEY_B64` | Clé SSH EC2 encodée base64 |
| `AWS_ACCESS_KEY_ID` | Credentials AWS (boto3, S3) |
| `AWS_SECRET_ACCESS_KEY` | Credentials AWS |
| `OVH_APP_KEY` | API DNS OVH |
| `OVH_APP_SECRET` | API DNS OVH |
| `OVH_CONSUMER_KEY` | API DNS OVH |
| `OP_SERVICE_ACCOUNT_TOKEN` | Bootstrap vault_loader → 1Password |

Chargés depuis 1Password via `vault_loader` (peuvent échouer si rate-limités) :

| Variable | Vault path |
|----------|--------------|
| `ANTHROPIC_API_KEY` | `op://Replit/ANTHROPIC_API_KEY/credential` |
| `SLACK_BOT_TOKEN` | `op://Replit/SLACK_BOT_TOKEN/credential` |
| `SLACK_WEBHOOK_URL` | `op://Replit/SLACK_WEBHOOK_URL/credential` |
| `SLACK_WEBHOOK_JEFF` | `op://Replit/SLACK_WEBHOOK_JEFF/credential` |
| `SLACK_USER_ID` | `op://Replit/SLACK_USER_ID/credential` |
| `NOTION_TOKEN` | `op://Replit/NOTION_TOKEN/credential` |
| `PD_GMAIL_APP_PASSWORD` | `op://Replit/PD_GMAIL_APP_PASSWORD/credential` |
| `GOOGLE_OAUTH_CLIENT_ID` | `op://Replit/GOOGLE_OAUTH_CLIENT_ID/credential` |
| `GOOGLE_OAUTH_CLIENT_SECRET` | `op://Replit/GOOGLE_OAUTH_CLIENT_SECRET/credential` |
| `GOOGLE_ADS_DEVELOPER_TOKEN` | `op://Replit/GOOGLE_ADS_DEVELOPER_TOKEN/credential` |
| `AWS_ACCESS_KEY_ID` (doublon) | `op://Replit/AWS_ACCESS_KEY_ID/credential` |
| `AWS_SECRET_ACCESS_KEY` (doublon) | `op://Replit/AWS_SECRET_ACCESS_KEY/credential` |
| `OVH_APP_KEY` (doublon) | `op://Replit/OVH_APP_KEY/credential` |
| `OVH_APP_SECRET` (doublon) | `op://Replit/OVH_APP_SECRET/credential` |
| `OVH_CONSUMER_KEY` (doublon) | `op://Replit/OVH_CONSUMER_KEY/credential` |
| `PD_API_KEY` (doublon) | `op://Replit/PD_API_KEY/credential` |

---

## Base de données Replit (PostgreSQL)

| Champ | Valeur |
|-------|--------|
| Présente | Oui (PostgreSQL 16, auto-provisionnée) |
| Tables applicatives | 0 |
| Taille | ~7.5 MB (overhead vide) |
| Utilisée par le code | Non — aucune référence dans `tools/` ni `app/` |
| Critique | Non — peut être ignorée |

Tout le stockage passe par fichiers JSON/CSV sur AWS EC2 (`data/`, `data/aws_sync/`).

---

## Déploiement

| Champ | Valeur |
|-------|--------|
| URL Replit (dev) | `https://pd-detection.replit.app` |
| URL production API | `https://stocks.generads.com` (AWS EC2 Lightsail) |
| Mode Replit | Always On (FastAPI + heartbeat Socle 5 min) |
| Autoscale | Non — instance unique |
| Charge prod | Faible (OAuth dormant + heartbeat uniquement) |
| Production réelle | AWS Lightsail Windows Server 2022 (`eu-west-2`) — **adresse IPv4 : inventaire AWS / poste opéré, pas recopiée dans ce dépôt public** |
| Proxy AWS | Caddy → HTTPS auto-TLS (Let's Encrypt) |
| `ENV=prod` détection | `REPLIT_DEPLOYMENT_ID` présent → réponse minimale sur `/` |

---

## Ressources externes

| Service | URL / Endpoint | Auth |
|---------|----------------|------|
| AWS EC2 Lightsail | `eu-west-2` (SSH / données) | `AWS_SSH_KEY_B64` |
| AWS S3 | Bucket heartbeat `health.json` | `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` |
| IBKR TWS | `localhost:4001` (sur EC2) | IBC + TOTP 2FA |
| Google OAuth | `https://accounts.google.com` | `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` |
| OAuth redirect URI | `https://pd-detection.replit.app/auth/google/callback` | — |
| OVH DNS API | `https://eu.api.ovh.com` (zone generads.com) | `OVH_APP_KEY` / `OVH_APP_SECRET` / `OVH_CONSUMER_KEY` |
| 1Password | `https://events.1password.com` | `OP_SERVICE_ACCOUNT_TOKEN` |
| Socle Weadu | `https://weadu-socle-v-5-lab.replit.app` | Aucune (endpoint interne) |
| GitHub | `github.com/JeffWeadu/pd-detection` | PAT `op://Replit/GITHUB_TOKEN/credential` |
| Gmail SMTP | `smtp.gmail.com:587` | `PD_GMAIL_APP_PASSWORD` |
| Google Ads API | `googleads.googleapis.com` | `GOOGLE_ADS_DEVELOPER_TOKEN` |
| Slack | `hooks.slack.com` | `SLACK_BOT_TOKEN` / `SLACK_WEBHOOK_*` |

---

_Document figé ; ne pas y coller de valeurs de secrets._
