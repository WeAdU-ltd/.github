# Règles communes agents WeAdU

## Source canonique

**Ce fichier** (`AGENTS.md` dans `WeAdU-ltd/.github`) est le **canon** pour la conduite des agents (Cursor, automation GitHub). Évolutions : PR sur ce dépôt (suivi [WEA-39](https://linear.app/weadu/issue/WEA-39/regles-communes-fichier-github-rappel-cursor-user-rules-lien-unique)).

**Charte agents** : [`docs/CHARTE_AGENTS_LINEAR_WEA17.md`](docs/CHARTE_AGENTS_LINEAR_WEA17.md) ([WEA-17](https://linear.app/weadu/issue/WEA-17/charte-agents-linear-source-interdits-features-nouveaux-projets)).

## Critères de fait avant Done (tous projets)

Règle absolue pour tous les agents (tous projets).

### Principe effort humain

Si une amélioration **réduit** le travail manuel répétitif (merge, statuts Linear, hooks) et que le **risque est faible**, l'agent ou l'assistant **le fait** ou **crée le ticket** sans redemander une validation explicite « oui/non ».

### Parallèle sur un même dépôt GitHub

- **À éviter** : plusieurs agents qui ouvrent **plusieurs PR en parallèle** sur le **même dépôt** sans file de fusion — cela crée des **conflits** et une file que l'humain ne doit pas découvrir.
- **Si plusieurs tickets** sur le **même** label `repo` : **un seul** agent actif sur ce dépôt **à la fois**, **ou** utiliser une **merge queue** / merges **séquentiels** quand l'infra le permet.
- **Interdit** de conseiller à l'humain de « tout lancer en parallèle » sur le même repo pour gagner du temps — le coût en conflits PR est trop souvent **supérieur** au gain.

### File de PR (aucun signalement humain requis)

- Après ouverture d'une PR : l'agent suit jusqu'à **merge** (ou échec documenté). S'il y a **conflits**, **Draft** non prêt, ou branche **DIRTY** : l'agent **rebase / résout** ou ouvre un **ticket de déblocage** (ex. type [WEA-41](https://linear.app/weadu/issue/WEA-41/github-deblayer-pr-ouvertes-rebase-merge-reste-wea)) **et** commente la PR — **sans** attendre que l'humain remonte le problème.
- **Avant** de mettre le ticket Linear parent en **Done** : la PR associée est **merged**, ou un ticket de déblocage existe et est traité.

### Statuts Linear (zéro friction pour l'humain)

Dès que les **critères de fait** sont remplis : passer le ticket en **Done** tout de suite. **Interdit** : laisser **In Progress** (ou autre statut « en cours ») alors que le travail est terminé — l'humain ne doit pas « rattraper » le statut à la main.

### Avant de mettre un ticket Linear en Done

1. Relire la section **« Critères de fait »** du ticket **ligne par ligne**.
2. Pour **chaque** critère : **fait** (avec lien ou fichier) **ou** **bloqué** (avec la prochaine action).
3. **Interdit** : mettre **Done** si un critère n'est pas rempli, sauf si l'humain a écrit **explicitement** sur le ticket qu'il accepte un report / un découpage.
4. Si quelque chose manque : **ne pas** attendre que l'humain demande « est-ce complet ? ». Écrire sur le ticket une liste **« Écart vs critères »** + ce que l'agent fait ensuite (compléter seul / sous-ticket / **une** question à l'humain).
5. **Fusion PR / CI vert** ≠ **Done** tant que les critères de fait du **ticket Linear** ne sont pas couverts.
6. Si `LINEAR_API_KEY` est absent dans la session : lister les écarts dans le message final au lieu de poster sur Linear.

### Si l'agent ne peut pas tout faire seul

- **Une** question ou **une** action claire à la fois.
- Ou créer un **sous-ticket** avec les critères restants.

### Cursor — règles utilisateur (à coller une fois par l'humain)

Coller dans **Cursor → Settings → Rules** (règles **User** / globales) :

```
Tous les agents : avant de mettre un ticket Linear en Done, applique intégralement AGENTS.md du dépôt WeAdU-ltd/.github :
https://github.com/WeAdU-ltd/.github/blob/main/AGENTS.md
Ne pas confondre « PR fusionnée » et « ticket terminé ». Ne pas attendre que l'humain demande si c'est complet : écrire sur le ticket tout écart par rapport aux critères de fait.
```

## Référence ticket obligatoire

Tout message écrit par un agent — commentaire Linear, description ou commentaire de PR, message Slack, email, résumé relayé à l'opérateur — se termine par une ligne de référence indiquant le ou les tickets concernés par ce message.

Format : `🎫 NEG-XXXX` — **l'identifiant du ticket seul, sans lien et sans titre** (décision Jeff 2026-07-23). Plusieurs tickets : identifiants séparés par une virgule, le ticket principal en premier — exemple `🎫 NEG-2017, NEG-2018`. Aucun ticket concerné : écrire `🎫 Aucun ticket` suivi de la raison en quelques mots. Cette ligne ne contient JAMAIS la mention arobase du bot Cursor (elle relancerait une session agent).

Détails : [`.cursor/rules/message-ticket-reference.mdc`](.cursor/rules/message-ticket-reference.mdc).

## Vérification anti-conflit avant nouvelle règle

Avant qu'un agent (Claude ou Cursor) **écrit ou modifie** une règle opérationnelle dans un **canon** — mémoire, document Linear, `AGENTS.md`, `.cursor/rules`, instructions projet, paramètres Cursor/GitHub — il **vérifie** qu'elle ne **contredit** pas une règle déjà en vigueur à un autre niveau (mémoire, instructions projet, Linear, dépôt, Cursor, GitHub, Settings). En cas de **contradiction détectée**, l'agent **ne tranche pas seul** : il signale le conflit à Jeff dans le canal habituel. **Anti-redondance** : si une règle est déjà canonique à un endroit, ne pas la dupliquer ailleurs.

## Où mettre à jour ces règles

- **Code** : PR sur `WeAdU-ltd/.github` (ce fichier + `.cursor/rules/`).
