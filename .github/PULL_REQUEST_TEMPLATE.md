## Résumé

<!-- Décrivez brièvement le changement. -->

## Critères de fait

<!-- Optionnel : le workflow « Linear sync PR criteria » recopie automatiquement la section depuis le ticket Linear (WEA-*) dans la PR. Sinon, collez la section depuis Linear ici et cochez `[x]` quand c’est fait. -->

## Avant d’ouvrir / avant merge (agents & humains)

- [ ] **Une PR par sujet** : éviter plusieurs PR qui touchent les mêmes fichiers « pivot » (`README.md`, `docs/SECRETS_CARTOGRAPHIE_WEA14.md`, `.gitignore`) en parallèle ; sinon rebaser souvent sur `main`.
- [ ] **Branche à jour** : `git fetch origin && git rebase origin/main` (ou merge) avant review ; résoudre les conflits localement, pousser, laisser la CI verte.
- [ ] **Pas de brouillon bloquant** : si la PR est prête, retirer le statut *Draft* pour que l’auto-merge puisse s’appliquer quand les checks passent.
- [ ] **File** : après merge, vérifier qu’il ne reste pas d’autres PR ouvertes sur le même dépôt qui traînent (Dependabot inclus).
