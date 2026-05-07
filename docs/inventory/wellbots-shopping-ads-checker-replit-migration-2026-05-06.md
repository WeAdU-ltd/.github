# wellbots-shopping-ads-checker — Replit → GitHub (Repl 5, WEA-67)

**Linear** : parent [WEA-67](https://linear.app/weadu/issue/WEA-67/repl-5-wellbots-shopping-ads-checker-migration-replit-github-societe) — chaîne [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents). **Ligne inventaire** : [WEA-33](./WEA-33-replit-inventory.md) #5.

**Dépôt GitHub cible (confirmé, 2026-05-06)** : **`https://github.com/WeAdU-ltd/SH-Checker-Bids`** (privé). Les agents sur ce dépôt `.github` ne lisent pas le filesystem Replit.

---

## 1. Brief agent Replit (WEA-68)

Export Markdown **dans** le Repl : non reproductible depuis l’agent GitHub seul — [WEA-35 §7](./WEA-35-weadu-socle-v5-lab-template.md).

**Consigne** à coller dans l’agent Cursor **du** Repl : formulaire §7 [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md).

---

## 2. Synthèse (WEA-69)

| Champ | État (doc dépôt) |
|-------|------------------|
| **Inventaire WEA-33** | Ligne #5 — snapshot mars 2026 ; croiser avec export Repl quand disponible. |
| **Git cible** | `WeAdU-ltd/SH-Checker-Bids` — aligner import depuis Repl. |

---

## 3. Dépôt GitHub (WEA-70)

| Rôle | URL |
|------|-----|
| **Application** | `https://github.com/WeAdU-ltd/SH-Checker-Bids` |

---

## 4. Code + README + CI (WEA-71)

Importer le code depuis le Repl ; README + CI selon le dépôt et [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md) si besoin.

**État dépôt** : arborescence applicative sur `main` (FastAPI, `app/`, Docker, `deploy/`). **README racine** : run Docker / venv, variables nommées, lien vers ce runbook et [WEA-67](https://linear.app/weadu/issue/WEA-67/repl-5-wellbots-shopping-ads-checker-migration-replit-github-societe). **CI** : [`.github/workflows/deploy.yml`](https://github.com/WeAdU-ltd/SH-Checker-Bids/blob/main/.github/workflows/deploy.yml) sur push `main` → déploiement **EC2** (voir §5).

---

## 5. Cutover (WEA-72) — validation agent dépôt `.github` (2026-05-07)

Source : lecture API GitHub du dépôt **`WeAdU-ltd/SH-Checker-Bids`** (`README.md`, `.github/workflows/deploy.yml`).

| Question | Verdict |
|----------|---------|
| **La prod documentée** passe-t-elle par le Repl ? | **Non.** Le README décrit un déploiement **GitHub Actions → EC2** : workflow **`Deploy to EC2`** sur push vers `main` (`appleboy/ssh-action`), script distant `git pull` sous `C:/Users/Administrator/wellbots` puis **`nssm restart Wellbots`**. Secrets repo attendus : `EC2_HOST`, `EC2_SSH_KEY`. Ce chemin est **hors Replit** pour la livraison de code sur l’hôte de prod. |
| **URL publique** listée dans ce dépôt ? | **Non** dans le README relu : pas d’équivalent `*.generads.com` explicite ; la prod est décrite comme **service Windows** sur l’hôte synchronisé depuis GitHub. |
| **Replit** joue-t-il encore un rôle ? | **Résiduel possible uniquement** : l’ancien Repl peut rester ouvert tant qu’il n’est pas fermé ; ce n’est **pas** le pipeline de prod documenté ci-dessus. |
| **Parité / features** | Une réponse API dans `main.py` mentionne un connecteur Google Sheets « Replit only » — à traiter dans le dépôt applicatif si la prod EC2 doit l’équivalent. |

**Décision pour la chaîne WEA-36** : le **cutover prod** (synchronisation opérationnelle depuis **GitHub vers EC2**, pas depuis Replit comme canal documenté) est **noté fait** pour l’inventaire. **Fermeture du Repl** et suppression des secrets / URLs Replit résiduels : [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete) et travail dans **SH-Checker-Bids**.

---

## 6. Intégration visée avec Negative-Terms (hors cutover immédiat)

Objectif **moyen terme** (produit WeAdU) : faire **collaborer** [**Negative-Terms**](https://github.com/WeAdU-ltd/Negative-Terms) (`NEG`) et ce dépôt (**SH-Checker-Bids**) dans une chaîne **Google Ads** cohérente (données, checks, workflows — détails à figer dans les repos applicatifs ou un ticket produit dédié).

Ce runbook ne couvre que **Replit → GitHub + cutover** ; la conception d’intégration (contrats d’API, secrets partagés, ordre de déploiement) est **hors périmètre** migration Replit.

Voir aussi : [Repl #4 — negative-search-terms-tool](./negative-search-terms-replit-migration-2026-05-06.md) §6.

---

_Document vivant ; création : 2026-05-06 ; validation cutover §5 : 2026-05-07 ; §6 vision NEG + SH : 2026-05._
