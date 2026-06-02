# WEA-28 — Audit Agency Plus (facture FR78255331, juin 2026)

Rapport d’audit pour répondre à la question : **faut-il garder l’hébergement Agency Plus (~696 € HT/an) ?**

**Facture** : FR78255331, 01/06/2026, **853,98 € TTC** (WeAdU ltd, nic `pj25000-ovh`).

**Poste principal** : renouvellement **Agency Plus** 12 mois — **695,88 € HT** — hébergement `weadufu.cluster028.hosting.ovh.net`.

---

## 1. Synthèse exécutive

| Question | Réponse |
|----------|---------|
| Agency Plus, c’est quoi ? | Nouveau nom OVH (gamme **Agencies 2027**) pour l’ancienne **Performance 3** ; **695,88 € HT/an** au catalogue ([blog OVH mai 2026](https://blog.ovhcloud.com/en-webhosting-2026/)). |
| Est-ce lié aux apps prod (COS, negative-terms, stocks…) ? | **Non** — ces URLs pointent vers **AWS** (`18.135.12.229`), pas vers le cluster OVH. |
| Est-ce lié à `weadu.com` ? | **Non** — `weadu.com` → `198.202.211.1` + Google Workspace. |
| À quoi sert Agency Plus chez WeAdU ? | Hébergement **mutualisé multisite** : **~220 domaines attachés** (instantané API 2026-05-03), **~8,9 Go** utilisés / quota élevé, CDN actif. |
| Faut-il résilier tout de suite ? | **Non** — sans liste complète des 220 sites, risque SEO / affiliation. |
| Recommandation (juin 2026) | **Garder à court terme**, ouvrir **purge + downgrade** : viser **Agency** (467,88 € HT/an) après audit des multisites ; **ne pas** couper DNS/email OVH avec l’hébergement. |

**Économie potentielle** : **~228 € HT/an** (Agency Plus → Agency) après validation des limites multisite ; plus si purge de sites morts (projet dédié).

---

## 2. Facturation et transition tarifaire OVH 2026

| Élément | Détail |
|---------|--------|
| Montant Agency Plus | **695,88 € HT / an** (= **57,99 € HT / mois**) |
| Ancien tarif Performance 3 (2016) | 356,28 € HT / an (**+95 %**) |
| Ancien tarif Performance 4 (2016) | 448,68 € HT / an — facture dit **Agency Plus**, pas Agency Max (923,88 €) |
| Offre API (mai 2026) | `hosting-performance-4` sur `weadufu.cluster028…` — mapping commercial à confirmer dans le **manager** |
| Renouvellement auto (capture manager) | **01/06/2027** pour hébergement + CDN |
| Avoir transition mai 2026 | OVH annonce remboursement auto si renouvelé avant 01/06 au **ancien** tarif — facture datée **01/06/2026** → **vérifier manuellement** dans [manager OVH](https://www.ovh.com/manager/) → Factures / Avoirs |
| Autres postes facture | Zimbra Starter 0,30 € HT ; CDN Basic inclus ; MX Plans / emails (rubrique non détaillée dans la capture) |

**API billing** (02/06/2026) : clés `OVH_APP_*` → `GET /me/bill`, `/me/order`, `/hosting/web` = **NOT_GRANTED**. Facturation : **console uniquement**.

---

## 3. Ce qui ne justifie pas Agency Plus (déjà ailleurs)

Audit DNS (zone `generads.com` accessible en API + lookups publics) :

| FQDN / service | IP / hébergement | Lien Agency Plus |
|----------------|------------------|------------------|
| `leadgen.generads.com` | AWS `18.135.12.229` | DNS OVH seulement |
| `negative-terms.generads.com` | AWS | idem |
| `staging-negative-terms.generads.com` | AWS | idem |
| `stocks.generads.com` | AWS | idem |
| `dash.generads.com` | AWS | idem |
| `weadu.com` | `198.202.211.1` (hors OVH mutualisé) | — |
| n8n, Wellbots, runner GitHub | AWS ([WEA-29](./WEA-29-aws-ec2-inventory.md)) | — |

**6/30** FQDN échantillonnés (DNS API + marque) = **doublon AWS** : la prod ne consomme pas le CPU/RAM Agency Plus.

---

## 4. Ce qui justifie encore un hébergement OVH (pas forcément Agency Plus)

| FQDN (échantillon audit 02/06/2026) | Catégorie audit | IP |
|-------------------------------------|-----------------|-----|
| `getweadu.com`, `www.getweadu.com` | **active** (HTTP 200) | OVH `213.186.33.5` |
| `weadu.co.uk` | **active** | OVH |
| `weadu.fr` | **unknown** (réponse HTTP ambiguë) | à revoir |
| `weadu.com` | **off_ovh_hosting** | autre hébergeur |

Les **~220 multisites** attachés au cluster (non listés en entier : API hosting **non accordée** au token actuel) représentent le **levier SEO / landing** historique — **8,9 Go** utilisés suggère du contenu réel, pas un plan vide.

---

## 5. Limites de l’audit automatisé (02/06/2026)

| Blocage | Impact |
|---------|--------|
| `OVH_APPLICATION_*` (1Password) | **Credential does not exist** — jeu invalide |
| `OVH_APP_*` + consumer key | Accès **partiel** : `GET /domain/zone` OK ; **`/hosting/web`**, **`/me/bill`**, records sur la plupart des zones = **403 NOT_GRANTED** |
| Liste 220 FQDN | **Non exportée** — instantané mai 2026 ([WEA-28](./WEA-28-ovh-duplicates.md)) inchangé côté API |
| Échantillon audité | **30 FQDN** (zone `generads.com` + domaines marque) |

**Action infra** : régénérer une **consumer key** OVH avec droits `GET /hosting/web/*`, `GET /me/bill`, `GET /domain/zone/*/record` (toutes zones), stocker dans 1Password (`OVH_APPLICATION_*` ou `OVH_APP_*` unifiés), puis relancer :

```bash
export OVH_APPLICATION_KEY=… OVH_APPLICATION_SECRET=… OVH_CONSUMER_KEY=…
python3 scripts/ovh_inventory_wea28.py --export-domains --write /tmp/ovh-snapshot.json
python3 scripts/ovh_audit_agency_plus.py --inventory /tmp/ovh-snapshot.json --write /tmp/ovh-audit-summary.json
```

---

## 6. Scénarios de décision (chiffrage)

| Scénario | Condition | Coût hébergement HT/an | Économie vs actuel | Risque |
|----------|-----------|------------------------|--------------------|--------|
| **A. Garder Agency Plus** | Majorité des 220 sites actifs / SEO | 695,88 € | 0 € | Faible |
| **B. Downgrade → Agency** | Ressources suffisantes, ≤ limite multisite offre Agency | 467,88 € | **~228 €** | Moyen — valider limites OVH |
| **C. Purge + Agency** | >50 % sites morts après audit complet | 467,88 € + temps purge | **228–400 €** | Moyen — SEO |
| **D. Migration statique AWS/S3** | Sites HTML/PHP simples, peu de BDD | ~120–360 € (ordre de grandeur) | variable | Élevé — projet |
| **E. Résiliation hébergement** | 0 site utile sur cluster | 0 € | **695,88 €** | **Très élevé** |

**Renouvellement 24/48 mois** (catalogue OVH) : Agency Plus à **45,99 € / 36,99 € HT/mois** — à comparer si vous **gardez** l’offre.

---

## 7. Recommandation opérationnelle

1. **Court terme** : conserver Agency Plus jusqu’à export des **220 FQDN** (manager ou API élargie).
2. **Vérifier** avoir OVH transition tarifaire (facture 01/06/2026).
3. **Moyen terme** : campagne **purge** sites morts + test **downgrade Agency** (économie **~228 € HT/an**).
4. **Ne pas** confondre avec résiliation **DNS / domaines / MX / Zimbra** — services **séparés** sur la facture.

---

## 8. Scripts ajoutés dans ce dépôt

| Script | Rôle |
|--------|------|
| [`scripts/ovh_inventory_wea28.py`](../../scripts/ovh_inventory_wea28.py) | Inventaire API + `--export-domains` + résolution 1Password SDK |
| [`scripts/ovh_audit_agency_plus.py`](../../scripts/ovh_audit_agency_plus.py) | Classification DNS/HTTP + billing (si droits API) |
| [`scripts/ovh_dns_zone_inventory.py`](../../scripts/ovh_dns_zone_inventory.py) | Export records DNS par zone (gestion erreurs par zone) |

---

## 9. Écart vs critères WEA-28

| Critère WEA-28 | État |
|----------------|------|
| Liste actifs OVH | **Partiel** — zones DNS + hosting mai 2026 ; **220 FQDN non rafraîchis** (API) |
| Décisions garder / migrer / couper | **Mises à jour** — voir [WEA-28 §3](./WEA-28-ovh-duplicates.md) |

Ticket : [WEA-28](https://linear.app/weadu/issue/WEA-28/ovh-inventaire-et-doublons-vs-aws-gcp).
