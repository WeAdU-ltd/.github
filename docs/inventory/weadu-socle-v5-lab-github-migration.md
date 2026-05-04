# Weadu-Socle-V5-Lab — ancrage GitHub (`WeAdU-ltd/.github`)

Document pour la migration **Replit → GitHub** du Repl inventaire **#1** ([WEA-33](./WEA-33-replit-inventory.md)). Parent Linear : [WEA-43](https://linear.app/weadu/issue/WEA-43/repl-1-weadu-socle-v5-lab-migration-replit-github-societe).

**Secrets** : aucune valeur ici — [WEA-15](../SECRETS_SOCLE_WEA15.md), secrets **organisation** GitHub pour la CI de ce dépôt.

---

## 1. Dépôt GitHub cible (confirmé)

| Rôle | URL |
|------|-----|
| **Vérité documentaire + workflows org + inventaires agents** | `https://github.com/WeAdU-ltd/.github` |

Ce dépôt **n’est pas** un export ligne-à-ligne du code FastAPI du Repl Socle ; il porte la **doc**, les **Actions réutilisables**, les **scripts** (`scripts/linear_*.py`, inventaires, smokes) et le **template minimal agent** ([WEA-35](./WEA-35-weadu-socle-v5-lab-template.md)). Le détail runtime du Repl (stack, secrets nommés, DB, déploiement) est dans le **snapshot agent Repl** : [`weadu-socle-v5-lab-replit-snapshot-2026-05-04.md`](./weadu-socle-v5-lab-replit-snapshot-2026-05-04.md).

---

## 2. Run local — **ce** dépôt (`WeAdU-ltd/.github`)

Prérequis : Python 3.11+, `git`, accès lecture au clone ; variables **optionnelles** selon le script (ex. `LINEAR_API_KEY`, `GITHUB_TOKEN` — noms dans [WEA-15](../SECRETS_SOCLE_WEA15.md), jamais dans le repo).

```bash
git clone https://github.com/WeAdU-ltd/.github.git
cd .github

# Optionnel : hooks secrets (voir README racine § Cursor hooks)
pip install pre-commit && pre-commit install

# Exemples de scripts (dry-run / lecture seule selon script)
python3 scripts/linear_create_wea36_repl_issues.py
python3 scripts/linear_github_inventory_wea12.py --help
```

CI sur `main` : voir [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) (actionlint, contrôles sur les workflows). Pas de serveur web à lancer pour la « prod doc » : GitHub sert les pages et le code.

Pour **reproduire l’ancienne app** Socle (FastAPI, AI Council, etc.), se référer au snapshot Repl §2 (commandes `bash tools/setup_ssh.sh && python main.py`) — exécution **dans le Repl** ou dans un futur dépôt applicatif dédié, hors périmètre de ce repo.

---

## 3. Alignement template agent (WEA-35)

Nouveau dépôt **application** : copier le socle minimal depuis [`templates/wea35-socle-minimal/`](../../templates/wea35-socle-minimal/README.md) ou exécuter :

```bash
bash scripts/init_wea35_socle_template.sh /chemin/vers/nouveau-repo
```

---

## 4. Cutover (rappel WEA-48)

Tant que des charge utiles (schedulers, Socket Mode, etc.) tournent **uniquement** sur le Repl, la ligne **résiduelle** du Repl #1 reste dans [WEA-36 §5](./WEA-36-replit-migration-societe.md). Retirer la ligne après bascule infra + retrait des secrets métier côté Replit (chaîne [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete)).

---

_Document vivant ; création : 2026-05-04._
