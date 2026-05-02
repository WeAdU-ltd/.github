# Brave Search API — clés, quotas et usage agents (WEA-22)

Document d’ancrage pour le ticket [WEA-22](https://linear.app/weadu/issue/WEA-22/brave-search-api-cles-et-quotas-pour-agents). Il complète le socle secrets ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)) et la cartographie ([WEA-14](https://linear.app/weadu/issue/WEA-14/secrets-cartographie-1password-github-cursor-regle-chercher-avant-de)).

---

## Critères de fait (ticket)

| Critère | Implémentation dans ce dépôt |
|---------|------------------------------|
| **Clé dans secrets** | Convention : variable d’environnement **`BRAVE_SEARCH_API_KEY`** (valeur = clé API Brave Search). À définir dans GitHub Encrypted Secrets (org ou dépôt), secrets Cursor cloud / workspace, ou fichier `.env` **non versionné** — jamais dans le code ou le chat. |
| **Test requête OK** | Script [`scripts/brave_search_smoke_wea22.py`](../scripts/brave_search_smoke_wea22.py) : smoke test HTTP GET vers l’API officielle ; exécuter **après** injection de la clé (CI optionnelle avec secret, ou localement). |

La dépendance [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh) : l’équipe positionne la clé dans le canal secrets convenu (pas ce fichier).

---

## API officielle

- **Web Search** : `GET https://api.search.brave.com/res/v1/web/search`
- **Authentification** : en-tête **`X-Subscription-Token: <clé>`** (pas de clé en query string).
- **Paramètres courants** : `q` (requête), `count` (nombre de résultats, selon plan).

Référence : [Brave Search API — documentation](https://api-dashboard.search.brave.com/documentation), [tableau de bord / clés](https://api-dashboard.search.brave.com/).

---

## Quotas et coûts

- Les **limites** (requêtes / mois, débit) dépendent du **plan** Brave Search API ; elles se consultent sur le **dashboard** Brave (compte API, usage).
- **Agents** : éviter les boucles de recherche en rafale ; privilégier **une** requête ciblée ou des batchs raisonnables, comme pour les autres APIs quota ([règle « chercher avant de demander »](./SECRETS_CARTOGRAPHIE_WEA14.md)).

---

## Vérification locale ou CI

```bash
export BRAVE_SEARCH_API_KEY="***"   # depuis secrets, pas depuis le dépôt
python3 scripts/brave_search_smoke_wea22.py
```

Variables optionnelles :

| Variable | Rôle |
|----------|------|
| `BRAVE_SEARCH_QUERY` | Requête de test (défaut : `Brave Search API`) |
| `BRAVE_SEARCH_COUNT` | Nombre de résultats demandés (défaut : `3`) |

En CI GitHub : ajouter le secret **`BRAVE_SEARCH_API_KEY`** au dépôt (ou à l’org), puis appeler le script dans un job qui expose `secrets.BRAVE_SEARCH_API_KEY` comme variable d’environnement — **uniquement** si l’équipe souhaite un test automatique ; sinon un humain ou un agent avec secret injecté suffit pour le critère « test requête OK ».

---

_Document statique ; mise à jour si Brave change l’URL, les en-têtes ou les noms de plans._
