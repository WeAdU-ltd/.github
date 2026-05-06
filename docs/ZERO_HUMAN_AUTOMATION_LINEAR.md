# Gabarit ticket Linear — automation « zéro humain » (GitHub)

À **créer une fois** dans Linear (équipe **WEA** ou équivalent). Copier-coller les blocs ci-dessous. Ne pas y mettre de secrets.

---

## Titre proposé

`Infra — automation « zéro humain » (audit protections + PR sans poste local)`

---

## Description

Réduire les manipulations répétitives pour l’humain (PAT dans un fichier local, PowerShell, merges manuels de doc d’audit, dépendance à l’UI GitHub pour des tâches routinières). Les agents et la CI doivent pouvoir tenir à jour les preuves et garde-fous **sans** solliciter Jeff pour la routine.

Périmètre initial : dépôt **`WeAdU-ltd/.github`** (script `scripts/github_branch_protection_audit_wea32.py`, doc `docs/GITHUB_BRANCH_PROTECTION_WEA32.md`). Étendre ensuite aux autres repos si besoin.

Lien principe agents : `AGENTS.md` (section *Principe « zéro humain »*).

---

## Critères de fait

* [ ] Secret **organisation** GitHub (nom figé, ex. `GITHUB_ORG_AUDIT_TOKEN`) : PAT ou token **machine** dédié, **SSO autorisé** pour `WeAdU-ltd`, scopes limités à la lecture des règles de branche + liste des repos ; **accessible** au workflow du dépôt `.github` (liste d’accès du secret).
* [ ] Workflow **planifié** (ex. hebdomadaire `cron`) sur `.github` : exécute l’audit, met à jour `docs/GITHUB_BRANCH_PROTECTION_WEA32.md`, ouvre une **PR** vers `main` ; **auto-merge** lorsque `Lint workflows` est vert (comme le reste du dépôt).
* [ ] Doc à jour : `docs/GITHUB_BRANCH_PROTECTION_WEA32.md` ou `README.md` indique que l’**audit de routine** ne nécessite pas d’exécution manuelle sur poste Windows.
* [ ] (Optionnel) **Ruleset** d’organisation documenté (ou ticket lié) pour harmoniser `main` sur tous les repos cibles sans refaire la même UI repo par repo.

---

## Hors périmètre (explicite)

- Ne pas committer de valeur de token dans GitHub.
- Ne pas demander à l’humain de coller un PAT dans le chat.

---

_Document miroir dans le dépôt `WeAdU-ltd/.github` ; le ticket réel vit dans Linear._

---

# Automatisation « zéro humain » — où vivent les secrets (miroir technique)

**Source d’intention (Linear / produit) :** principe [AGENTS.md](../AGENTS.md) et tickets type [WEA-42](https://linear.app/weadu/issue/WEA-42/infra-automation-zero-humain-audit-protections-pr-sans-poste-local) (automation routinière sans PowerShell ni PAT dans un fichier local).

Ce fichier vit dans le dépôt pour que les agents et la CI renvoient toujours vers la même vérité : **où vivent les secrets**, et **ce qui n’est jamais dans Git**.

---

## 1. Ce qui est « zéro effort » pour l’humain

- **Jobs planifiés** (cron), PR automatiques, auto-merge quand la CI est verte : pas de merge manuel répété pour la même routine.
- **Noms de secrets figés** dans [`docs/SECRETS_SOCLE_WEA15.md`](./SECRETS_SOCLE_WEA15.md) — pas de chasse au libellé dans le chat.
- **Commentaires Linear** : les agents postent via **`LINEAR_API_KEY`** et le script [`scripts/linear_issue_comment.py`](../scripts/linear_issue_comment.py) (ou équivalent dans `scripts/linear_*.py`) — pas de « copie ce bloc dans Linear » pour l’humain.

---

## 2. Ce qui reste une fois par besoin (non répétitif)

Certaines automatisations exigent un **jeton d’API** stocké dans **GitHub → Organization secrets** (ou coffre d’équipe aligné sur le même nom). **Aucun agent ne peut inventer ce jeton** : il n’existe pas dans le dépôt, et ne doit pas être collé dans Linear ni dans le chat.

**Personne de référence pour les valeurs** (création / rotation des secrets org) : voir [AGENTS.md](../AGENTS.md) — canal unique côté organisation.

---

## 3. Où est la « valeur » d’un secret org (ex. `GITHUB_ORG_AUDIT_TOKEN`) ?

| Question | Réponse |
|----------|--------|
| Est-ce un fichier dans ce repo ? | **Non.** Aucun secret d’exploitation n’est versionné. |
| Est-ce dans le message d’un agent ? | **Non** (hors principe sécurité + règles WeAdU). |
| Où la mettre ? | **GitHub** → *Organization* → *Settings* → *Secrets and variables* → *Actions* → secret dont le **nom** est documenté (ex. `GITHUB_ORG_AUDIT_TOKEN`), avec **accès explicite** aux dépôts concernés. |
| D’où vient le caractère secret ? | Généré **une fois** dans l’UI GitHub (PAT / GitHub App install token) ou **réutilisation** d’un PAT déjà conservé (ex. coffre **1Password**) sous un **autre titre** — même valeur collée dans le champ org si les portées suffisent ; pas de deuxième PAT sans besoin. |

Pour l’audit des protections de branche (WEA-32 / WEA-42), le détail des portées acceptables et le lien vers la procédure PAT : [`docs/GITHUB_BRANCH_PROTECTION_WEA32.md`](./GITHUB_BRANCH_PROTECTION_WEA32.md) § « Origine du jeton… » et [`docs/SECRETS_SOCLE_WEA15.md`](./SECRETS_SOCLE_WEA15.md).

### Liste partagée des alias (optionnel)

Pour éviter les doublons **humains** : dans le vault équipe, certains items peuvent porter un champ ou une note du type **« aussi utilisé comme secret GitHub org : `GITHUB_ORG_AUDIT_TOKEN` »**. Ce dépôt ne peut pas contenir la valeur ; il documente seulement les **noms** attendus par les workflows ([`SECRETS_SOCLE_WEA15.md`](./SECRETS_SOCLE_WEA15.md)).

---

## 4. Règle pour les agents (éviter la question « où est la valeur ? »)

Lorsqu’un workflow introduit un **nouveau** nom de secret d’organisation :

1. **Documenter** le nom dans [`SECRETS_SOCLE_WEA15.md`](./SECRETS_SOCLE_WEA15.md) (et le runbook métier si besoin).
2. **Chercher un PAT ou jeton existant** (GitHub org secrets, vault **1Password** sous d’autres noms) avant de proposer une création ; [`SECRETS_CARTOGRAPHIE_WEA14.md`](./SECRETS_CARTOGRAPHIE_WEA14.md).
3. **Expliquer dans la même PR** : la valeur n’est pas dans le repo ; réutilisation possible depuis le coffre aligné sur les portées ; sinon création côté référent et collage dans le secret org ; liste d’accès des dépôts.
4. **Ne pas** demander à l’humain non référent de « trouver » une valeur : indiquer **qui** la crée ou la relie (canal unique) et **où** elle est stockée (UI GitHub), avec lien vers ce fichier ou WEA-15.

---

_Document technique du dépôt `WeAdU-ltd/.github` ; aligné avec le principe « zéro humain » pour la répétition, pas pour nier l’existence d’un bootstrap secrets._
