# Google Ads + Analytics — API agents (WEA-21)

Document d’ancrage pour le ticket [WEA-21](https://linear.app/weadu/issue/WEA-21/google-ads-analytics-api-agents-autonomie-note-risque). Il complète le runbook OAuth ([WEA-20](./GOOGLE_OAUTH_WEA20.md)), le socle secrets ([WEA-15](./SECRETS_SOCLE_WEA15.md)) et l’inventaire GCP ([WEA-27](./inventory/WEA-27-google-cloud.md)).

**Dépendance Linear** : ce ticket est **bloqué par** [WEA-20](https://linear.app/weadu/issue/WEA-20/google-passe-oauth-gmail-drive-docs-sheets-ads-analytics) (passe OAuth / clients GCP). Tant que WEA-20 n’est pas satisfait, traiter ce fichier comme **spécification** ; les preuves « critères de fait » du ticket WEA-21 se valident une fois les clients et scopes en place.

---

## Noms des secrets / comptes (valeurs hors dépôt)

| Nom (variable ou secret d’organisation) | Rôle |
|----------------------------------------|------|
| `GOOGLE_OAUTH_CLIENT_ID` | Identifiant client OAuth (Web ou Desktop selon le consommateur) — pas la valeur dans le dépôt. |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Secret client OAuth ; stockage WEA-15 uniquement. |
| `GOOGLE_OAUTH_REFRESH_TOKEN` | Jeton de rafraîchissement utilisateur (flux installé / bureau ou échange serveur) pour obtenir des `access_token` sans interaction à chaque run. |
| `GOOGLE_OAUTH_ACCESS_TOKEN` | Jeton d’accès court ; souvent **dérivé** en CI ou par l’agent au moment du run (ne pas versionner). |
| `GOOGLE_ADS_DEVELOPER_TOKEN` | **Developer token** Google Ads (compte manager / API Center) ; requis pour les appels REST et gRPC Google Ads en plus du bearer OAuth. |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | Optionnel : ID client Google Ads du **MCC** (chiffres, sans tirets) pour l’en-tête `login-customer-id` quand l’accès passe par un compte manager. |
| Compte de service GCP (nom logique, ex. `google-ads-analytics-agent`) | Alternative **serveur à serveur** : clé JSON **non** commitée ; IAM sur le projet GCP ; pour les APIs Google « cloud », pas un substitut automatique du **developer token** Ads ni du lien OAuth compte Ads sans configuration Ads spécifique. |

Les scopes OAuth utiles sont listés dans [GOOGLE_OAUTH_WEA20.md](./GOOGLE_OAUTH_WEA20.md) (sections Google Ads et Google Analytics). Pour le smoke script ci-dessous : accès **lecture** Analytics Admin (`analytics.readonly` ou équivalent selon la méthode) et scope Ads (`adwords`).

---

## Risque (autonomie agents)

Les agents autorisés à appeler ces APIs peuvent, selon les scopes et comptes réels, **lire des données business sensibles** (coûts, audiences, conversions) ou **modifier** budgets, campagnes, entités Analytics (propriétés, flux, audiences). Il n’y a **pas** de plafond imposé par le ticket : la maîtrise du risque repose sur **scopes minimaux**, **comptes de test** / environnements dédiés, **revue humaine** des changements destructifs, **audit** des journaux GCP et Google Ads, et **séparation** des identités (OAuth prod vs lab). Une erreur d’agent ou un prompt injection peut déclencher des écritures coûteuses ou des fuites de mesure ; documenter qui approuve l’activation « write » en production.

---

## Test minimal d’appel API (lecture)

Script : [`scripts/google_ads_analytics_smoke_wea21.py`](../scripts/google_ads_analytics_smoke_wea21.py).

| Appel | Méthode REST | Condition |
|-------|----------------|-----------|
| **Google Analytics Admin** | `GET https://analyticsadmin.googleapis.com/v1beta/accountSummaries?pageSize=1` | `GOOGLE_OAUTH_ACCESS_TOKEN` avec scope Analytics Admin en lecture. |
| **Google Ads** | `GET https://googleads.googleapis.com/v{version}/customers:listAccessibleCustomers` | Même bearer + en-tête `developer-token` (`GOOGLE_ADS_DEVELOPER_TOKEN`) ; `GOOGLE_ADS_API_VERSION` optionnel (défaut `v21`). |

Obtenir un `access_token` : flux documenté sous WEA-20 (échange refresh token, ou bibliothèque OAuth adaptée à l’agent) — ne pas coller de jeton dans le dépôt ni dans le chat.

```bash
export GOOGLE_OAUTH_ACCESS_TOKEN="***"   # depuis flux OAuth / secret injecté
export GOOGLE_ADS_DEVELOPER_TOKEN="***"  # pour inclure l’appel Ads
# optionnel : export GOOGLE_ADS_LOGIN_CUSTOMER_ID="1234567890"
python3 scripts/google_ads_analytics_smoke_wea21.py
```

CI sans secrets : `python3 scripts/google_ads_analytics_smoke_wea21.py --dry-run`

---

## Chemin pour écriture (hors smoke)

Les smoke tests ci-dessus sont **lecture seule**. Pour les modifications autonomes **acceptées** par l’organisation :

| Produit | Direction | Exemples de surface (à implémenter hors de ce smoke) |
|---------|-----------|------------------------------------------------------|
| **Google Ads** | Write | `googleads.googleapis.com` — ressources `customers/*/campaigns`, `campaignBudgets`, `adGroups`, mutations via **Google Ads API** (REST ou gRPC) avec les mêmes en-têtes `Authorization` + `developer-token` (+ `login-customer-id` si MCC). Référence : [Google Ads API](https://developers.google.com/google-ads/api/docs/start). |
| **Google Analytics (GA4)** | Write | **Analytics Admin API** — création / mise à jour de propriétés, flux de données, audiences (`properties/...` en PATCH ou méthodes dédiées selon ressource). Référence : [Admin API](https://developers.google.com/analytics/devguides/config/admin/v1). |
| **Rapports / données** | Read / export | **Analytics Data API** (rapports, audiences) — distinct de l’Admin API ; scopes et quotas séparés. |

Toute écriture doit être alignée avec la section **Risque** (approbation, comptes de test, journalisation).

---

## Critères de fait (WEA-21) — lien avec ce dépôt

| Critère | Où c’est couvert |
|---------|------------------|
| Tokens / compte de service ou OAuth documentés (**noms seulement**) | Tableau « Noms des secrets » ci-dessus + [GOOGLE_OAUTH_WEA20.md](./GOOGLE_OAUTH_WEA20.md). |
| Test minimal d’appel API (read) + chemin pour write | Script smoke (read) ; section « Chemin pour écriture ». |

---

_Document statique ; ajuster les versions d’API Ads (`v21`, etc.) quand l’équipe fige une version supportée._
