# WEA-33 — Replit : inventaire (~15 projets) et dépendances

Document d’ancrage pour le ticket [WEA-33](https://linear.app/weadu/issue/WEA-33/replit-inventaire-15-projets-et-dependances) dans le dépôt **`WeAdU-ltd/.github`**.

**Dépendances Linear** : [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces) (inventaire GitHub), [WEA-13](https://linear.app/weadu/issue/WEA-13/github-modele-dacces-interne-partage-perso-finance-rh-isole) (modèle d’accès perso / société / finance-RH). Chaîne suite migration : [WEA-35](https://linear.app/weadu/issue/WEA-35/weadu-socle-v5-lab-audit-template-github-cursor) → [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents) → [WEA-37](https://linear.app/weadu/issue/WEA-37/replit-migration-repos-perso-isolation-acces) → [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete).

**Secrets** : ne pas copier de valeurs dans ce fichier. Les jetons et mots de passe vivent dans **Secrets** de chaque Repl, le **socle secrets** ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)) et, le cas échéant, 1Password (ex. coffre d’équipe nommé `Replit` pour des clés transverses — voir inventaires OVH / scripts qui référencent `op://Replit/…`). Ici : **noms publics, oui/non, liens, priorités**.

---

## 1. Comment remplir l’inventaire (source de vérité Replit)

Pour **chaque** Repl (~15 au total visé par le ticket) :

1. **Replit — aperçu** : nom affiché, URL `https://replit.com/@…/…` (ou équivalent), propriétaire / équipe.
2. **Git** : onglet *Version control* ou équivalent — Repl lié à un dépôt GitHub/GitLab (**oui**) ou code uniquement sur Replit (**non**) ; si oui, noter `org/repo` ou URL (aligné [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces)).
3. **Dépendances Replit** : **Database** (Replit DB / autre) **oui/non** ; **Always On** (ou équivalent résilience) **oui/non** ; autres add-ons payants utiles pour la migration.
4. **Secrets** : présence de variables / *Secrets* dans le Repl (**oui/non** + nature **sans valeur** : ex. « API OpenAI », « clé AWS », « webhook n8n »).
5. **Lien AWS** : usage documenté ou observé (EC2, S3, IAM user, etc.) — **oui/non** + référence courte (compte / région / ticket), croiser avec [WEA-29](https://linear.app/weadu/issue/WEA-29/aws-inventaire-ec2-ubuntu-windows-taches-selenium) si pertinent.
6. **Priorité migration** : proposition **P0** (bloquant / prod) … **P3** (peu urgent) ou **À décider** après revue avec [WEA-13](https://linear.app/weadu/issue/WEA-13/github-modele-dacces-interne-partage-perso-finance-rh-isole) (perso vs société).
7. **Statut ligne** : `À vérifier` → `Vérifié` quand les colonnes sont complétées par un humain ou un agent avec accès compte Replit.

**Automatisation future** : une fois un jeton **Replit** (OAuth ou clé API documentée et stockée dans le socle secrets) disponible pour un job ou un agent, on pourra compléter ce tableau via script (API / export) ; jusqu’alors la console Replit reste la source fiable.

---

## 2. Tableau des Repls + statut

| # | Nom Repl (public) | URL / slug | Statut inventaire | Git (oui/non + lien ou repo) | Replit DB | Always On | Secrets (oui/non + nature sans valeur) | Lien AWS | Priorité migration | Perso / Société / Finance-RH (WEA-13) | Notes |
|---|---------------------|------------|---------------------|------------------------------|-----------|------------|----------------------------------------|----------|----------------------|----------------------------------------|-------|
| 1 | *à compléter* | | À vérifier | | | | | | À décider | | |
| 2 | *à compléter* | | À vérifier | | | | | | À décider | | |
| 3 | *à compléter* | | À vérifier | | | | | | À décider | | |
| 4 | *à compléter* | | À vérifier | | | | | | À décider | | |
| 5 | *à compléter* | | À vérifier | | | | | | À décider | | |
| 6 | *à compléter* | | À vérifier | | | | | | À décider | | |
| 7 | *à compléter* | | À vérifier | | | | | | À décider | | |
| 8 | *à compléter* | | À vérifier | | | | | | À décider | | |
| 9 | *à compléter* | | À vérifier | | | | | | À décider | | |
| 10 | *à compléter* | | À vérifier | | | | | | À décider | | |
| 11 | *à compléter* | | À vérifier | | | | | | À décider | | |
| 12 | *à compléter* | | À vérifier | | | | | | À décider | | |
| 13 | *à compléter* | | À vérifier | | | | | | À décider | | |
| 14 | *à compléter* | | À vérifier | | | | | | À décider | | |
| 15 | *à compléter* | | À vérifier | | | | | | À décider | | |

**Synthèse** : objectif **~15** lignes utiles ; supprimer les lignes excédentaires ou en ajouter si le compte réel dépasse 15.

---

## 3. Écart vs critères de fait (agent cloud, sans accès Replit)

- **Critère** : tableau des Repls + statut.  
- **État** : **structure** du tableau et procédure de collecte sont en place dans ce dépôt ; les **données** (noms réels, Git, DB, Always On, secrets, AWS) ne sont **pas** remplies depuis l’agent Cursor cloud : **aucun secret `REPLIT_*` ni token API Replit** n’est injecté dans l’environnement d’exécution actuel, et l’API Replit n’a pas été appelée.  
- **Suite** : une session avec accès compte Replit (dashboard ou token documenté [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)) doit remplir les lignes §2 et passer chaque **Statut inventaire** à **Vérifié** ; ensuite seulement le ticket peut passer **Done** au sens des [critères de fait](https://linear.app/weadu/document/regle-agents-criteres-de-fait-avant-done-tous-projets-2b32aec9e234).

---

_Document vivant : à mettre à jour après chaque vague d’audit Replit._
