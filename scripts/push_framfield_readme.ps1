#!/usr/bin/env pwsh
# Adds README.md at repo root (WEA-59 template) and pushes to origin/main.
# Run on Jeff's machine from any directory (uses absolute paths by default).
# Requires: framfield_github_pat.txt (one line = PAT with repo scope).
# Usage: pwsh -File scripts/push_framfield_readme.ps1
#    or: pwsh -File ... -RepoDir 'D:\path' -PatFile 'D:\path\pat.txt'

param(
    [string]$RepoDir = $(Join-Path 'G:\Shared drives\Tech Projects\Personal Projects' 'After Framfield'),
    [string]$PatFile = $(Join-Path 'G:\Shared drives\Tech Projects\Personal Projects' 'framfield_github_pat.txt')
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Set-Location -LiteralPath $RepoDir
if (-not (Test-Path -LiteralPath '.git')) { throw "Pas de .git dans $RepoDir" }
if (-not (Test-Path -LiteralPath $PatFile)) { throw "Fichier PAT manquant : $PatFile" }

$readme = @'
# after-framfield-cockpit

Migration depuis Replit — périmètre **perso** (pas WeAdU-ltd).

## Prérequis

- **Python 3.x** (le dépôt contient des scripts sous `tools/`, ex. `run_massive_sim.py`, `sensitivity_checker.py` — adapter la version si besoin).

## Configuration (noms seulement)

- Variables d’environnement / secrets Replit : à lister depuis l’onglet **Secrets** du Repl (**pas de valeurs** dans ce README).
- OAuth / Google : redirects stables — [GOOGLE_OAUTH_WEA20 (doc WeAdU)](https://github.com/WeAdU-ltd/.github/blob/main/docs/GOOGLE_OAUTH_WEA20.md).

## Lancer en local

```bash
# Exemple : installer les deps si un requirements.txt est ajouté plus tard, puis :
python tools/sensitivity_checker.py --help
python tools/run_massive_sim.py --help
```

(Complète avec les commandes exactes une fois alignées sur le Repl.)

## Données

- `output/simulation_results.csv` — sorties locales ; ne pas committer de données sensibles volumineuses si tu ajoutes d’autres fichiers.

## CI

Optionnel : ajouter une workflow GitHub Actions quand la stack est fixée.

---
*README ajouté pour le critère Linear [WEA-59](https://linear.app/weadu/issue/WEA-59/after-framfield-cockpit-code-importe-readme-procedure-de-run) — gabarit aligné sur le runbook WeAdU.*
'@

Set-Content -LiteralPath (Join-Path $RepoDir 'README.md') -Value $readme -Encoding utf8

git add README.md
if (git diff --cached --quiet) {
    Write-Host 'README.md inchangé (déjà identique).'
    exit 0
}

git commit -m 'docs: add README for WEA-59 (runbook template)'
$pat = (Get-Content -LiteralPath $PatFile -Raw -Encoding utf8).Trim()
if (-not $pat) { throw 'PAT vide' }
$enc = [Uri]::EscapeDataString($pat)
git remote set-url origin "https://JeffWeadu:${enc}@github.com/JeffWeadu/after-framfield-cockpit.git"
git push -u origin main
git remote set-url origin 'https://github.com/JeffWeadu/after-framfield-cockpit.git'
Write-Host 'OK : README.md poussé sur origin/main.'
