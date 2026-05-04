# Règles communes agents WeAdU

## Source canonique

Avant de mettre un ticket Linear en **Done**, appliquer intégralement le document canonique (critères de fait, liste d’écarts, etc.) :

**[Règle agents — Critères de fait avant Done (tous projets)](https://linear.app/weadu/document/regle-agents-criteres-de-fait-avant-done-tous-projets-2b32aec9e234)**

Ce fichier (`AGENTS.md` dans `WeAdU-ltd/.github`) est le **miroir technique** : rappel court + lien. La **norme** et le texte à jour sont sur la page Linear ci-dessus.

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

## Délégation : autres agents, autres dépôts, Replit

**Préférence opérationnelle (Jeff)** : gagner du temps en **demandant explicitement à l’humain** d’interroger les **agents Cursor qui ont déjà accès** à un autre projet / un autre dépôt (infra, secrets, prod, etc.) plutôt que de tout refaire depuis ce repo seul.

- Les agents sur ces projets peuvent exécuter des commandes, lire la config, ou coller des sorties **sans exposer de secrets** dans le chat.
- **Replit** : même principe — si le besoin concerne un projet ou un environnement Replit, **proposer une consigne courte** à copier-coller vers l’agent / la session Replit qui a accès.

**Règle pour les agents qui lisent ce fichier** : dès qu’une tâche suppose un accès que tu n’as pas (AWS, Windows, Replit, autre org GitHub, etc.), **indique en une phrase** à l’humain : *« Peux-tu demander à l’agent du repo X [ou Replit] de faire Y et te coller le résultat ? »* — avec le **texte exact** à transmettre si possible, plutôt que de bloquer en silence.

## Secrets GitHub — personne de référence (WeAdU-ltd)

Les **valeurs** des secrets (organisation et dépôts, y compris OAuth Gmail / Google) sont créées et tenues à jour par **une seule personne** : **Jeff** (propriétaire unique). Les agents et la doc ne doivent pas renvoyer vers un « autre admin » pour ces secrets : la procédure et les noms canoniques suffisent ; les valeurs viennent de ce canal unique.

## PR en parallèle sur ce dépôt (`.github`)

Pour limiter les files de PR en conflit et le travail de « déblayage » :

1. **Éviter** d’ouvrir plusieurs PR qui modifient les mêmes fichiers « pivot » en même temps : en pratique `README.md`, `docs/SECRETS_CARTOGRAPHIE_WEA14.md`, `.gitignore`, et les workflows sous `.github/workflows/`. Préférer **une PR** qui regroupe les liens / tableaux, ou enchaîner les sujets après merge sur `main`.
2. **Rebaser sur `main`** avant review finale et après tout merge voisin ; pousser la branche rebasée pour que GitHub ne reste pas en `CONFLICTING` / `DIRTY`.
3. **Draft** : ne laisser en brouillon que ce qui est vraiment inachevé ; sinon l’auto-merge ne s’applique pas et la file grossit.
4. **Fin de série** : quand une vague d’agents se termine, vérifier les PR ouvertes **et** les PR Dependabot sur ce dépôt ; traiter ou fermer explicitement ce qui reste.
