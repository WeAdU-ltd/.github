# WEA-29 — Inventaire AWS EC2 (Ubuntu / Windows, Selenium, coûts indicatifs)

Document d’ancrage pour le ticket [WEA-29](https://linear.app/weadu/issue/WEA-29/aws-inventaire-ec2-ubuntu-windows-taches-selenium). Il complète la chaîne cloud ([WEA-27](https://linear.app/weadu/issue/WEA-27/google-cloud-inventaire-projets-uris-oauth-doublons) … [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete)) et dépend du socle secrets [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh) pour les accès réels (pas de secrets dans ce fichier).

---

## 1. Ce que l’API AWS voit / ne voit pas

| Source | Couverture |
|--------|------------|
| **EC2 DescribeInstances** | Type, état, IP, VPC, sous-réseau, security groups, volumes attachés, tags, AMI / plateforme Windows vs Linux |
| **Pas dans ce script** | Processus (Selenium), **tâches planifiées Windows**, unités **systemd** sur Ubuntu — à compléter en §3 ou via **SSM** une fois [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh) OK |

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

À remplir après connexion **SSH (Ubuntu)** / **RDP ou SSM (Windows)** ou audit ops. Ne pas y coller de mots de passe ou clés.

| Hôte (Name tag / ID) | OS réel | Rôle / services | Tâches planifiées / cron / systemd | Selenium (oui/non + où) | Sauvegardes | Notes sécurité |
|---------------------|---------|-----------------|-------------------------------------|---------------------------|-------------|----------------|
| _ex. i-xxx — prod-bot_ | Ubuntu 22.04 | … | … | … | … | … |
| _ex. i-yyy — scraper-win_ | Windows Server | … | Planificateur : … | … | … | … |

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
