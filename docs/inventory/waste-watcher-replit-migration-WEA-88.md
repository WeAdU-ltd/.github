# Waste Watcher — migration Replit → GitHub (société, Repl #8)

**Linear** : [WEA-88](https://linear.app/weadu/issue/WEA-88/waste-watcher-depot-github-wead-u-ltd-cree-ou-confirme) (dépôt) ; après [WEA-87](https://linear.app/weadu/issue/WEA-87) (synthèse) — chaîne [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents) Repl **#8**. **Inventaire** : [WEA-33](./WEA-33-replit-inventory.md) **ligne #8** (Repl ID préfixe `f09a27de-…`, priorité **P2**, périmètre **Société**). **Nom UI Repl** : *Waste Controller* — `waste-controller.replit.app`.

Les agents **uniquement** sur `WeAdU-ltd/.github` n’ont pas le workspace Replit ; l’export est dans [`waste-watcher-replit-export-2026-05-26.md`](./waste-watcher-replit-export-2026-05-26.md).

---

## 1. Synthèse (WEA-87)

| Étape | État |
|-------|------|
| Export Repl | **Fait** — [`waste-watcher-replit-export-2026-05-26.md`](./waste-watcher-replit-export-2026-05-26.md) |
| Synthèse inventaire | **Fait** — [`waste-watcher-replit-synthesis-WEA-87.md`](./waste-watcher-replit-synthesis-WEA-87.md) |

---

## 2. Dépôt GitHub (WEA-88)

| Rôle | État |
|------|------|
| **URL canonique** | **`https://github.com/WeAdU-ltd/waste-watcher`** |
| **Slug** | `waste-watcher` (libellé inventaire *Waste Watcher* ; UI Repl *Waste Controller*) |
| **Création / bootstrap** | Script [`scripts/waste_watcher_repo_wea88.py`](../../scripts/waste_watcher_repo_wea88.py) ; CI [`waste-watcher-repo-wea88.yml`](../../.github/workflows/waste-watcher-repo-wea88.yml) — secret org **`GITHUB_ORG_REPO_CREATE_TOKEN`** (PAT avec droit de **créer** un dépôt sous `WeAdU-ltd`, ex. réutiliser le PAT 1Password `shared_github_pat` si portées suffisantes — voir passation Feed Optimizer) + `LINEAR_API_KEY` |
| **Label Linear `repo`** | **`WeAdU-ltd/waste-watcher`** ([WEA-17](../CHARTE_AGENTS_LINEAR_WEA17.md)) — remplace `WeAdU-ltd/.github` sur le ticket WEA-88 |
| **Inventaire org [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces)** | Régénérer après création effective du dépôt |

---

## 3. Code + README (ticket suivant)

| Exigence | État |
|----------|------|
| Code métier importé depuis Replit | **À faire** — monorepo pnpm (voir export § Run local) |
| README applicatif + CI | **Partiel** — README migration + socle WEA-35 sur `main` après bootstrap WEA-88 |

---

## 4. Cutover (ticket suivant)

| Exigence | État |
|----------|------|
| Prod hors `waste-controller.replit.app` **ou** résiduel [WEA-36 §5](./WEA-36-replit-migration-societe.md) | **À faire** — prod encore sur Replit (**2026-05-28**) |

---

## Écart vs critères de fait (WEA-88)

| Critère | État |
|---------|------|
| URL `https://github.com/WeAdU-ltd/waste-watcher` connue et notée sur le ticket | **Fait** (doc + script ; confirmation API après `--apply` ou workflow) |
| Label Linear groupe `repo` aligné | **Fait** (cible `WeAdU-ltd/waste-watcher` ; appliqué par script avec `LINEAR_API_KEY`) |

**Bloquant Done strict** : le dépôt doit **exister** sur GitHub (`gh repo view WeAdU-ltd/waste-watcher`). Le `GITHUB_TOKEN` Actions **seul** ne suffit pas (org : `createRepository` refusé — run [26565910020](https://github.com/WeAdU-ltd/.github/actions/runs/26565910020)). Ajouter le secret org **`GITHUB_ORG_REPO_CREATE_TOKEN`** puis relancer le workflow **`Bootstrap waste-watcher repo (WEA-88)`** sur `main`.

---

_Document vivant ; création **2026-05-28** ([WEA-88](https://linear.app/weadu/issue/WEA-88))._
