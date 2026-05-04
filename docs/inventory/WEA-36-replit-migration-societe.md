# WEA-36 — Replit : migration par vagues (repos société, agents)

Document d’ancrage pour le ticket [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents) dans le dépôt **`WeAdU-ltd/.github`**.

**Dépendances Linear** : [WEA-33](./WEA-33-replit-inventory.md) (inventaire Replit), [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md) (template / audit socle), [WEA-15](../SECRETS_SOCLE_WEA15.md) (socle secrets). Suite : [WEA-37](https://linear.app/weadu/issue/WEA-37/replit-migration-repos-perso-isolation-acces) (perso), [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete) (fermeture Replit).

**Secrets** : aucune valeur dans ce fichier. Les noms utiles pour CI / run local sont ceux du [socle WEA-15](../SECRETS_SOCLE_WEA15.md) et de la doc du dépôt cible.

---

## 1. Objectif et critères de fait (rappel)

- Chaque Repl **interne** listé dans [WEA-33](./WEA-33-replit-inventory.md) doit avoir un **dépôt GitHub** équivalent (société : typiquement `WeAdU-ltd/…`) et une **procédure de run** documentée (local, CI, ou hébergement cible).
- Replit n’est conservé **que** tant que le cutover n’est pas fini ; tenir une **liste résiduelle** (§5).

**Périmètre WEA-36** : Repl classés **Société** ou **Société / Perso à trancher** dans WEA-33. Le Repl **pd-detection** (Finance-RH) est rappelé pour cohérence inventaire ; la migration d’isolation suit surtout [WEA-37](https://linear.app/weadu/issue/WEA-37/replit-migration-repos-perso-isolation-acces).

---

## 2. Modèle commun (template WEA-35)

Pour tout **nouveau** dépôt applicatif ou pour aligner un existant :

1. **Initialiser** depuis le socle minimal : [`templates/wea35-socle-minimal/`](../../templates/wea35-socle-minimal/README.md) et [`scripts/init_wea35_socle_template.sh`](../../scripts/init_wea35_socle_template.sh) (voir [WEA-35 §5](./WEA-35-weadu-socle-v5-lab-template.md)).
2. **Secrets** : pas de secrets dans le repo ; créer les secrets **repo** ou **org** `WeAdU-ltd` selon [WEA-15](../SECRETS_SOCLE_WEA15.md) ; label Linear **`repo`** = `WeAdU-ltd/<nom>` pour les tickets agents ([WEA-17](../CHARTE_AGENTS_LINEAR_WEA17.md)).
3. **Run documenté** (minimum) : dans le `README` du dépôt cible — prérequis (runtime, `LINEAR_API_KEY` si besoin, secrets nommés), commande(s) `dev` / `test` / `deploy`, et **où** s’exécute la charge de prod (GitHub Actions, EC2, autre) si ce n’est pas Replit.

---

## 3. Vagues et tableau Repl → GitHub → procédure de run

Les **priorités P0–P3** reprennent [WEA-33](./WEA-33-replit-inventory.md). Les URLs GitHub « connues dans la doc dépôt » sont indiquées ; le reste est **à confirmer** via inventaire GitHub ([WEA-12](./WEA-12-github-linear.md)) ou création de dépôt sous `WeAdU-ltd`.

| Vague | # WEA-33 | Repl (nom) | Dépôt GitHub cible (équivalent) | Procédure de run (référence) |
|-------|----------|------------|----------------------------------|------------------------------|
| **P0** | 1 | Weadu-Socle-V5-Lab | `WeAdU-ltd/.github` | Doc + scripts d’inventaire Linear/GitHub dans ce dépôt ; plus de run « prod » Replit requis — [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md). |
| **P0** | 2 | Chief of Staff Virtuel IA (COS) | **à confirmer** (code déployé **EC2**, pas Replit — voir WEA-33 / [WEA-29](./WEA-29-aws-ec2-inventory.md)) | Runbook hébergement : serveur Windows / Caddy / tâches planifiées sur l’instance documentée côté infra ; secrets hors Repl ([WEA-15](../SECRETS_SOCLE_WEA15.md)). |
| **P1** | 3 | after-framfield-cockpit | **à trancher** Perso vs Société puis `WeAdU-ltd/…` ou compte perso | Après arbitrage : README du dépôt + redirect OAuth selon [WEA-20](../GOOGLE_OAUTH_WEA20.md). |
| **P1** | 4 | negative-search-terms-tool | `WeAdU-ltd/Negative-Terms` | README / workflows du dépôt ; migration cutover = développement sur GitHub + désactivation du Repl quand la prod ne dépend plus de Replit. |
| **P1** | 5 | wellbots-shopping-ads-checker | `WeAdU-ltd/SH-Checker-Bids` | Idem : README du dépôt + CI. |
| **P2** | 6–15, 17–20 | WeAdU LeadGen, Max Conv Val Budget Mngt, Waste Watcher, Automatic Google Ads…, Wellbots real-time figures, suspended accounts clean up, Dashboard — Carmino & monPL, Recommandations mngt, Ads Performance Analyze, Feed Optimizer, bad performers, Dashboard — Epic Extender, Bad Performer labels, Test tracker | **à créer ou à confirmer** (`WeAdU-ltd/<slug>`) — non listés dans le snapshot partiel [github-org-repo-snapshot-2026-05-02.json](./github-org-repo-snapshot-2026-05-02.json) | Pour chaque ligne : créer le repo (template WEA-35), pousser le code exporté depuis Replit, documenter run local + prod dans le README ; croiser AWS si applicable ([WEA-29](./WEA-29-aws-ec2-inventory.md)). |
| **RH / iso** | 15 | pd-detection | **à confirmer** — périmètre [WEA-37](https://linear.app/weadu/issue/WEA-37/replit-migration-repos-perso-isolation-acces) / secrets isolés | Documenter run + isolation Finance-RH selon [WEA-13](./WEA-13-github-access-model.md). |
| **Décision** | 21 | Divers | Archivage ou repo dédié **à décider** | Pas de run prod tant que le statut n’est pas tranché. |

**Note.** Les dépôts `WeAdU-ltd/Negative-Terms` et `WeAdU-ltd/SH-Checker-Bids` sont les équivalents documentaires **probables** pour les Repls #4 et #5 (noms d’époque Replit). En cas de divergence (fork historique, rename), mettre à jour la colonne « Dépôt GitHub » après vérification dans l’onglet Git du Repl ou l’historique GitHub.

---

## 4. Ordre d’exécution recommandé (agents)

1. **Geler** la vérité GitHub : PAT org avec liste complète des repos `WeAdU-ltd` ([WEA-12](./WEA-12-github-linear.md)) ; compléter les lignes « à confirmer » du tableau §3.
2. **P0** : traiter Socle (déjà ancré sur `.github`) et COS (runbook EC2, pas replication Replit).
3. **P1** : basculer **negative-search-terms-tool** et **wellbots-shopping-ads-checker** vers les dépôts connus ; trancher **after-framfield-cockpit**.
4. **P2 / P3** : une vague par famille (Google Ads outillage, dashboards, etc.) — même PR socle (`AGENTS.md`, CI gitleaks) puis import code + README run.
5. Ouvrir ou mettre à jour les sous-labels Linear **`repo`** pour chaque dépôt stabilisé.

---

## 5. Liste résiduelle Replit (cutover non fini)

| Repl (# WEA-33) | Raison résiduelle | Action pour fermer |
|-----------------|-------------------|---------------------|
| _À remplir au fil de la migration_ | ex. prod encore sur `.replit.app` | Basculer DNS / secrets vers GitHub ou hébergement cible ; puis retirer la ligne |

Mettre à jour ce tableau quand un Repl n’a plus de déploiement actif ni secret métier unique côté Replit.

---

## 6. Écart vs critères de fait ([règle Done](https://linear.app/weadu/document/regle-agents-criteres-de-fait-avant-done-tous-projets-2b32aec9e234))

| Critère | État | Détail |
|---------|------|--------|
| Tous les Repls WEA-33 ont un dépôt GitHub **équivalent** documenté | **Partiel** | Équivalences **explicites** pour : Socle → `.github`, inventaire probable Negative-Terms / SH-Checker-Bids. Le reste est **à confirmer ou à créer** sous `WeAdU-ltd` (voir §3). |
| Procédure de run documentée pour chacun | **Partiel** | Modèle §2 + références pour P0/P1 ; README à exiger pour chaque nouveau repo P2/P3. |
| Replit uniquement si cutover non fini | **À suivre** | Liste résiduelle §5 ; tenir à jour jusqu’à [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete). |

**Suite pour un Done strict** : compléter le tableau §3 avec les **URLs réelles** (`https://github.com/WeAdU-ltd/…`) pour les 21 lignes (ou décision d’archivage), et ajouter dans chaque dépôt un **README** de run minimal ; vider la liste résiduelle §5 ou justifier chaque ligne restante.

---

_Document vivant ; première intégration dépôt : 2026-05-04._
