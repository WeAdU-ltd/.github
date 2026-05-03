# Brave Search API — clés, quotas et usage agents (WEA-22)

Document d’ancrage pour le ticket [WEA-22](https://linear.app/weadu/issue/WEA-22/brave-search-api-cles-et-quotas-pour-agents). Il complète le socle secrets ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)) et la cartographie ([WEA-14](https://linear.app/weadu/issue/WEA-14/secrets-cartographie-1password-github-cursor-regle-chercher-avant-de)).

---

## Critères de fait (ticket)

| Critère | Implémentation dans ce dépôt |
|---------|------------------------------|
| **Clé dans secrets** | La clé vit dans **1Password**, **GitHub** (secrets Actions org ou dépôt) et **Cursor** (workspace / cloud), pas dans le dépôt. Au runtime, les agents lisent l’une des variables d’environnement suivantes (même valeur) : **`BRAVE_SEARCH_API_KEY`** (nom préféré) ou **`Brave_API`** (alias si déjà mappé ainsi). Fichier `.env` local **non versionné** possible — jamais dans le code ou le chat. |
| **Test requête OK** | Script [`scripts/brave_search_smoke_wea22.py`](../scripts/brave_search_smoke_wea22.py) : smoke test HTTP GET vers l’API officielle ; exécuter **après** injection de la clé (CI optionnelle avec secret, ou localement). |

La dépendance [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh) : le socle secrets (1Password ↔ GitHub ↔ Cursor) est la source de vérité opérationnelle ; ce fichier ne fait que documenter les noms exposés aux jobs et agents.

---

## Où est la clé (équipe)

| Lieu | Rôle |
|------|------|
| **1Password** | Stockage humain / rotation ; ne pas coller la valeur dans Linear ou le chat. |
| **GitHub** | Secrets chiffrés (org ou dépôt) ; mapper vers `BRAVE_SEARCH_API_KEY` ou `Brave_API` dans le workflow (`env:` / `secrets:`). |
| **Cursor** | Secrets du workspace / agent cloud injectés comme variables d’environnement au lancement. |

Les deux noms **`BRAVE_SEARCH_API_KEY`** et **`Brave_API`** sont utilisés côté équipe : le script de smoke test et les intégrations doivent accepter l’un ou l’autre (voir ci-dessous).

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
export BRAVE_SEARCH_API_KEY="***"   # ou : export Brave_API="***" — depuis 1Password / GitHub / Cursor, pas depuis le dépôt
python3 scripts/brave_search_smoke_wea22.py
```

Le script cherche la clé dans cet ordre : **`BRAVE_SEARCH_API_KEY`**, puis **`Brave_API`** (les deux ne sont pas nécessaires en même temps).

Variables optionnelles :

| Variable | Rôle |
|----------|------|
| `BRAVE_SEARCH_QUERY` | Requête de test (défaut : `Brave Search API`) |
| `BRAVE_SEARCH_COUNT` | Nombre de résultats demandés (défaut : `3`) |

En CI GitHub : le secret peut s’appeler **`BRAVE_SEARCH_API_KEY`** ou **`Brave_API`** dans l’UI GitHub ; exposez-le au job sous l’une des deux variables d’environnement ci-dessus (ex. `env: { BRAVE_SEARCH_API_KEY: ${{ secrets.BRAVE_SEARCH_API_KEY }} }`). **Uniquement** si l’équipe souhaite un test automatique ; sinon un humain ou un agent avec secret injecté suffit pour le critère « test requête OK ».

---

_Document statique ; mise à jour si Brave change l’URL, les en-têtes ou les noms de plans._
