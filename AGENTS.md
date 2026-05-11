# Règles communes agents WeAdU

## Source canonique

Avant de mettre un ticket Linear en **Done**, appliquer intégralement le document canonique (critères de fait, liste d’écarts, etc.) :

**[Règle agents — Critères de fait avant Done (tous projets)](https://linear.app/weadu/document/regle-agents-criteres-de-fait-avant-done-tous-projets-2b32aec9e234)**

Ce fichier (`AGENTS.md` dans `WeAdU-ltd/.github`) est le **miroir technique** : rappel court + lien. La **norme** et le texte à jour sont sur la page Linear ci-dessus.

**Charte agents** (Linear source, interdits features / nouveaux projets, règle Cursor, communication humain) : [`docs/CHARTE_AGENTS_LINEAR_WEA17.md`](docs/CHARTE_AGENTS_LINEAR_WEA17.md) ([WEA-17](https://linear.app/weadu/issue/WEA-17/charte-agents-linear-source-interdits-features-nouveaux-projets)).

## Linear : API uniquement (ne pas s’appuyer sur le MCP Cursor)

Les changements Linear (tickets, projet, commentaires) passent par la **clé d’API** `LINEAR_API_KEY` — dans l’environnement de l’agent shell quand elle est injectée, ou dans **GitHub Actions** via le secret du même nom — et les scripts / workflows du dépôt (`scripts/linear_*.py`, `.github/workflows/linear-*.yml`).

- **Ne pas** utiliser le **serveur MCP Linear** de Cursor comme chemin principal : le tableau d’intégration peut afficher *Connected* sans que la session d’agent expose d’outils MCP exploitables (état `needsAuth`, cloud agent, autre déconnexion).
- **Ne pas** demander à l’humain de configurer ou déboguer le MCP pour exécuter un ticket ; étendre un script existant ou un workflow si un cas manque.
- Ne **pas** proposer en premier « connecter le MCP Linear » : le MCP est **optionnel** (confort IDE) et souvent **`needsAuth`** en cloud ; tant que **`LINEAR_API_KEY`** est disponible, l’**API GraphQL** (scripts du dépôt, ex. `scripts/linear_pr_common.py`) fait le travail.
- **Commentaires et preuves sur Linear** : poster avec **`scripts/linear_issue_comment.py`** (ou `comment_create` dans un script) ; **ne jamais** demander à l’humain de coller un livrable, un tableau ou une synthèse dans l’UI Linear. Si la clé API est absente dans la session, le dire explicitement (*non accessible : LINEAR_API_KEY*) après une tentative, pas une demande de copier-coller.

## Communication — ne pas renvoyer vers l’ouverture de fichiers

Si une procédure ou un extrait d’un fichier du dépôt suffit pour agir : **reproduire dans le message** (chat ou commentaire Linear) les **étapes ou le tableau utiles**, pas seulement « ouvre `docs/…` » ou un lien seul. Les fichiers restent la **source versionnée** ; l’humain ne doit pas perdre du temps à ouvrir un fichier quand l’agent peut en copier le contenu **nécessaire** dans la réponse. Exception raisonnable : fichiers **énormes**, **générés**, ou quand l’action côté Git est **déjà couverte par l’auto-merge** sur `WeAdU-ltd/.github` (PR prête, non brouillon) — dans ce cas : indiquer que la fusion est **automatique après CI**, pas une procédure pas à pas vers l’UI GitHub ; dans les autres cas de merge / PR, résumer au minimum l’intention.

## Instructions UI / console — une page à la fois

Pour guider un humain dans une **interface web** (AWS, GitHub, Linear, etc.) : **un seul écran ou une seule page par message** — uniquement les clics/champs pour **cette** page, ni plus ni moins. Attendre **OK / capture / « c’est fait »** avant d’envoyer les instructions de la **page suivante**.

## AWS — contrôle serveurs (SSM)

Pour **checks répétitifs** ou **commandes** sur des VMs AWS : viser **Systems Manager** (instance **Online** dans **Fleet Manager**) + **GitHub Actions** / OIDC — pas demander à l’humain du **RDP** pour la routine. Norme versionnée : [`docs/AWS_SSM_WEADU_STANDARD.md`](docs/AWS_SSM_WEADU_STANDARD.md) ; quand tu guides un humain, **inclure les étapes pertinentes dans le message** (cf. section *Communication* ci-dessus).

## Migration Replit — preuve sans arbitrage URL (WEA-36)

Après lecture du **dépôt applicatif** cible (`README`, `docs/STAGING_*`, workflows `deploy-*.yml`, présence de `.replit` / `replit.md`), l’agent **met à jour** le runbook `docs/inventory/*` correspondant et la **liste résiduelle** [§5 WEA-36](docs/inventory/WEA-36-replit-migration-societe.md) :

1. **Couper prod vs résiduel** : si la **production** documentée pointe vers **AWS / GitHub Actions** (pas `*.replit.app`), le **cutover prod** est **noté comme fait** avec lien vers les fichiers cités.
2. **Résiduel** : toute URL `.replit.app` encore mentionnée pour **staging/E2E** est une **ligne résiduelle** ou une **tâche dans le repo applicatif** pour la retirer — **pas** une question ouverte à l’humain dans le chat.
3. **Ne pas** reformuler « migration à finaliser » si le code et les déploiements prod sont déjà sur GitHub/AWS ; reformuler en « résiduel documenté » ou « fermer le Repl ».
4. **Import code / étape franchie** : dès qu’un **premier import** vers le dépôt cible est fait (push depuis l’hôte, Repl, ou script du dépôt `.github`), l’agent **met à jour** le runbook `docs/inventory/*`, le tableau **§3 / §5 WEA-36**, et **poste** sur le ticket Linear concerné un commentaire API (`linear_issue_comment.py`) avec la **preuve** — **sans** attendre que l’humain « confirme » la doc.
5. **Inventaire [WEA-33](docs/inventory/WEA-33-replit-inventory.md)** : un Repl **Team** peut **manquer** au tableau s’il **n’était pas branché** au Socle à l’export ; **ne pas** l’assimiler à une ligne existante sans **même Repl ID**. Sinon **ajouter une ligne** au §3 puis migrer selon [WEA-36](docs/inventory/WEA-36-replit-migration-societe.md).

## Règles essentielles (rappel)

1. Relire la section **« Critères de fait »** du ticket **ligne par ligne**.
2. Pour chaque critère : **fait** (avec preuve / lien) ou **bloqué** (prochaine action).
3. **Ne pas** mettre **Done** si un critère manque, sauf acceptation **explicite** de l’humain sur le ticket (report / découpage).
4. **Ne pas** attendre la question « est-ce complet ? » : écrire sur le ticket une liste **« Écart vs critères »** + la suite (compléter / sous-ticket / **une** question ciblée).
5. **PR fusionnée / CI vert** ≠ **Done** tant que les critères de fait du **ticket Linear** ne sont pas couverts.

## Où mettre à jour ces règles

- **Code / miroir** : PR sur le dépôt `WeAdU-ltd/.github` (notamment ce fichier `AGENTS.md`).
- **Norme détaillée** : édition du document Linear lié ci-dessus.

**Ne pas** modifier les réglages Cursor globaux (User rules) d’un poste sans instruction explicite de l’humain ; l’humain ne maintient qu’un **court** renvoi vers le doc Linear (voir ce même document Linear, section Cursor).

## Blocage GitHub / CI (WeAdU-ltd)

- Les **échecs** des workflows listés dans [`docs/GITHUB_CI_FAILURE_ALERT.md`](docs/GITHUB_CI_FAILURE_ALERT.md) génèrent une **issue** sur le dépôt `WeAdU-ltd/.github` et une alerte **Slack** optionnelle. **Traiter en priorité** : lire le run, corriger, relancer.
- **Ne pas** appliquer de correctifs de sécurité (gitleaks, secrets) en **contournant** la revue ; branche + PR + CI verte comme d’habitude.
- Un **déblocage entièrement automatique** (merge à la place de l’humain sur tout type d’échec) n’est **pas** activé : risque de merger du code non revu ou d’aggraver un incident.

## Principe « zéro humain » (ops / GitHub)

**Objectif** : concentrer l’humain sur la vision et les fonctionnalités ; réduire les allers-retours répétitifs (UI GitHub, PowerShell local, copier-coller de secrets).

Les agents **privilégient** : secrets **organisation** / compte machine, **GitHub Actions** (cron, PR automatique, auto-merge), **rulesets** d’organisation, et des **tickets Linear** pour toute étape encore **ponctuelle** et non automatisée (première SSO, création d’App, etc.).

**Backlog d’implémentation** : gabarit de ticket à créer dans Linear — [`docs/ZERO_HUMAN_AUTOMATION_LINEAR.md`](docs/ZERO_HUMAN_AUTOMATION_LINEAR.md).

## Zéro friction référent (PR `.github`, briefs Replit)

Objectif : **pas de check-list « merge PR » ou « ouvre Replit »** pour le référent sur la routine Socle.

1. **Fusion des PR sur `WeAdU-ltd/.github`** : le workflow [`.github/workflows/auto-merge-pr.yml`](.github/workflows/auto-merge-pr.yml) met en file d’attente l’**auto-merge** pour les PR **non brouillon** vers la branche par défaut, dès que les garde-fous GitHub le permettent. Les agents **ne doivent pas** terminer par une procédure manuelle *Merge pull request* pour le référent, **sauf** blocage explicite (PR en brouillon, CI requise rouge, conflit, règle d’organisation qui exige une revue manquante). Si seul l’auto-merge est en attente et la CI est verte ou en cours : indiquer **« Rien à faire de ton côté pour la fusion : auto-merge après CI »** (pas d’étapes GitHub pas à pas).
2. **Tickets « brief agent Replit »** (premier sous-ticket WEA-36, [WEA-44](https://linear.app/weadu/issue/WEA-44/weadu-socle-v5-lab-brief-agent-replit-infos-migration), équivalents) : le travail **dans** le Repl n’est **pas** une consigne adressée au référent par message. **Exécution** : session **Cursor (ou équivalent) ouverte dans le Repl** qui porte le code, ou tout opérateur avec workspace Repl — avec la consigne canonique [WEA-35 §7](docs/inventory/WEA-35-weadu-socle-v5-lab-template.md). Côté dépôt `.github`, le livrable agent reste : runbook `docs/inventory/*`, mise à jour WEA-33/WEA-36 si besoin, preuve sur Linear via **`scripts/linear_issue_comment.py`**. Pour les **nouveaux** tickets Linear : préférer un **renvoi** vers WEA-35 §7 + un runbook plutôt qu’un long copier-coller à maintenir en double.
3. **Linear** : commentaires et preuves toujours par **API** si `LINEAR_API_KEY` est disponible ; **pas** de demande au référent de coller un livrable dans l’UI Linear.

## Délégation : autres agents, autres dépôts, Replit

**Préférence opérationnelle** : enchaîner **automation / API / agent avec le bon workspace** plutôt qu’une relayrace où le référent coordonne chaque clic.

- Les agents sur les autres dépôts peuvent exécuter des commandes, lire la config, ou coller des sorties **sans exposer de secrets** dans le chat.
- **Replit** : l’agent du dépôt `.github` **n’a pas** le workspace Repl — l’exécution du **brief** se fait **dans** le Repl (voir section **Zéro friction référent** ci-dessus), pas comme liste d’actions pour le référent dans le chat. **Linear** : tout commentaire sur un ticket se fait par **API** si `LINEAR_API_KEY` est disponible.

**Règle pour les agents qui lisent ce fichier** : dès qu’une tâche suppose un accès que tu n’as pas (**AWS, Windows, Replit**, autre org GitHub, etc.), documenter le **délégataire technique** (ex. agent avec workspace Repl, repo applicatif) et le **point d’entrée versionné** (runbook, WEA-35 §7) — **sauf** pour Linear : là, utiliser l’API ou documenter *non accessible*. Ne pas demander au référent de « coller dans Linear » ni d’enchaîner merge + Replit pour la routine Socle (voir **Zéro friction référent**).

## 1Password (`op` vs `OP_SERVICE_ACCOUNT_TOKEN`, SDK)

- Le secret **`OP_SERVICE_ACCOUNT_TOKEN`** (Cursor / env) n’installe **pas** le binaire **`op`**. Voir [`docs/ONEPASSWORD_AGENTS.md`](docs/ONEPASSWORD_AGENTS.md) : **devcontainer** pour `op`, **script** `onepassword_resolve_ref.py` pour le **SDK** sans CLI.
- Ne pas supposer `command -v op` dans une session Cloud Agent tant que Cursor ne livre pas la CLI dans l’image.

## Secrets GitHub — personne de référence (WeAdU-ltd)

Les **valeurs** des secrets (organisation et dépôts, y compris OAuth Gmail / Google) sont créées et tenues à jour par **une seule personne** : **Jeff** (propriétaire unique). Les agents et la doc ne doivent pas renvoyer vers un « autre admin » pour ces secrets : la procédure et les noms canoniques suffisent ; les valeurs viennent de ce canal unique.

## Zéro humain — secrets d’organisation (éviter « où est la valeur ? »)

Les **noms** des secrets (`GITHUB_ORG_AUDIT_TOKEN`, `LINEAR_API_KEY`, etc.) sont dans [`docs/SECRETS_SOCLE_WEA15.md`](docs/SECRETS_SOCLE_WEA15.md). Les **valeurs** n’existent pas dans le dépôt : elles sont créées **une fois** dans l’UI GitHub (PAT / jeton machine), puis saisies dans *Organization secrets* — jamais dans Linear ni dans le chat des agents.

**Avant** de proposer de créer un nouveau PAT : appliquer [WEA-14](docs/SECRETS_CARTOGRAPHIE_WEA14.md) **y compris 1Password** (même jeton, autre nom d’item) quand l’intégration est réellement accessible ; ne pas supposer l’absence d’un secret existant.

Quand une PR ajoute un workflow qui lit `secrets.NOM` : documenter le nom, pointer ce paragraphe + [`docs/ZERO_HUMAN_AUTOMATION_LINEAR.md`](docs/ZERO_HUMAN_AUTOMATION_LINEAR.md), et indiquer **référent unique pour la valeur** (ci-dessus). Ne pas laisser l’humain non référent se demander où « télécharger » le secret : il n’y a pas de fichier ; seule la création GitHub org compte.

## PR en parallèle sur ce dépôt (`.github`)

Pour limiter les files de PR en conflit et le travail de « déblayage » :

1. **Éviter** d’ouvrir plusieurs PR qui modifient les mêmes fichiers « pivot » en même temps : en pratique `README.md`, `docs/SECRETS_CARTOGRAPHIE_WEA14.md`, `.gitignore`, et les workflows sous `.github/workflows/`. Préférer **une PR** qui regroupe les liens / tableaux, ou enchaîner les sujets après merge sur `main`.
2. **Rebaser sur `main`** avant review finale et après tout merge voisin ; pousser la branche rebasée pour que GitHub ne reste pas en `CONFLICTING` / `DIRTY`.
3. **Draft** : ne laisser en brouillon que ce qui est vraiment inachevé ; sinon l’auto-merge ne s’applique pas et la file grossit.
4. **Fin de série** : quand une vague d’agents se termine, vérifier les PR ouvertes **et** les PR Dependabot sur ce dépôt ; traiter ou fermer explicitement ce qui reste.
