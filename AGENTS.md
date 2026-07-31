# Règles communes agents WeAdU

## Source canonique

**[Règle agents — Critères de fait avant Done (tous projets)](https://linear.app/weadu/document/regle-agents-criteres-de-fait-avant-done-tous-projets-2b32aec9e234)**

**Charte agents** : [`docs/CHARTE_AGENTS_LINEAR_WEA17.md`](docs/CHARTE_AGENTS_LINEAR_WEA17.md) ([WEA-17](https://linear.app/weadu/issue/WEA-17/charte-agents-linear-source-interdits-features-nouveaux-projets)).

## Règles essentielles

1. Relire les **critères de fait** du ticket ligne par ligne.
2. Pour chaque critère : **fait** (preuve / lien) ou **bloqué** (prochaine action).
3. **Ne pas** mettre **Done** si un critère manque, sauf acceptation explicite de l'humain.
4. Écrire la liste **« Écart vs critères »** + la suite — ne pas attendre qu'on demande.
5. **PR fusionnée / CI vert ≠ Done** tant que les critères de fait ne sont pas couverts.
6. Si `LINEAR_API_KEY` est absent dans la session : lister les écarts dans le message final au lieu de poster sur Linear.
7. **Référence ticket obligatoire** : tout message d'agent se termine par une ligne `🎫 NEG-XXXX` (identifiant seul, sans lien ni titre) ou `🎫 Aucun ticket` + raison.
   Détails : [`.cursor/rules/message-ticket-reference.mdc`](.cursor/rules/message-ticket-reference.mdc).

## Vérification anti-conflit avant nouvelle règle

Avant qu'un agent (Claude ou Cursor) **écrit ou modifie** une règle opérationnelle dans un **canon** — mémoire, document Linear, `AGENTS.md`, `.cursor/rules`, instructions projet, paramètres Cursor/GitHub — il **vérifie** qu'elle ne **contredit** pas une règle déjà en vigueur à un autre niveau (mémoire, instructions projet, Linear, dépôt, Cursor, GitHub, Settings). En cas de **contradiction détectée**, l'agent **ne tranche pas seul** : il signale le conflit à Jeff dans le canal habituel. **Anti-redondance** : si une règle est déjà canonique à un endroit, ne pas la dupliquer ailleurs.

## Où mettre à jour ces règles

- **Code** : PR sur `WeAdU-ltd/.github` (ce fichier + `.cursor/rules/`).
- **Norme détaillée** : document Linear lié ci-dessus.
