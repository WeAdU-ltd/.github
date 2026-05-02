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
python3 scripts/linear_github_inventory_wea12.py -o docs/GITHUB_LINEAR_INVENTORY_WEA12.md
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

### Labels Linear (groupe `repo`) → dépôt GitHub

_(Non généré — exécuter le script avec `-o docs/GITHUB_LINEAR_INVENTORY_WEA12.md`.)_

| Label Linear (`owner/repo`) | URL GitHub |
|-----------------------------|------------|
| — | — |

### Dépôts GitHub sans label Linear correspondant

_(Scan limité aux organisations passées en `--github-org` ou déduites des labels.)_

| Dépôt | Note |
|-------|------|
| — | — |

### Tickets Linear ouverts (équipe configurée), récents sans sous-label `repo`

| Issue | Mis à jour | Titre |
|-------|------------|-------|
| — | — | — |

<!-- WEA12_INVENTORY_END -->

---

_Dernière mise à jour manuelle de ce squelette : génération CI locale ou agent._
