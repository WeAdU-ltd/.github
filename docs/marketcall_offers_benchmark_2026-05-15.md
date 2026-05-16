# Marketcall — benchmark offres (snapshot) & cadre Google Ads / mobile

**Date du snapshot CSV :** 2026-05-15  
**Source données :** `docs/marketcall_offers_active_snapshot_2026-05-15.csv` (export API `GET /api/v1/affiliate/offers`, offres **actives** + 3 en *Paused (Limits)* sur 192 lignes).  
**Doc API :** [MarketCall — API docs](https://www.marketcall.com/affiliate/api/docs)

**Limite d’analyse :** les colonnes exportées ne contiennent pas les **règles complètes** (géo, créneaux, compagnies cibles, etc.) : le potentiel réel dépend du **détail offre** dans Marketcall + de ta capacité opérationnelle (réponse appel, conformité acheteur). Les métriques **epcw**, **icr**, **key_calls_percent** sont des **indices Marketcall**, pas des garanties de marge.

---

## 1. Vue d’ensemble du portefeuille (192 lignes)

| Indicateur | Valeur |
|------------|--------|
| Pays **US** | 185 offres |
| Autres pays (GB, GH, IT, FR, UA, RU) | 7 offres |
| États | 189 *Active*, 3 *Paused (Limits)* |
| **Smartlink** | 0 sur ce snapshot |
| **Call tracking** (colonne) | 100 % `True` sur les lignes exportées |

**Catégories (IDs Marketcall — les libellés exacts sont dans `GET /categories`)**  
Les IDs les plus fréquents : `3` (78), `12` (40), `4` (26), `33` (16), `2` (15), `11` (14), `30` (13), `7` (9), …  
→ le portefeuille est **très orienté “home / services” (3)** et **assurance / santé (12, 30, 31, …)**, avec un bloc **voyage / vols (4)** significatif.

**Régions (IDs)** : `73` (52), `12` (49), `15` (10), … — à recouper avec `/regions` pour le sens géographique exact.

**Distribution epcw (toutes offres avec valeur)**  
min ≈ **0** | médiane ≈ **0,37** | max ≈ **21,39**

**Distribution icr**  
min **0,14** | médiane **1,29** | max **147,57**  
→ quelques offres avec **icr très élevé** : traiter comme **signal de risque / complexité** (enchères, friction, qualité d’appel) jusqu’à preuve du contraire via tes stats.

**Distribution key_calls_percent**  
min **0,24** | médiane **7,27** | max **89,53**  
→ utile comme **proxy de “qualité d’intention”** relative (à valider sur **tes** appels facturés).

---

## 2. Segments “métier” (heuristique titre, approximatif)

| Segment (mot-clé titre) | Nb offres | epcw médian (approx.) |
|-------------------------|-----------|------------------------|
| **Flight** | 23 | ≈ 2,99 |
| **Home services** (HVAC, plomberie, toiture, solaire, nuisibles, etc.) | 51 | (hétérogène) |
| **Assurance / ACA / U65** | 34 | (hétérogène) |

Les **vols** ne sont pas la majorité du catalogue, mais plusieurs offres ont un **epcw élevé** (voir §4).

---

## 3. Top “epcw” brut (signal revenu **affiché** Marketcall)

| id | epcw | icr | key% | Titre (extrait) |
|----|------|-----|------|-----------------|
| 6786 | 21,39 | 51,86 | 89,53 | Flight American RAW No refusals Dynamic |
| 10047 | 20,53 | 71,14 | 70,69 | Flight Delta RAW Experience Required No refusals |
| 10056 | 15,71 | 16,43 | 69,65 | Flight United RAW Experience Required No refusal |
| 10072 | 14,56 | 8,14 | 16,77 | Pest Control RTB Only Dynamic |
| 11212 | 13,88 | 0,29 | 21,15 | Home Insurance 120–180s post IVR Dynamic |
| … | … | … | … | (voir CSV complet) |

**Lecture prudente :** un **epcw** élevé avec **icr** élevé peut signifier **plus de concurrence / plus de refus / qualité d’appel plus dure**. Ne pas trier uniquement sur epcw.

---

## 4. Classement “potentiel équilibré” (heuristique interne)

Formule indicative utilisée pour le tableau ci-dessous :  
`score = epcw / (1 + icr/50) * (1 + key_calls_percent/200)`  
→ récompense **epcw** et **key%**, pénalise un peu les **icr** extrêmes. **Ce n’est pas une vérité financière**, uniquement un **tri exploratoire** pour prioriser des tests.

**Top 10 (heuristique)**

1. **10056** — United flight RAW Experience — epcw 15,71, icr 16,43, key 69,65  
2. **11212** — Home Insurance post IVR — epcw 13,88, icr **0,29**, key 21,15  
3. **6786** — American flight RAW No refusals — epcw 21,39, icr 51,86, key 89,53  
4. **10209** — Flooring RTB only — epcw 13,57, icr bas  
5. **10072** — Pest RTB only — epcw 14,56  
6. **12399** — Electrical GMB RTB — epcw 11,5  
7. **12551** — Final Expense RTB — epcw 10,84  
8. **10047** — Delta flight Experience Required — epcw 20,53, icr 71,14  
9. **11323** — Pest & Wildlife Static post IVR — epcw 12,71  
10. **9889** — AT&T GMB 90s post IVR — epcw 10,8  

**Vol / voyage à surveiller aussi (epcw solide, icr modéré)** : **3284** (Changes & cancellations international), **9027** (Delta dynamic), **8665** (International experience required), **6759** / **8796** (Southwest / JetBlue avec **icr très élevé** → test petit budget d’abord).

---

## 5. Promotion sur Google Ads — **cadre conforme** (pas de grey / black hat)

Je **ne décris pas** et **je ne recommande pas** de tactiques **grey hat** ou de contournement des règles (cloaking, marques trompeuses, pages pont, cloaking de policy, faux numéros, etc.). Ce type de pratique expose le compte à **suspension**, au **non-paiement** des appels et au **litige** avec l’acheteur Marketcall.

### Leviers **agressifs mais conformes** (souvent les plus rentables à long terme)

1. **Alignement intention** : mots-clés / annonces / **landing** / script d’accroche téléphonique **cohérents** (aide *Landing page experience* Google).  
2. **Campagnes d’appels** + **extensions d’appel** : numéro **identique** partout, **vérifié**, plages d’affichage = heures où l’offre accepte les appels.  
3. **Search** sur intentions **transactionnelles** (“book … flight”, “change flight”, “cancel flight”, etc.) — en respectant **marques / destinations / pays cibles** de l’offre.  
4. **Remarketing / Customer Match** (si éligible) pour **ré-engager** les clics sans baisser la qualité d’appel.  
5. **Postbacks Marketcall** plutôt que polling API massif (limite **60 req/min** / clé).  
6. **Segmentation** : une **campagne / groupe d’annonces par “famille” d’offre** (vols vs domicile vs assurance) pour isoler CPA et refus.

### Verticals **à sensibilité policy Google** (attention renforcée)

- **Santé / assurance** (U65, ACA, etc.) : politiques **strictes** ; transparence, pays, exclusions, pas de promesses médicales.  
- **Rehab / addiction** : **très sensible** ; éviter le sensationnalisme ; landing claire sur le service.  
- **Crédit / dette** : formulations honnêtes sur le modèle économique.  
- **Télécom / GMB** : souvent **“Experience required”** ou canaux limités — lire les règles Marketcall **avant** d’acheter du trafic Search large.

---

## 6. Effort **site web mobile** (estimation — à affiner par offre)

| Niveau | Critères typiques | Effort indicatif |
|--------|-------------------|------------------|
| **S** | Une landing **statique** par offre ou par famille (tel, identité légale, texte règles résumées, pas de logique métier) | **0,5–2 j** dev + revue conformité |
| **M** | Variantes **géo / langue** (EN/ES), plusieurs **DBA**, pages **légales** distinctes, tracking conversion appel | **2–5 j** |
| **L** | **RTB / intégrations**, **IVR** maison, **smartlinks**, pages **dynamiques** par source, A/B nombreux | **1–3 sem.** équivalent dev (selon stack) |

**Offres “Pre-Approval”, “Experience Required”, “GMB only”, “RTB only”** → presque toujours **M–L** côté process + conformité, pas seulement “une page”.

---

## 7. Idées **supplémentaires** pour sélectionner les offres (hors Google)

1. **Filet de sécurité** : privilégier les offres où tu peux **répondre aux créneaux** et respecter la **durée min d’appel** sans saturer.  
2. **Tester petit** sur les offres **icr extrême** avant scale.  
3. **Corréler** epcw / refus / durée avec les **rapports Marketcall** par *program* (pas seulement l’offre catalogue).  
4. **Diversification** : le CSV montre beaucoup de **home services** — souvent **moins policy-friction** que santé/voyage si landing honnête et géo correcte.  
5. **Régénérer l’export** périodiquement (`scripts/marketcall_fetch_offers.py`) pour capter les **Paused/Active** et nouvelles offres.

---

## 8. Suite possible (données)

- Appeler `GET /categories` et `GET /regions` une fois, **mapper les IDs** en libellés dans le CSV (sans clé dans le dépôt : script + env).  
- Pour chaque **shortlist** (10–15 offres), ouvrir la fiche Marketcall et noter : **GEO**, **heures**, **durée min**, **traffic autorisé**, **motifs de refus** → score manuel **Risque / Effort / Potentiel**.

---

*Document généré pour priorisation interne ; pas un conseil juridique ou fiscal.*
