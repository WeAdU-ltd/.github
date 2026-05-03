# Routage LLM, coût et budget global (WEA-18)

Document d’ancrage pour le ticket [WEA-18](https://linear.app/weadu/issue/WEA-18/llm-routage-cout-cascade-orchestration-budget-global). Objectif : **routage par type de tâche** (modèle économique d’abord, escalade si la qualité ne suffit pas), **cascade / orchestration**, et **budget global** cohérent avec la cible **&lt; 1000 €/mois** tout compris (IA + infra + outils).

**Dépendance :** le socle clés / billing isolé ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)) ; voir aussi la cartographie secrets ([WEA-14](https://linear.app/weadu/issue/WEA-14/secrets-cartographie-1password-github-cursor-regle-chercher-avant-de), [`SECRETS_CARTOGRAPHIE_WEA14.md`](./SECRETS_CARTOGRAPHIE_WEA14.md)).

---

## 1. Où voir la dépense (mesure / estimation)

| Canal | Où regarder | Ce que ça couvre |
|-------|-------------|------------------|
| **Cursor** | [cursor.com/settings](https://cursor.com/settings) (compte / facturation / usage selon l’offre) | Abonnement Cursor, crédits ou usage **agent / modèles** intégrés au produit. C’est la source **primaire** pour le coût « poste agent » Cursor, distinct des appels API que vous facturez ailleurs. |
| **Fournisseurs LLM (API)** | Tableaux de bord **Billing** / **Usage** du compte (OpenAI, Anthropic, Google AI Studio / Vertex, Azure OpenAI, etc.) | Coût **token** ou requêtes ; export CSV ou API billing si disponible. Aligner le **compte** avec celui dont les clés vivent dans le socle secrets ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)). |
| **GitHub Actions** | *Organization* ou *Repository* → **Settings** → **Billing** (ou vue org **Billing & plans**) + onglet **Usage** des workflows | Minutes runner, stockage artefacts ; utile pour la part **infra CI**, pas le détail token LLM sauf si un job appelle des APIs facturées depuis ce pipeline. |
| **Infra / hébergement** | Factures OVH, AWS, GCP, VPS, n8n ([WEA-26](https://linear.app/weadu/issue/WEA-26/n8n-hebergement-20-euromois-cloud-vs-vps-mise-en-service)), etc. | Complète le « tout compris » du budget global. |
| **Synthèse mensuelle** | Tableur ou outil BI : **une ligne par fournisseur** (Cursor + chaque API + infra) | Permet de sommer et de comparer au plafond **&lt; 1000 €/mois** sans double compter (ex. ne pas additionner une facture Cursor **et** la même consommation déjà incluse dans un forfait, selon votre modèle de facturation). |

**Estimation** quand l’usage n’est pas encore stabilisé : prix public au million de tokens (ou équivalent) × volume observé sur une fenêtre courte, puis révision après le premier mois complet.

---

## 2. Matrice brouillon — type de tâche → modèle / fournisseur

Principe : **premier essai = petit modèle / bon marché** ; **escalade** (modèle plus capable ou autre fournisseur) seulement si les critères de qualité ne sont pas atteints (tests, revue humaine, score, ou échec structuré).

| Type de tâche | Premier choix (draft) | Escalade si insuffisant | Notes |
|----------------|----------------------|-------------------------|--------|
| **Classification / labels courts** | Fournisseur **petit modèle** rapide (ex. famille « mini » / Flash selon disponibilité) | Modèle un cran au-dessus sur le même fournisseur | Peu de tokens ; privilégier latence et coût. |
| **Extraction structurée** (JSON, champs fixes) | Idem petit modèle + **prompt strict** / schema | Modèle **reasoning** ou plus grand si erreurs fréquentes | Valider avec jeux de tests. |
| **Résumé long document** | Modèle **contexte long** économique du catalogue utilisé | Modèle plus capable si omissions graves | Surveiller la fenêtre de contexte vs chunking. |
| **Génération de code (simple)** | Modèle **code** entrée de gamme du stack choisi | Modèle **code** supérieur ou revue agent secondaire | Aligner avec politique IDE (Cursor). |
| **Génération de code (complexe / refactor large)** | Modèle **code** milieu/haut de gamme directement | Second passage ou humain | Évite boucles coûteuses en cascade inutile. |
| **Raisonnement / plan multi-étapes** | Modèle **reasoning** ou équivalent si déjà requis par la tâche | Autre fournisseur ou modèle « pro » | Coût élevé : limiter le contexte et le nombre d’étapes. |
| **Chat utilisateur sensible qualité** | Selon SLA : petit modèle + garde-fous | Escalade modèle ou transfert humain | Documenter SLA par canal. |

Les **noms exacts** de modèles (ex. `gpt-*`, `claude-*`, `gemini-*`) changent souvent : maintenir une **table interne** (wiki, dépôt config, ou variables d’environnement) révisée trimestriellement, plutôt que de figer ici des SKU obsolètes.

---

## 3. Cascade et orchestration (règles opérationnelles)

1. **Budget global** : avant lancement d’une orchestration coûteuse, connaître un **plafond** (tokens, appels, ou € équivalent) pour le run ; arrêt ou dégradation gracieuse si le plafond est atteint.
2. **Critère d’escalade explicite** : échec de parsing, score &lt; seuil, ou liste de checks automatisés ; éviter l’escalade « au feeling » en boucle.
3. **Journal minimal** : type de tâche, modèle utilisé, escalade oui/non (sans loguer de secrets ni PII inutile) pour ajuster la matrice.
4. **Secrets** : jamais de clés dans le dépôt ; utiliser le flux [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh).

---

## 4. Écart vs critères de fait (à mettre à jour sur le ticket Linear)

| Critère | Statut |
|---------|--------|
| Matrice type de tâche → modèle / fournisseur (brouillon OK) | **Fait** dans ce dépôt : section 2 + tableau section 1 pour les sources de coût. |
| Mesure / estimation : où voir la dépense (Cursor, factures API) | **Fait** : section 1. |

Si le socle [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh) n’est pas encore en place, noter sur Linear que le **routage en production** reste **bloqué** sur la gestion des clés et comptes de facturation, sans invalider le brouillon ci-dessus.

---

_Document vivant : réviser après choix concrets de fournisseurs et après première synthèse budget réelle._
