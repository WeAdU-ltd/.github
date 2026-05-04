# WEA-27 — Google Cloud : inventaire (projets, APIs, OAuth / URIs, doublons)

Document d’ancrage pour le ticket [WEA-27](https://linear.app/weadu/issue/WEA-27/google-cloud-inventaire-projets-uris-oauth-doublons). Il complète la cartographie secrets ([WEA-14](../SECRETS_CARTOGRAPHIE_WEA14.md)) et la chaîne Google OAuth ([WEA-20](https://linear.app/weadu/issue/WEA-20/google-passe-oauth-gmail-drive-docs-sheets-ads-analytics)).

**Dépendance** : le socle secrets ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)) — ce dépôt ne stocke pas de secrets GCP ; les sorties d’inventaire automatisé restent **sans clés** (IDs de projet et noms de services uniquement).

---

## Lien avec doublons AWS / OVH

Les chevauchements de noms de projets, comptes de facturation ou domaines d’redirect OAuth entre **GCP**, **AWS** et **OVH** sont traités dans le périmètre cloud global — voir [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete) (fermeture Replit / bascule cloud). Ce ticket **WEA-27** couvre exclusivement **Google Cloud** ; en cas de doublon inter-cloud, ouvrir ou compléter un ticket dédié référencé depuis WEA-38.

---

## Régénération (script)

Prérequis : [Google Cloud SDK](https://cloud.google.com/sdk) (`gcloud`), compte authentifié avec droits de lecture sur l’organisation ou les projets ciblés.

```bash
cd /path/to/clone/of/.github
gcloud auth login   # ou auth application-default login pour CI / machine
# Optionnel : filtrer par dossier parent (resource manager)
export GCP_PARENT='organizations/123456789012'   # ou folders/...
python3 scripts/gcp_inventory_wea27.py -o docs/inventory/WEA-27-google-cloud.md
```

Sans variable `GCP_PARENT`, le script interroge la liste des projets accessibles au compte courant (`gcloud projects list`).

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

## Snapshot manuel — projet `weadu-shared-auth` (2026-05-04)

Référence figée pour éviter de reposer la question « qu’est-ce qui est déjà activé ? » sur ce projet d’auth partagé.

| Champ | Valeur |
|-------|--------|
| **projectId** | `weadu-shared-auth` |
| **Console** | [APIs & Services — Dashboard](https://console.cloud.google.com/apis/dashboard?project=weadu-shared-auth) |
| **Source** | Export console / PDF équipe (38 APIs enabled, même liste que le dashboard). |

### APIs activées (liste complète au 2026-05-04)

| API |
|-----|
| Analytics Hub API |
| Apps Script API |
| BigQuery API |
| BigQuery Connection API |
| BigQuery Data Policy API |
| BigQuery Data Transfer API |
| BigQuery Migration API |
| BigQuery Reservation API |
| BigQuery Storage API |
| Cloud Dataplex API |
| Cloud Datastore API |
| Cloud Logging API |
| Cloud Monitoring API |
| Cloud SQL |
| Cloud Storage |
| Cloud Storage API |
| Cloud Trace API |
| Content API for Shopping |
| Dataform API |
| Gemini API |
| Gmail API |
| Google Ads API |
| Google Analytics Admin API |
| Google Analytics API |
| Google Calendar API |
| Google Cloud APIs |
| Google Cloud Storage JSON API |
| Google Docs API |
| Google Drive API |
| Google Search Console API |
| Google Sheets API |
| Google Tasks API |
| Local Services API |
| Merchant API |
| Real-time Bidding API |
| Service Management API |
| Service Usage API |
| YouTube Data API v3 |

### Alignement avec la chaîne agents / OAuth ([WEA-20](../GOOGLE_OAUTH_WEA20.md))

Les APIs **déjà activées** sur ce projet couvrent Gmail, Drive, Docs, Sheets, Ads, Analytics (y compris Admin) et un large périmètre data / marketing. Rien d’**obligatoire** en plus pour WEA-20 / WEA-24 sur la base de ce snapshot.

**Optionnel (activer seulement si un workflow futur l’exige)** — souvent absent tant que personne ne consomme l’API :

| API | Usage typique |
|-----|----------------|
| **People API** | Contacts / fusion avec profil Google (rare pour nos smokes ; Gmail/Drive n’en ont pas besoin par défaut). |

Pour une liste régénérable par script (`gcloud`), utiliser la section [Régénération (script)](#régénération-script) ci-dessus.

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
