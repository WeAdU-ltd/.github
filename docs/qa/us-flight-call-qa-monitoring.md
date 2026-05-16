# QA des appels — monitoring, écoute, exclusions (vols US / Marketcall)

Procédure **opérable** sans doc externe. Ajuster fréquences selon volume.

## 1. Rôles

| Rôle | Action |
|------|--------|
| **Média buyer** | Export Search terms, budgets, pause / exclusions négatives |
| **Ops / QA call** | Écoute échantillon, grille qualité, remontée acheteur |
| **Référent Marketcall** | Validation refus contestables, alignement règles programme |

## 2. Fréquence minimale

| Période | Action |
|---------|--------|
| **J+1 à J+7** quotidien | Export Search terms + 2 à 5 **écoutes** / jour si volume faible ; monter si > N appels/j (fixer N). |
| **Hebdo** | Revue **motifs de refus** Marketcall + top raisons hors cible. |
| **Mensuel** | Audit **cohérence** LP / annonces + mise à jour négatifs. |

## 3. Échantillonnage (appels enregistrés)

1. Tirer **aléatoirement** k appels dans la période (k = 5 à 20 selon volume, biais réduit).  
2. Remplir une **fiche** par appel : date, heure, ID interne (sans PII dans tickets publics), durée, résultat (réservation / abandon / hors cible), tags.  
3. **Ne pas** stocker PII dans Linear ; utiliser table interne (Sheet chiffré, CRM).

## 4. Grille d’écoute (exemple)

- **Accroche** : annonce / LP alignées (pas de promesse absente au téléphone).  
- **Compliance** : pas de claims interdits (réf. brief acheteur).  
- **Qualification** : IVR / agent filtre geo + intent.  
- **Expérience** : attente, transfert, abandon.

Score simple (1–4) ou binaire par ligne ; **seuil** de réaction si moyenne < X deux semaines d’affilée.

## 5. Triggers d’exclusion / pause

| Condition | Action documentée |
|-----------|-------------------|
| Pic de **refus** “hors geo” | Vérifier géo campagne + négatifs + LP ; pause sous-ensemble d’annonces si isolé. |
| Hausse **IVR abandon** | Réviser script IVR + annonces (message trop large ?). |
| **CPA** Google >> cible | Réduire enchères / mots-clés larges ; ajouter négatifs issus Search terms. |
| **Fraude** numéro / spam | Escalade sécurité ; consigner incident (sans détail secret). |

Chaque action doit laisser une **trace** : ligne dans journal (date, auteur, lien export, décision).

## 6. Feedback vers acheteur Marketcall

1. Ouvrir un **ticket interne** (ou fil Linear privé) avec : période, % refus, 3 exemples anonymisés, demande clarification règle.  
2. **SLA** de réponse attendu noté ; si silence, escalade référent.

## 7. Process correctif (boucle fermée)

```
Mesure → Cause (Search term / créa / IVR / geo) → Changement (négatif, RSA, horaire, LP)
→ Date déploiement → Vérification J+2 sur même métrique
```

Si la métrique ne bouge pas, **documenter** l’hypothèse suivante (enchères, saisonnalité, cap acheteur).
