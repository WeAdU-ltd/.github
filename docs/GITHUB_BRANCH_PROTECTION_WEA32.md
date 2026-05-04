# WEA-32 — GitHub : protections de branche + anti-secrets en clair

Document d’ancrage pour le ticket [WEA-32](https://linear.app/weadu/issue/WEA-32/github-protections-branches-anti-secrets-en-clair). Il complète le modèle d’accès [WEA-13](https://linear.app/weadu/issue/WEA-13/github-modele-dacces-interne-partage-perso-finance-rh-isole) ([`inventory/WEA-13-github-access-model.md`](./inventory/WEA-13-github-access-model.md)), l’inventaire dépôts [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces) et le socle secrets [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh).

---

## 1. Objectif

- **Branche principale** (`main` ou branche par défaut du dépôt) : règles de protection cohérentes sur les dépôts **société** (`WeAdU-ltd`, etc.).
- **Secrets** : ne pas committer de jetons en clair ; rappel dans la doc agents + **scan** basique en CI (Gitleaks dans ce dépôt) + hook **pre-commit** optionnel pour les postes qui l’installent.

---

## 2. Branch protection (GitHub UI)

À appliquer sur la **branche par défaut** de chaque dépôt interne (souvent `main`). *Organization → Repositories → [repo] → Settings → Branches → Branch protection rules → Add rule* (ou règle existante).

Recommandation **standard** (ajuster selon criticité ; les repos **finance-RH** : exiger au moins une revue humaine, voir [WEA-13 §2](https://linear.app/weadu/issue/WEA-13/github-modele-dacces-interne-partage-perso-finance-rh-isole)) :

| Réglage | Recommandation |
|---------|------------------|
| **Require a pull request before merging** | Activé |
| **Required approvals** | ≥ 1 pour les dépôts sensibles ; 0 acceptable pour petits dépôts outillage si d’autres garde-fous (CI, bots) sont en place |
| **Require status checks to pass** | Inclure au minimum le job CI du dépôt (dans `.github` : un seul job **`actionlint`** couvre actionlint, smoke IBKR sec et **gitleaks**) |
| **Require branches to be up to date** | Souhaitable quand la CI est rapide |
| **Do not allow bypassing the above settings** | Activé pour que les administrateurs suivent les mêmes règles |
| **Restrict who can push to matching branches** | Optionnel ; utile si seules des machines ou des rôles précis doivent pousser directement |

**Auto-merge** : compatible avec les protections si « Allow auto-merge » est activé au niveau dépôt et que les **checks requis** sont listés dans la règle (voir [README principal](../README.md) pour ce dépôt `.github`).

---

## 3. Audit automatisé (critère de fait)

Le script [`scripts/github_branch_protection_audit_wea32.py`](../scripts/github_branch_protection_audit_wea32.py) interroge l’API GitHub : pour chaque dépôt non archivé de l’organisation, présence de règles sur la **branche par défaut**.

### Mise à jour de routine (sans poste local)

Un workflow planifié maintient ce document **sans** exécution manuelle sur Windows :

- Workflow : [`.github/workflows/branch-protection-audit-wea32.yml`](../.github/workflows/branch-protection-audit-wea32.yml) — **cron** hebdomadaire + déclenchement manuel (*Actions* → **Branch protection audit (WEA-32)** → *Run workflow*).
- Secret d’**organisation** **`GITHUB_ORG_AUDIT_TOKEN`** : le **nom** est figé ; la **valeur** est un PAT créé dans GitHub (pas un fichier du repo) — voir [§ Origine du jeton](#origine-du-jeton-github_org_audit_token) et la section dédiée dans [WEA-15](../SECRETS_SOCLE_WEA15.md). Le dépôt `WeAdU-ltd/.github` doit figurer dans la liste d’accès du secret.

#### Origine du jeton (`GITHUB_ORG_AUDIT_TOKEN`)

Tu ne « récupères » pas cette valeur dans le clone : elle est **créée une fois** (compte autorisé sur l’org), puis enregistrée **uniquement** dans *Organization secrets* sous le nom `GITHUB_ORG_AUDIT_TOKEN`. Portées et SSO : [`SECRETS_SOCLE_WEA15.md`](../SECRETS_SOCLE_WEA15.md). Principe général : [`ZERO_HUMAN_AUTOMATION_LINEAR.md`](./ZERO_HUMAN_AUTOMATION_LINEAR.md).
- Le job régénère la table, pousse la branche `automated/wea32-branch-protection-audit`, ouvre une **PR** vers `main` si besoin, puis [auto-merge](../README.md#auto-merge-pull-requests-to-main) en file d’attente lorsque le job **Lint workflows** (`ci.yml`) est vert.

### Exécution locale ou ponctuelle (optionnel)

Prérequis : `GITHUB_TOKEN` **ou** `GITHUB_ORG_AUDIT_TOKEN` avec droits suffisants pour lire les règles (souvent `repo` sur un PAT, ou portée adaptée côté org).

```bash
cd /path/to/clone/of/.github
export GITHUB_TOKEN=...   # ou GITHUB_ORG_AUDIT_TOKEN
python3 scripts/github_branch_protection_audit_wea32.py --github-org WeAdU-ltd \
  -o docs/GITHUB_BRANCH_PROTECTION_WEA32.md
```

- Sans `--fail` : le script met à jour ce fichier et se termine avec le code 0 (audit informatif).
- Avec `--fail` : code de sortie **1** si au moins un dépôt n’a **aucune** règle sur la branche par défaut (utile pour une future étape CI une fois tous les dépôts conformes).

Pour cocher le critère Linear **« Règles appliquées sur au moins la branche principale des repos société cibles »** : la table régénérée ci-dessous doit montrer une protection présente sur chaque dépôt concerné (pas « aucune »). **Sans action récurrente de ta part** : une fois les règles posées sur `main` (ou une **ruleset** d’organisation qui cible les dépôts société), l’état reste stable ; la table suit les changements via le workflow ci-dessus (ou régénération locale après ajout de dépôts / changement de branche par défaut).

### Rulesets d’organisation (optionnel)

Pour harmoniser `main` sur **tous** les dépôts cibles sans refaire la même UI dépôt par dépôt : *Organization settings* → **Rules** → **Rulesets** (ciblage par propriété de dépôt ou liste). Une stratégie org-wide peut compléter ou remplacer les règles par dépôt ; si un ticket Linear dédié est nécessaire pour la décision (périmètre repos, exceptions), le lier depuis [WEA-32](https://linear.app/weadu/issue/WEA-32/github-protections-branches-anti-secrets-en-clair) ou un sous-ticket infra.

<!-- WEA32_PROTECTION_BEGIN -->
_Généré le 2026-05-04 12:59:09 (UTC) — organisations : WeAdU-ltd._

Lecture API : présence de règles sur la **branche par défaut** (`GET .../branches/{branch}/protection`). « Aucune » = HTTP 404 / pas de règle.

| Dépôt | Branche défaut | Protection | Revues PR requises | Status checks | Admins assujettis | Commits signés |
|-------|----------------|------------|--------------------|--------------|-------------------|----------------|
| `WeAdU-ltd/.github` | `main` | oui | non | oui (1 check(s)) | oui | non |
| `WeAdU-ltd/Negative-Terms` | `main` | oui | non | oui (4 check(s)) | non | non |
| `WeAdU-ltd/SH-Checker-Bids` | `main` | minimal | non | non | oui | non |
<!-- WEA32_PROTECTION_END -->

---

## 4. Anti-secrets en clair

### 4.1 Règles pour les humains et les agents

- Ne jamais committer de clés API, mots de passe, jetons OAuth, certificats ou `.env` avec valeurs réelles.
- Stocker les valeurs dans **GitHub Encrypted Secrets**, **Environments**, Cursor, 1Password selon [WEA-14](https://linear.app/weadu/issue/WEA-14/secrets-cartographie-1password-github-cursor-regle-chercher-avant-de) / [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh).
- Pour les modèles : fichiers `*.example`, `op.env.example`, sans valeurs sensibles.

### 4.2 CI (ce dépôt)

Le workflow [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) exécute **Gitleaks** dans le **même** job que actionlint (nom du check GitHub inchangé : `actionlint`). Ainsi, si `main` exige déjà ce check, le scan secrets est appliqué **sans** ajouter un second statut obligatoire dans les paramètres. Commande : `gitleaks detect --redact` sur l’historique complet (`fetch-depth: 0`). Les dépôts applicatifs peuvent réutiliser la même recette.

### 4.3 Pre-commit (optionnel, poste local)

Fichier [`.pre-commit-config.yaml`](../.pre-commit-config.yaml) à la racine : après `pip install pre-commit` dans le clone, `pre-commit install` lance Gitleaks avant chaque commit. Les agents cloud n’ont pas toujours pre-commit ; la CI reste la garantie commune.

---

## 5. Critères de fait (auto-contrôle)

| Critère | Comment le valider |
|--------|----------------------|
| Règles sur la branche principale des repos société cibles | Table générée §3 sans ligne « aucune » pour ces dépôts ; ou capture / note d’admin sur les règles org-wide si utilisées |
| Rappel + scan basique ou pre-commit | Ce document + Gitleaks dans le job CI `actionlint` + config pre-commit dans le dépôt |

---

_Dernière mise à jour : alignement avec le dépôt `WeAdU-ltd/.github` (WEA-32)._
