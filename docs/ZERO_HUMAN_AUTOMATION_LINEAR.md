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
