# Charte agents — Linear comme source, interdits (features / nouveaux projets)

Ticket : [WEA-17](https://linear.app/weadu/issue/WEA-17/charte-agents-linear-source-interdits-features-nouveaux-projets).  
Projet Linear : **Autonomie agents (Cursor, GitHub, Google…)**.

**Synchronisation** : à chaque push sur `main` qui modifie ce fichier, le workflow [`.github/workflows/linear-sync-autonomie-project.yml`](../.github/workflows/linear-sync-autonomie-project.yml) vérifie que le projet Linear contient le lien canonique vers ce document (script [`scripts/linear_sync_autonomie_project_doc.py`](../scripts/linear_sync_autonomie_project_doc.py), secret `LINEAR_API_KEY`). Ainsi les agents n’ont pas à éditer le projet à la main pour ce critère.

## Objectif

Documenter la **charte agents** : le travail se fait **à partir d’un ticket Linear** ; **sans accord humain explicite**, il est **interdit** de lancer une nouvelle **feature produit** ou un nouveau **projet / dépôt**. Le reste (PR, merge, déploiement lorsque les garde-fous Git et l’organisation le permettent) reste **autorisé** selon la politique du dépôt et des workflows (CI, protections de branches, secrets).

## Fermeture d’un ticket — **obligatoire** (tous agents, tous projets)

Avant de marquer un ticket **Done**, appliquer le document canonique (critères de fait, écarts, etc.) :

**[Règle agents — Critères de fait avant Done (tous projets)](https://linear.app/weadu/document/regle-agents-criteres-de-fait-avant-done-tous-projets-2b32aec9e234)**

## Communication avec l’humain (obligatoire)

- **Par défaut** : l’agent **fait** ce qui peut être fait (API, outils, dépôt) sans transformer l’humain en « exécutant technique ».
- **Si bloqué** : donner **une seule étape** à la fois (où cliquer, quoi valider), en disant clairement **pourquoi l’agent ne peut pas le faire à sa place** (ex. connexion navigateur, paiement, 2FA).
- **Pas** de longue explication technique ni de liste d’options ; une phrase de contexte suffit sauf demande contraire.

## Règle Cursor (repo cible)

- Avant tout run agent **Cursor** : le ticket doit porter **exactement un** label du groupe `repo` pointant vers le **bon** dépôt GitHub (`owner/repo`), sauf exception documentée (ex. ticket purement infra sans code).
- **Interdit** : laisser l’agent travailler dans le **repo ouvert par défaut** dans Cursor si ce n’est pas celui du label `repo`.
- Si le ticket n’a pas de label `repo` : l’agent **n’écrit pas de code** — il ajoute le label ou demande clarification selon la procédure validée dans [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces).
- **Convention** : n’utiliser que des labels `WeAdU-ltd/…` (ou autre owner GitHub réel) — les `JeffWeadu/*` ont été retirés du workspace (2026-05-02).

## Références

- Inventaire GitHub ↔ Linear et trous de labels : [WEA-12 — GitHub inventaire](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces).
- Miroir court dans ce dépôt : [`AGENTS.md`](../AGENTS.md).
