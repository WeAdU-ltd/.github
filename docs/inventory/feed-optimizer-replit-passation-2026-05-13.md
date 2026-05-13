# Passation — Feed Optimizer (lien Max Conv Val Budget Mngt)

_Date **2026-05-13** — reprise depuis le Repl (aucune valeur de secret, **pas d’adresse IP** dans ce fichier ; croiser [WEA-29](./WEA-29-aws-ec2-inventory.md) et le dépôt org)._  
_Relation inventaire : [WEA-33](./WEA-33-replit-inventory.md) **#17** Feed Optimizer ; chaîne [WEA-139](https://linear.app/weadu/issue/WEA-139) ; export antérieur [`feed-optimizer-replit-export-2026-05-12.md`](./feed-optimizer-replit-export-2026-05-12.md)._

## Contexte

- **Produit** : optimiseur de titres **Google Shopping** (client Wellbots).
- **Runtime** : FastAPI port **5000** sur Replit ; cible déploiement **EC2 Windows Server 2022**, **eu-west-2** (hôte : voir procédures dans le dépôt org, pas d’IPv4 ici).
- **Dépôts** :
  - [`JeffWeadu/feed-optimizer`](https://github.com/JeffWeadu/feed-optimizer) — remote du workspace Replit.
  - [`WeAdU-ltd/max-conv-val-budget-mngt`](https://github.com/WeAdU-ltd/max-conv-val-budget-mngt) — dépôt **organisation** (branche `main` ; description GitHub cite **WEA-79** ; passation Repl cite **WEA-83** — **à réconcilier** sur Linear).

## Réalisé (session Repl rapportée)

| Zone | Détail |
|------|--------|
| **Pipeline Shopping** | `app/shopping/` — extract → analyze → generate → inject (Merchant supplemental feed, rollback, limites, termes interdits). |
| **OAuth Google** | `app/auth/google_oauth.py` — multi-scopes ; tokens fichier `config/google_tokens.json` (**gitignored**). |
| **Secrets** | `app/utils/vault_loader.py` — 1Password vault **Replit** ; seul `OP_SERVICE_ACCOUNT_TOKEN` dans Replit Secrets ; cache TTL (chemin cache signalé par le Repl, non dupliqué ici). |
| **Sync** | `app/sync/` — Drive, GitHub push (`GITHUB_PAT` / jetons via vault selon export 2026-05-12). |
| **Heartbeat** | `app/heartbeat.py` → Socle Portfolio (`weadu-socle-v-5-lab.replit.app`), ~5 min. |
| **EC2 (scripts)** | `tools/bootstrap_ec2.ps1`, `update_ec2.ps1`, `check_ec2.ps1`. |
| **Push org** | Arborescence poussée vers **`WeAdU-ltd/max-conv-val-budget-mngt`** via **GitHub Trees API** (deux commits rapportés : `bafa3ae`, `b75bde0`). Preuve côté Repl : `docs/WEA-83-verification.json` (non reproduit ici). Token : rapport Repl indique usage **`GITHUB_TOKEN`** (`op://…`) après **403** avec `shared_github_pat` sur l’org. |

## Blocants prod (rappel opérationnel — pas des secrets d’inventaire)

1. **IDs Google Ads / Merchant** dans `app/shopping/config.py` (champs vides à compléter — **non secrets**, règle métier).
2. **`config/google_tokens.json`** absent — lancer le flux OAuth (`GET /auth/google`, etc.).
3. **EC2** : bootstrap non exécuté depuis la passation — commandes dans `tools/*.ps1` ; prérequis `OP_SERVICE_ACCOUNT_TOKEN` sur l’hôte cible.

## Fichiers gouvernance (ne pas modifier sans accord explicite)

- `config/governance.md`
- `replit.md`
- `app/utils/vault_loader.py`
- `app/core/config.py`
- `.replit`

## Références complémentaires Google Ads (1Password)

Rapport Repl : quatre références `op://Replit/GOOGLE_ADS_*` à créer / brancher dans `vault_loader` quand les items existent — **noms uniquement**, pas de valeurs dans ce dépôt.

---

_Intégration dépôt `WeAdU-ltd/.github` : **2026-05-13**._
