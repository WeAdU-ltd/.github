#Requires -Version 5.1
<#
.SYNOPSIS
  Envoie le code COS depuis C:\Scripts\weadu\cos vers https://github.com/WeAdU-ltd/cos
  en fusionnant avec le README déjà sur GitHub (historiques sans lien commun).

.VERSION
  2026-05-08 — identité git locale + variables GIT_AUTHOR_* ; fetch sans erreur PowerShell.

.EXAMPLE
  $env:GITHUB_COS_PAT = '<PAT depuis 1Password ou GitHub Settings>'
  powershell -ExecutionPolicy Bypass -File .\scripts\cos_push_from_windows.ps1

.NOTES
  Exécuter sur le serveur Windows où existe C:\Scripts\weadu\cos.
  Ne pas partager le PAT dans le chat.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$CosRoot = 'C:\Scripts\weadu\cos'
$RepoSlug = 'WeAdU-ltd/cos'
$RemoteName = 'origin'

if (-not (Test-Path -LiteralPath $CosRoot)) {
    throw "Dossier introuvable: $CosRoot"
}

$requiredIgnore = @(
    '',
    '# --- WeAdU / sécurité (ne pas versionner) ---',
    '.env',
    '.env.*',
    'aws_secrets.env',
    'new_secrets.txt',
    '*.log',
    'leadgen_direct.log',
    '__pycache__/',
    '.pytest_cache/',
    '.local/',
    '.upm/'
)

$gitignorePath = Join-Path $CosRoot '.gitignore'
if (-not (Test-Path -LiteralPath $gitignorePath)) {
    New-Item -Path $gitignorePath -ItemType File -Force | Out-Null
}
$gi = Get-Content -LiteralPath $gitignorePath -Raw -ErrorAction SilentlyContinue
if (-not $gi) { $gi = '' }
foreach ($line in $requiredIgnore) {
    if ($line -eq '') { continue }
    if ($gi -notmatch [regex]::Escape($line.Trim())) {
        Add-Content -LiteralPath $gitignorePath -Value $line.Trim() -Encoding UTF8
        $gi += "`n$($line.Trim())"
    }
}

if (-not $env:GITHUB_COS_PAT -or $env:GITHUB_COS_PAT.Length -lt 10) {
    throw 'Définissez GITHUB_COS_PAT (PAT avec scope repo sur WeAdU-ltd/cos).'
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git introuvable dans PATH.'
}

$pat = $env:GITHUB_COS_PAT
$authenticatedRemote = "https://${pat}@github.com/${RepoSlug}.git"
$cleanRemote = "https://github.com/${RepoSlug}.git"

Push-Location $CosRoot
try {
    Write-Host 'cos_push_from_windows.ps1 — version doc .VERSION 2026-05-08'

    $env:GIT_AUTHOR_EMAIL = 'cos-import@weadu.com'
    $env:GIT_AUTHOR_NAME = 'WeAdU COS Windows Import'
    $env:GIT_COMMITTER_EMAIL = $env:GIT_AUTHOR_EMAIL
    $env:GIT_COMMITTER_NAME = $env:GIT_AUTHOR_NAME

    if (-not (Test-Path -LiteralPath (Join-Path $CosRoot '.git'))) {
        & git init
    }

    & git config --local user.email "cos-import@weadu.com"
    & git config --local user.name "WeAdU COS Windows Import"

    $remotes = @(& git remote 2>$null)
    if ($remotes -contains $RemoteName) {
        & git remote remove $RemoteName
    }

    & git remote add $RemoteName $authenticatedRemote

    & git add -A
    & git diff --cached --quiet
    if ($LASTEXITCODE -eq 0) {
        throw 'Aucun fichier stagé — vérifie .gitignore (ne pas tout ignorer par erreur).'
    }

    & git commit -m "chore: import COS depuis Windows (C:\Scripts\weadu\cos)"

    & git branch -M main

    $fetchOk = $false
    # git envoie du texte sur stderr : éviter que PowerShell (StrictMode) arrête le script
    $prevEa = $ErrorActionPreference
    $ErrorActionPreference = 'SilentlyContinue'
    try {
        $null = & git fetch $RemoteName main 2>&1
        $fetchOk = $LASTEXITCODE -eq 0
    } finally {
        $ErrorActionPreference = $prevEa
    }

    if ($fetchOk) {
        $prevEa = $ErrorActionPreference
        $ErrorActionPreference = 'SilentlyContinue'
        try {
            $null = & git merge "${RemoteName}/main" --allow-unrelated-histories --no-edit -m "Merge branch 'main' of GitHub (README) + COS import" 2>&1
            $mergeOk = $LASTEXITCODE -eq 0
        } finally {
            $ErrorActionPreference = $prevEa
        }
        if (-not $mergeOk) {
            throw 'Conflit git après merge. Résous les conflits puis: git add -A && git commit && git push'
        }
    }

    $prevEa = $ErrorActionPreference
    $ErrorActionPreference = 'SilentlyContinue'
    try {
        $null = & git push -u $RemoteName main 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "git push a échoué (code $($LASTEXITCODE))"
        }
    } finally {
        $ErrorActionPreference = $prevEa
    }

    & git remote set-url $RemoteName $cleanRemote
}
finally {
    Pop-Location
    Remove-Item Env:GITHUB_COS_PAT -ErrorAction SilentlyContinue
}

Write-Host 'OK. Remote réinitialisé sans PAT dans URL. Configure les credentiels Git sur ce serveur si tu dois pousser encore (ou utilise un nouveau PAT dans une session).'
