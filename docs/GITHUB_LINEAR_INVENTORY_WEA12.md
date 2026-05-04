# Inventaire GitHub ↔ Linear (WEA-12)

Document d’ancrage pour le ticket [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces). Les sections **générées** ci-dessous sont remplies ou écrasées par le script `scripts/linear_github_inventory_wea12.py`. Voir aussi la cartographie secrets / 1Password / Cursor : [`SECRETS_CARTOGRAPHIE_WEA14.md`](./SECRETS_CARTOGRAPHIE_WEA14.md) ([WEA-14](https://linear.app/weadu/issue/WEA-14/secrets-cartographie-1password-github-cursor-regle-chercher-avant-de)).

**Origine** : même contenu que la proposition [Negative-Terms#638](https://github.com/WeAdU-ltd/Negative-Terms/pull/638), adaptée au dépôt `WeAdU-ltd/.github`.

---

## Régénération

Prérequis : variables d’environnement `LINEAR_API_KEY` et `GITHUB_TOKEN` (droits lecture repos org + Linear).

```bash
cd /path/to/clone/of/.github
export LINEAR_API_KEY=...
export GITHUB_TOKEN=...
# Optionnel : équipe Linear (sinon `WEA`)
export LINEAR_TEAM_KEY=WEA
# Optionnel : organisations GitHub à scanner (sinon déduction depuis les labels `repo`)
python3 scripts/linear_github_inventory_wea12.py -o docs/GITHUB_LINEAR_INVENTORY_WEA12.md --github-org WeAdU-ltd --markdown-label-prefix "WeAdU-ltd/"
```

---

## Décision : agents sans label `repo`

- Ne pas se fier au dépôt par défaut du tableau de bord Cursor.
- Exiger **un** sous-label du groupe Linear **`repo`** (format `owner/repo`, convention **`WeAdU-ltd/…`**) **ou** une consigne explicite dans le ticket du type `@Cursor` + `[repo=owner/repo]`.
- Détail et extension : [WEA-17](https://linear.app/weadu/issue/WEA-17).

---

## Compatibilité `chain` vs `repo`

- **`chain`** : ordre / séquence des sous-tickets (workflow), pas le choix du dépôt Git.
- **`repo`** : cible GitHub pour les agents. Orthogonal à `chain`.

---

<!-- WEA12_INVENTORY_BEGIN -->

_Généré le 2026-05-04 21:27:59 (UTC)._
_Tableau des labels `repo` **filtré** : noms commençant par `WeAdU-ltd/` (périmètre société WeAdU-ltd). Les calculs « dépôts sans label » et « tickets sans repo » restent basés sur **tous** les enfants du groupe `repo` dans Linear._

### Labels Linear (groupe `repo`) → dépôt GitHub

| Label Linear (`owner/repo`) | URL GitHub |
|----------------------------|------------|
| `WeAdU-ltd/.github` | https://github.com/WeAdU-ltd/.github |
| `WeAdU-ltd/Negative-Terms` | https://github.com/WeAdU-ltd/Negative-Terms |
| `WeAdU-ltd/SH-Checker-Bids` | https://github.com/WeAdU-ltd/SH-Checker-Bids |

### Dépôts GitHub sans label Linear correspondant

_Organisations scannées : WeAdU-ltd._

| Dépôt | Note |
|-------|------|
| — | Aucun trou dans le périmètre scanné |

### Tickets Linear ouverts (équipe configurée), sans sous-label `repo`

| Issue | Mis à jour | Titre |
|-------|------------|-------|
| — | — | — |

<!-- WEA12_INVENTORY_END -->

---

_Les lignes entre les marqueurs `WEA12_INVENTORY_*` sont écrasées par le script ; régénérer après changement de labels ou de dépôts._
