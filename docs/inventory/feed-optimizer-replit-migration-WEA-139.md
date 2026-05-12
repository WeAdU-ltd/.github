# Feed Optimizer — Replit → GitHub (Repl 17, WEA-139)

**Linear** : parent [WEA-139](https://linear.app/weadu/issue/WEA-139/repl-17-feed-optimizer-migration-replit-github-societe) — chaîne [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents). **Ligne inventaire** : [WEA-33](./WEA-33-replit-inventory.md) #17.

**Priorité migration** : **P3**. **Périmètre ticket** : société — **écart documenté** : le code applicatif est sur le dépôt **perso** [`JeffWeadu/feed-optimizer`](https://github.com/JeffWeadu/feed-optimizer) (privé) ; alignement `WeAdU-ltd/…` : voir **WEA-142**. **Replit ID (préfixe)** : `cb7bc686-…`.

**Export agent Repl** : [`feed-optimizer-replit-export-2026-05-12.md`](./feed-optimizer-replit-export-2026-05-12.md) (**2026-05-12**).

---

## 1. Brief agent Replit — [WEA-140](https://linear.app/weadu/issue/WEA-140)

| Champ | État |
|-------|------|
| Export Markdown agent Repl | **Reçu** — [`feed-optimizer-replit-export-2026-05-12.md`](./feed-optimizer-replit-export-2026-05-12.md) |

---

## 2. Synthèse inventaire — [WEA-141](https://linear.app/weadu/issue/WEA-141)

| Champ | État |
|-------|------|
| Colonnes WEA-33 / PR dépôt `.github` | **Partiel → enrichi** : ligne **#17** alignée avec l’export **2026-05-12** ; détail runtime / preuves cutover à finaliser avec **WEA-144**. |

### 2.1 Synthèse post-export (2026-05-12)

| Thème | Synthèse |
|-------|------------|
| **Stack** | Python 3.11, FastAPI, SQLite maison, APScheduler, Anthropic, Google Ads/Merchant/Drive/OAuth, 1Password SDK |
| **Run** | `uv sync` ; `python main.py` ; port **5000** ; prérequis `OP_SERVICE_ACCOUNT_TOKEN` |
| **Git** | `main` ; remote canonique **sans PAT** : `https://github.com/JeffWeadu/feed-optimizer.git` ; backup Replit `gitsafe` |
| **Secrets** | Bootstrap Replit : `OP_SERVICE_ACCOUNT_TOKEN` ; reste via **1Password** (noms dans l’export, pas de valeurs) |
| **DB** | Pas de Replit DB ; SQLite `data/shopping_optimizer.db` (gitignored) |
| **Replit** | Pas de `.replit.app` actif ; AO **non** ; charge **dev** |
| **Prod** | **EC2** Windows, NSSM **FeedOptimizer**, port 5000 — **pas d’IP dans l’inventaire** ; croiser [WEA-29](./WEA-29-aws-ec2-inventory.md) |
| **Externes** | Heartbeat → Socle `weadu-socle-v-5-lab.replit.app` ; Google APIs ; Slack ; Notion ; SerpAPI |

---

## 3. Dépôt GitHub — [WEA-142](https://linear.app/weadu/issue/WEA-142)

| Champ | État |
|-------|------|
| **Dépôt applicatif actuel** | [`https://github.com/JeffWeadu/feed-optimizer`](https://github.com/JeffWeadu/feed-optimizer) (privé) — **confirmé** par l’export **2026-05-12**. |
| **Org société `WeAdU-ltd`** | **Non** — aucun repo `WeAdU-ltd/*` identifié pour ce projet (contrôle précédent §3.1). **À trancher** : transfert / miroir / nouveau repo org + mise à jour label Linear `repo` ([WEA-17](../CHARTE_AGENTS_LINEAR_WEA17.md)). |

### 3.1 Vérifications org WeAdU-ltd (agent Socle, 2026-05-12)

1. **`gh search repos`** : propriétaire `WeAdU-ltd`, filtre `feed` / `optim` → **aucun** dépôt.
2. **Snapshot** [`github-org-repo-snapshot-2026-05-02.json`](./github-org-repo-snapshot-2026-05-02.json) : idem.

---

## 4. Code importé + README — [WEA-143](https://linear.app/weadu/issue/WEA-143)

| Champ | État |
|-------|------|
| Code sur `main` + README | **Existant** sur `JeffWeadu/feed-optimizer` (hors vérification CI dans ce ticket) ; revue README / CI / alignement template [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md) si migration vers `WeAdU-ltd`. |

---

## 5. Cutover — [WEA-144](https://linear.app/weadu/issue/WEA-144)

| Verdict | État |
|---------|------|
| **Prod hors Replit** | **Probable** à qualifier : charge prod décrite sur **EC2** Windows (NSSM), pas sur `.replit.app` — preuve finale (DNS, monitoring, arrêt Repl) : **WEA-144**. |
| **Résiduel** | Socle heartbeat + secrets Replit / 1Password à cadrer dans la clôture **WEA-144** + [WEA-36 §5](./WEA-36-replit-migration-societe.md). |

---

_Document vivant ; export Repl **2026-05-12** ; alignement inventaire **2026-05-12**._
