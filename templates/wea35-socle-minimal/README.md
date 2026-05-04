# Socle minimal agent (WEA-35)

Arbre de fichiers **réduit** pour initialiser un dépôt d’application WeAdU avec les mêmes conventions de base que le socle documentaire (`WeAdU-ltd/.github`).

**Documentation complète** (audit Replit Socle, liste abandonné / repris, procédure GitHub Template) : [`docs/inventory/WEA-35-weadu-socle-v5-lab-template.md`](../../docs/inventory/WEA-35-weadu-socle-v5-lab-template.md).

## Contenu

| Élément | Rôle |
|---------|------|
| `AGENTS.md` | Renvoi vers les règles communes WeAdU (miroir dans `.github`) |
| `.cursor/hooks.json` | Schéma hooks Cursor valide (`version` + `hooks` vide) |
| `.gitignore` | Python / caches locaux usuels |
| `.pre-commit-config.yaml` | Gitleaks en local (optionnel ; la CI du dépôt d’app doit aussi scanner) |

**Non inclus** : workflows GitHub, secrets, `devcontainer`, code métier — à ajouter par dépôt selon [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh) et la charte [WEA-17](https://linear.app/weadu/issue/WEA-17/charte-agents-linear-source-interdits-features-nouveaux-projets).

## Init depuis le dépôt `.github`

À la racine d’un clone de `WeAdU-ltd/.github` :

```bash
bash scripts/init_wea35_socle_template.sh --help
bash scripts/init_wea35_socle_template.sh /chemin/vers/mon-nouveau-repo
```
