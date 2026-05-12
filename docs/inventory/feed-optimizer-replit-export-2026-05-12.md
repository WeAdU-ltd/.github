# Feed Optimizer — Export structuré (Repl, ligne WEA-33 #17)

_Généré le **2026-05-12** depuis l’agent Cursor **dans** le Repl. Aucune **valeur** de secret incluse._  
_Miroir dépôt : aligné [WEA-140](https://linear.app/weadu/issue/WEA-140), parent [WEA-139](https://linear.app/weadu/issue/WEA-139/repl-17-feed-optimizer-migration-replit-github-societe), [WEA-35 §7](./WEA-35-weadu-socle-v5-lab-template.md)._

**Règle inventaire** : pas d’adresse IPv4 ni de jeton dans ce fichier — croiser [WEA-29](./WEA-29-aws-ec2-inventory.md) et le dépôt applicatif pour l’hôte EC2.

---

## Stack

| Composant | Valeur |
|-----------|--------|
| **Langage** | Python 3.11.14 |
| **Framework web** | FastAPI 0.135+ / Uvicorn 0.41+ |
| **ORM / DB** | SQLite via couche maison (`app/shopping/database.py`) |
| **Scheduler** | APScheduler 3.11+ (`BackgroundScheduler`) |
| **IA** | Anthropic SDK 0.84+ (Claude) |
| **Google APIs** | `google-ads` 29.2+, `google-api-python-client` 2.192+, `google-auth` 2.49+, `google-auth-oauthlib` 1.2+ |
| **Secrets** | `onepassword-sdk` 0.4+ |
| **Validation** | Pydantic 2.12+ |

**Fichiers d’entrée**

| Fichier | Rôle |
|---------|------|
| `main.py` | Point d’entrée FastAPI — port **5000** |
| `pyproject.toml` | Dépendances (gestionnaire : **uv**) |
| `app/core/config.py` | Config projet (IDs comptes, pas de secrets en clair) |
| `app/utils/vault_loader.py` | Chargeur secrets 1Password au démarrage |
| `config/governance.md` | Règles de gouvernance IA (R1–R10) |
| `config/google_tokens.json` | Tokens OAuth Google (**gitignored**) |
| `data/shopping_optimizer.db` | Base SQLite (**gitignored**) |

---

## Run local

```bash
uv sync
python main.py
```

**Prérequis** : variable `OP_SERVICE_ACCOUNT_TOKEN` dans l’environnement (Replit Secrets ou poste local) — **valeur** hors repo.

---

## Git

| Clé | Valeur |
|-----|--------|
| **Branche par défaut** | `main` |
| **Remote principal** | `https://github.com/JeffWeadu/feed-optimizer.git` (sans jeton dans l’URL versionnée ici) |
| **Remote backup** | `git://gitsafe:5418/backup.git` (backup Replit interne) |
| **Dernier commit (export)** | `db17552` — Add 5-min Socle Portfolio heartbeat (auto-start on startup) |
| **Commit précédent** | `009565a` — Add EC2 deploy scripts, migrate to `op://Replit/` vault, add `google-auth-oauthlib` |

---

## Secrets (noms uniquement)

**Replit Secrets (bootstrap)** : `OP_SERVICE_ACCOUNT_TOKEN` — seul secret stocké directement dans Replit Secrets ; le reste via 1Password (`op://`).

**Variables résolues via 1Password** (noms signalés à l’export — **pas de valeurs** ici) :

| Variable | Usage |
|----------|--------|
| `ANTHROPIC_API_KEY` | Claude API |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Service Account (Drive, Merchant Center) |
| `GOOGLE_OAUTH_CLIENT_ID` | OAuth 2.0 — Client ID |
| `GOOGLE_OAUTH_CLIENT_SECRET` | OAuth 2.0 — Client Secret |
| `GITHUB_PAT` | Push GitHub (`op://Replit/shared_github_pat` à l’export) |
| `SLACK_BOT_TOKEN` | Slack |
| `SLACK_WEBHOOK_URL` | Webhook Slack |
| `SLACK_WEBHOOK_JEFF` | Webhook Slack (Jeff) |
| `SLACK_USER_ID` | ID utilisateur Slack |
| `NOTION_TOKEN` | API Notion |
| `SERPAPI_KEY` | SerpAPI |
| `AWS_SSH_KEY_B64` | Clé SSH EC2 (base64) |

**Variables Google Ads / Merchant** (config applicative, état à l’export) :

| Variable | Statut |
|----------|--------|
| `GOOGLE_ADS_CUSTOMER_ID` | Vide — à renseigner |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | Vide — à renseigner |
| `GOOGLE_MERCHANT_CENTER_ID` | Vide — à renseigner |

---

## Base Replit

**Replit DB (KV)** : **non** — pas d’usage.

**Données** : SQLite locale → `data/shopping_optimizer.db` (**gitignored**). Tables principales (noms fonctionnels à l’export) : produits, search terms, n-grams scorés, suggestions de titres, historique des injections, historique pipeline.

---

## Déploiement

| Paramètre | Valeur |
|-----------|--------|
| **URL `.replit.app`** | Non publié / pas actif à l’export (`deploymentTarget` = Cloud Run configuré mais non déclenché) |
| **Always On** | Non activé |
| **Charge Replit** | Expérimentation / dev — pas de trafic prod décrit sur Replit |
| **Prod cible** | **AWS EC2** — Windows Server 2022, **eu-west-2** (London) ; service Windows **FeedOptimizer** (NSSM, auto-start, port **5000**) |
| **URL prod** | HTTP sur hôte EC2 (port 5000) — **adresse IP non recopiée** dans ce dépôt ([WEA-33](./WEA-33-replit-inventory.md) §1) |
| **Scripts deploy** | `tools/bootstrap_ec2.ps1`, `tools/update_ec2.ps1`, `tools/check_ec2.ps1` |

---

## Externes

| Service | Usage | Référence (export) |
|---------|--------|-------------------|
| **Google Ads API** | Search terms | `app/shopping/extractor.py` — scope `adwords` |
| **Google Merchant Center** | Produits + supplemental feed | `app/shopping/extractor.py`, `app/shopping/injector.py` |
| **Google Drive API** | Export CSV/JSON | `app/sync/drive_sync.py` |
| **Google OAuth 2.0** | Multi-scopes | `app/auth/google_oauth.py` |
| **OAuth redirect** | `{base_url}/auth/google/callback` | `main.py` + `app/auth/google_oauth.py` |
| **Anthropic** | Titres Shopping | `app/multi_agent/agents.py`, `app/shopping/title_generator.py` |
| **Socle Portfolio** | Heartbeat ~5 min | `app/heartbeat.py` → `https://weadu-socle-v-5-lab.replit.app/portfolio/heartbeat` |
| **GitHub** | Push code | `app/sync/github_sync.py` → `github.com/JeffWeadu/feed-optimizer` |
| **AWS EC2** | Prod Windows | `tools/*.ps1` ; SSH **Administrator** sur hôte EC2 (détail hors inventaire IP) |
| **1Password** | Secrets | `app/utils/vault_loader.py` — vault **Replit** |

---

_Document vivant ; intégration dépôt `WeAdU-ltd/.github` : **2026-05-12**._
