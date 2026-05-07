# negative-search-terms-tool — Replit → GitHub (Repl 4, WEA-61)

**Linear** : parent [WEA-61](https://linear.app/weadu/issue/WEA-61/repl-4-negative-search-terms-tool-migration-replit-github-societe) — chaîne [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents). **Ligne inventaire** : [WEA-33](./WEA-33-replit-inventory.md) #4.

**Dépôt GitHub cible (confirmé, 2026-05-06)** : **`https://github.com/WeAdU-ltd/Negative-Terms`** (privé). Les agents sur ce dépôt `.github` ne lisent pas le filesystem Replit.

---

## 1. Brief agent Replit (WEA-62)

Export Markdown **dans** le Repl : non reproductible depuis l’agent GitHub seul — même logique que [WEA-35 §7](./WEA-35-weadu-socle-v5-lab-template.md).

**Consigne** à coller dans l’agent Cursor **du** Repl : formulaire §7 [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md) (stack, run, Git, secrets **noms**, DB, déploiement, externes).

---

## 2. Synthèse (WEA-63)

| Champ | État (doc dépôt) |
|-------|------------------|
| **Inventaire WEA-33** | Ligne #4 — snapshot mars 2026 ; croiser avec export Repl quand disponible. |
| **Git cible** | `WeAdU-ltd/Negative-Terms` — aligner `git remote` du Repl ou import zip vers ce repo. |

---

## 3. Dépôt GitHub (WEA-64)

| Rôle | URL |
|------|-----|
| **Application** | `https://github.com/WeAdU-ltd/Negative-Terms` |

---

## 4. Code + README + CI (WEA-65)

Importer le code depuis le Repl ; README run + CI selon le dépôt cible et [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md) si besoin.

**État dépôt** : base applicative sur `main`, CI GitHub, déploiements AWS documentés (voir README du dépôt applicatif).

---

## 5. Cutover (WEA-66) — validation agent dépôt `.github` (2026-05-06)

Source : lecture API GitHub du dépôt **`WeAdU-ltd/Negative-Terms`** (`README.md`, `docs/STAGING_AND_E2E_BASE_URL_NEG220.md`, `docs/STAGING_WORKFLOW.md`, `.github/workflows/deploy-aws.yml`, `staging-url-smoke.yml`, `scripts/pull_from_replit.py`).

| Question | Verdict |
|----------|---------|
| **Production** dépend-elle du Repl pour servir le site public ? | **Non.** Prod documentée : `https://negative-terms.generads.com` ; mise à jour **Promote production (AWS)** depuis GitHub (NEG-232 / NEG-228). |
| **Staging principal** est-il sur AWS ? | **Oui.** `https://staging-negative-terms.generads.com` — alimenté par **Main push CI** (`main`) et workflow **Deploy to AWS staging** (branche `staging`). |
| **Replit** joue-t-il encore un rôle ? | **Optionnel / résiduel uniquement** : `https://negative-terms.replit.app` reste dans la doc applicative comme origine **staging / E2E** et valeur canonique suggérée pour `E2E_BASE_URL` — **hors pipeline AWS** (sync manuelle depuis le workspace Replit). Ce n’est **pas** la prod. |
| **`pull_from_replit.py`** | Marqué **DEPRECATED / obsolete** dans le dépôt — ne pas utiliser comme chemin opérationnel. |

**Décision pour la chaîne WEA-36** : le **cutover prod** (clients → AWS, pas Replit) est **assumé fait** au sens inventaire. Ce qui peut rester ouvert est uniquement la **fermeture du Repl** ou le **repointage doc** de `E2E_BASE_URL` vers le staging AWS si l’équipe veut **zéro URL Replit** dans les docs applicatives — travail dans le dépôt **Negative-Terms**, pas arbitrage par l’humain sur ce ticket.

---

## 6. Intégration visée avec SH-Checker-Bids (hors cutover immédiat)

Objectif **moyen terme** : articuler **Negative-Terms** et [**SH-Checker-Bids**](https://github.com/WeAdU-ltd/SH-Checker-Bids) comme **outillage commun** Google Ads (flux de données, contrôles complémentaires). À traiter dans les dépôts applicatifs ou un ticket Linear produit ; **pas** dans ce runbook de migration Replit.

Voir : [Repl #5 — wellbots-shopping-ads-checker](./wellbots-shopping-ads-checker-replit-migration-2026-05-06.md) §6.

---

_Document vivant ; création : 2026-05-06 ; validation cutover : 2026-05-06 ; §6 vision NEG + SH : 2026-05._
