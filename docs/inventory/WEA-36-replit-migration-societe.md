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

### 2.1 Linear : un parent par Repl, sous-tickets ordonnés

- **Génération** (ré-exécutable, idempotent par ligne `[Repl N]` dans le titre du parent) : [`scripts/linear_create_wea36_repl_issues.py`](../../scripts/linear_create_wea36_repl_issues.py). Prérequis : `LINEAR_API_KEY`. Dry-run par défaut ; `python3 scripts/linear_create_wea36_repl_issues.py --apply` pour créer les issues sur l’équipe **WEA**, projet **Autonomie agents**.

- **Par Repl** : un ticket **parent** `[Repl N] <nom> — migration Replit → GitHub` et **cinq sous-tickets** (ordre logique, chaque étape **bloque** la suivante) :
  1. **Brief agent Replit** — interroger l’agent Cursor du Repl pour la vérité projet (Socle ne suffit pas). **Ne pas** formuler cela comme des actions *merge PR* ou *coller dans Replit* pour le référent : exécution **dans** le Repl (session avec workspace), consigne canonique [WEA-35 §7](./WEA-35-weadu-socle-v5-lab-template.md) ; PR sur `.github` = **auto-merge** après CI ([`AGENTS.md`](../../AGENTS.md) *Zéro friction référent*).
  2. **Synthèse** — inventaire / ticket à jour.
  3. **Dépôt GitHub** créé ou confirmé (`WeAdU-ltd/…`).
  4. **Code + README** procédure de run.
  5. **Cutover** — prod hors Replit + résiduel.

- **WEA-36** : le sous-ticket **cutover** de chaque Repl **bloque** [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents) (relation Linear `blocks`). Ainsi **WEA-36** ne peut être terminé que lorsque **tous** les cutovers sont faits (ou après retrait manuel des relations si une ligne est abandonnée).

- **Commentaires Linear (preuves, exports agent)** : les agents postent via [`scripts/linear_issue_comment.py`](../../scripts/linear_issue_comment.py) (stdin ou `--file`) — **ne pas** demander à l’humain de coller dans l’UI. Exemple miroir dépôt (Repl 1, sans IP) : [`WEA-36-export-repl-01-weadu-socle-v5-lab.md`](./WEA-36-export-repl-01-weadu-socle-v5-lab.md).

---

## 3. Vagues et tableau Repl → GitHub → procédure de run

Les **priorités P0–P3** reprennent [WEA-33](./WEA-33-replit-inventory.md). Les URLs GitHub « connues dans la doc dépôt » sont indiquées ; le reste est **à confirmer** via inventaire GitHub ([WEA-12](./WEA-12-github-linear.md)) ou création de dépôt sous `WeAdU-ltd`.

| Vague | # WEA-33 | Repl (nom) | Dépôt GitHub cible (équivalent) | Procédure de run (référence) |
|-------|----------|------------|----------------------------------|------------------------------|
| **P0** | 1 | Weadu-Socle-V5-Lab | `WeAdU-ltd/.github` | Doc + scripts d’inventaire Linear/GitHub dans ce dépôt ; plus de run « prod » Replit requis — [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md). |
| **P0** | 2 | Chief of Staff Virtuel IA (COS) | **`https://github.com/WeAdU-ltd/cos`** (privé) — runbook : [`cos-replit-ec2-migration-2026-05-04.md`](./cos-replit-ec2-migration-2026-05-04.md) ; **import initial du code** (**2026-05-08**, script [`cos_push_from_windows.ps1`](../../scripts/cos_push_from_windows.ps1)) ; **Repl Replit COS fermé** (**2026-05**) | Runbook : Windows / Caddy / tâches `WeAdU-COS` — [WEA-29](./WEA-29-aws-ec2-inventory.md) §3 ; OIDC/SSM — [`AWS_GITHUB_OIDC_SSM.md`](../AWS_GITHUB_OIDC_SSM.md) ; secrets hors Repl ([WEA-15](../SECRETS_SOCLE_WEA15.md)). |
| **P1** | 3 | after-framfield-cockpit | **`JeffWeadu/after-framfield-cockpit`** (perso) — Repl **supprimé** sur Replit (**2026-05-05**) ; prod = **Google Sheet** + accès API via secrets GitHub | GitHub Actions smoke Sheets + README sur `main` ; OAuth côté Google Cloud / compte de service — [WEA-20](../GOOGLE_OAUTH_WEA20.md) ; runbook [`after-framfield-cockpit-replit-2026-05-05.md`](./after-framfield-cockpit-replit-2026-05-05.md). |
| **P1** | 4 | negative-search-terms-tool | `WeAdU-ltd/Negative-Terms` | README / workflows du dépôt ; migration cutover = développement sur GitHub + désactivation du Repl quand la prod ne dépend plus de Replit. |
| **P1** | 5 | wellbots-shopping-ads-checker | `WeAdU-ltd/SH-Checker-Bids` — **chaîne migration terminée** (**2026-05**, confirmé équipe) | README + CI ; **prod** : GitHub Actions → **EC2 Windows** — [runbook Repl #5](./wellbots-shopping-ads-checker-replit-migration-2026-05-06.md) §5 ; parent Linear [WEA-67](https://linear.app/weadu/issue/WEA-67/repl-5-wellbots-shopping-ads-checker-migration-replit-github-societe). |
| **P2** | 6–10, 12–14, 16–20 | WeAdU LeadGen, Max Conv Val Budget Mngt, Waste Watcher, Automatic Google Ads…, Wellbots real-time figures, Dashboard — Carmino & monPL, Recommandations mngt, Ads Performance Analyze, Feed Optimizer, bad performers, Dashboard — Epic Extender, Bad Performer labels, Test tracker | **à créer ou à confirmer** (`WeAdU-ltd/<slug>`) — non listés dans le snapshot partiel [github-org-repo-snapshot-2026-05-02.json](./github-org-repo-snapshot-2026-05-02.json) | Pour chaque ligne : créer le repo (template WEA-35), pousser le code exporté depuis Replit, documenter run local + prod dans le README ; croiser AWS si applicable ([WEA-29](./WEA-29-aws-ec2-inventory.md)). *(Repl **#15 pd-detection** est traité à part — ligne **RH / iso**, dépôt perso documenté.)* |
| **RH / iso** | 15 | pd-detection | **`https://github.com/JeffWeadu/pd-detection`** (privé, perso) — **confirmé** (**2026-05-11**) ; pas sous `WeAdU-ltd/` à ce stade ([WEA-37](https://linear.app/weadu/issue/WEA-37/replit-migration-repos-perso-isolation-acces)) | Documenter run + isolation Finance-RH selon [WEA-13](./WEA-13-github-access-model.md). Runbook [pd-detection](./pd-detection-replit-migration-WEA-128.md) — [WEA-128](https://linear.app/weadu/issue/WEA-128/pd-detection-brief-agent-replit-infos-migration) · [WEA-129](https://linear.app/weadu/issue/WEA-129/pd-detection-synthese-inventaire-ticket-a-jour) · [WEA-130](https://linear.app/weadu/issue/WEA-130). |
| **Décision** | 21 | Divers | Archivage ou repo dédié **à décider** | Pas de run prod tant que le statut n’est pas tranché. |

**Note — Repl #17 (Feed Optimizer).** Export agent Repl **2026-05-12** : [`feed-optimizer-replit-export-2026-05-12.md`](./feed-optimizer-replit-export-2026-05-12.md) ; dépôt applicatif **privé** actuel : [`JeffWeadu/feed-optimizer`](https://github.com/JeffWeadu/feed-optimizer) — chaîne Linear [WEA-139](https://linear.app/weadu/issue/WEA-139/repl-17-feed-optimizer-migration-replit-github-societe) ; runbook [`feed-optimizer-replit-migration-WEA-139.md`](./feed-optimizer-replit-migration-WEA-139.md). **Trancher** alignement org **WeAdU-ltd** vs maintien perso + isolation ([WEA-13](./WEA-13-github-access-model.md), [WEA-37](https://linear.app/weadu/issue/WEA-37/replit-migration-repos-perso-isolation-acces)) sur **WEA-142**.

**Note.** Les dépôts `WeAdU-ltd/Negative-Terms` et `WeAdU-ltd/SH-Checker-Bids` sont les équivalents **confirmés** pour les Repls #4 et #5 (vérification API GitHub **2026-05-06** ; runbooks : [Repl #4](./negative-search-terms-replit-migration-2026-05-06.md), [Repl #5](./wellbots-shopping-ads-checker-replit-migration-2026-05-06.md)). En cas de divergence, mettre à jour le tableau §3 après vérification dans l’onglet Git du Repl.

**Hors vague WEA-36 (Linear).** Le Repl **#11 — suspended accounts clean up** reste dans [WEA-33](./WEA-33-replit-inventory.md) pour l’historique Socle, mais **n’a plus d’épique** `[Repl 11] …` sur Linear (suppression **2026-05-05**) : pas de chaîne migration GitHub associée ; le script [`linear_create_wea36_repl_issues.py`](../../scripts/linear_create_wea36_repl_issues.py) **ne doit pas** recréer ce parent.

---

## 4. Ordre d’exécution recommandé (agents)

1. **Geler** la vérité GitHub : PAT org avec liste complète des repos `WeAdU-ltd` ([WEA-12](./WEA-12-github-linear.md)) ; compléter les lignes « à confirmer » du tableau §3.
2. **P0** : traiter Socle (déjà ancré sur `.github`) et COS (**Repl fermé**, code sur GitHub — [`cos`](https://github.com/WeAdU-ltd/cos)) ; rotation secrets Replit résiduels si besoin ([WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete)).
3. **P1** : **Negative-Terms** — prod validée sur **AWS** ([runbook Repl #4](./negative-search-terms-replit-migration-2026-05-06.md) §5) ; résiduel doc optionnel. **SH-Checker-Bids** — **migration chaîne terminée** (**2026-05**) ; ligne **#5** retirée du tableau résiduel ci-dessous (paragraphe **Historique — Repl #5**). Suite optionnelle : **Repl** / secrets Replit ([WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete)). Vision **moyen terme** : **NEG + SH-Checker** (§6 runbooks Repl #4 / #5). **after-framfield-cockpit** → fait ([runbook](./after-framfield-cockpit-replit-2026-05-05.md)).
4. **P2 / P3** : une vague par famille (Google Ads outillage, dashboards, etc.) — même PR socle (`AGENTS.md`, CI gitleaks) puis import code + README run.
5. Ouvrir ou mettre à jour les sous-labels Linear **`repo`** pour chaque dépôt stabilisé.

---

## 5. Liste résiduelle Replit (cutover non fini)

| Repl (# WEA-33) | Raison résiduelle | Action pour fermer |
|-----------------|-------------------|---------------------|
| **1 — Weadu-Socle-V5-Lab** | Le **hub doc + scripts** est basculé sur `WeAdU-ltd/.github` ([runbook](./weadu-socle-v5-lab-github-migration.md)) ; en revanche le snapshot agent Repl (**2026-05-04**) documente encore une **charge applicative** (FastAPI, AI Council Socket Mode, tâches planifiées, push secrets vers EC2, etc.) sur le Repl tant que cette charge n’est pas hébergée ailleurs ou arrêtée. | Migrer ou éteindre les workloads décrits dans [`weadu-socle-v5-lab-replit-snapshot-2026-05-04.md`](./weadu-socle-v5-lab-replit-snapshot-2026-05-04.md) ; retirer / faire tourner les secrets Replit concernés ; puis retirer cette ligne (voir [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete)). |
| **15 — pd-detection** | Cutover ouvert ([WEA-132](https://linear.app/weadu/issue/WEA-132)) ; export agent Repl : [`pd-detection-replit-export-2026-05-12.md`](./pd-detection-replit-export-2026-05-12.md) (**2026-05-12**). | Overlay gabarit si besoin ; basculer prod hors `.replit.app` ; secrets hors Replit ; clôturer [WEA-132](https://linear.app/weadu/issue/WEA-132). |
| _Autres_ | _À remplir au fil de la migration_ | Basculer DNS / secrets vers GitHub ou hébergement cible ; puis retirer la ligne |

**Historique — Repl #5 (wellbots-shopping-ads-checker / SH-Checker-Bids).** La **chaîne migration Replit → GitHub** pour [**`WeAdU-ltd/SH-Checker-Bids`**](https://github.com/WeAdU-ltd/SH-Checker-Bids) est **terminée** (**2026-05**, confirmé équipe) — cutover prod **GitHub → EC2** : [runbook](./wellbots-shopping-ads-checker-replit-migration-2026-05-06.md) §5 ; parent [WEA-67](https://linear.app/weadu/issue/WEA-67/repl-5-wellbots-shopping-ads-checker-migration-replit-github-societe). La ligne **#5** n’apparaît plus dans le tableau résiduel. Suite **optionnelle** : fermeture du Repl Replit et ménage des secrets / références dans le dépôt ou le vault ([WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete)).

**Historique — Repl #4 fermé.** Le Repl **negative-search-terms-tool** / projet **`negative-terms.replit.app`** a été **supprimé côté Replit** ; la ligne **#4** n’est plus dans le tableau ci-dessus. **Doc / code applicatif :** PR [**#704**](https://github.com/WeAdU-ltd/Negative-Terms/pull/704) sur [`WeAdU-ltd/Negative-Terms`](https://github.com/WeAdU-ltd/Negative-Terms) (NEG-220, README, workflows smoke, E2E exemples, `pull_from_replit.py`, etc.). **Optionnel :** vérifier les **secrets / variables GitHub** `E2E_BASE_URL` / `STAGING_E2E_BASE_URL` vers **`https://staging-negative-terms.generads.com`** si l’ancien host y traîne encore ; **`replit.md`** — mise à jour manuelle si besoin (gouvernance [`AGENTS.md`](../../AGENTS.md)), sans toucher au vault 1Password « Replit » (nom de coffre, pas la plateforme). Détail : [negative-search-terms-replit-migration-2026-05-06.md](./negative-search-terms-replit-migration-2026-05-06.md) §5.

**Historique — Repl #2 (COS).** Le **Repl Replit COS** a été **fermé** (**2026-05**, confirmé équipe) ; la ligne **#2** n’apparaît plus dans le tableau résiduel. Suite : **README** / **CI** dans **`WeAdU-ltd/cos`** si besoin ; rotation des secrets Replit encore référencés ([WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete)).

**Note — COS (infra).** L’**accès agents / GitHub Actions** à l’hôte Windows via **SSM** (OIDC, **`mi-08ba03ce367298b11`**) reste documenté dans [`cos-replit-ec2-migration-2026-05-04.md`](./cos-replit-ec2-migration-2026-05-04.md) §2.1 et [`AWS_GITHUB_OIDC_SSM.md`](../AWS_GITHUB_OIDC_SSM.md).

Mettre à jour ce tableau quand un Repl n’a plus de déploiement actif ni secret métier unique côté Replit.

---

## 6. Écart vs critères de fait ([règle Done](https://linear.app/weadu/document/regle-agents-criteres-de-fait-avant-done-tous-projets-2b32aec9e234))

| Critère | État | Détail |
|---------|------|--------|
| Tous les Repls WEA-33 ont un dépôt GitHub **équivalent** documenté | **Partiel** | Équivalences **explicites** pour : Socle → `.github`, **COS → `WeAdU-ltd/cos`**, Negative-Terms, SH-Checker-Bids, **pd-detection → [`JeffWeadu/pd-detection`](https://github.com/JeffWeadu/pd-detection)** (perso, Finance-RH). Le reste sous `WeAdU-ltd` est **à confirmer ou à créer** (voir §3). |
| Procédure de run documentée pour chacun | **Partiel** | Modèle §2 + références pour P0/P1 ; README à exiger pour chaque nouveau repo P2/P3. |
| Replit uniquement si cutover non fini | **À suivre** | Liste résiduelle §5 ; tenir à jour jusqu’à [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete). |

**Suite pour un Done strict** : compléter le tableau §3 avec les **URLs réelles** (`https://github.com/WeAdU-ltd/…`) pour les 21 lignes (ou décision d’archivage), et ajouter dans chaque dépôt un **README** de run minimal ; vider la liste résiduelle §5 ou justifier chaque ligne restante.

---

_Document vivant ; première intégration dépôt : 2026-05-04._
