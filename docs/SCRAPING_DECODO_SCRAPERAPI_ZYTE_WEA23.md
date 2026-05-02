# Scraping — Decodo, ScraperAPI, Zyte (WEA-23)

Document d’ancrage pour le ticket [WEA-23](https://linear.app/weadu/issue/WEA-23/scraping-decodo-scraperapi-zyte-cles-routage). Il complète la cartographie des secrets ([WEA-14](https://linear.app/weadu/issue/WEA-14/secrets-cartographie-1password-github-cursor-regle-chercher-avant-de), [`SECRETS_CARTOGRAPHIE_WEA14.md`](./SECRETS_CARTOGRAPHIE_WEA14.md)) et s’aligne sur le socle secrets ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)) : **noms de variables et routage** ici ; **stockage effectif** des valeurs (coffre, GitHub Secrets, injection agent) selon les conventions validées en WEA-15.

---

## Inventaire des clés (convention agents / CI)

Les agents et les workflows doivent **lire** les identifiants depuis l’environnement ou les secrets injectés, jamais depuis le dépôt en clair.

| Fournisseur | Rôle | Variables d’environnement recommandées | Doc officielle (point d’entrée) |
|-------------|------|------------------------------------------|-----------------------------------|
| **Decodo** | Scraping managé (proxies, anti-bot, rendu JS selon offre), sorties structurées | `DECODO_USERNAME` + `DECODO_PASSWORD` (auth Basic), ou équivalent token si le tableau de bord expose un seul secret — à aligner sur le libellé du compte | [Decodo — Web Scraping API (introduction)](https://help.decodo.com/docs/web-scraping-api-introduction) |
| **ScraperAPI** | Rendu optionnel, rotation de proxies, paramètres simples via URL | `SCRAPERAPI_API_KEY` (passée en `api_key=` selon la doc du produit) | [ScraperAPI — documentation](https://www.scraperapi.com/documentation/) |
| **Zyte** | Extraction à fort taux de réussite (Zyte API / plateforme), cas difficiles | `ZYTE_API_KEY` | [Zyte — documentation](https://docs.zyte.com/) |

Si un dépôt applicatif utilise d’autres noms (`secrets.DECODO_*` dans GitHub Actions, etc.), **documenter le mapping** dans le README ou le workflow appelant pour que les agents ne « devinent » pas.

---

## Matrice « cas → fournisseur » (qualité vs coût)

Règle d’or : **commencer par le moins coûteux qui suffit** ; monter d’un cran si échecs répétés (403, CAPTCHA, HTML vide, timeouts).

| Cas d’usage | Fournisseur privilégié | Pourquoi |
|-------------|------------------------|-----------|
| Page statique ou API JSON, peu de protection | **ScraperAPI** (sans options lourdes) ou requête directe hors fournisseur si autorisé | Coût généralement plus maîtrisable pour du volume « simple » |
| Site avec JS léger, anti-bot modéré, besoin rapide sans orchestrer les proxies | **ScraperAPI** avec options adaptées (selon doc : render, pays, etc.) | Bon compromis simplicité / coût |
| E-commerce, moteurs de recherche, sites agressifs, besoin de fiabilité élevée ou formats riches (ex. structuration) | **Decodo** | Offre « tout-en-un » orientée succès et volumétrie ; ajuster pool premium vs standard côté compte |
| Cas très difficiles, extraction structurée avancée, SLA / tooling plateforme Zyte | **Zyte** | Souvent le choix « qualité max » quand les deux autres échouent ou quand l’équipe standardise sur Zyte API |

**Anti-patterns**

- Activer partout le niveau « premium » ou Zyte pour du contenu public trivial : **surcoût**.
- Enchaîner les trois fournisseurs sur chaque URL sans critère : **définir** une cascade (ex. direct → ScraperAPI → Decodo → Zyte) dans le code ou le runbook du dépôt concerné.

---

## Où chercher les valeurs (agents)

1. Secrets du **dépôt** / **organisation** GitHub et variables d’environnement du job (voir [WEA-14](https://linear.app/weadu/issue/WEA-14/secrets-cartographie-1password-github-cursor-regle-chercher-avant-de)).
2. Injection **Cursor Cloud** / workspace si le produit le prévoit.
3. **1Password** ou coffre équipe **en dernier recours**, une lecture ciblée (même principe que `SECRETS_CARTOGRAPHIE_WEA14.md`).

---

_Document statique ; réviser après clôture du socle secrets (WEA-15) ou changement de tarifs / noms de produits côté fournisseurs._
