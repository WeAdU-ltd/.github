# Checklist go-live — campagne Google Ads + landing appels (vols US)

Chaque ligne est **binaire** : cocher uniquement quand c’est vérifié. Adapter les mentions légales au **programme Marketcall** et à l’entité annonceur.

## A. Landing & conformité annonceur

- [ ] URL finale = **HTTPS** ; pas de chaîne de redirections inutile vers la LP.
- [ ] **Canonical** = URL finale publiée ; cohérent avec l’URL déclarée dans Google Ads.
- [ ] **Mobile** : viewport, tap targets, numéro cliquable `tel:` testé sur appareil réel.
- [ ] **Même numéro** visible (texte + `tel:`) = numéro **Google forwarding / pool** ou numéro validé dans le compte.
- [ ] Identité : **nom commercial + entité légale** visibles (selon brief acheteur).
- [ ] Disclaimer **non compagnie officielle** présent si requis par le programme / le juridique.
- [ ] Pas de **prix trompeur** ni de promesse de tarif non vérifiable au téléphone.
- [ ] **Politique de confidentialité** et (si applicable) **CCPA “Do Not Sell or Share”** liés et à jour.
- [ ] **Conditions** / mentions liées au service téléphonique accessibles sans piège UX.

## B. Google Ads — structure & créatifs

- [ ] Campagne / groupes d’annonces alignés sur **intentions** validées (pas seulement mots-clés génériques).
- [ ] Liste **négative** importée ou collée (voir `docs/google-ads/us-flight-call-negative-keywords.csv`) + négatifs compte si politique interne.
- [ ] RSA : au moins **3 titres / 2 descriptions** distincts testés en prévisualisation (fuite de troncature).
- [ ] **Extensions d’appel** : texte + numéro vérifié ; cohérent avec la LP (voir doc extensions).
- [ ] **Structured snippets** (si utilisés) : valeurs conformes aux **règles Google** (pas de superlatifs interdits).
- [ ] **Paramètres de suivi** (UTM / valeur custom) si stack marketing l’exige — sans casser la final URL.
- [ ] **Géo** campagne = périmètre **US** (ou sous-ensemble) aligné programme Marketcall.
- [ ] **Horaires annonces** alignés **décroché** centre d’appels + fuseaux.
- [ ] **Stratégie d’enchères** et budget : plafonds / règles de pause documentés.

## C. Tracking & conversions

- [ ] **Conversion appels** (durée / catégorie) configurée et **non dupliquée** inutilement avec Marketcall.
- [ ] **Fenêtre d’attribution** documentée (compte + rapport interne).
- [ ] **Import offline** ou pont CRM — si applicable, testé sur un appel fictif / banc d’essai.
- [ ] **Google Tag Assistant** / DebugView (si GA4) utilisé pour un parcours test mobile.
- [ ] **Marketcall** : postback / rapport = même fuseau horaire documenté pour corrélation.

## D. QA technique & qualité

- [ ] **Prévisualisation annonce** (aperçu mobile) sans extension manquante critique.
- [ ] **Liens** LP : aucun 404 ; ancres FAQ si présentes fonctionnelles.
- [ ] **Accessibilité** de base : contrastes, focus clavier sur CTA principal.
- [ ] **Performance** : LCP / INP raisonnables sur 4G simulé (pas de bloqueurs lourds au-dessus de la ligne de flottaison).
- [ ] **Consentement** bannière cookies / tags : n’empêche pas l’appel si non requis pour le CTA principal.

## E. Process humain & gouvernance

- [ ] **RACI** : qui valide copy LP vs annonces (même personne ou liste de diffusion documentée).
- [ ] **Journal des changements** (date, auteur, résumé) pour toute modif post-launch.
- [ ] **Plan QA appels** (échantillonnage) activé — voir `docs/qa/us-flight-call-qa-monitoring.md`.
- [ ] **Seuil d’arrêt** : règles si CPA appel / taux de refus Marketcall dépassent X (valeur à fixer).

## F. Post-lancement J+1 à J+7

- [ ] J+1 : export **Search terms** + ajouts négatifs si fuite d’intent.
- [ ] J+3 : corrélation **Google conversions appels** vs **rapports Marketcall** (ordre de grandeur).
- [ ] J+7 : revue **extensions**, RSA faibles, et **LP** (scroll / taux de rebond mobile si dispo).
