# after-framfield-cockpit — Replit (Repl 3, WEA-55)

**Linear** : parent [WEA-55](https://linear.app/weadu/issue/WEA-55/repl-3-after-framfield-cockpit-migration-replit-github-persosociete-a-trancher) — chaîne [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents). **Ligne inventaire** : [WEA-33](./WEA-33-replit-inventory.md) #3.

**Décision (2026-05-05 — Jeff)** : périmètre **personnel** — dépôt cible sur le compte GitHub **`JeffWeadu`** : `https://github.com/JeffWeadu/after-framfield-cockpit`. **Statut (2026-05-05)** : dépôt **créé** sur GitHub (privé — l’agent ne peut pas l’ouvrir en API ; validation = confirmation humaine). **Secrets** : isolation [WEA-13](./WEA-13-github-access-model.md) / [WEA-37](https://linear.app/weadu/issue/WEA-37/replit-migration-repos-perso-isolation-acces) — rien d’applicatif ici.

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
| Git / GitHub | **`https://github.com/JeffWeadu/after-framfield-cockpit`** (privé) — **code + README** sur `main` (commits initiaux + `d71eed1`). |
| Suite | **OAuth** : enregistrer une redirect **stable** vers l’URL du repo / hébergement cible — [WEA-20](../GOOGLE_OAUTH_WEA20.md). Puis **archiver ou supprimer** le Repl quand tu n’en as plus besoin ; révoquer les secrets Replit à ce moment-là ([WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete)). |

---

## 3. Dépôt GitHub cible (WEA-58) — compte perso

| Rôle | URL |
|------|-----|
| **Dépôt applicatif (perso)** | `https://github.com/JeffWeadu/after-framfield-cockpit` |
| **Doc / migration (société)** | `https://github.com/WeAdU-ltd/.github` — ce runbook |

Le label Linear groupe **`repo`** ne s’applique pas à un dépôt perso ; les tickets liés restent sur le label **`WeAdU-ltd/.github`** pour le suivi **docs** côté org.

### 3.1 Créer le dépôt sur GitHub.com — **fait**

~~Création impossible via l’API agent (403).~~ **Création confirmée** (Jeff, 2026-05-05).

### 3.2 Premier push (Repl ou poste local)

1. Dans le Repl **after-framfield-cockpit** (ou après export du code), initialiser ou ajouter le remote :
   ```bash
   git remote add origin https://github.com/JeffWeadu/after-framfield-cockpit.git
   # ou SSH : git@github.com:JeffWeadu/after-framfield-cockpit.git
   ```
2. Authentification GitHub : PAT personnel avec scope **`repo`** sur ton compte (pas le PAT org WeAdU-ltd).
3. `git branch -M main` si besoin, puis `git push -u origin main`.

Voir [WEA-59](https://linear.app/weadu/issue/WEA-59/after-framfield-cockpit-code-importe-readme-procedure-de-run) — README minimal §4 ci-dessous.

---

## 4. Code + README + CI (WEA-59)

Importer le code depuis le Repl dans **`JeffWeadu/after-framfield-cockpit`** (§3.2). Coller au minimum ce **README** à la racine du repo perso (adapter la stack) :

```markdown
# after-framfield-cockpit

Migration depuis Replit — périmètre **perso** (pas WeAdU-ltd).

## Prérequis

- (ex. Python 3.x / Node … — à compléter selon le Repl)

## Configuration (noms seulement)

- Variables d'environnement / secrets à prévoir : *(à lister depuis Replit Secrets — **pas de valeurs** dans ce README)*

## Lancer en local

(faire suivre les commandes exactes exportées depuis Replit ; exemple typique : dépendances puis `python …` ou `npm run dev`.)

## OAuth / Google

Redirects stables : voir convention WeAdU [GOOGLE_OAUTH_WEA20.md](https://github.com/WeAdU-ltd/.github/blob/main/docs/GOOGLE_OAUTH_WEA20.md) (doc org).

## CI

Optionnel : ajouter une workflow GitHub Actions quand la stack est fixée.
```

**Critères WEA-59** : cocher sur Linear quand ce README est dans le repo **et** le code importé ; CI optionnelle pour un repo perso.

**Automatisation (machine Jeff)** : script [`push_framfield_readme.ps1`](https://github.com/WeAdU-ltd/.github/blob/main/scripts/push_framfield_readme.ps1) — crée `README.md` à la racine du clone local et pousse sur `origin/main` (lit le même `framfield_github_pat.txt` que pour le premier push).

---

## 5. Cutover (WEA-60)

**État cutover « doc WeAdU » (2026-05-05)** :

- **Vérité code** : le dépôt **`JeffWeadu/after-framfield-cockpit`** est la **référence** (historique Git sur `main`, README présent).
- **Replit** : peut rester ouvert tant que tu l’utilises pour **dev** ou tant que les **redirects OAuth** pointent encore vers un hostname workspace **éphémère** — dès que la prod ou les tests passent par des URLs **stables**, mets à jour la **Google Cloud Console** (voir [WEA-20](../GOOGLE_OAUTH_WEA20.md)).
- **Secrets Replit** : les retirer / les faire tourner **quand** tu fermes ou archives le Repl (chaîne [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete)) ; pas d’action automatique depuis ce dépôt `.github`.

La [liste résiduelle §5](./WEA-36-replit-migration-societe.md) mentionne encore le Repl **#3** tant que **OAuth non stabilisé** ou **Repl non fermé** ; retire la ligne quand les deux sont vrais.

---

_Document vivant ; création : 2026-05-05 ; cutover doc : 2026-05-05._
