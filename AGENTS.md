# Règles communes agents WeAdU

## Source canonique

**Ce fichier** (`AGENTS.md` dans `WeAdU-ltd/.github`) est le **canon** pour la conduite des agents (Cursor, automation GitHub). Évolutions : PR sur ce dépôt (suivi [WEA-39](https://linear.app/weadu/issue/WEA-39/regles-communes-fichier-github-rappel-cursor-user-rules-lien-unique)).

**Charte agents** : [`docs/CHARTE_AGENTS_LINEAR_WEA17.md`](docs/CHARTE_AGENTS_LINEAR_WEA17.md) ([WEA-17](https://linear.app/weadu/issue/WEA-17/charte-agents-linear-source-interdits-features-nouveaux-projets)).

## Critères de fait avant Done (tous projets)

Règle absolue pour tous les agents (tous projets).

### Principe effort humain

Si une amélioration **réduit** le travail manuel répétitif (merge, statuts Linear, hooks) et que le **risque est faible**, l'agent ou l'assistant **le fait** ou **crée le ticket** sans redemander une validation explicite « oui/non ».

Arbitrage WEA-239 conflit 2 (option A, 2026-08-11T20:37Z) : **autonomie par défaut**. **8** gestes, et 8 seulement, exigent l'accord préalable de Jeff :

| # | Geste réservé | Seuil / périmètre exact |
| -- | -- | -- |
| 1 | Dépense | 20 $/mois, tout coût récurrent, ou dépassement d'un plafond ponctuel déjà fixé |
| 2 | Contenu des comptes | Toute mutation Google Ads, Merchant Center, Shopify ou Google Sheets touchant la sémantique, le manifeste, les règles métier ou les seuils |
| 3 | Stratégie | Structure de campagnes, routage, arbitrages de couverture (dont réplication multi-sites), décisions produit (dont le lancement d'une nouvelle fonctionnalité produit) |
| 4 | Communication externe | Emails clients, échanges Google, tout envoi sortant |
| 5 | Lancement d'un agent Cursor | Tout déclenchement, y compris une relance — règle du 2026-08-06 |
| 6 | Modification des règles elles-mêmes | Écrire ou modifier une règle opérationnelle dans un canon : `AGENTS.md`, `.cursor/rules`, `config/governance.md`, charte [WEA-17](https://linear.app/weadu/issue/WEA-17/charte-agents-linear-source-interdits-features-nouveaux-projets), instructions projet |
| 7 | Secrets et accès | Créer, faire tourner, révoquer un identifiant, ou élargir le périmètre d'un accès existant |
| 8 | Ouverture d'un périmètre nouveau | Créer un dépôt GitHub, ou créer un projet Linear |

Les gestes **6** et **7** ne sont pas nouveaux : ils étendent au canon d'organisation les règles déjà locales **R10** (« les règles ne changent pas d'elles-mêmes ») et **R2** (secrets hors périmètre interdit) de `config/governance.md` dans `WeAdU-ltd/Negative-Terms`.

Le geste **8** : créer un dépôt engage un périmètre durable — secrets, coût d'intégration continue, et une copie de règles supplémentaire à maintenir.

**Tout ce qui n'est pas dans ce tableau s'exécute sans demander**, et l'agent informe après coup. Cela inclut explicitement : diagnostics en lecture seule, création et cadrage de tickets, étiquettes et statuts Linear, fusion d'une demande prête, plomberie d'intégration continue (rebase, fermeture de demande, déblocage de contrôle), surveillance et clôtures.

### Parallèle sur un même dépôt GitHub

- **À éviter** : plusieurs agents qui ouvrent **plusieurs PR en parallèle** sur le **même dépôt** sans file de fusion — cela crée des **conflits** et une file que l'humain ne doit pas découvrir.
- **Si plusieurs tickets** sur le **même** label `repo` : **un seul** agent actif sur ce dépôt **à la fois**, **ou** utiliser une **merge queue** / merges **séquentiels** quand l'infra le permet.
- **Interdit** de conseiller à l'humain de « tout lancer en parallèle » sur le même repo pour gagner du temps — le coût en conflits PR est trop souvent **supérieur** au gain.

### File de PR (aucun signalement humain requis)

- Après ouverture d'une PR : l'agent suit jusqu'à **merge** (ou échec documenté). S'il y a **conflits**, **Draft** non prêt, ou branche **DIRTY** : l'agent **rebase / résout** ou ouvre un **ticket de déblocage** (ex. type [WEA-41](https://linear.app/weadu/issue/WEA-41/github-deblayer-pr-ouvertes-rebase-merge-reste-wea)) **et** commente la PR — **sans** attendre que l'humain remonte le problème.
- **Avant** de mettre le ticket Linear parent en **Done** : la PR associée est **merged**, ou un ticket de déblocage existe et est traité.

### Statuts Linear (zéro friction pour l'humain)

Arbitrage WEA-239 conflit 1 (option B, 2026-08-11T16:04Z) :

1. **Règle générale** : dès que les **critères de fait** sont prouvés, l'agent passe le ticket en **Done**. **Interdit** : laisser **In Progress** (ou autre statut « en cours ») alors que le travail est terminé — l'humain ne doit pas « rattraper » le statut à la main.
2. **Exception unique (Done Guard)** : sur le dépôt `WeAdU-ltd/Negative-Terms` et l'équipe Linear qui le porte, un agent Cursor **ne passe pas** le ticket à Done. Il écrit son verdict, liste les critères remplis, et s'arrête. La clôture est posée par le compte opérateur (`LINEAR_OPERATOR_USER_ID`), sous lequel agit le connecteur Linear de l'architecte.
3. **Motif** : c'est le seul dépôt qui mute Google Ads en production ; une clôture prématurée y a un coût financier.
4. **Rien n'attend Jeff** dans aucun des deux cas.

### Avant de mettre un ticket Linear en Done

Qui pose le Done (agent Cursor vs compte opérateur sur `Negative-Terms`) : voir **Statuts Linear** ci-dessus. Les points suivants restent obligatoires avant toute clôture :

1. Relire la section **« Critères de fait »** du ticket **ligne par ligne**.
2. Pour **chaque** critère : **fait** (avec lien ou fichier) **ou** **bloqué** (avec la prochaine action).
3. **Interdit** : clôturer si un critère n'est pas rempli, sauf si l'humain a écrit **explicitement** sur le ticket qu'il accepte un report / un découpage.
4. Si quelque chose manque : **ne pas** attendre que l'humain demande « est-ce complet ? ». Écrire sur le ticket une liste **« Écart vs critères »** + ce que l'agent fait ensuite (compléter seul / sous-ticket / **une** question à l'humain).
5. **Fusion PR / CI vert** ≠ critères de fait couverts — et donc ≠ Done — tant que la checklist du **ticket Linear** n'est pas prouvée.
6. Si `LINEAR_API_KEY` est absent dans la session : lister les écarts dans le message final au lieu de poster sur Linear.

### Si l'agent ne peut pas tout faire seul

- **Une** question ou **une** action claire à la fois.
- Ou créer un **sous-ticket** avec les critères restants.

Les agents lisent ce fichier directement depuis le dépôt ; aucune copie hors dépôt n'est nécessaire ni souhaitée.

## Référence ticket obligatoire

Tout message écrit par un agent — commentaire Linear, description ou commentaire de PR, message Slack, email, résumé relayé à l'opérateur — se termine par une ligne de référence indiquant le ou les tickets concernés par ce message.

Format : `🎫 XXXX` — **l'identifiant du ticket seul, sans préfixe « NEG- », sans lien et sans titre** (décision Jeff 2026-07-28). Plusieurs tickets : identifiants séparés par un tiret, le ticket principal en premier — exemple `🎫 2017-2018`. Aucun ticket concerné : écrire `🎫 Aucun ticket` suivi de la raison en quelques mots. Cette ligne ne contient JAMAIS la mention arobase du bot Cursor (elle relancerait une session agent).

Détails : [`.cursor/rules/message-ticket-reference.mdc`](.cursor/rules/message-ticket-reference.mdc).

## Vérification anti-conflit avant nouvelle règle

Avant qu'un agent (Claude ou Cursor) **écrit ou modifie** une règle opérationnelle dans un **canon** — mémoire, document Linear, `AGENTS.md`, `.cursor/rules`, instructions projet, paramètres Cursor/GitHub — il **vérifie** qu'elle ne **contredit** pas une règle déjà en vigueur à un autre niveau (mémoire, instructions projet, Linear, dépôt, Cursor, GitHub, Settings). En cas de **contradiction détectée**, l'agent **ne tranche pas seul** : il signale le conflit à Jeff dans le canal habituel. **Anti-redondance** : si une règle est déjà canonique à un endroit, ne pas la dupliquer ailleurs.

## Couverture vérificateur obligatoire (NEG-2532)

Toute PR qui **crée un nouveau mécanisme récurrent** doit mettre à jour le vérificateur Wellbots en parallèle, ou documenter explicitement pourquoi ce n'est pas nécessaire.

### Mécanismes concernés

- Workflow GitHub Actions avec déclencheur `schedule:` (cron)
- Mutation Google Ads automatisée (script ou cron avec apply)
- Règle de doctrine (`.cursor/rules`, manifeste yaml, garde-fou architectural)

### Obligation dans la PR

Dans la **même PR**, l'une des deux options :

1. **Ajouter la règle manifeste** correspondante dans `workbench/config/wellbots/verifier/` (ou l'extension du vérificateur adaptée), **ou**
2. **Ligne explicite** dans la description de PR : `Couverture vérificateur : non nécessaire — <raison>`

### CI (Negative-Terms)

Le workflow `verifier-guard` émet un **warning** (non bloquant) si la PR ajoute un fichier `.github/workflows/*.yml` contenant `schedule:` sans mention `Couverture vérificateur` dans le corps de la PR.

Filet quotidien matrice de couverture : ticket NEG-2533.

## Où mettre à jour ces règles

- **Code** : PR sur `WeAdU-ltd/.github` (ce fichier + `.cursor/rules/`).
