# 1Password — agents (CLI `op`, SDK Python, Cursor Cloud)

Ce dépôt fournit :

1. **Dev Container** : installe la **CLI `op`** dans un environnement que tu contrôles (VS Code / Cursor « Reopen in Container »).
2. **Script Python** [`scripts/onepassword_resolve_ref.py`](../scripts/onepassword_resolve_ref.py) : résout une référence `op://…` via le **SDK officiel** (`onepassword-sdk`) avec **`OP_SERVICE_ACCOUNT_TOKEN`** — **sans** binaire `op`.

Les valeurs secrètes restent hors Git ; alignement [WEA-15](SECRETS_SOCLE_WEA15.md) et [WEA-14](SECRETS_CARTOGRAPHIE_WEA14.md).

---

## Demander à Cursor d’inclure `op` sur **tous** les Cloud Agents

Seule l’**équipe Cursor** peut modifier l’**image** des sessions cloud. Piste usuelle :

1. Ouvre **[cursor.com/help](https://cursor.com/help)** (ou **?** / **Support** dans l’app).
2. Envoie une demande du type : *« Please ship 1Password CLI (`op`) in the Cloud Agent base image, or document how to opt in; we inject `OP_SERVICE_ACCOUNT_TOKEN` but the binary is missing. »*
3. Option **Forum / Discord** Cursor si disponible depuis le Help Center — même message court.

En attendant une réponse produit, utilise le **devcontainer** ou le **SDK** ci-dessous.

---

## Étape 1 — Dev Container (CLI `op` dans ce repo)

**Prérequis** : Docker installé sur ta machine ; Cursor ou VS Code avec l’extension Dev Containers.

1. Clone / ouvre le dépôt **`WeAdU-ltd/.github`** localement.
2. Commande palette : **« Dev Containers: Reopen in Container »**.
3. Au premier démarrage, le script **[`.devcontainer/install-op-cli.sh`](../.devcontainer/install-op-cli.sh)** installe `op` (méthode officielle [serveur Linux](https://developer.1password.com/docs/cli/install-server/)).
4. Dans le terminal **du container**, vérifie : `op --version`.

Pour utiliser le vault avec `op`, exporte ou colle **`OP_SERVICE_ACCOUNT_TOKEN`** dans un fichier `.env` **non versionné** ou dans les secrets Cursor pour les sessions qui montent ce workspace — **ne pas** committer le token.

---

## Étape 2 — Script Python (sans CLI)

**Prérequis** : `pip install -r requirements-onepassword.txt` (fait dans le devcontainer au `postCreate`).

```bash
export OP_SERVICE_ACCOUNT_TOKEN="…"   # déjà injecté par Cursor Cloud pour les agents si configuré
python3 scripts/onepassword_resolve_ref.py op://VaultName/ItemName/password
```

Par défaut le script **n’affiche pas** la valeur (évite les fuites dans les logs). Pour debug **local uniquement** :

```bash
python3 scripts/onepassword_resolve_ref.py --print-value op://VaultName/ItemName/password
```

**CI** : le job valide la syntaxe et un `--dry-run` sans appel réseau.

---

## SDK vs CLI

| Besoin | Outil |
|--------|--------|
| Automatisation, agents, pas de binaire | **`onepassword-sdk`** + `OP_SERVICE_ACCOUNT_TOKEN` |
| Scripts shell, `op read`, intégrations existantes | **CLI `op`** (devcontainer ou poste local) |

Référence développeur : [1Password Python SDK](https://github.com/1Password/onepassword-sdk-python).

---

_Document statique ; mise à jour si Cursor documente une image avec `op` ou si la procédure support change._
