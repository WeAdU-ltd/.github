# after-framfield-cockpit — Replit (Repl 3, WEA-55)

**Linear** : parent [WEA-55](https://linear.app/weadu/issue/WEA-55/repl-3-after-framfield-cockpit-migration-replit-github-persosociete-a-trancher) — chaîne [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents). **Ligne inventaire** : [WEA-33](./WEA-33-replit-inventory.md) #3.

**Décision (2026-05-05 — Jeff)** : périmètre **personnel** — dépôt cible sur le compte GitHub **`JeffWeadu`** : `https://github.com/JeffWeadu/after-framfield-cockpit`. **Repl Replit** : **supprimé** (**2026-05-05**, confirmation humaine). **Prod** : **Google Sheet** (pas d’URL Replit). **Secrets** : isolation [WEA-13](./WEA-13-github-access-model.md) / [WEA-37](https://linear.app/weadu/issue/WEA-37/replit-migration-repos-perso-isolation-acces) ; jetons côté **GitHub Actions** + 1Password — plus de Secrets Replit pour ce projet.

---

## 1. Brief agent Replit (WEA-56)

Un export Markdown produit **dans** le Repl `after-framfield-cockpit` n’est pas reproductible depuis l’agent qui ne fait qu’analyser ce dépôt `.github`.

**Justification documentée** : même logique que [WEA-35 §7](./WEA-35-weadu-socle-v5-lab-template.md). Pour la vue **inventaire dépôt** : OAuth redirect sur hostname workspace **éphémère** (instable) — [WEA-33](./WEA-33-replit-inventory.md) ligne #3 ; redirect durables et scopes : [WEA-20](../GOOGLE_OAUTH_WEA20.md).

**Consigne** (à coller dans l’agent Cursor **du** Repl si besoin d’un export Repl-only) : formulaire §7 [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md).

---

## 2. Synthèse inventaire (WEA-57)

| Champ | État (doc dépôt, sans ouverture Repl) |
|-------|--------------------------------------|
| Déploiement | **Google Sheet** (prod) ; **Repl Replit supprimé** (**2026-05-05**). |
| Git / GitHub | **`https://github.com/JeffWeadu/after-framfield-cockpit`** (privé) — **code + README** + workflow **Sheets smoke test** sur `main`. |
| Suite | Vérifier les **redirects OAuth** dans Google Cloud si tu utilises encore un flux navigateur (sinon **compte de service** suffit pour l’API) — [WEA-20](../GOOGLE_OAUTH_WEA20.md). Suivi global fermeture Replit : [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete). |

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

**Statut (2026-05-05)** : **Repl supprimé** sur Replit ; **vérité code** = repo GitHub privé ; **accès Sheet** = compte de service + secrets GitHub (smoke Actions vert). **Résiduelle WEA-36 §5** : ligne **Repl #3 retirée** du tableau migration dans ce dépôt.

**OAuth** : si des redirect URIs Replit **éphémères** restent dans Google Cloud Console pour un ancien client OAuth, les **retirer** ou les remplacer par des URLs **stables** ([WEA-20](../GOOGLE_OAUTH_WEA20.md)) — nettoyage manuel dans la console Google.

---

_Document vivant ; création : 2026-05-05 ; cutover doc : 2026-05-05 ; Repl supprimé : 2026-05-05._
