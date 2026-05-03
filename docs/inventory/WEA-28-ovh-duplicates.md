# WEA-28 — OVH : inventaire et doublons (vs AWS, GCP…)

Document d’ancrage pour le ticket [WEA-28](https://linear.app/weadu/issue/WEA-28/ovh-inventaire-et-doublons-vs-aws-gcp) dans le dépôt **`WeAdU-ltd/.github`**.

**Dépendance** : le ticket indique une dépendance à [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh) (socle secrets). Les **secrets** (mot de passe manager, clés API complètes) ne doivent **pas** être copiés dans ce fichier ; ils vivent dans 1Password (coffre d’équipe, ex. `Replit` : entrées `OVHcloud`, `OVH_APPLICATION_*`, `OVH_CONSUMER_KEY`, etc.). Ici : **noms publics, inventaire API, décisions**.

**Source des données ci-dessous** : appels en **lecture seule** à l’API OVHcloud EU (`https://eu.api.ovh.com/1.0`) avec les trois variables `OVH_APPLICATION_KEY`, `OVH_APPLICATION_SECRET`, `OVH_CONSUMER_KEY` (fournies via `op run` ou l’environnement agent). **Instantané** : 2026-05-03 (compte nic `pj25000-ovh`, filiale FR).

**Regénération** : voir [section 5](#5-regénération-inventaire-api).

**Console** : [Espace client OVHcloud](https://www.ovh.com/manager/) pour facturation, renouvellements et détails non exposés par l’API.

---

## 1. Actifs OVH (liste)

### 1.1 Noms de domaine (zones DNS gérées chez OVH)

| Zone DNS | Rôle (aperçu) | Notes |
|----------|---------------|-------|
| `generads.com` | Zone active | Croiser avec usages e-mail / sites |
| `getweadu.com` | Zone active | |
| `weadu.co.uk` | Zone active | |
| `weadu.com` | Zone active | Marque / prod probable |
| `weadu.fr` | Zone active | |
| `xn--natureetdcouvertes-jwb.com` | Zone active | IDN (libellé humain : nature et découvertes) |
| `zananas.mq` | Zone active | |

### 1.2 VPS / instances / Public Cloud

| Nom / hostname | Région | Rôle | Notes |
|----------------|--------|------|-------|
| *(aucun)* | — | — | `GET /vps` → liste vide au 2026-05-03 |

### 1.3 E-mail (domaines « e-mail OVH » déclarés)

| Domaine | Notes |
|---------|-------|
| `arasaka-sarl.com` | Présent en e-mail, **absent** des zones DNS §1.1 (hébergement DNS ailleurs ou zone non API) |
| `blada.gf` | Idem |
| `generads.com` | Aussi zone DNS §1.1 |
| `getweadu.com` | Idem |
| `keywy.com` | Idem |
| `verifiedcoupons.shop` | Idem |
| `weadu.co.uk` | Idem |
| `weadu.com` | Idem |
| `weadu.fr` | Idem |
| `xn--natureetdcouvertes-jwb.com` | Idem |
| `zananas.mq` | Idem |

### 1.4 Hébergement web / bases / fichiers

| Hébergement | Offre / état | Stockage | Multisites | Notes |
|-------------|--------------|----------|------------|-------|
| `weadufu.cluster028.hosting.ovh.net` | `hosting-performance-4`, **active**, DC `eu-west-gra`, CDN **oui** | ~8,9 Go utilisés sur **1000** Go quota | **220** noms (domaines / sous-domaines attachés) | Très fort levier SEO / risque migration ; ne pas lister les 220 FQDN dans le dépôt (sortie JSON locale possible via script) |

### 1.5 Autres (IP dédiées, Public Cloud, serveurs dédiés)

| Service OVH | Inventaire API (2026-05-03) |
|-------------|-----------------------------|
| IP / Failover | `GET /ip` → **aucune** entrée |
| Public Cloud | `GET /cloud/project` → **aucun** projet |
| Serveurs dédiés | `GET /dedicated/server` → **aucun** |
| VPS | `GET /vps` → **aucun** |

---

## 2. Doublons et chevauchements (vs AWS, GCP, autres)

L’API OVH ne voit **pas** les actifs AWS / GCP : le tableau reste **à compléter** après lecture de l’inventaire GCP ([WEA-27](https://linear.app/weadu/issue/WEA-27/google-cloud-inventaire-projets-uris-oauth-doublons)) et de toute cartographie AWS.

| Actif OVH (réf. section 1) | Recouvrement possible | Fournisseur / ressource cible | Gravité | Action proposée (voir section 3) |
|----------------------------|------------------------|-------------------------------|---------|----------------------------------|
| 220 multisites sur hébergement mutualisé | Sites ou landing pages déjà servis depuis un bucket / Cloud Run / autre | GCP / AWS / autre | Coût + complexité migration + SEO | **À valider** avec inventaire cloud ; plan de migration par vagues si doublon |
| Zones DNS weadu* / génériques | DNS géré chez un autre registrar ou Cloud DNS | GCP / AWS / Cloudflare | Divergence NS si double pilotage | **À valider** (qui est maître NS pour chaque TLD) |
| Messagerie sur domaines §1.3 | Google Workspace / Gmail / autre MX | Google / autre | Double fournisseur si MX déjà basculés | Vérifier enregistrements MX réels par domaine (hors API seule) |

**Références internes** : inventaire Google Cloud [WEA-27](https://linear.app/weadu/issue/WEA-27/google-cloud-inventaire-projets-uris-oauth-doublons) ; inventaire GitHub / déploiements [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces).

---

## 3. Décisions brouillon — garder / migrer / couper

| Actif ou groupe | Décision | Cible si migration | Dépendances | Notes |
|-----------------|----------|--------------------|-------------|-------|
| Zones DNS §1.1 | **Garder** (brouillon) | — | Alignement avec stratégie DNS globale | Rien n’indique côté API un second hébergeur DNS |
| Hébergement `weadufu.cluster028…` + multisites | **Garder** / **Migrer** (à trancher) | GCP / AWS / autre si doublon avéré | WEA-27, analyse coût, runbook DNS + TLS | Volume multisite élevé : migration = projet dédié |
| E-mail domaines §1.3 | **Garder** (brouillon) | — | Vérification MX réelle | Compléter si messagerie déjà partiellement ailleurs |
| VPS / Public Cloud / IP OVH | **Couper** ou *non applicable* | — | — | Aucun actif listé au 2026-05-03 |

---

## 4. Suite opérationnelle

1. Croiser la section 2 avec les projets GCP / stacks AWS réels (WEA-27 et runbooks internes).
2. Si besoin de **lister les 220 FQDN** : exécuter le script localement, sortie JSON (`--write`) — ne pas committer cette liste en masse sans revue (PII / spam / historique).
3. Après validation humaine des critères de fait sur Linear, mettre à jour les décisions §3 et ouvrir les sous-tickets de migration ou de résiliation si besoin.

---

## 5. Regénération inventaire (API)

Prérequis : [CLI 1Password](https://developer.1password.com/docs/cli) (`op`) et accès lecture aux entrées `OVH_APPLICATION_KEY`, `OVH_APPLICATION_SECRET`, `OVH_CONSUMER_KEY` (chemins 1Password ajustables).

```bash
# Copier l’exemple vers un fichier local (gitignored) et adapter les chemins op:// si besoin
cp scripts/ovh_inventory_wea28.op.env.example scripts/ovh_inventory_wea28.op.env

op run --no-masking --env-file=scripts/ovh_inventory_wea28.op.env -- \
  python3 scripts/ovh_inventory_wea28.py --json
```

Variables d’environnement alternatives : définir `OVH_APPLICATION_KEY`, `OVH_APPLICATION_SECRET`, `OVH_CONSUMER_KEY` (valeurs en clair ou références `op://…`) sans fichier env.
