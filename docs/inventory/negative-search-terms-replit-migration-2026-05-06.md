# negative-search-terms-tool — Replit → GitHub (Repl 4, WEA-61)

**Linear** : parent [WEA-61](https://linear.app/weadu/issue/WEA-61/repl-4-negative-search-terms-tool-migration-replit-github-societe) — chaîne [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents). **Ligne inventaire** : [WEA-33](./WEA-33-replit-inventory.md) #4.

**Dépôt GitHub cible (confirmé, 2026-05-06)** : **`https://github.com/WeAdU-ltd/Negative-Terms`** (privé). Les agents sur ce dépôt `.github` ne lisent pas le filesystem Replit.

---

## 1. Brief agent Replit (WEA-62)

Export Markdown **dans** le Repl : non reproductible depuis l’agent GitHub seul — même logique que [WEA-35 §7](./WEA-35-weadu-socle-v5-lab-template.md).

**Consigne** à coller dans l’agent Cursor **du** Repl : formulaire §7 [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md) (stack, run, Git, secrets **noms**, DB, déploiement, externes).

---

## 2. Synthèse (WEA-63)

| Champ | État (doc dépôt) |
|-------|------------------|
| **Inventaire WEA-33** | Ligne #4 — snapshot mars 2026 ; croiser avec export Repl quand disponible. |
| **Git cible** | `WeAdU-ltd/Negative-Terms` — aligner `git remote` du Repl ou import zip vers ce repo. |

---

## 3. Dépôt GitHub (WEA-64)

| Rôle | URL |
|------|-----|
| **Application** | `https://github.com/WeAdU-ltd/Negative-Terms` |

---

## 4. Code + README + CI (WEA-65)

Importer le code depuis le Repl ; README run + CI selon le dépôt cible et [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md) si besoin.

**État dépôt (agent GitHub, 2026-05-05)** : le dépôt cible contient déjà une base applicative riche (pytest, workflows AWS, README racine). PR **doc** ajoutant une section **Replit migration** avec lien vers ce runbook + WEA-61 : https://github.com/WeAdU-ltd/Negative-Terms/pull/680 — **auto-merge (squash) activé** sur la PR ; elle part en merge quand les garde-fous CI / review du dépôt sont verts. L’alignement exact du code avec le Repl reste à valider depuis Replit ou un diff manuel avant cutover (WEA-66).

## 5. Cutover (WEA-66)

Quand la prod ne dépend plus du Repl : retirer la ligne **#4** dans [WEA-36 §5](./WEA-36-replit-migration-societe.md) ; secrets Replit → [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete).

---

_Document vivant ; création : 2026-05-06._
