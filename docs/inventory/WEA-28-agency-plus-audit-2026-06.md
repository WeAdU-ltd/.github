# WEA-28 — Audit Agency Plus (facture FR78255331, juin 2026)

Rapport d’audit pour répondre à la question : **faut-il garder l’hébergement Agency Plus (~696 € HT/an) ?**

**Facture** : FR78255331, 01/06/2026, **853,98 € TTC** (WeAdU ltd, nic `pj25000-ovh`).

**Poste principal** : renouvellement **Agency Plus** 12 mois — **695,88 € HT** — hébergement `weadufu.cluster028.hosting.ovh.net`.

**Audit automatisé** : 2026-06-02, clés 1Password `OVH_WeAdU_Unlimited`, scripts `ovh_inventory_wea28.py` + `ovh_audit_agency_plus.py` (+ sonde Host sur IP cluster).

---

## 1. Synthèse exécutive

| Question | Réponse |
|----------|---------|
| Agency Plus, c’est quoi ? | Gamme **Agencies 2027** (ex **Performance 3** catalogue) — **695,88 € HT/an** ([blog OVH mai 2026](https://blog.ovhcloud.com/en-webhosting-2026/)). |
| Lié aux apps prod (`leadgen`, `negative-terms`, `stocks`…) ? | **Non** — **AWS** `18.135.12.229` ; **generads.com** n’est pas dans les 220 multisites attachés. |
| Lié à `weadu.com` / `getweadu.com` / `weadu.fr` ? | **Non** — ces domaines **ne figurent pas** dans les 220 attachés ; hébergement / DNS ailleurs. |
| À quoi sert Agency Plus ? | **220 entrées multisite** sur le cluster, surtout domaines **SEO compagnies aériennes** (`a2zflights.online`, `airlines.city`, `airlines-usa.com`, etc.) + quelques `keywy.com`, `arasaka-sarl.com`, `*.repair`. |
| Combien sont vraiment « vivants » ? | **~22** répondent en HTTP sur le cluster (sonde `Host:` sur `213.186.33.5`) ; **197** renvoient **404** ; **199** n’ont **aucun** enregistrement DNS public. |
| Faut-il garder Agency Plus ? | **Non au tarif actuel** — payer **~696 € HT/an** pour ~22 sites dont le trafic public passe souvent par **Cloudflare / AWS / autre** est disproportionné. |
| Recommandation | **Purge massive** des multisites morts (199+), **détacher** les 21 dont le DNS ne pointe plus vers OVH, puis **downgrade** (cible **Agency** 467,88 € HT/an ou inférieur selon quota multisite restant). |

**Économie réaliste** : **228–400 € HT/an** (downgrade + purge) ; potentiellement plus si le nombre de multisites actifs tombe sous un palier d’offre inférieur.

---

## 2. Facturation (API OVH, 2026-06-02)

| Ligne facture FR78255331 | Montant HT |
|--------------------------|------------|
| **Agency Plus renewal (12 months)** | **695,88 €** |
| Zimbra Starter monthly pricing | 0,30 € |
| CDN basic option rental 12 months | 0,00 € |
| weadu.fr / weadu.co.uk renouvellement | ~15,77 € |
| Zones DNS / divers | ~0 € |

**TTC** : **853,98 €** (TVA 142,33 €).

| Élément technique | Valeur |
|-------------------|--------|
| Offre API | `hosting-performance-4` |
| Libellé facture | **Agency Plus** |
| Stockage utilisé | ~8,6 Go / 1000 Go |
| Renouvellement auto (manager, mai 2026) | **01/06/2027** |

**Transition tarifaire OVH 2026** : hausse **+95 %** vs ancien Performance 3 (356,28 € → 695,88 € HT). Vérifier dans le manager un **avoir** si renouvellement avant 01/06/2026 au tarif historique (facture datée 01/06/2026).

---

## 3. Résultats audit — 220 multisites attachés

### 3.1 Classification DNS publique (script audit)

| Catégorie | Nombre | Signification |
|-----------|--------|---------------|
| **dns_none** | **199** | Aucune résolution DNS `A`/`AAAA` pour le FQDN — site **inaccessible** depuis Internet tel quel. |
| **off_ovh_hosting** | **21** | DNS pointe vers **Cloudflare**, **AWS**, ou autre — pas vers `213.186.33.x`. |

Aucun FQDN attaché ne pointe vers l’IP mutualisée classique **213.186.33.5** en DNS public.

### 3.2 Sondage direct sur le cluster OVH (`Host:` + IP)

| Population | HTTP 2xx sur cluster | HTTP 4xx / erreur |
|------------|----------------------|-------------------|
| 199 × `dns_none` | **2** | **197** (surtout 404 — entrée multisite **morte**) |
| 21 × `off_ovh_hosting` | **20** | **1** |

**Total « contenu encore servi par le cluster »** : **~22 FQDN** (dont le trafic réel peut aller ailleurs via DNS, ex. `keywy.com` → Cloudflare).

### 3.3 Répartition par suffixe (220 attachés)

| Suffixe | Sites attachés |
|---------|----------------|
| `a2zflights.online` | 42 |
| `airlines.city` | 34 |
| `airlines-usa.com` | 34 |
| `airlines-phone-directory.com` | 27 |
| `airlines-usa.click` | 17 |
| `phoenix-az.repair` / `same-day.repair` | 10 chacun |
| `keywy.com` / `arasaka-sarl.com` | 6 chacun |
| Autres (`change-flights.to`, `same-day.pro`, …) | reste |

### 3.4 Exemples `off_ovh_hosting` (DNS ailleurs, fichier encore sur OVH)

| FQDN | DNS actuel (aperçu) |
|------|---------------------|
| `keywy.com`, `www.keywy.com` | Cloudflare |
| `change-flights.to`, `airlines.change-flights.to` | AWS / parking |
| `pestwipe.com` | Hébergeur tiers |
| `same-day.pro`, `hvac-sys.com` | Autre IP |

→ Candidats à **détachement** du multisite (le trafic ne passe pas par ce cluster).

---

## 4. Ce qui ne dépend pas d’Agency Plus

| Service | Hébergement |
|---------|-------------|
| `*.generads.com` prod (COS, negative-terms, stocks, …) | **AWS** |
| `weadu.com` | Autre IP + Google Workspace |
| `getweadu.com`, `weadu.fr` (marque) | **Pas** dans les 220 multisites — DNS/hébergement séparés |
| Zones DNS OVH, MX, Zimbra | Facturés **à part** |

---

## 5. Scénarios de décision (chiffrage)

| Scénario | Condition | Économie HT/an | Risque |
|----------|-----------|----------------|--------|
| **A. Garder Agency Plus** | Statu quo | 0 € | **Élevé** — surpaiement pour ~22 sites utiles |
| **B. Purge + Agency** | &lt;50 multisites actifs après nettoyage | **~228 €** (695 → 468 €) | Moyen — vérifier quota OVH |
| **C. Purge agressive + offre inférieure** | &lt;10 sites réellement servis | **400–600 €** | Moyen — valider avec OVH commercial |
| **D. Résiliation hébergement** | Aucun site conservé | **695 €** | **Très élevé** si une landing génère encore du CA |

**Recommandation** : **B ou C** — commencer par supprimer les **199** entrées sans DNS + **404** sur cluster, puis détacher les **21** « DNS ailleurs », recompter les multisites restants, **downgrader** avant le 01/06/2027.

---

## 6. Plan d’action opérationnel

1. **Manager OVH** → Hébergements → `weadufu.cluster028…` → multisites : export / suppression par lots (priorité : `dns_none` + 404 confirmés).
2. **Vérifier** les **2** FQDN `dns_none` qui répondent encore en Host-header — seuls à investiguer avant suppression.
3. **Revoir** les **20** `off_ovh_hosting` qui répondent encore sur OVH — migrer fichiers si besoin, puis **détacher**.
4. **Demander downgrade** vers **Agency** (ou offre adaptée au nombre de multisites restants).
5. **Conserver** `OVH_WeAdU_Unlimited` dans 1Password pour scripts ; laisser `OVH_APP_*` en droits restreints pour `pd-detection` si souhaité.

---

## 7. Régénération de l’audit

```bash
export OVH_APPLICATION_KEY=$(python3 scripts/onepassword_resolve_ref.py --print-value "op://Replit/OVH_WeAdU_Unlimited/Application Key")
export OVH_APPLICATION_SECRET=$(python3 scripts/onepassword_resolve_ref.py --print-value "op://Replit/OVH_WeAdU_Unlimited/Application Secret")
export OVH_CONSUMER_KEY=$(python3 scripts/onepassword_resolve_ref.py --print-value "op://Replit/OVH_WeAdU_Unlimited/Consumer Key")

python3 scripts/ovh_inventory_wea28.py --export-domains --write /tmp/ovh-snapshot.json
python3 scripts/ovh_audit_agency_plus.py --inventory /tmp/ovh-snapshot.json --write /tmp/ovh-audit-summary.json --csv /tmp/ovh-audit-sites.csv
```

Ne pas committer `/tmp/ovh-snapshot.json` (liste complète des FQDN).

---

## 8. Scripts

| Script | Rôle |
|--------|------|
| [`scripts/ovh_inventory_wea28.py`](../../scripts/ovh_inventory_wea28.py) | Inventaire API + `--export-domains` |
| [`scripts/ovh_audit_agency_plus.py`](../../scripts/ovh_audit_agency_plus.py) | DNS + HTTP + billing |
| [`scripts/ovh_dns_zone_inventory.py`](../../scripts/ovh_dns_zone_inventory.py) | Records par zone DNS |

Credentials : **`op://Replit/OVH_WeAdU_Unlimited/{Application Key,Application Secret,Consumer Key}`**.

---

## 9. Écart vs critères WEA-28

| Critère | État |
|---------|------|
| Liste actifs OVH | **Fait** — 220 FQDN exportés (2026-06-02) |
| Décisions garder / migrer / couper | **Fait** — purge + downgrade ; voir [WEA-28 §3](./WEA-28-ovh-duplicates.md) |

Ticket : [WEA-28](https://linear.app/weadu/issue/WEA-28/ovh-inventaire-et-doublons-vs-aws-gcp).
