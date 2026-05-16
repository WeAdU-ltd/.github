# Extensions Google Ads — copy initiale (appel + structured snippets)

Texte **prêt à coller** dans l’UI Google Ads. Remplacer `{{CALL_TRACKING_NUMBER}}` par le **numéro de renvoi Google** ou le numéro validé dans le compte. **Ne pas** publier sans relecture juridique / acheteur Marketcall.

> Note WEA-194 : la référence « 598-278-9382 » du ticket n’est **pas** utilisée ici comme numéro de production (format ambigu hors contexte) ; utiliser uniquement le numéro issu de **Google Ads → Outils → Conversions / appels** ou du portail Marketcall.

## 1. Extension d’appel (Call extension)

| Champ | Texte proposé |
|-------|----------------|
| **Numéro** | `{{CALL_TRACKING_NUMBER}}` |
| **Pays** | États-Unis |
| **Libellé (optionnel)** | US flight booking — agents now |

**Texte d’appel (Call reporting)** : activer selon les besoins du compte ; cohérent avec le plan `docs/google-ads/google-ads-marketcall-call-tracking-plan.md`.

## 2. Fil de l’annonceur (si extension « fil » / disclaimer court)

**Proposition** (anglais, US) :

> Independent booking help. **Not** Delta, United, or American Airlines. US domestic flights. Total price before you pay.

(Traduire ou raccourcir selon limite de caractères de l’extension réellement utilisée dans le compte.)

## 3. Structured snippets — types possibles

Choisir **un** type aligné Google ; valeurs factuelles, sans superlatifs non prouvés.

**Type « Services »** (exemple de valeurs, une par ligne UI, ≤ 25 caractères chacun si limite) :

- `Domestic US flights`
- `Live phone agents`
- `Fees explained upfront`
- `IVR screening`

**Type « Types »** (alternative) :

- `Round trip`
- `One way`
- `Multi city`

## 4. Checklist avant mise en ligne

- [ ] Mention **not official airline** (ou équivalent approuvé) visible **annonce ou LP** selon stratégie validée.  
- [ ] Aucune marque **Delta / United / American** dans une phrase qui impliquerait **official site** sans disclaimer.  
- [ ] **Même numéro** que sur la landing.  
- [ ] **Horaires** d’affichage de l’extension = plage de prise d’appel réelle.

## 5. Où saisir dans Google Ads

1. **Extensions** au niveau compte ou campagne.  
2. **Extensions d’appel** : créer → coller numéro → libellé.  
3. **Structured snippet** : créer → type → valeurs (min. 3 selon règles Google du moment).  
4. Vérifier l’**aperçu** mobile après liaison aux groupes d’annonces.
