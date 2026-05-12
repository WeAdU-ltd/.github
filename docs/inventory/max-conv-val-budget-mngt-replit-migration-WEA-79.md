# Max Conv Val Budget Mngt — migration Replit → GitHub (société)

**Référent WeAdU** : PR sur `WeAdU-ltd/.github` en **auto-merge** après CI quand la PR n’est pas brouillon ([`AGENTS.md`](../../AGENTS.md)). La **section 1** est à exécuter depuis une session **Cursor dans le Repl** *Max Conv Val Budget Mngt*, pas comme liste d’actions dans le chat — aligné [WEA-35 §7](./WEA-35-weadu-socle-v5-lab-template.md).

**Linear** : parent [WEA-79](https://linear.app/weadu/issue/WEA-79) ; chaîne ordonnée **WEA-80** (brief) → **WEA-81** (synthèse) → **WEA-82** (dépôt) → **WEA-83** (code + README) → **WEA-84** (cutover) — dernière étape **bloque** [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents). **Inventaire** : [WEA-33](./WEA-33-replit-inventory.md) **ligne #7** (Repl ID préfixe `d32b27a6-…`, priorité **P2**, périmètre **Société**).

Les agents **uniquement** sur ce dépôt `.github` n’ont pas le workspace Replit : pas d’export runtime ni Secrets sans session **dans** ce Repl.

---

## 1. Consigne vers l’agent Cursor du Repl

Produire un export structuré (**Markdown**, **aucune valeur de secret**) avec :

1. **Stack** : langage, frameworks, points d’entrée (`main`, `package.json`, `requirements.txt`, etc.).
2. **Run local** : commandes exactes pour le dev.
3. **Git** : remote(s), branche par défaut, dernier commit court.
4. **Secrets** : **noms** des variables Replit Secrets uniquement.
5. **Base Replit** : oui/non ; usage si pertinent.
6. **Déploiement** : URL `.replit.app`, Always On / autoscale, prod vs expérimentation.
7. **Externes** : AWS / GCP / API / OAuth si visibles dans le code ou la config.

Puis lier le résultat sur **WEA-80** et copier le fichier ici sous **§2** (nom type `max-conv-val-budget-mngt-replit-export-YYYY-MM-DD.md`).

---

## 2. Export ingéré (miroir dépôt)

| Bloc | État |
|------|------|
| Markdown produit par l’agent **dans** le Repl | **À faire** — aucun fichier d’export versionné dans ce dépôt à la date **2026-05-12**. |

---

## 3. Synthèse (WEA-81) — inventaire / ticket à jour

| Champ | État |
|-------|------|
| **WEA-33 ligne #7** | Toujours **Partiel** côté Socle ; mise à jour après export **§2** et confirmation Git / déploiement. |
| **Réponse agent Repl** | **En attente** de **WEA-80**. |

---

## 4. Dépôt GitHub (WEA-82)

| Rôle | État |
|------|------|
| **`WeAdU-ltd/<repo>`** créé ou confirmé | **À faire** — croiser [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces). |
| **Label Linear `repo`** | À aligner sur l’URL retenue ([WEA-17](https://linear.app/weadu/issue/WEA-17/charte-agents-linear-source-interdits-features-nouveaux-projets)). |

---

## 5. Code + README (WEA-83)

| Exigence | État |
|----------|------|
| Code poussé sur le dépôt cible + README run / test / deploy | **À faire** après **WEA-82** ; gabarit minimal : [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md) + [`templates/wea35-socle-minimal/`](../../templates/wea35-socle-minimal/README.md). |

---

## 6. Cutover (WEA-84)

| Exigence | État |
|----------|------|
| Prod / scheduling hors Replit **ou** ligne résiduelle justifiée dans [WEA-36 §5](./WEA-36-replit-migration-societe.md) | **Ouvert** — traité sur **WEA-84** ; fermeture Replit : [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete). |

---

_Document vivant ; création dépôt **2026-05-12** (agent socle `.github`)._
