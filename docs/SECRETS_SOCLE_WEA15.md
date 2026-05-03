# Socle secrets partagé (WEA-15)

Document d’ancrage pour le ticket [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh). Il matérialise le **socle** : où vivent les secrets (GitHub org / environnements / dépôt, Cursor), **noms canoniques** (valeurs **hors** Linear et hors ce dépôt), et la **convention** pour tout nouveau dépôt interne société. S’appuie sur le modèle d’accès [WEA-13](./inventory/WEA-13-github-access-model.md) et la cartographie « chercher avant de demander » [WEA-14](./SECRETS_CARTOGRAPHIE_WEA14.md).

---

## 1. Principes

1. **Un secret, un rôle** : ne pas réutiliser le même jeton pour deux outils quand une séparation réduit le blast radius (ex. Linear API pour CI ≠ PAT humain large).
2. **Partage maximal sans copier partout** : préférer les **secrets d’organisation** (liste d’accès repos explicite) ou les **variables d’organisation** pour les non-secrets, plutôt que dupliquer la même valeur dans chaque dépôt.
3. **Finance / RH isolés** : pas les mêmes **GitHub Environments** ni les mêmes **préfixes de noms** que le socle généraliste ; voir §4.
4. **Cursor** : clés et MCP dans l’UI / le cloud workspace — jamais dans le chat ni dans le dépôt ; aligner les noms d’items 1Password (si utilisé) avec les noms GitHub documentés ici pour limiter la confusion.

---

## 2. Secrets GitHub — noms documentés (socle WeAdU-ltd)

Ces noms sont ceux **référencés par les workflows** de ce dépôt (`WeAdU-ltd/.github`) ou explicitement prévus pour l’org. Les **valeurs** se créent dans GitHub (org ou repo) par un administrateur ; ne pas les coller dans Linear.

| Nom (référence workflow / convention) | Niveau recommandé | Usage |
|---------------------------------------|-------------------|--------|
| `LINEAR_API_KEY` | **Organisation**, avec liste de repos autorisés incluant ceux qui exécutent `linear-done-on-merge.yml` | API Linear pour marquer les issues Done après merge (voir [`README.md`](../README.md)) |
| `GITHUB_TOKEN` | Fourni **automatiquement** par GitHub Actions sur les jobs ; pas à créer manuellement | `auto-merge-pr.yml`, permissions `contents` + `pull-requests` |
| `GMAIL_OAUTH_CLIENT_ID`, `GMAIL_OAUTH_CLIENT_SECRET`, `GMAIL_OAUTH_REFRESH_TOKEN` | **Organisation** ou **dépôt** selon blast radius ; pas dans Linear | Gmail agents ([WEA-24](./GMAIL_AGENTS_WEA24.md)) ; client OAuth selon [WEA-20](./GOOGLE_OAUTH_WEA20.md) |
| `env_file`, `ssh_private_key`, `ssh_known_hosts` | **Dépôt appelant** (secrets passés au `workflow_call` du réutilisable) | Déploiement via [`auto-deploy.yml`](../.github/workflows/auto-deploy.yml) ; les **noms côté appelant** sont libres mais l’exemple standard utilise `PRODUCTION_ENV_FILE`, `PRODUCTION_SSH_PRIVATE_KEY`, `PRODUCTION_SSH_KNOWN_HOSTS` (voir [`README.md`](../README.md)) |

**Création côté org** : *Organization settings* → *Secrets and variables* → *Actions* → *New organization secret* ; restreindre l’accès aux repositories concernés (politique « repository access »).

---

## 3. Convention : où ajouter un secret pour un **nouveau** dépôt interne (société)

Ordre de décision :

1. **Lire** `.github/workflows/` du nouveau dépôt et toute doc `docs/` ou `README` pour les noms déjà attendus (`secrets.*`).
2. **Secret partagé par plusieurs repos** (même intégration, même blast radius acceptable) : créer ou réutiliser un secret **d’organisation** `WeAdU-ltd`, puis **ajouter explicitement** le nouveau dépôt à la liste d’accès du secret (ou politique équivalente). Documenter le nom ici ou dans le README du dépôt consommateur.
3. **Secret propre au dépôt** (clé de déploiement, `.env` de prod pour une seule app) : *Repository* → *Settings* → *Secrets and variables* → *Actions* → *New repository secret*. Si le job utilise un **Environment** (`environment: production`, etc.), préférer *Environments* → *Environment secrets* pour bénéficier des règles de protection.
4. **Workflow réutilisable** `WeAdU-ltd/.github/.../auto-deploy.yml` : les secrets **ne vivent pas** dans `.github` ; ils sont déclarés dans le workflow **appelant** du dépôt application et passés dans la section `secrets:` du `uses:` (voir [README](../README.md)).
5. **Mettre à jour l’inventaire** : si le secret est nouveau au niveau org ou change la cartographie, mettre à jour ce fichier ou [`SECRETS_CARTOGRAPHIE_WEA14.md`](./SECRETS_CARTOGRAPHIE_WEA14.md) et, si besoin, l’inventaire [WEA-12](./GITHUB_LINEAR_INVENTORY_WEA12.md).

Jetons **distincts** quand utile : par exemple un PAT « packages read » pour CI ≠ un PAT « admin org » ; un compte service Google par produit si les quotas ou l’audit l’exigent (détails dans les tickets outils, ex. [WEA-20](https://linear.app/weadu/issue/WEA-20/google-passe-oauth-gmail-drive-docs-sheets-ads-analytics)).

---

## 4. Environments GitHub — généraliste vs finance-RH

| Zone | Exemples de noms d’`environment` | Secrets |
|------|----------------------------------|---------|
| Interne partagé (hors finance-RH) | `staging`, `production`, `preview` | Préfixes du type `STAGING_*`, `PRODUCTION_*` ou noms métier alignés sur le workflow |
| Compta / paie / RH | `production-finance`, `hr-batch`, … (noms figés par équipe) | **Préfixes dédiés** (ex. `PRODUCTION_FINANCE_*`, `HR_BATCH_*`) — **ne pas** réutiliser les secrets `PRODUCTION_*` généralistes pour ces jobs |

Aligné avec [WEA-13 §2](./inventory/WEA-13-github-access-model.md).

---

## 5. Cursor (Desktop / Cloud)

- Configurer les clés API et MCP dans les **paramètres du workspace** ou l’**agent cloud**, pas dans les fichiers versionnés.
- Réutiliser les **mêmes conventions de noms** que GitHub/1Password dans la documentation d’équipe pour qu’un humain sache où mettre à jour une valeur sans dupliquer sous trois libellés différents.
- Agents sur périmètre sensible : cibler le **bon** dépôt (label Linear `repo`, voir [WEA-17](https://linear.app/weadu/issue/WEA-17/charte-agents-linear-source-interdits-features-nouveaux-projets)) ; ne pas exposer les secrets finance-RH aux workspaces généralistes.

---

## 6. Écart vs critères de fait (pour fermeture du ticket)

| Critère | Preuve / action |
|---------|-----------------|
| Secrets de base créés (noms documentés, pas les valeurs dans Linear) | Ce fichier + workflows ; les **valeurs** sont à confirmer côté GitHub org par un admin (l’API inventaire agent ne liste pas les secrets existants, cf. WEA-12). |
| Convention pour un nouveau repo interne | §3 ci-dessus. |

---

_Document vivant : évolutions du socle → mettre à jour ce fichier et les renvois dans [`SECRETS_CARTOGRAPHIE_WEA14.md`](./SECRETS_CARTOGRAPHIE_WEA14.md)._
