# Waste Watcher — synthèse inventaire / ticket à jour (WEA-87)

Document d’ancrage pour le ticket [WEA-87](https://linear.app/weadu/issue/WEA-87) dans le dépôt **`WeAdU-ltd/.github`**.

**Inventaire source** : [WEA-33 — ligne #8](./WEA-33-replit-inventory.md) (*Waste Watcher*, préfixe Repl ID `f09a27de-…`, priorité **P2**, périmètre **Société**). **Nom UI / URL Repl (2026-05-26)** : *Waste Controller* — `waste-controller.replit.app`. Chaîne migration : [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents) ([doc dépôt](./WEA-36-replit-migration-societe.md)).

**Secrets** : aucune valeur dans ce fichier — [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh).

---

## 1. Consolidation du fil Linear (agent Cursor Cloud / Repl)

Les messages visibles sur **WEA-87** au **2026-05-26** montrent surtout des tentatives d’attachement du ticket au dépôt **`WeAdU-ltd/.github`** : l’agent signalait *« Could not find repository WeAdU-ltd/.github in any of your connected SCM providers »* tant que le **fournisseur SCM** de la session Cloud n’était pas aligné avec l’URL complète ou le label groupe **`repo`** (`WeAdU-ltd/.github`).

**Consolidation opérationnelle (sans secrets)** :

| Sujet | Verdict documenté |
|-------|-------------------|
| URL canonique du dépôt inventaire / procédures | `https://github.com/WeAdU-ltd/.github` (clone : `.git` suffixe optionnel). |
| Cause des boucles « repo introuvable » | Session **Cursor Cloud** sans accès SCM au dépôt cible — pas une absence du repo GitHub côté org. |
| Action côté configuration | Vérifier connexion GitHub + label **`repo`** = `WeAdU-ltd/.github` sur le ticket ([WEA-17](../CHARTE_AGENTS_LINEAR_WEA17.md)). |

---

## 2. Consigne à coller vers l’agent Cursor **dans** le Repl (Waste Watcher / Waste Controller)

Aligné [WEA-35 §7](./WEA-35-weadu-socle-v5-lab-template.md) — exécutée **2026-05-26** ; résultat : [`waste-watcher-replit-export-2026-05-26.md`](./waste-watcher-replit-export-2026-05-26.md).

---

## 3. Export ingéré (miroir dépôt)

| Bloc | État |
|------|------|
| Markdown produit par l’agent **dans** le Repl | **Ingéré** (**2026-05-26**) — [`waste-watcher-replit-export-2026-05-26.md`](./waste-watcher-replit-export-2026-05-26.md). **Source unique** pour stack, Git, DB, déploiement, secrets **noms**, externes. |

---

## 4. Colonnes équivalentes [WEA-33 §3](./WEA-33-replit-inventory.md) — état après export

| Colonne WEA-33 | État |
|----------------|------|
| **# / Nom / ID / Priorité / Perso-Société** | Ligne **#8** *Waste Watcher* ; nom UI **Waste Controller** documenté dans l’export. |
| **URL / déploiement** | `waste-controller.replit.app` ; **Autoscale** (pas Always On) — [export § Déploiement](./waste-watcher-replit-export-2026-05-26.md). |
| **Statut inventaire** | **Partiel** (GitHub org **absent** ; prod encore sur Replit). |
| **Git** | **Pas de remote GitHub** ; `gitsafe-backup` + `subrepl-*` ; branche `master` ; commit `0f35522` — [export § Git](./waste-watcher-replit-export-2026-05-26.md). |
| **Replit DB** | **Oui** (PG 16) — `api_cache`, `client_settings`. |
| **Always On** | **Non** (autoscale). |
| **Secrets (noms)** | 7 variables — [export § Secrets](./waste-watcher-replit-export-2026-05-26.md). |
| **AWS** | **Non** (export § Externes). |
| **Notes** | WEA-87 + ce fichier + export **2026-05-26**. |

---

## 5. Écart vs critères de fait ([règle Done](https://linear.app/weadu/document/regle-agents-criteres-de-fait-avant-done-tous-projets-2b32aec9e234))

| Critère WEA-87 | État |
|----------------|------|
| Consolider la réponse de l’agent Repl **ou** lien doc dépôt / PR | **Fait** : export [`waste-watcher-replit-export-2026-05-26.md`](./waste-watcher-replit-export-2026-05-26.md) + synthèse ici. |
| Colonnes équivalentes WEA-33 mises à jour **ou** lien vers PR dépôt | **Fait** : tableau §3 [WEA-33](./WEA-33-replit-inventory.md) ligne **#8** aligné sur l’export (sauf équivalent `WeAdU-ltd/<repo>` — **à créer** en migration [WEA-36](./WEA-36-replit-migration-societe.md)). |

**Suite (hors WEA-87 strict)** : créer dépôt `WeAdU-ltd/<slug>` (ex. `waste-controller`), pousser le code, CI + README ; cutover prod ou ligne résiduelle Replit ; [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete).

---

_Document vivant ; création : 2026-05-26 ; export Repl ingéré : **2026-05-26**._

