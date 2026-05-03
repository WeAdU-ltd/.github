# WEA-27 — Google Cloud : inventaire (projets, APIs, OAuth / URIs, doublons)

Document d’ancrage pour le ticket [WEA-27](https://linear.app/weadu/issue/WEA-27/google-cloud-inventaire-projets-uris-oauth-doublons). Il complète la cartographie secrets ([WEA-14](../SECRETS_CARTOGRAPHIE_WEA14.md)) et la chaîne Google OAuth ([WEA-20](https://linear.app/weadu/issue/WEA-20/google-passe-oauth-gmail-drive-docs-sheets-ads-analytics)).

**Dépendance** : le socle secrets ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)) — ce dépôt ne stocke pas de secrets GCP ; les sorties d’inventaire automatisé restent **sans clés** (IDs de projet et noms de services uniquement).

---

## Lien avec doublons AWS / OVH

Les chevauchements de noms de projets, comptes de facturation ou domaines d’redirect OAuth entre **GCP**, **AWS** et **OVH** sont traités dans le périmètre cloud global — voir [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete) (fermeture Replit / bascule cloud). Ce ticket **WEA-27** couvre exclusivement **Google Cloud** ; en cas de doublon inter-cloud, ouvrir ou compléter un ticket dédié référencé depuis WEA-38.

---

## Régénération (script)

Prérequis : [Google Cloud SDK](https://cloud.google.com/sdk) (`gcloud`), compte authentifié avec droits de lecture sur l’organisation ou les projets ciblés.

### Windows (recommandé — zéro variable d’environnement)

Depuis une fenêtre **PowerShell** (7 ou 5.1), dans le clone du dépôt :

```powershell
Set-Location "chemin\vers\ton\clone\.github"
.\scripts\run_gcp_inventory_wea27.ps1
```

Tu peux aussi lancer le `.ps1` par **chemin absolu** depuis n’importe quel dossier courant (le script se place tout seul à la racine du dépôt).

### Linux / macOS ou ligne de commande manuelle

```bash
cd /path/to/clone/of/.github
gcloud auth login   # ou auth application-default login pour CI / machine
# Optionnel : filtrer par dossier parent (resource manager)
export GCP_PARENT='organizations/123456789012'   # ou folders/...
python3 scripts/gcp_inventory_wea27.py -o docs/inventory/WEA-27-google-cloud.md
```

Sous **Windows**, si tu préfères appeler Python directement (PATH différent) :

```powershell
$env:GCLOUD_PATH = "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
python scripts\gcp_inventory_wea27.py -o docs\inventory\WEA-27-google-cloud.md
```

Si `GCLOUD_PATH` est ignoré (vieux script ou environnement bizarre), **mets à jour** (`git pull`) puis passe le chemin en argument :

```powershell
python scripts\gcp_inventory_wea27.py --gcloud "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" -o docs\inventory\WEA-27-google-cloud.md
```

Si ce chemin n’existe pas, affiche le vrai emplacement utilisé par PowerShell puis copie-le dans `GCLOUD_PATH` (de préférence le `gcloud.cmd` du dossier `bin`, pas le `gcloud.ps1` seul) :

```powershell
(Get-Command gcloud).Source
```

Sans variable `GCP_PARENT`, le script interroge la liste des projets accessibles au compte courant (`gcloud projects list`).

### Publier la sortie dans ce dépôt Git (ou non)

La section entre `WEA27_GCP_INVENTORY_*` ne contient en principe **que** des identifiants de projet et des noms d’APIs publics (pas de clés). Tu peux :

- **Ne pas committer** et garder uniquement la copie sur ton disque / Drive partagé (suffisant pour une preuve locale ou une revue perso).
- **Committer** si l’équipe veut une trace partagée : relire le diff (surtout les tableaux OAuth remplis à la main), puis `git add docs/inventory/WEA-27-google-cloud.md`, commit, PR — uniquement quand tu acceptes que ces noms de projets soient visibles dans l’historique public du dépôt.

**OAuth 2.0 (clients web / desktop / redirect URIs)** : l’API publique stable accessible au CLI pour *tous* les clients « APIs & Services → Credentials » n’est pas exposée de façon uniforme par `gcloud` sur tous les projets. Pour une liste exhaustive des **Authorized redirect URIs** et **JavaScript origins**, compléter manuellement la section ci-dessous depuis la console **Google Cloud → APIs & Services → Credentials**, ou activer **Cloud Asset Inventory** et exporter les ressources pertinentes. Le script documente les **services activés** et les **doublons de noms de services** entre projets pour repérer des incohérences.

---

## Incohérences connues à corriger (manuel)

_Remplir lors de la revue humaine ; ne pas committer de données sensibles._

| Projet (ID) | Problème | Action |
|-------------|----------|--------|
| — | — | — |

---

## OAuth clients / URIs (complément manuel)

| Projet | Nom du client (Console) | Type | Redirect URIs / Origins (aperçu) | Notes |
|--------|-------------------------|------|----------------------------------|-------|
| — | — | — | — | — |

---

<!-- WEA27_GCP_INVENTORY_BEGIN -->

_Section générée : exécuter `scripts/gcp_inventory_wea27.py` après authentification `gcloud`._

### Projets (extrait)

| projectId | name | lifecycleState |
|-----------|------|----------------|
| — | _non généré — exécuter le script_ | — |

### APIs activées — résumé

| service | # projets où activé | projets |
|---------|---------------------|---------|
| — | — | — |

### Incohérences détectées (automatique)

- _En attente d’une exécution locale avec `gcloud` authentifié._

<!-- WEA27_GCP_INVENTORY_END -->

---

_Les lignes entre `WEA27_GCP_INVENTORY_*` sont écrasées par le script ; le reste du fichier est éditorial._
