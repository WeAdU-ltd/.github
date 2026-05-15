# Max Conv Val Budget Mngt — migration Replit → GitHub (société)

**Référent WeAdU** : PR sur `WeAdU-ltd/.github` en **auto-merge** après CI quand la PR n’est pas brouillon ([`AGENTS.md`](../../AGENTS.md)). La **section 1** est à exécuter depuis une session **Cursor dans le Repl** *Max Conv Val Budget Mngt*, pas comme liste d’actions dans le chat — aligné [WEA-35 §7](./WEA-35-weadu-socle-v5-lab-template.md).

**Linear** : parent [WEA-79](https://linear.app/weadu/issue/WEA-79) ; chaîne ordonnée **WEA-80** (brief) → **WEA-81** (synthèse) → **WEA-82** (dépôt) → **WEA-83** (code + README) → **WEA-84** (cutover) — dernière étape **bloque** [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents). **Inventaire** : [WEA-33](./WEA-33-replit-inventory.md) **ligne #7** (Repl ID préfixe `d32b27a6-…`, priorité **P2**, périmètre **Société**).

Les agents **uniquement** sur ce dépôt `.github` n’ont pas le workspace Replit : pas d’export runtime ni Secrets sans session **dans** ce Repl.

---

## 1. Consigne vers l’agent Cursor du Repl

Produire un export structuré (**Markdown**, **aucune valeur de secret**) avec :

1. **Stack** : langage, frameworks, points d’entrée (`main`, `package.json`, `requirements.txt`, etc.).
2. **Run local** : commandes exactes pour le dev.
3. **Git** : remote(s), branche par défaut, dernier commit court.
4. **Secrets** : **noms** des variables Replit Secrets uniquement.
5. **Base Replit** : oui/non ; usage si pertinent.
6. **Déploiement** : URL `.replit.app`, Always On / autoscale, prod vs expérimentation.
7. **Externes** : AWS / GCP / API / OAuth si visibles dans le code ou la config.

Puis lier le résultat sur **WEA-80** et copier le fichier ici sous **§2** (nom type `max-conv-val-budget-mngt-replit-export-YYYY-MM-DD.md`).

---

## 2. Export ingéré (miroir dépôt)

| Bloc | État |
|------|------|
| Markdown (Repl / référent) | **Ingéré** — [`max-conv-val-budget-mngt-replit-export-2026-05-12.md`](./max-conv-val-budget-mngt-replit-export-2026-05-12.md) (**2026-05-12**). En-tête source **Wellbots / Socle V5.1** : note d’alignement en tête de fichier ; **IPv4** retirée (inventaire AWS). |

---

## 3. Synthèse (WEA-81) — inventaire / ticket à jour

| Champ | État |
|-------|------|
| **WEA-33 ligne #7** | **Partiel** : colonnes runtime partiellement dérivées de l’export (**2026-05-12**) ; Git = [`WeAdU-ltd/max-conv-val-budget-mngt`](https://github.com/WeAdU-ltd/max-conv-val-budget-mngt). |
| **Réponse agent Repl / référent** | **Consolidée** dans l’export **§2** ci-dessus. |
| **Synthèse Socle (pré-export)** | [`max-conv-val-budget-mngt-replit-synthese-socle-2026-05-12.md`](./max-conv-val-budget-mngt-replit-synthese-socle-2026-05-12.md) — historique ; la vérité détaillée est l’**export**. |

---

## 4. Dépôt GitHub (WEA-82)

| Rôle | État |
|------|------|
| **URL canonique** | **`https://github.com/WeAdU-ltd/max-conv-val-budget-mngt`** — dépôt **privé** créé **2026-05-12** (slug aligné ticket `max-conv-val-budget-mngt`). |
| **Inventaire org [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces)** | À rafraîchir côté procédure inventaire si ce repo n’y figure pas encore. |
| **Label Linear `repo`** | À aligner sur **`WeAdU-ltd/max-conv-val-budget-mngt`** ([WEA-17](https://linear.app/weadu/issue/WEA-17/charte-agents-linear-source-interdits-features-nouveaux-projets)). |

---

## 5. Code + README (WEA-83)

| Exigence | État |
|----------|------|
| Code métier importé depuis Replit | **Fait** — push applicatif **2026-05-13** depuis le workspace **Feed Optimizer** (Repl #17) vers [`WeAdU-ltd/max-conv-val-budget-mngt`](https://github.com/WeAdU-ltd/max-conv-val-budget-mngt) `main` ; preuve et procédure : [`feed-optimizer-replit-passation-2026-05-13.md`](./feed-optimizer-replit-passation-2026-05-13.md) (commits `bafa3ae`, `b75bde0` dixit passation). |
| README + socle minimal | **Partiel** — compléter le README applicatif selon **§2 Run local** de l’export ; squelette WEA-35 remplacé côté arborescence par le push applicatif. |

---

## 6. Cutover (WEA-84)

| Exigence | État |
|----------|------|
| Prod / scheduling hors Replit **ou** ligne résiduelle justifiée dans [WEA-36 §5](./WEA-36-replit-migration-societe.md) | **Fait** (**2026-05-13**) — selon l’[export §6](./max-conv-val-budget-mngt-replit-export-2026-05-12.md), la **production** du script budget Wellbots est sur **AWS Lambda** `wellbots-budget-lambda-prod` (secrets **SSM** `/wellbots/prod/*`, déclencheur **EventBridge** `wellbots-daily-trigger-prod`) ; la **FastAPI Replit** y est indiquée **non déployée en production** (dev / orchestration). La ligne résiduelle **Repl #7** a été **retirée** du tableau [WEA-36 §5](./WEA-36-replit-migration-societe.md) ; paragraphe **Historique — Repl #7** conservé. **Replit n’est pas critique** pour la boucle prod + scheduling **documentée** du script budget. Suite optionnelle : fermeture Repl et rotation `OP_SERVICE_ACCOUNT_TOKEN` côté Repl si le workspace n’est plus utilisé — [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete). |

---

_Document vivant ; création dépôt + squelette **2026-05-12** ; export Repl / référent ingéré **2026-05-12** ; code sur `main` + cutover documentés **2026-05-13** ([WEA-84](https://linear.app/weadu/issue/WEA-84/max-conv-val-budget-mngt-cutover-hors-replit-ou-classement-residuel-justifie))._
