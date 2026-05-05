# after-framfield-cockpit — Replit (Repl 3, WEA-55)

**Linear** : parent [WEA-55](https://linear.app/weadu/issue/WEA-55/repl-3-after-framfield-cockpit-migration-replit-github-persosociete-a-trancher) — chaîne [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents). **Ligne inventaire** : [WEA-33](./WEA-33-replit-inventory.md) #3.

**Décision (2026-05-05 — Jeff)** : périmètre **personnel** — dépôt cible sur le compte GitHub **`JeffWeadu`** : `https://github.com/JeffWeadu/after-framfield-cockpit` (repo à créer par toi si besoin, voir §3.1 ; le jeton d’agent org **ne peut pas** créer un repo perso). **Secrets** : isolation [WEA-13](./WEA-13-github-access-model.md) / [WEA-37](https://linear.app/weadu/issue/WEA-37/replit-migration-repos-perso-isolation-acces) — rien d’applicatif ici.

---

## 1. Brief agent Replit (WEA-56)

Un export Markdown produit **dans** le Repl `after-framfield-cockpit` n’est pas reproductible depuis l’agent qui ne fait qu’analyser ce dépôt `.github`.

**Justification documentée** : même logique que [WEA-35 §7](./WEA-35-weadu-socle-v5-lab-template.md). Pour la vue **inventaire dépôt** : OAuth redirect sur hostname workspace **éphémère** (instable) — [WEA-33](./WEA-33-replit-inventory.md) ligne #3 ; redirect durables et scopes : [WEA-20](../GOOGLE_OAUTH_WEA20.md).

**Consigne** (à coller dans l’agent Cursor **du** Repl si besoin d’un export Repl-only) : formulaire §7 [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md).

---

## 2. Synthèse inventaire (WEA-57)

| Champ | État (doc dépôt, sans ouverture Repl) |
|-------|--------------------------------------|
| Déploiement | Redirect OAuth **non stable** (hostname workspace éphémère) — photo mars 2026 [WEA-33](./WEA-33-replit-inventory.md). |
| Git / GitHub | Cible : **`https://github.com/JeffWeadu/after-framfield-cockpit`** (compte perso) — repo à initialiser côté GitHub (§3.1) avant `git push`. |
| Suite | Importer le code depuis le Repl, ajouter un `README` + redirects OAuth stables — [WEA-20](../GOOGLE_OAUTH_WEA20.md). |

---

## 3. Dépôt GitHub cible (WEA-58) — compte perso

| Rôle | URL |
|------|-----|
| **Dépôt applicatif (perso)** | `https://github.com/JeffWeadu/after-framfield-cockpit` |
| **Doc / migration (société)** | `https://github.com/WeAdU-ltd/.github` — ce runbook |

Le label Linear groupe **`repo`** ne s’applique pas à un dépôt perso ; les tickets liés restent sur le label **`WeAdU-ltd/.github`** pour le suivi **docs** côté org.

### 3.1 Créer le dépôt (une action sur GitHub.com)

L’API GitHub a refusé la création automatique depuis l’environnement d’agent (PAT org sans `repo` **user**). **Crée** le dépôt toi-même :

1. Ouvre **https://github.com/new**
2. **Owner** : `JeffWeadu`
3. **Repository name** : `after-framfield-cockpit`
4. Coche **Private** (recommandé pour un projet perso)
5. Ne coche pas d’auto-template ; clique **Create repository**

Ensuite, depuis le Repl ou ton poste : `git remote add origin https://github.com/JeffWeadu/after-framfield-cockpit.git` puis premier push (voir [WEA-59](https://linear.app/weadu/issue/WEA-59/after-framfield-cockpit-code-importe-readme-procedure-de-run) sur Linear).

---

## 4. Code + README + CI (WEA-59)

Importer le code depuis le Repl dans **`JeffWeadu/after-framfield-cockpit`** après §3.1. README minimal : runtime, prérequis, secrets **nommés** (sans valeurs). Pas d’obligation d’alignement template WeAdU pour un repo **perso** ; optionnel : CI GitHub Actions basique (`pytest`, `npm test`, etc.) selon la stack une fois le code importé.

---

## 5. Cutover (WEA-60)

Tant que le périmètre repo et les redirect OAuth **production** ne sont pas fixés, le Repl peut rester dans la [liste résiduelle §5](./WEA-36-replit-migration-societe.md) ; fermeture après cutover + [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete).

---

_Document vivant ; création : 2026-05-05 ; décision Perso + URL cible : 2026-05-05._
