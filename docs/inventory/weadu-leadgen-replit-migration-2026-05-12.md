# WeAdU LeadGen — Replit → GitHub (Repl 6, WEA-73)

**Lecture rapide (moins de 3 minutes)** : le tableau **« Où en est la chaîne »** ci-dessous indique l’étape courante et ce qui bloque. La **décision finale** (prod hors Replit *vs* résiduel justifié) est portée par le cutover — **non tranchée** tant que [WEA-78](https://linear.app/weadu/issue/WEA-78) n’est pas clos avec preuve.

**Linear** : parent [WEA-73](https://linear.app/weadu/issue/WEA-73/repl-6-weadu-leadgen-migration-replit-github-societe) — projet [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents). **Inventaire** : [WEA-33](./WEA-33-replit-inventory.md) ligne **#6**. **Slug ticket** : `weadu-leadgen`.

**Repl source (rappel)** : nom Replit **WeAdU LeadGen** ; ID (préfixe) **`345d8dd5-…`** ; priorité migration **P2** ; périmètre **société**. Ne pas confondre l’URL prod **COS** (`leadgen.generads.com` côté EC2 — voir ligne **#2** inventaire) avec ce Repl **LeadGen** : chemins et hébergements sont à **confirmer** depuis l’agent du Repl ([WEA-74](https://linear.app/weadu/issue/WEA-74)).

Les agents sur ce dépôt `.github` **n’ont pas** le workspace Replit ; l’export structuré se fait **dans** le Repl ([WEA-35 §7](./WEA-35-weadu-socle-v5-lab-template.md)).

---

## Où en est la chaîne (ordre d’exécution)

| # | Étape | Ticket | Rôle |
|---|--------|--------|------|
| 1 | Brief agent Replit | [WEA-74](https://linear.app/weadu/issue/WEA-74) | Vérité stack, secrets **noms**, run, déploiement — **bloque** la suite |
| 2 | Synthèse inventaire | [WEA-75](https://linear.app/weadu/issue/WEA-75) | Consolider dans Linear ou PR `.github` |
| 3 | Dépôt GitHub | [WEA-76](https://linear.app/weadu/issue/WEA-76) | Créer ou confirmer `WeAdU-ltd/…` |
| 4 | Code + README | [WEA-77](https://linear.app/weadu/issue/WEA-77) | Import code, doc de run, CI si besoin |
| 5 | Cutover ou résiduel | [WEA-78](https://linear.app/weadu/issue/WEA-78) | Prod hors Replit **ou** entrée résiduelle justifiée ([WEA-36 §5](./WEA-36-replit-migration-societe.md)) ; **bloque** [WEA-36](https://linear.app/weadu/issue/WEA-36) |

**Étape bloquante actuelle (2026-05-12)** : **WEA-74** (brief Repl) — aucune synthèse exploitable tant que l’agent **dans** le Repl n’a pas produit l’export.

**Décision finale prod / Replit** : **à déterminer** — sera explicitée au clos de **WEA-78** (migré hors Replit *ou* résiduel documenté).

---

## 1. Brief agent Replit (WEA-74)

Export Markdown **dans** le Repl : non reproductible depuis l’agent GitHub seul — [WEA-35 §7](./WEA-35-weadu-socle-v5-lab-template.md).

**Consigne** : même gabarit que les autres Repl société (checklist stack, Git, secrets noms, DB Replit, déploiement `.replit.app`, externes).

---

## 2. Synthèse (WEA-75)

| Champ | État |
|-------|------|
| **Inventaire WEA-33** | Ligne #6 — colonne **Notes** pointe vers ce runbook + parent **WEA-73** |
| **Git cible** | **Inconnu** — à confirmer après WEA-74 / [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces) |

---

## 3. Dépôt GitHub (WEA-76)

| Rôle | URL |
|------|-----|
| **Application** | *À confirmer* (`WeAdU-ltd/<repo>` ou équivalent existant) |

---

## 4. Code + README + CI (WEA-77)

À remplir après création / confirmation du dépôt : import depuis Replit, `README` (prérequis, commandes, secrets nommés), CI alignée [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md) si nouveau repo.

---

## 5. Cutover (WEA-78)

Quand le dépôt et le README décrivent la prod réelle : vérifier si le trafic / les tâches passent encore par Replit ; sinon documenter **GitHub / EC2 / autre** et mettre à jour [WEA-36 §5](./WEA-36-replit-migration-societe.md) si résiduel.

---

_Document vivant ; création **2026-05-12** — ancrage dépôt pour le pilotage [WEA-73](https://linear.app/weadu/issue/WEA-73/repl-6-weadu-leadgen-migration-replit-github-societe)._
