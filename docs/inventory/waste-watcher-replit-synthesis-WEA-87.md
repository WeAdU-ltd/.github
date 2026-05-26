# Waste Watcher — synthèse inventaire / ticket à jour (WEA-87)

Document d’ancrage pour le ticket [WEA-87](https://linear.app/weadu/issue/WEA-87) dans le dépôt **`WeAdU-ltd/.github`**.

**Inventaire source** : [WEA-33 — ligne #8](./WEA-33-replit-inventory.md) (*Waste Watcher*, préfixe Repl ID `f09a27de-…`, priorité **P2**, périmètre **Société**). Chaîne migration : [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents) ([doc dépôt](./WEA-36-replit-migration-societe.md)).

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

Ceci **ne remplace pas** un export technique depuis le **Repl Waste Watcher** (stack, Git, déploiement, secrets nommés).

---

## 2. Consigne à coller vers l’agent Cursor **dans** le Repl **Waste Watcher**

Aligné [WEA-35 §7](./WEA-35-weadu-socle-v5-lab-template.md) — à exécuter **depuis le workspace Replit**, pas depuis le seul dépôt `.github`.

Produire un export structuré (**Markdown**, **aucune valeur de secret**) avec :

1. **Stack** : langage, frameworks, fichiers d’entrée (`main`, `package.json`, `requirements.txt`, etc.).
2. **Run local** : commandes exactes pour lancer en dev.
3. **Git** : remote(s) connus, branche par défaut, dernier commit court.
4. **Secrets** : liste des **noms** de variables (pas les valeurs) dans Replit Secrets.
5. **Base Replit** : oui/non ; tables ou usage si pertinent.
6. **Déploiement** : URL `.replit.app`, Always On / autoscale, charge prod vs expérimentation.
7. **Externes** : AWS/GCP/API/OAuth redirect si visible dans le code ou la config.

Après revue : soit **issue comment** sur Linear (résumé sans secrets), soit fichier miroir dans ce dépôt du type `waste-watcher-replit-export-YYYY-MM-DD.md` (même principe que [pd-detection](./pd-detection-replit-export-2026-05-12.md)).

---

## 3. Export ingéré (miroir dépôt)

| Bloc | État |
|------|------|
| Markdown produit par l’agent **dans** le Repl **Waste Watcher** | **En attente** — aucun export runtime n’a été fourni dans le fil **WEA-87** au 2026-05-26. |

---

## 4. Colonnes équivalentes [WEA-33 §3](./WEA-33-replit-inventory.md) — état après cette PR

| Colonne WEA-33 | État |
|----------------|------|
| **# / Nom / ID / Priorité / Perso-Société** | Inchangés (déjà renseignés ligne #8). |
| **URL / déploiement** | Toujours **idem** (photo Socle ~mars 2026) — pas de vérification Repl dans cette itération. |
| **Statut inventaire** | **Partiel** (inchangé tant que l’export §3 est vide). |
| **Git** | **inconnu** — à compléter après export Repl ou inventaire [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces). |
| **Replit DB / Always On / Secrets / AWS** | Inchangés sur les faits techniques ; hypothèses « probable Google Ads + kit » conservées. |
| **Notes** | **Mises à jour** : lien **WEA-87** + ce fichier ; traçabilité consolidation fil SCM ; consigne Repl §2. |

---

## 5. Écart vs critères de fait ([règle Done](https://linear.app/weadu/document/regle-agents-criteres-de-fait-avant-done-tous-projets-2b32aec9e234))

| Critère WEA-87 | État |
|----------------|------|
| Consolider la réponse de l’agent Repl **ou** lien doc dépôt / PR | **Partiel** : le fil utile est **documenté** (§1) ; la **réponse technique Repl** (stack, Git, etc.) reste **à produire** dans le Repl (§2–3). |
| Colonnes équivalentes WEA-33 mises à jour **ou** lien vers PR dépôt | **PR dépôt** : mise à jour **Notes** + intro **WEA-33** + ce fichier = preuve d’itération ; colonnes runtime **non** toutes remplies (honnêteté §4). |

**Suite** : exécuter §2 dans le Repl → ingérer l’export → mettre à jour le tableau §3 [WEA-33](./WEA-33-replit-inventory.md) (Git, URL, DB, AO, secrets noms, AWS) et ouvrir / rattacher la chaîne épique migration [WEA-36](./WEA-36-replit-migration-societe.md) quand un dépôt GitHub cible existe.

---

_Document vivant ; création : 2026-05-26 (agent dépôt `WeAdU-ltd/.github`, sans accès filesystem Replit)._

