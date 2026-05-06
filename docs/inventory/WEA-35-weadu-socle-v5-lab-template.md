# WEA-35 — Weadu-Socle-V5-Lab : audit → template GitHub + Cursor

Document d’ancrage pour le ticket [WEA-35](https://linear.app/weadu/issue/WEA-35/weadu-socle-v5-lab-audit-template-github-cursor) dans le dépôt **`WeAdU-ltd/.github`**.

**Dépendances Linear** : [WEA-33](https://linear.app/weadu/issue/WEA-33/replit-inventaire-15-projets-et-dependances) (inventaire Replit), [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh) (socle secrets). Chaîne : WEA-33 → **WEA-35** → [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents) ([doc dépôt](./WEA-36-replit-migration-societe.md)) → [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete).

**Liens source (Replit, hors dépôt)** : [Weadu-Socle-V5-Lab sur Replit](https://replit.com/t/fabio-herizo-jeff/repls/Weadu-Socle-V5-Lab), [weadu-socle-v-5-lab.replit.app](https://weadu-socle-v-5-lab.replit.app).

**Secrets** : aucune valeur dans ce fichier. Les jetons et mots de passe restent dans le [socle secrets WEA-15](../SECRETS_SOCLE_WEA15.md), GitHub Encrypted Secrets, Cursor, 1Password — pas dans un dépôt d’application.

---

## 1. Rôle historique du Repl « Socle » (audit fonctionnel)

D’après l’inventaire [WEA-33](./WEA-33-replit-inventory.md) (export Socle V5.1, **2026-03-29**), **Weadu-Socle-V5-Lab** servait de **hub** sur Replit : orchestration, documentation des secrets (noms), ponts vers **AWS** (SSH EC2, DynamoDB), **Slack**, **base PostgreSQL managée Replit**, inventaire des autres Repls. Ce dépôt **`.github`** reprend déjà la **vérité documentaire** et une partie des **scripts** (inventaires, smokes, Linear) : le Repl n’est plus la source unique ni la plus à jour pour les conventions agents.

**Limite** : sans ouvrir le Repl, le détail exact de chaque script ou fichier du Socle Replit n’est pas reproduit ici ; l’audit ci-dessous est **décisionnel** (que garder sous Git vs ce qu’on abandonne côté Replit comme socle).

---

## 2. Critères de fait (ticket WEA-35)

| Critère | État | Preuve / suite |
|---------|------|----------------|
| Dépôt template (ou doc) GitHub avec conventions + scripts d’init | **Fait (doc + arbre minimal dans ce dépôt)** | Ce fichier ; dossier [`templates/wea35-socle-minimal/`](../../templates/wea35-socle-minimal/README.md) ; script [`scripts/init_wea35_socle_template.sh`](../../scripts/init_wea35_socle_template.sh) |
| Liste abandonné vs repris | **Fait** | §3 et §4 ci-dessous |

---

## 3. Abandonné (Replit Socle / V5-Lab) — ne pas recréer tel quel sur GitHub

| Sujet | Détail |
|-------|--------|
| **Socle « vivant » sur Replit** | Hub unique dans un Repl (Always On inconnu, secrets dans l’UI Replit, déploiement `.replit.app` non stable au snapshot WEA-33). La **cible** est GitHub + Cursor + secrets org ([WEA-15](../SECRETS_SOCLE_WEA15.md)). |
| **PostgreSQL managé Replit** | Données et connexion liées au Repl ; ne pas en faire le socle d’un nouveau projet app. Pour les apps : Postgres géré ailleurs (RDS, Neon, etc.) selon le projet. |
| **Couplage SSH / DynamoDB / stacks** documentés côté Socle | Restent des **projets d’infra** (EC2 COS, etc.) ; pas dupliqués dans le template minimal agent. Inventaires : [WEA-29](./WEA-29-aws-ec2-inventory.md), scripts `scripts/aws_inventory_wea29.py`, etc. |
| **Secrets dans le Repl** | Abandonné comme **canal de référence** ; migration vers GitHub / Cursor / 1Password selon WEA-15. |
| **Runtime unique Replit** | Pas d’équivalent obligatoire ; les agents utilisent Cursor Cloud, Actions, poste local, ou le runtime du dépôt d’app. |

---

## 4. Repris — où le trouver (GitHub + Cursor)

| Capacité (vue Socle) | Remplacement documentaire / technique |
|----------------------|--------------------------------------|
| **Règles agents, critères Done, Linear API** | [`AGENTS.md`](../../AGENTS.md), [`docs/CHARTE_AGENTS_LINEAR_WEA17.md`](../CHARTE_AGENTS_LINEAR_WEA17.md), scripts `scripts/linear_*.py` |
| **Socle secrets, noms canoniques** | [`docs/SECRETS_SOCLE_WEA15.md`](../SECRETS_SOCLE_WEA15.md), [`docs/SECRETS_CARTOGRAPHIE_WEA14.md`](../SECRETS_CARTOGRAPHIE_WEA14.md) |
| **Label `repo` Cursor / bon dépôt** | Charte [WEA-17](../CHARTE_AGENTS_LINEAR_WEA17.md) § *Règle Cursor* |
| **Hooks Cursor valides** | [`templates/wea35-socle-minimal/.cursor/hooks.json`](../../templates/wea35-socle-minimal/.cursor/hooks.json) (copie dans le repo d’app) ; rappel dans [`README.md`](../../README.md) § *Cursor hooks* |
| **Anti-secrets en CI** | [`/.github/workflows/ci.yml`](../../.github/workflows/ci.yml) (gitleaks), [`/.pre-commit-config.yaml`](../../.pre-commit-config.yaml) ; pour un **nouveau** dépôt app : réutiliser le même motif ou appeler un workflow réutilisable org |
| **Inventaires Replit / migration** | [WEA-33](./WEA-33-replit-inventory.md), puis [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents) |

---

## 5. Template minimal — utilisation

1. **Arbre de référence** (fichiers à la racine d’un nouveau dépôt ou à fusionner avec un existant) : [`templates/wea35-socle-minimal/`](../../templates/wea35-socle-minimal/README.md).
2. **Depuis un clone de `WeAdU-ltd/.github`** :  
   `bash scripts/init_wea35_socle_template.sh /chemin/vers/nouveau-repo`  
   (`--dry-run` puis `--force` si vous acceptez d’écraser des fichiers déjà présents — voir `--help` du script).
3. **Dépôt GitHub dédié « Template repository » (optionnel)** : créer un repo vide **WeAdU** (ex. `socle-agent-starter`), y pousser le contenu de `templates/wea35-socle-minimal/` **une fois** validé par l’humain, activer **Template repository** dans les paramètres GitHub ; les nouvelles apps utilisent « Use this template ». Ce dépôt `.github` reste la **source** des mises à jour ; resynchroniser le repo template après changement du sous-arbre.

---

## 6. Écart vs critères de fait (règle Done)

Aucun écart ouvert pour les deux critères du ticket **une fois** la PR qui ajoute ce document + le dossier `templates/` + le script est **fusionnée** sur `main`.

**Suite hors WEA-35** : migration des autres Repls ([WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents)), fermeture Replit ([WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete)).

---

## 7. WEA-44 — Brief agent Cursor **dans** le Repl (export migration)

Le ticket [WEA-44](https://linear.app/weadu/issue/WEA-44/weadu-socle-v5-lab-brief-agent-replit-infos-migration) demande un export **à jour** depuis l’agent Cursor **du Repl** (dépendances réelles, noms des secrets Replit, commandes de run, volumétrie DB, déploiement `.replit.app`, etc.). **Un agent exécuté uniquement sur ce dépôt GitHub (Cursor Cloud, CI) n’a pas accès au filesystem ni au runtime Replit** : on ne peut pas produire ici l’export runtime à la place du Repl.

**Justification documentée (critère de fait WEA-44)** : la preuve d’inaccessibilité depuis cet environnement est ce paragraphe, plus l’inventaire **figé** [WEA-33](./WEA-33-replit-inventory.md) (Socle V5.1, mars 2026) pour la vue « ce qu’on savait sans ouvrir le Repl ».

### Consigne (à coller dans le chat de l’agent Cursor **du** Repl)

Produire un export structuré (**Markdown**, aucune valeur de secret) avec :

1. **Stack** : langage, frameworks, fichiers d’entrée (`main`, `package.json`, `requirements.txt`, etc.).
2. **Run local** : commandes exactes pour lancer en dev.
3. **Git** : remote(s) connus, branche par défaut, dernier commit court.
4. **Secrets** : liste des **noms** de variables (pas les valeurs) dans Replit Secrets.
5. **Base Replit** : oui/non ; tables ou usage si pertinent.
6. **Déploiement** : URL `.replit.app`, Always On / autoscale, charge prod vs expérimentation.
7. **Externes** : AWS/GCP/API/OAuth redirect si visible dans le code ou la config.

Ne pas coller de secrets dans Linear ; résumer sur le ticket ou dans le dépôt cible après revue.

**Export Repl ingéré (miroir dépôt)** : [`weadu-socle-v5-lab-replit-snapshot-2026-05-04.md`](./weadu-socle-v5-lab-replit-snapshot-2026-05-04.md) — produit par l’agent Cursor **dans** le Repl (2026-05-04), collé ici pour la chaîne migration / audit hors Replit.

---

_Document vivant ; première intégration dépôt : 2026-05-04._
