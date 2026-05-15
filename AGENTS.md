# Règles communes agents WeAdU

## Source canonique

Avant de mettre un ticket Linear en **Done**, appliquer intégralement le document canonique :

**[Règle agents — Critères de fait avant Done (tous projets)](https://linear.app/weadu/document/regle-agents-criteres-de-fait-avant-done-tous-projets-2b32aec9e234)**

**Charte agents** : [`docs/CHARTE_AGENTS_LINEAR_WEA17.md`](docs/CHARTE_AGENTS_LINEAR_WEA17.md) ([WEA-17](https://linear.app/weadu/issue/WEA-17/charte-agents-linear-source-interdits-features-nouveaux-projets)).

## Règles essentielles

1. Relire les **critères de fait** du ticket ligne par ligne.
2. Pour chaque critère : **fait** (preuve / lien) ou **bloqué** (prochaine action).
3. **Ne pas** mettre **Done** si un critère manque, sauf acceptation explicite de l'humain.
4. Écrire sur le ticket une liste **« Écart vs critères »** + la suite — ne pas attendre qu'on demande.
5. **PR fusionnée / CI vert ≠ Done** tant que les critères de fait ne sont pas couverts.

## Règles détaillées

Les règles opérationnelles (Linear API, secrets, CI, Replit, AWS, 1Password, communication, git) sont dans **`.cursor/rules/`** (fichiers `.mdc` conditionnels). Chaque fichier s'active uniquement quand le contexte est pertinent (glob ou description).

## Où mettre à jour ces règles

- **Code** : PR sur `WeAdU-ltd/.github` (ce fichier + `.cursor/rules/`).
- **Norme détaillée** : document Linear lié ci-dessus.
- **Ne pas** modifier les User Rules Cursor d'un poste sans instruction explicite de l'humain.
