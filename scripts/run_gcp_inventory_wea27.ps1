#Requires -Version 5.1
<#
.SYNOPSIS
  Régénère docs/inventory/WEA-27-google-cloud.md (WEA-27) sans configurer GCLOUD_PATH à la main.

.DESCRIPTION
  Cherche gcloud.cmd (LOCALAPPDATA, GCLOUD_PATH, ou Get-Command gcloud), puis lance le script Python.
  À exécuter depuis n'importe où : le dépôt est déduit depuis l'emplacement de ce fichier.

.EXAMPLE
  .\scripts\run_gcp_inventory_wea27.ps1
#>
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $RepoRoot

function Find-GcloudCmd {
    $p = $env:GCLOUD_PATH
    if ($p -and (Test-Path -LiteralPath $p)) { return (Resolve-Path -LiteralPath $p).Path }

    $candidate = Join-Path $env:LOCALAPPDATA 'Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd'
    if (Test-Path -LiteralPath $candidate) { return (Resolve-Path -LiteralPath $candidate).Path }

    $g = Get-Command gcloud -ErrorAction SilentlyContinue
    if (-not $g) { return $null }

    $src = $g.Source
    if ($src -match '\.ps1$') {
        $cmd = Join-Path (Split-Path -Parent $src) 'gcloud.cmd'
        if (Test-Path -LiteralPath $cmd) { return (Resolve-Path -LiteralPath $cmd).Path }
    }
    if (Test-Path -LiteralPath $src) { return (Resolve-Path -LiteralPath $src).Path }
    return $null
}

$gcloudCmd = Find-GcloudCmd
if (-not $gcloudCmd) {
    Write-Error @"
gcloud introuvable. Installe le Google Cloud SDK (winget install Google.CloudSDK), puis :
  gcloud auth login
Ou définis le chemin complet :
  `$env:GCLOUD_PATH = 'C:\...\gcloud.cmd'
"@
}

$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue }
if (-not $py) {
    Write-Error 'python introuvable dans le PATH. Installe Python ou ajoute-le au PATH.'
}

$scriptPy = Join-Path $RepoRoot 'scripts\gcp_inventory_wea27.py'
$outMd = Join-Path $RepoRoot 'docs\inventory\WEA-27-google-cloud.md'

$exe = $py.Path
if (-not $exe) { $exe = $py.Source }
if (-not $exe) { $exe = $py.Definition }

Write-Host "Dépôt : $RepoRoot"
Write-Host "gcloud : $gcloudCmd"
Write-Host "Python : $exe"

$isPyLauncher = ($py.Name -eq 'py.exe') -or ($exe -like '*\py.exe')
if ($isPyLauncher) {
    & $exe '-3' $scriptPy '--gcloud' $gcloudCmd '-o' $outMd
} else {
    & $exe $scriptPy '--gcloud' $gcloudCmd '-o' $outMd
}
exit $LASTEXITCODE
