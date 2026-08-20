# Waste Watcher — code, README, CI (WEA-89)

**Linear** : [WEA-89](https://linear.app/weadu/issue/WEA-89/waste-watcher-code-importe-readme-procedure-de-run) — suite de [WEA-88](./waste-watcher-replit-migration-WEA-88.md) pour le dépôt cible `WeAdU-ltd/waste-watcher`.

**Source Replit documentée** : [export Waste Controller 2026-05-26](./waste-watcher-replit-export-2026-05-26.md) (stack, commandes, secrets nommés, prod Replit). Aucune valeur de secret n'est stockée dans ce dépôt.

---

## État constaté depuis `WeAdU-ltd/.github`

| Élément | État |
|---|---|
| Dépôt cible `WeAdU-ltd/waste-watcher` | **Bloqué** — `gh repo view WeAdU-ltd/waste-watcher` retourne `Could not resolve to a Repository` dans la session du 2026-06-09. |
| Code Replit importable depuis cette session | **Absent** — pas de dossier `artifacts/`, pas de `pnpm-workspace.yaml`, pas de sources `waste-controller` / `api-server` dans `WeAdU-ltd/.github`. |
| README procédure de run | **Préparé** dans le bootstrap [`scripts/waste_watcher_repo_wea88.py`](../../scripts/waste_watcher_repo_wea88.py) : prérequis, installation, commandes local/test/build/deploy, secrets nommés. |
| CI minimale | **Préparée** dans le même bootstrap : `.github/workflows/ci.yml` du dépôt cible vérifie les fichiers socle et exécute `pnpm` dès que le code applicatif est importé. |

---

## README applicatif prévu dans `WeAdU-ltd/waste-watcher`

Le bootstrap génère un README couvrant :

- prérequis : Node.js 24, Corepack/pnpm, PostgreSQL 16, accès Google Ads API ;
- installation : `corepack enable`, `pnpm install --frozen-lockfile` ;
- run local : `pnpm --filter @workspace/api-server run dev` et `pnpm --filter @workspace/waste-controller run dev` ;
- tests/build : `pnpm run typecheck`, `pnpm --filter @workspace/waste-controller test`, `pnpm run build` ;
- déploiement : production encore sur `https://waste-controller.replit.app`, puis étapes de cutover hors Replit ;
- secrets **nommés uniquement** : `DATABASE_URL`, `GOOGLE_ADS_CLIENT_ID`, `GOOGLE_ADS_CLIENT_SECRET`, `GOOGLE_ADS_CUSTOMER_ID`, `GOOGLE_ADS_DEVELOPER_TOKEN`, `GOOGLE_ADS_LOGIN_CUSTOMER_ID`, `GOOGLE_ADS_REFRESH_TOKEN`, `PORT`.

Les valeurs restent hors dépôt, conformément à [WEA-15](../SECRETS_SOCLE_WEA15.md).

---

## CI minimale prévue

Workflow généré dans le dépôt cible :

1. `pull_request` + `push` sur `main`.
2. Vérification socle : `README.md` et `AGENTS.md`.
3. Si `package.json` existe : `actions/setup-node@v6` avec Node 24.
4. Installation `pnpm` avec lockfile strict si `pnpm-lock.yaml` existe.
5. Exécution conditionnelle :
   - `pnpm run typecheck --if-present` ;
   - `pnpm -r test --if-present` ;
   - `pnpm run build --if-present`.

La CI reste donc minimale au bootstrap et devient applicative dès l'import du monorepo Replit.

---

## Écart vs critères de fait (WEA-89)

| Critère | État | Preuve / prochaine action |
|---|---|---|
| `README` avec prérequis, commandes, secrets nommés | **Préparé, non livré dans le dépôt cible** | Généré par [`scripts/waste_watcher_repo_wea88.py`](../../scripts/waste_watcher_repo_wea88.py). Prochaine action : créer/confirmer `WeAdU-ltd/waste-watcher`, relancer le bootstrap, puis importer le code Replit. |
| CI minimale ou alignement template WEA-35 si nouveau dépôt | **Préparé, non livré dans le dépôt cible** | Workflow cible généré par le bootstrap ; CI `.github` teste la syntaxe/dry-run du script. |
| Code importé | **Bloqué** | Le dépôt cible n'existe pas / n'est pas accessible depuis cette session et le code Replit n'est pas présent dans `WeAdU-ltd/.github`. Prochaine action : exécuter l'import depuis le Repl ou fournir l'archive/export source, puis pousser dans `WeAdU-ltd/waste-watcher`. |

**Conclusion Done strict** : WEA-89 ne doit pas être marqué Done tant que le dépôt cible ne contient pas effectivement le code importé, le README et la CI sur sa branche par défaut.

---

_Document vivant ; création 2026-06-09._
