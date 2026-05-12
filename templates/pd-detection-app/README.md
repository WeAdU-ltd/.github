# pd-detection

Application **Finance-RH** (inventaire Replit [WEA-33](https://github.com/WeAdU-ltd/.github/blob/main/docs/inventory/WEA-33-replit-inventory.md) ligne 15). Ce dépôt est initialisé depuis le gabarit **WeAdU-ltd/.github** ([WEA-131](https://linear.app/weadu/issue/WEA-131/pd-detection-code-importe-readme-procedure-de-run)) : socle **WEA-35** + point d’entrée Python minimal. Le **code métier** issu du Repl doit être fusionné ensuite (export [WEA-128](https://linear.app/weadu/issue/WEA-128/pd-detection-brief-agent-replit-infos-migration), runbook [pd-detection-replit-migration-WEA-128.md](https://github.com/WeAdU-ltd/.github/blob/main/docs/inventory/pd-detection-replit-migration-WEA-128.md)).

## Prérequis

- **Python** 3.11 ou 3.12 (aligné CI GitHub Actions).
- **Git**.
- Droits **push** sur **`JeffWeadu/pd-detection`** (dépôt applicatif privé documenté dans l’inventaire) **ou**, pour une création org, droits **`WeAdU-ltd`**.

## Option A — Déposer le gabarit dans `JeffWeadu/pd-detection` (cas actuel)

1. Cloner le dépôt existant et un clone de **`WeAdU-ltd/.github`** (pour le script et `templates/pd-detection-app/`).
2. Overlay du gabarit (**sans écraser à l’aveugle** : relire `git diff`) :

```bash
cd /chemin/vers/WeAdU-ltd/.github
bash scripts/init_pd_detection_app_template.sh --force /chemin/vers/pd-detection
cd /chemin/vers/pd-detection
git add -A
git status
git commit -m "chore: overlay WeAdU pd-detection template (WEA-131)"
git push origin HEAD
```

3. Fusionner le **code métier** venant du Repl après lecture du runbook [§2 export](https://github.com/WeAdU-ltd/.github/blob/main/docs/inventory/pd-detection-replit-migration-WEA-128.md).

## Option B — Nouveau dépôt sous `WeAdU-ltd/pd-detection`

À la racine d’un clone de **`WeAdU-ltd/.github`** :

```bash
bash scripts/init_pd_detection_app_template.sh --help
bash scripts/init_pd_detection_app_template.sh /chemin/vers/pd-detection
cd /chemin/vers/pd-detection
git init
git add .
git commit -m "chore: init pd-detection from WeAdU template (WEA-131)"
```

Créer le dépôt vide **`WeAdU-ltd/pd-detection`** sur GitHub (sans README/license auto si vous poussez déjà un commit) puis :

```bash
git remote add origin https://github.com/WeAdU-ltd/pd-detection.git
git branch -M main
git push -u origin main
```

## Importer l’historique Git depuis Replit (si disponible)

Objectif : garder l’historique du Repl **avant** ou **après** avoir posé le socle ci-dessus.

1. Dans le Repl **pd-detection** (Replit), ouvrir l’outil **Git** et noter l’URL de clone (HTTPS avec token Replit ou SSH selon ce que Replit expose).
2. Sur votre machine (ou agent avec accès), pousser vers **`JeffWeadu/pd-detection`** ou **`WeAdU-ltd/pd-detection`** selon la cible :

```bash
git clone <URL_REPLIT> pd-detection-import
cd pd-detection-import
git remote add github https://github.com/JeffWeadu/pd-detection.git
git push -u github --all
git push github --tags
```

3. Ensuite, **fusionner** le socle WeAdU (fichiers `AGENTS.md`, `.github/workflows/ci.yml`, `pyproject.toml`, etc.) dans cette branche : soit `init_pd_detection_app_template.sh --force` sur le clone du dépôt GitHub, soit `git merge` / `git cherry-pick` selon la divergence.

Les valeurs secrètes ne doivent **jamais** être commitées ; elles restent dans le [socle secrets WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh) (GitHub Encrypted Secrets, vault, Cursor).

## Commandes — développement local

Créer un environnement virtuel, installer le package en mode éditable, lancer les tests et le serveur de dev :

```bash
cd /chemin/vers/pd-detection
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
python -m pytest -q
python -m pd_detection.cli --host 127.0.0.1 --port 5000
```

Sans `pip install -e .` (exécution directe depuis les sources) :

```bash
PYTHONPATH=src python -m pd_detection.cli --host 127.0.0.1 --port 5000
```

Avec le script console installé par le package :

```bash
pd-detection-serve --host 127.0.0.1 --port 5000
```

Endpoint de smoke : `GET /health` → JSON `status: ok`.

Variables d’environnement **non secrètes** (défauts entre parenthèses) :

| Nom | Rôle |
|-----|------|
| `PD_DETECTION_HOST` | Adresse d’écoute du serveur de dev (`127.0.0.1`). |
| `PD_DETECTION_PORT` | Port TCP (`5000`). |

## Secrets — noms (valeurs hors dépôt)

Les **valeurs** ne sont pas dans ce README. Elles sont créées une fois dans **GitHub Encrypted Secrets** (repo ou org), Cursor, ou 1Password selon [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh) et [WEA-14 cartographie](https://github.com/WeAdU-ltd/.github/blob/main/docs/SECRETS_CARTOGRAPHIE_WEA14.md).

| Nom | Obligatoire pour le socle minimal | Rôle |
|-----|-----------------------------------|------|
| *(aucun pour `/health` + pytest)* | Non | Le gabarit actuel n’exige pas de secret. |

Après fusion du code Replit, **recopier ici uniquement les noms** des variables documentées dans l’export [WEA-128](https://linear.app/weadu/issue/WEA-128/pd-detection-brief-agent-replit-infos-migration) (section 2 du runbook une fois ingéré). Ne pas renommer arbitrairement les secrets déjà utilisés par le code métier sans adapter le code.

## CI

Le workflow `.github/workflows/ci.yml` exécute **pytest** et **gitleaks** sur chaque push / PR vers `main` (alignement anti-secrets [WEA-32](https://linear.app/weadu/issue/WEA-32/github-protections-branches-anti-secrets-en-clair), même version de gitleaks que le dépôt `.github`).

## Déploiement

1. Définir la cible (AWS, autre hôte) selon le runbook post-export Replit.
2. Stocker les secrets sous les **noms** documentés ci-dessus dans GitHub Actions ou le vault Finance-RH.
3. Ajouter un workflow `deploy-*.yml` ou réutiliser le workflow réutilisable org [`auto-deploy.yml`](https://github.com/WeAdU-ltd/.github/blob/main/README.md) lorsque la procédure d’infra est figée.

## Références Linear / dépôt `.github`

- [WEA-132 — cutover prod hors Replit + résiduel](https://linear.app/weadu/issue/WEA-132)
- [WEA-131 — code importé + README](https://linear.app/weadu/issue/WEA-131/pd-detection-code-importe-readme-procedure-de-run)
- [WEA-128 — brief agent Repl](https://linear.app/weadu/issue/WEA-128/pd-detection-brief-agent-replit-infos-migration)
- [WEA-35 — template socle](https://linear.app/weadu/issue/WEA-35/weadu-socle-v5-lab-audit-template-github-cursor)
