# Feed Optimizer — Replit → GitHub (Repl 17, WEA-139)

**Linear** : parent [WEA-139](https://linear.app/weadu/issue/WEA-139/repl-17-feed-optimizer-migration-replit-github-societe) — chaîne [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents). **Ligne inventaire** : [WEA-33](./WEA-33-replit-inventory.md) #17.

**Priorité migration** : **P3**. **Replit ID (préfixe)** : `cb7bc686-…`.

**Documents** : export [`feed-optimizer-replit-export-2026-05-12.md`](./feed-optimizer-replit-export-2026-05-12.md) ; passation Repl [`feed-optimizer-replit-passation-2026-05-13.md`](./feed-optimizer-replit-passation-2026-05-13.md).

---

## 1. Brief agent Replit — [WEA-140](https://linear.app/weadu/issue/WEA-140)

| Champ | État |
|-------|------|
| Export Markdown agent Repl | **Done** — export **2026-05-12** + passation **2026-05-13**. |

---

## 2. Synthèse inventaire — [WEA-141](https://linear.app/weadu/issue/WEA-141)

| Champ | État |
|-------|------|
| Colonnes WEA-33 / WEA-36 | **Enrichi** **2026-05-13** : dépôt org, push Trees API, liens **WEA-83** / **WEA-79** à réconcilier ; ligne **#7** vs **#17** (UUID distincts) notée. |

### 2.1 Synthèse opérationnelle (post passation 2026-05-13)

| Thème | Synthèse |
|-------|----------|
| **Repos** | Workspace : `JeffWeadu/feed-optimizer` ; **org** : [`WeAdU-ltd/max-conv-val-budget-mngt`](https://github.com/WeAdU-ltd/max-conv-val-budget-mngt) (`main`, commits `bafa3ae`, `b75bde0` dixit Repl). |
| **Prod** | EC2 Windows **eu-west-2** + NSSM **FeedOptimizer** — déploiement hôte **non finalisé** ; pas d’IP dans l’inventaire ([WEA-29](./WEA-29-aws-ec2-inventory.md)). |
| **Blocants** | IDs Ads/Merchant dans `config.py` ; fichier OAuth absent ; bootstrap EC2 non fait — voir passation § « Blocants prod ». |

---

## 3. Dépôt GitHub — [WEA-142](https://linear.app/weadu/issue/WEA-142)

| Champ | État |
|-------|------|
| **URL org (société)** | **`https://github.com/WeAdU-ltd/max-conv-val-budget-mngt`** — **confirmé** (API GitHub **2026-05-13** ; description dépôt cite [WEA-79](https://linear.app/weadu/issue/WEA-79) ; passation Repl cite [WEA-83](https://linear.app/weadu/issue/WEA-83) — **aligner** le ticket Linear canonique sur le dépôt). |
| **Workspace Replit** | [`JeffWeadu/feed-optimizer`](https://github.com/JeffWeadu/feed-optimizer) (privé). |
| **Label Linear `repo`** | À aligner sur **`WeAdU-ltd/max-conv-val-budget-mngt`** pour les tickets code agents ([WEA-17](../CHARTE_AGENTS_LINEAR_WEA17.md)). |

### 3.1 Vérifications historiques org (2026-05-12)

Recherche initiale `feed` / `optim` sur `WeAdU-ltd` n’avait pas trouvé ce dépôt (**nom différent**). Le slug **`max-conv-val-budget-mngt`** correspond à l’inventaire [WEA-33](./WEA-33-replit-inventory.md) ligne **#7** (*Max Conv Val Budget Mngt*) — **réconciliation UUID Repl** #7 vs #17 : **à clarifier** avec le Repl (deux entrées inventaire, un artefact org).

---

## 4. Code importé + README — [WEA-143](https://linear.app/weadu/issue/WEA-143)

| Champ | État |
|-------|------|
| Code sur `main` (org) | **Poussé** (Trees API, **2026-05-13** dixit passation) — README / CI / template [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md) : **à valider** sur le dépôt org. |
| Critères « README procédure » | **Partiel** tant que blocants prod + doc run ne sont pas clos côté dépôt applicatif. |

---

## 5. Cutover — [WEA-144](https://linear.app/weadu/issue/WEA-144)

| Verdict | État |
|---------|------|
| **Prod hors Replit** | **En cours** : cible EC2 documentée ; **bootstrap non exécuté** ; OAuth / IDs manquants — preuve cutover : **WEA-144**. |
| **Résiduel** | Heartbeat Socle + Replit dev : voir [WEA-36 §5](./WEA-36-replit-migration-societe.md) à la clôture. |

---

_Document vivant ; dernier passage **2026-05-13**._
