# WEA-12 — GitHub : inventaire orgs, comptes, repos et accès

Ce document est le livrable principal du ticket [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces) dans le dépôt **`WeAdU-ltd/.github`**. Les tableaux **Linear ↔ GitHub** sont régénérés automatiquement dans [`docs/GITHUB_LINEAR_INVENTORY_WEA12.md`](../GITHUB_LINEAR_INVENTORY_WEA12.md) (voir section générée entre les marqueurs `WEA12_INVENTORY`).

---

## Synthèse des zones d’incertitude (à clarifier hors agent)

1. **Membres et rôles org GitHub** : l’API « integration » utilisée dans l’environnement agent ne permet pas `GET /orgs/WeAdU-ltd/members` ni les équipes org (403). La liste nominative des comptes humains et de leur rôle doit être complétée par un **admin org** (GitHub → Organization → People).
2. **Liste exhaustive des dépôts org** : le même jeton ne retourne qu’un sous-ensemble public des dépôts via `GET /orgs/WeAdU-ltd/repos` (un dépôt visible dans le snapshot du 2026-05-02). Les labels Linear sous **`repo`** font office de **liste fonctionnelle** des dépôts ciblés par les agents (trois entrées au 2026-05-02) ; tout dépôt privé absent de l’API doit être aligné manuellement ou via un PAT avec droits **repo** / **metadata** org.
3. **Secrets GitHub (noms)** : l’API des secrets Actions (org ou repo) est **inaccessible** avec ce jeton (403). L’inventaire des noms réels en production repose sur **Settings → Secrets** (org/repos) par un administrateur.
4. **Perso vs société** : règle appliquée ici — tout `WeAdU-ltd/*` = **société** ; tout autre `owner/*` hors cette org = **hors périmètre société** ou à qualifier (comptes personnels, forks, etc.).

---

## 1. Organisations et comptes concernés

| Organisation / compte | Rôle dans l’inventaire | Détail vérifiable ici |
|------------------------|-------------------------|------------------------|
| **`WeAdU-ltd`** (GitHub Organization) | Org société, périmètre principal WEA-12 | [Organisation sur GitHub](https://github.com/WeAdU-ltd) |
| Comptes humains (People) | À maintenir côté GitHub | Non exportable depuis cet environnement (API 403) ; source : **Org → People** |
| Bot / intégration **`cursor`** (compte GitHub utilisé par l’agent cloud) | Accès limité (repos publics visibles, pas membres/secrets) | Constats techniques documentés dans [`github-org-repo-snapshot-2026-05-02.json`](github-org-repo-snapshot-2026-05-02.json) |

---

## 2. Dépôts (liste et perso vs société)

### 2.1 Dépôts étiquetés Linear (`repo` → enfants `owner/repo`)

Alignés sur la génération du **2026-05-02** (voir aussi le tableau dans `GITHUB_LINEAR_INVENTORY_WEA12.md`) :

| `owner/repo` | Perso / société | Remarque |
|--------------|-----------------|----------|
| `WeAdU-ltd/.github` | Société | Dépôt des workflows partagés et de cette doc |
| `WeAdU-ltd/Negative-Terms` | Société | Ticket / code NEG |
| `WeAdU-ltd/SH-Checker-Bids` | Société | |

### 2.2 Export machine (snapshot API partiel)

Fichier : [`github-org-repo-snapshot-2026-05-02.json`](github-org-repo-snapshot-2026-05-02.json) — contient la réponse brute limitée du jeton agent + la liste des trois dépôts déclarés côté Linear pour comparaison.

---

## 3. Accès, équipes, secrets (noms)

| Élément | Statut dans ce dépôt |
|---------|----------------------|
| **Teams GitHub ↔ repos** | Non exportable (API org teams 403) ; à documenter par un admin. |
| **Branch protections** | Par dépôt application ; hors périmètre `.github` sauf pour ce repo. |
| **Secrets Actions — noms documentés dans ce repo** | Le workflow réutilisable [`auto-deploy.yml`](../../.github/workflows/auto-deploy.yml) attend des **secrets nommés par le dépôt appelant** : `env_file`, `ssh_private_key`, `ssh_known_hosts` (voir [`README.md`](../../README.md)). Ce ne sont pas des secrets stockés dans `.github` lui-même, mais la **convention de noms** exposée aux repos consommateurs. |
| **Secrets org/repo (noms réels en prod)** | Non listables via l’API avec le jeton agent ; inventaire manuel admin. |

---

## 4. Linear ↔ labels `repo` (équipe WeAdU)

- **Convention** : uniquement des enfants du groupe parent **`repo`** au format **`WeAdU-ltd/…`** (anciens `JeffWeadu/*` supprimés le 2026-05-02).
- **Tableau label → dépôt**, **repos sans label**, **tickets ouverts récents sans sous-label `repo`** : section générée dans [`docs/GITHUB_LINEAR_INVENTORY_WEA12.md`](../GITHUB_LINEAR_INVENTORY_WEA12.md).

---

## 5. Décision : agents **sans** label `repo`

- Ne pas se fier au dépôt par défaut Cursor.
- Exiger **un** sous-label enfant de **`repo`** (`WeAdU-ltd/…`) **ou** une consigne explicite du type `[repo=owner/repo]` dans le ticket.
- Charte étendue : [WEA-17](https://linear.app/weadu/issue/WEA-17).

---

## 6. Compatibilité **`chain`** et **`repo`**

- **`chain`** : enchaînement des sous-tickets (workflow).
- **`repo`** : cible GitHub pour le code. **Orthogonaux** ; un ticket peut porter les deux.

---

## 7. Régénération

```bash
export LINEAR_API_KEY=…
export GITHUB_TOKEN=…   # PAT avec droits org + repos attendus
export LINEAR_TEAM_KEY=WEA
python3 scripts/linear_github_inventory_wea12.py -o docs/GITHUB_LINEAR_INVENTORY_WEA12.md --github-org WeAdU-ltd
```
