# Waste Controller — snapshot technique (26 mai 2026)

**Inventaire WeAdU** : ligne [WEA-33 §3](./WEA-33-replit-inventory.md) **#8** (*Waste Watcher*, Repl ID préfixe `f09a27de-…`). **Nom affiché / URL** : *Waste Controller* — `waste-controller.replit.app` (à ne pas confondre avec le libellé Socle mars 2026).

**Ticket** : [WEA-87](https://linear.app/weadu/issue/WEA-87) — synthèse [`waste-watcher-replit-synthesis-WEA-87.md`](./waste-watcher-replit-synthesis-WEA-87.md).

**Secrets** : aucune valeur dans ce fichier.

---

## Stack

| Couche | Technologie |
|---|---|
| Runtime | Node.js 24, Python 3.11 (non utilisé), PostgreSQL 16 |
| Langage | TypeScript (strict) |
| Monorepo | pnpm workspaces (`pnpm-workspace.yaml`) |
| Frontend | React 19 + Vite 7, TailwindCSS v4, TanStack Query v5, TanStack Table v8, Wouter (routing), Recharts, Framer Motion, Radix UI |
| Backend | Express 5, `google-ads-api` v23, Drizzle ORM, Pino (logging) |
| Tests | Vitest 4 + Testing Library |
| Build tools | tsx (dev), esbuild (prod build) |

**Fichiers d'entrée principaux**

| Artifact | Entrée |
|---|---|
| Frontend (`waste-controller`) | `artifacts/waste-controller/src/main.tsx` |
| Backend (`api-server`) | `artifacts/api-server/src/index.ts` |
| Config monorepo | `pnpm-workspace.yaml`, `package.json` (racine) |
| Config Replit | `.replit` |

---

## Run local (dev)

```bash
# Tout en parallèle (depuis la racine du monorepo)
pnpm --filter @workspace/api-server run dev      # API Express → PORT assigné par Replit
pnpm --filter @workspace/waste-controller run dev # Vite frontend → PORT assigné par Replit

# Tests unitaires
pnpm --filter @workspace/waste-controller test

# Typecheck complet
pnpm run typecheck
```

Les ports sont injectés via la variable `PORT` par Replit — ne pas les coder en dur.

---

## Git

| Clé | Valeur |
|---|---|
| Remote principal | `gitsafe-backup` → `git://gitsafe:5418/backup.git` |
| Remotes sub-agents | `subrepl-*` → `git+ssh://git@ssh.riker.replit.dev:/home/runner/workspace` (nombreux, internes Replit) |
| Remote externe (GitHub…) | **Aucun** — pas de remote GitHub/GitLab configuré |
| Branche par défaut | `master` |
| Dernier commit | `0f35522` — *Published your App* |
| Avant-dernier | `5400967` — *Organize exported data into separate columns for each variable* |

---

## Secrets (noms uniquement)

| Variable | Usage |
|---|---|
| `GOOGLE_ADS_CLIENT_ID` | OAuth2 client ID pour l'API Google Ads |
| `GOOGLE_ADS_CLIENT_SECRET` | OAuth2 client secret |
| `GOOGLE_ADS_CUSTOMER_ID` | ID compte Google Ads par défaut (MCC root ou leaf) |
| `GOOGLE_ADS_DEVELOPER_TOKEN` | Token développeur Google Ads API |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | ID MCC de connexion |
| `GOOGLE_ADS_REFRESH_TOKEN` | Refresh token OAuth2 (accès offline) |
| `DATABASE_URL` | Connection string PostgreSQL (injectée automatiquement par Replit) |

---

## Base de données Replit (PostgreSQL 16)

**Oui** — base PostgreSQL managée par Replit, accessible via `DATABASE_URL`.

| Table | Colonnes clés | Usage |
|---|---|---|
| `api_cache` | `cache_key`, `data` (JSON texte), `expires_at` | Cache des réponses Google Ads API (évite les quotas) |
| `client_settings` | `customer_id` (PK), `min_roas`, `max_roas`, `preferred_contact_name`, `preferred_contact_email` | Seuils ROAS et contacts par compte client |

---

## Déploiement

| Clé | Valeur |
|---|---|
| URL prod | `https://waste-controller.replit.app` |
| Cible | **Autoscale** (`deploymentTarget = "autoscale"`) |
| Always On | Non (autoscale = scale-to-zero possible) |
| Router | `application` (path-based) |
| Post-build | `pnpm store prune` (avec `CI=true`) |
| Post-merge | `scripts/post-merge.sh` (timeout 20 s) — applique migrations DB après merge de tâche agent |
| Usage actuel | Expérimentation / usage interne — comptes Google Ads documentés côté opérateur (MCC + clients leaf ; pas de valeurs de secrets ici) |

---

## Externes

| Service | Type | Visible dans |
|---|---|---|
| **Google Ads API** (`googleads.googleapis.com`) | REST/gRPC via `google-ads-api` v23 | `artifacts/api-server/src/lib/googleAds.ts` |
| **OAuth2 Google** (`accounts.google.com`) | Refresh token flow (offline, pas de redirect URI côté serveur) | Même fichier — credentials via secrets |
| **Replit Heartbeat** | POST interne Replit (monitoring) | `artifacts/api-server/src/lib/heartbeat.ts` |

Aucun AWS, GCP direct, Stripe, ni autre service tiers détecté dans le code.

---

_Document ingéré dans `WeAdU-ltd/.github` le 2026-05-26 ; source : agent Cursor dans le Repl (export opérateur)._

