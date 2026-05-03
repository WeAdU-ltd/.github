# WEA-29 — Inventaire AWS EC2 (Ubuntu / Windows, Selenium, coûts indicatifs)

Document d’ancrage pour le ticket [WEA-29](https://linear.app/weadu/issue/WEA-29/aws-inventaire-ec2-ubuntu-windows-taches-selenium). Il complète la chaîne cloud ([WEA-27](https://linear.app/weadu/issue/WEA-27/google-cloud-inventaire-projets-uris-oauth-doublons) … [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete)) et dépend du socle secrets [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh) pour les accès réels (pas de secrets dans ce fichier).

---

## 1. Ce que l’API AWS voit / ne voit pas

| Source | Couverture |
|--------|------------|
| **EC2 DescribeInstances** | Type, état, IP, VPC, sous-réseau, security groups, volumes attachés, tags, AMI / plateforme Windows vs Linux |
| **Pas dans ce script** | Processus (Selenium), **tâches planifiées Windows**, unités **systemd** sur Ubuntu — complété en **§3** (capture invitée) ; pour un état à jour, réexécuter les commandes sur les hôtes ou via **SSM** |

---

## 2. Régénération (section automatique)

Prérequis : `pip install boto3` et identifiants AWS (profil `AWS_PROFILE` ou variables d’environnement standard).

```bash
cd /path/to/clone/of/.github
pip install boto3   # si besoin
export AWS_PROFILE=...   # ou AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_SESSION_TOKEN
# Optionnel : limiter les régions ; --dry-run affiche le Markdown sans écrire le fichier
python3 scripts/aws_inventory_wea29.py --regions eu-west-1,eu-central-1 \
  -o docs/inventory/WEA-29-aws-ec2-inventory.md
python3 scripts/aws_inventory_wea29.py --regions eu-west-1 --dry-run
```

Les lignes entre les marqueurs ci-dessous sont **écrasées** à chaque exécution du script.

<!-- WEA29_INVENTORY_BEGIN -->

_Exécutez le script ci-dessus pour remplir cette zone._

<!-- WEA29_INVENTORY_END -->

---

## 3. Complément manuel — ce qui tourne sur les hôtes (OS invité)

Renseigné à partir d’une **capture invitée** (SSH / PowerShell sur les serveurs), **2026-05-03**. Pas de secrets ni d’IP publique dans ce tableau. Hostname interne Ubuntu : `ip-172-31-19-126` (compléter le **Name tag / instanceId** via §2 ou la console AWS si besoin d’alignement exact).

| Hôte (Name tag / ID) | OS réel | Rôle / services | Tâches planifiées / cron / systemd | Selenium (oui/non + où) | Sauvegardes | Notes sécurité |
|---------------------|---------|-----------------|-------------------------------------|---------------------------|-------------|----------------|
| Ubuntu EC2 (`ip-172-31-19-126`) | Ubuntu 24.04.4 LTS | **nginx**, **n8n** (`n8n.service`), **negative-terms** (FastAPI), **PostgreSQL 16**, **Docker** + **containerd**, **chrony**, **fail2ban**, **Amazon SSM Agent** (snap), **certbot** (timer), maintenance (`apt`, `logrotate`, `unattended-upgrades`, etc.) | **systemd** : unités ci-dessus + timers sysadmin (certbot, apt-daily, logrotate, sysstat, etc.). **Cron root** : non lisible depuis la session utilisée | **Non** — aucun processus correspondant à Selenium / chromedriver / geckodriver / webdriver / Playwright au moment de la capture | Non visible dans la capture ; à confirmer côté AWS (snapshots EBS / politique org) | fail2ban + mises à jour automatiques actives ; surface Docker à suivre |
| Windows EC2 | Microsoft Windows Server 2022 Datacenter | **Caddy**, **NegativeTerms-WebApp** + **NegativeTerms-WebApp-Staging**, **Wellbots**, **PostgreSQL 16**, **Docker**, **OpenSSH Server**, **RDP** (TermService), **SSM**, **Windows Defender** | **Planificateur** : nombreuses tâches **Microsoft** standard + tâches **métier** racine et `\WeAdU\` (voir §3.1). Pas de détail d’horaires dans ce doc | **Non** au moment de la capture (filtre Chrome / Edge / Firefox / Java / drivers vide) | Non visible dans la capture ; à confirmer (EBS, SQL dump, etc.) | Bastion logique : SSH + RDP ; tâches `PD_*` / scraping à cartographier dans un runbook séparé si besoin |

### 3.1 Tâches planifiées Windows — périmètre WeAdU / métier (noms)

_Hors tâches `\Microsoft\Windows\...` et hors GoogleUpdater / .NET NGEN._

- `\WeAdU\` : `WeAdU-Caddy`, `WeAdU-COS`, `WeAdU-COS-Watchdog`, `WeAdU-Dashboard`, `DismissGoogleAdsRecommendations`
- **Wellbots** : `WellbotsAdsSync`, `WellbotsWatchdog`
- **Racine `\`** (échantillon non exhaustif) : `PD_*` (monitoring, scrape, sedar, sessions, notify, infra, etc.), `NgamBatched`, `NgamV4`, `NgromDebug`, `NegativeKeywords_Weekly`, `MLPumpScorer`, `DashboardDaily`, `TradeManager_Hourly`, `Capture2FA`, `LaunchGateway`, `EnumWindows`, `TOTP_Autofill`, migrations / SQL (`RunMigration`, `RunPGInstall`, `RunSQL`, `SetupPG`, `VerifyPG`, `SetDBURL`), `StocksAPI`, `SysCheck`, etc.

Pour la liste complète à l’instant T, réexécuter sur le serveur :  
`Get-ScheduledTask | Where-Object State -eq 'Ready' | Select TaskName, TaskPath`

---

## 4. Prochaines actions (sécurité, sauvegardes)

À découper en **sous-tickets** Linear si une ligne dépasse le périmètre de ce ticket.

| # | Action | Détail |
|---|--------|--------|
| 1 | **Secrets & accès** | Aligner SSH/RDP/IAM avec [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh) ; éviter clés longue durée exposées |
| 2 | **Surface réseau** | Revoir security groups (SSH/RDP ouverts sur `0.0.0.0/0`), bastion ou SSM préféré |
| 3 | **Sauvegardes** | Snapshots EBS / AMI selon RPO ; taguer les volumes critiques |
| 4 | **Windows + Selenium** | Inventaire **Planificateur de tâches**, compte de service, dépendances navigateur / drivers |
| 5 | **Ubuntu** | `systemd` timers / cron pour jobs agents ; mise à jour unattended-upgrades si politique |

---

## 5. Critères de fait (auto-contrôle)

| Critère | Où c’est couvert |
|--------|------------------|
| Liste des ressources + ce qui tourne (même partiel) | §2 (API) + tableau §3 (invité) |
| Prochaines actions en sous-tickets si besoin | §4 + création d’issues dédiées |
