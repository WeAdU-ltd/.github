# Plan de tracking — appels (Google Ads + Marketcall)

Documentation **process** (sans code) pour déployer et vérifier le suivi des appels. Adapter les noms de compte, fuseaux et IDs internes.

## 1. Objectifs de mesure

| Signal | Usage |
|--------|--------|
| Appels depuis annonces / site (Google) | Optimisation enchères, preuve diffusion |
| Appels facturables / qualifiés (Marketcall) | Rentabilité programme, alignement acheteur |
| (Optionnel) GA4 / CRM | Parcours multi-touch — seulement si politique privacy OK |

## 2. Google Ads — conversions d’appel

1. **Numéro Google** : utiliser un numéro **renvoi d’appel Google** (ou pool si éligible et configuré) **identique** entre annonces et LP.  
2. Créer une action de conversion **Appels depuis les annonces** (durée minimale recommandée alignée sur l’**IVR / SLA** programme — valeur à fixer avec l’acheteur).  
3. Ajouter si pertinent **Appels depuis un numéro de téléphone sur le site web** (même numéro forwarding sur la LP).  
4. **Fenêtre d’attribution** : noter celle du compte (ex. 30 j. clic) et la comparer au **délai de réconciliation Marketcall**.  
5. **Test** : lancer un appel test depuis une **prévisualisation d’annonce** ou un appareil réel ; vérifier dans **Conversions** (lag jusqu’à 24–48 h possible).  
6. **Doublons** : éviter deux actions comptant le même physique sans règle claire (documenter laquelle est **“primary”** pour enchères).

## 3. Marketcall — corrélation

1. Les **IDs programme / offre** et le **numéro de suivi** Marketcall doivent correspondre au numéro affiché côté Google / LP.  
2. Exporter les **rapports d’appels** (horodatage, durée, statut, motif de refus si disponible) sur la même **timezone** que Google (documenter la TZ utilisée).  
3. **Postbacks** (si activés) : URL, secret, mapping statuts — tenir un **schéma** (tableau champ → action) dans le wiki interne ; ne pas exposer les secrets dans ce dépôt.  
4. **Écart Google vs Marketcall** : normal en cas de filtres acheteur ; documenter le **seuil d’investigation** (ex. écart > 30 % sur 7 j glissants).

## 4. QA rapide (checklist technique)

- [ ] Un appel test déclenche une ligne **Google** conversion (après délai).  
- [ ] Le même apparaît côté **Marketcall** avec statut attendu (ou refus documenté si test hors règles).  
- [ ] La **LP** affiche le même E.164 / format que l’UI Google (pas de numéro “caché” différent).  
- [ ] Aucun **tag** bloquant le clic `tel:` (bannière consentement, overlay).

## 5. Avertissements connus (à compléter en interne)

- **Délai de latence** conversions Google : ne pas optimiser sur J0 seul.  
- **IVR** : les appels très courts peuvent être exclus des conversions Google mais visibles Marketcall — documenter.  
- **Spam / robots** : si volume anormal, activer exclusions / captcha côté LP **sans** casser l’accessibilité (valider juridique).

## 6. Références

- Aide Google : conversions d’appel, annonces d’appel, vérification de numéro.  
- Marketcall : documentation API et portail affilié (`https://www.marketcall.com/affiliate/api/docs`).
