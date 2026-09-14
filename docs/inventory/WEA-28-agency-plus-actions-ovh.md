# WEA-28 — « Supprimer » vs « détacher » un multisite OVH

Vocabulaire pour l’hébergement mutualisé `weadufu.cluster028.hosting.ovh.net`.

## Ce qu’est un « multisite attaché »

Sur l’offre **Agency Plus**, OVH permet d’associer jusqu’à **N noms** (domaines / sous-domaines) au **même** hébergement. Pour chaque nom :

- le serveur web du cluster sait répondre quand l’en-tête HTTP `Host:` vaut ce nom ;
- des fichiers peuvent exister dans un répertoire dédié (FTP / File Manager) ;
- cela **compte** dans le quota « multisites » de l’offre.

Cela **ne signifie pas** que le domaine est enregistré chez OVH, ni que le DNS public pointe vers OVH.

## Détacher (recommandé dans la plupart des cas)

**Action dans le manager** : Hébergements → votre hébergement → **Multisite** / **Domaines attachés** → **Détacher** / **Supprimer le domaine attaché** (libellé OVH variable).

**Effet** :

- le nom n’est plus lié au plan d’hébergement ;
- le trafic n’est plus servi par ce vhost sur le cluster (sauf autre config) ;
- les **fichiers** sur le FTP peuvent **rester** jusqu’à suppression manuelle ;
- le **nom de domaine** (registrar), la **zone DNS** et les **e-mails** ne sont **pas** supprimés automatiquement.

**Quand** : DNS absent ou pointe ailleurs (Cloudflare, AWS…), ou HTTP 404 sur le cluster → entrée multisite **inutile** mais vous payez encore la capacité de l’offre.

## Supprimer (précision — ne pas confondre)

Dans l’audit, « supprimer » voulait dire **retirer l’entrée multisite** (= **détacher**), **pas** :

| Action destructive | Conséquence |
|--------------------|-------------|
| Supprimer le **nom de domaine** chez OVH | Perte du domaine à l’échéance |
| Supprimer la **zone DNS** | Casse mail / sous-domaines |
| Supprimer les **fichiers** FTP | Perte du site sur le disque |
| **Résilier** l’hébergement Agency Plus | Arrêt de tout le cluster (220 sites) |

Après **détachement** en masse, vous pourrez **downgrader** l’offre (ex. Agency Plus → Agency) si le nombre de multisites restants le permet.

## Tableau des 220 domaines

Fichier CSV (import Google Sheets : Fichier → Importer) :

[`WEA-28-agency-plus-multisites-2026-06.csv`](./WEA-28-agency-plus-multisites-2026-06.csv)

Colonnes : FQDN, DNS public, IP DNS, HTTP via DNS, HTTP via cluster (sonde Host), catégorie, situation, action recommandée.
