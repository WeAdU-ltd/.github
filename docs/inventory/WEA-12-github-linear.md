# WEA-12 — GitHub : inventaire orgs, comptes, repos et accès

Ce document reprend le livrable prévu pour le ticket [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces) (copié depuis le commentaire Linear **« Contraintes respectées (agent) »**, initialement destiné à être ajouté depuis la proposition sur `WeAdU-ltd/Negative-Terms` [#638](https://github.com/WeAdU-ltd/Negative-Terms/pull/638)).

---

## Contraintes respectées (agent)

- **Dépôt cible** : le travail d’inventaire documentaire vit dans **`WeAdU-ltd/.github`** (ce dépôt). La PR sur Negative-Terms devait être **fermée sans merge** si l’objectif est de ne pas mélanger ce périmètre avec le code NEG.
- **Convention repo (Linear)** : utiliser uniquement les labels **`WeAdU-ltd/…`** sous le groupe parent **`repo`** ; les anciens `JeffWeadu/*` ont été supprimés (2026-05-02) pour éviter la confusion.

---

## Rapport / checklist WEA-12

### 1. Organisations & comptes

| Élément | Action / source | Statut |
|--------|------------------|--------|
| Org société | `WeAdU-ltd` (GitHub) | À confirmer membres / facturation |
| Comptes humains avec accès org | GitHub → **Organization → People** | À compléter (noms rôles) |
| Comptes perso vs pro | Politique interne (WEA-13) | Zone d’incertitude si pas documenté |

### 2. Dépôts (inventaire)

| Élément | Action | Statut |
|--------|--------|--------|
| Liste `owner/repo` sous `WeAdU-ltd` | `gh repo list WeAdU-ltd --limit 200` ou API avec PAT **Metadata** org | À exécuter hors agent |
| Perso vs société | Heuristique : owner `WeAdU-ltd/*` = société ; autres owners = perso ou tiers | À étiqueter manuellement |
| Archives | Décider si inclus dans inventaire | Optionnel |

### 3. Accès (hors périmètre script)

| Élément | Source | Statut |
|--------|--------|--------|
| Teams GitHub & repos | Org **Teams** | Manuel |
| Branch protections | Repo **Settings → Rules** | Manuel |
| Actions secrets (noms seulement) | **Settings → Secrets** (pas les valeurs) | Manuel / admin |
| SSO SAML | Org **Security** | Si applicable |

### 4. Linear ↔ labels `repo` (WeAdU / équipe concernée)

| Élément | Action | Statut |
|--------|--------|--------|
| Groupe parent **`repo`** (workspace) | Linear **Settings → Labels** | Vérifier nom exact `repo` |
| Enfants `RealOwner/repo` | Un label enfant = un dépôt ; **convention** : uniquement **`WeAdU-ltd/…`** (anciens `JeffWeadu/*` supprimés 2026-05-02) | Corriger côté Linear si résidu |
| Tableau label → URL GitHub | Pour chaque enfant : `https://github.com/<même chaîne>` | Voir aussi `docs/GITHUB_LINEAR_INVENTORY_WEA12.md` (régénération via script) |
| Repos GitHub **sans** label Linear correspondant | Comparer liste org vs enfants `repo` | Liste des trous |
| Tickets récents **ouverts** sans enfant `repo` | Filtre Linear : équipe WEA + état non terminal + sans label du groupe `repo` | À corriger ou règle explicite |

### 5. Décision agents **sans** label `repo**

- **Ne pas** s’appuyer sur le dépôt par défaut du dashboard Cursor.
- Soit **interdiction** de lancer l’agent sur du code tant qu’il n’y a pas exactement **un** enfant `repo` **ou** une ligne explicite `[repo=owner/repo]` dans le commentaire `@Cursor`.
- Soit **repo par défaut nommé** uniquement si documenté par équipe/projet (moins sûr).
- Charte détaillée : ticket **WEA-17**.

### 6. Compatibilité **`chain`**

- Le label **`chain`** qualifie le **workflow séquentiel** (parent / sous-tickets), pas le checkout Git.
- Le label **`repo`** (groupe parent) choisit le **dépôt** pour Cursor. Les deux sont **orthogonaux** ; pas de conflit si chaque ticket « code » a son `repo` (ou `[repo=…]`) en plus du parent `chain` le cas échéant.

---

## Prochain pas recommandé

1. Régénérer les tableaux dynamiques avec `scripts/linear_github_inventory_wea12.py` (voir `docs/GITHUB_LINEAR_INVENTORY_WEA12.md`).
2. Cocher les lignes du présent fichier au fur et à mesure.
3. Pour les données live (liste repos, labels), utiliser GitHub / Linear en UI ou le script avec secrets dans un environnement de confiance.
