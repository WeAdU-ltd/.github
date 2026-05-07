# Chief of Staff Virtuel IA (COS) — Replit, EC2, dépôt Git (WEA-49)

**Linear** : parent [WEA-49](https://linear.app/weadu/issue/WEA-49/repl-2-chief-of-staff-virtuel-ia-cos-migration-replit-github-societe) — chaîne [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents). **Ligne inventaire** : [WEA-33](./WEA-33-replit-inventory.md) #2.

**Secrets** : aucune valeur — [WEA-15](../SECRETS_SOCLE_WEA15.md), 1Password, Windows `C:\ProgramData\.secret_cache\` côté hôte (noms seulement, voir [snapshot Socle](./weadu-socle-v5-lab-replit-snapshot-2026-05-04.md) §4 / §6).

---

## 1. Brief agent Replit (WEA-50) — ce qu’on peut prouver sans ouvrir le Repl

Un **export structuré produit par l’agent Cursor à l’intérieur du Repl** `Chief of Staff Virtuel IA (COS)` n’est **pas** reproductible depuis ce dépôt : l’agent GitHub n’a ni le filesystem Replit ni l’UI Secrets / Deployments.

**Justification documentée (critère de fait)** : même principe que [WEA-44](https://linear.app/weadu/issue/WEA-44/weadu-socle-v5-lab-brief-agent-replit-infos-migration) / §7 de [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md) — ici, la **charge prod** est déjà documentée **hors Replit** (EC2), et le **pont Socle → EC2** est décrit dans le [snapshot Weadu-Socle-V5-Lab](./weadu-socle-v5-lab-replit-snapshot-2026-05-04.md) (§6 *Services externes* : tâches `WeAdU-COS` / `WeAdU-COS-Watchdog` côté Windows, health `localhost:5050`, push config `C:\Scripts\weadu\cos\aws_secrets.env`, secrets dans `C:\ProgramData\.secret_cache\`).

**Consigne** (historique — le **Repl COS est fermé**, **2026-05**) : si un export détaillé était encore nécessaire autrefois, le formulaire était celui de §7 [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md).

---

## 2. Synthèse migration (WEA-51) — alignement inventaire

| Thème | État documentaire |
|-------|-------------------|
| **Prod** | Trafic public via **EC2** (`leadgen.generads.com` → Caddy → app) — [WEA-33](./WEA-33-replit-inventory.md) ligne #2 ; pas de dépendance Replit pour la prod web décrite là. |
| **Hôte Windows** | Tâches planifiées `\WeAdU\` : `WeAdU-COS`, `WeAdU-COS-Watchdog` — [WEA-29](./WEA-29-aws-ec2-inventory.md) §3.1. |
| **Pont depuis Socle** | SSH / push secrets / health COS — [snapshot Socle](./weadu-socle-v5-lab-replit-snapshot-2026-05-04.md) §6 *AWS Lightsail (EC2)*. |
| **Dépôt GitHub applicatif** | **`https://github.com/WeAdU-ltd/cos`** (privé) — **import initial du code fait** (**2026-05-08**) depuis l’hôte Windows via [`cos_push_from_windows.ps1`](../../scripts/cos_push_from_windows.ps1) ; **Repl Replit COS fermé** (confirmé **2026-05**) ; reste : **README** / **CI** dans le dépôt `cos` si besoin. |

### 2.1 Automation GitHub OIDC + SSM (hôte Windows, 2026-05)

| Élément | Détail |
|---------|--------|
| **CI / agents** | Workflows **`AWS OIDC smoke`** et **`AWS SSM send-command smoke`** sur **`WeAdU-ltd/.github`** ; secret repo **`AWS_ROLE_ARN`** ; rôle IAM **`WeAdUGitHubOIDC-SSM`**. |
| **Instance SSM (hybrid)** | **`mi-08ba03ce367298b11`** — **`eu-west-2`** — Windows COS (Lightsail **Windows_Server_2022-1**). |
| **Doc** | [`docs/AWS_GITHUB_OIDC_SSM.md`](../AWS_GITHUB_OIDC_SSM.md) — OIDC, smoke SSM, policy Lightsail lecture seule optionnelle. |

---

## 3. Dépôt GitHub (WEA-52)

| Rôle | URL / statut |
|------|----------------|
| **Doc / procédure (ce dépôt)** | `https://github.com/WeAdU-ltd/.github` — ce fichier. |
| **Code applicatif COS** | **`https://github.com/WeAdU-ltd/cos`** — code sur **`main`** ; affiner **README** / **CI** si besoin (voir §4). |

Le label Linear groupe **`repo`** sur les tickets applicatifs : **`WeAdU-ltd/cos`** pour le code COS ; alignement **`.github`** via **`WeAdU-ltd/.github`** pour la doc infrastructure.

---

## 4. Code + README + CI (WEA-53)

- **Aujourd’hui** : le run **opérationnel** reste **sur l’instance Windows** (Caddy, tâches WeAdU-COS, secrets poussés depuis Socle). Le dépôt **`WeAdU-ltd/cos`** contient une copie **importée** du workspace (`C:\Scripts\weadu\cos`) — procédure : [`cos_push_from_windows.ps1`](../../scripts/cos_push_from_windows.ps1).
- **Suite** : stabiliser le **`README`** dans **`cos`** (prérequis Windows, secrets **nommés**, commande de build/run) ; CI minimale ou alignement [template WEA-35](./WEA-35-weadu-socle-v5-lab-template.md). **Repl Replit** : **fermé** — rotation / retrait des secrets Replit encore référencés côté vault selon [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete).
- **Référence infra** : [WEA-29](./WEA-29-aws-ec2-inventory.md) §3–4 (hôte, durcissement, sauvegardes).

---

## 5. Cutover Replit + résiduel (WEA-54)

- **Constat** : la **prod décrite** pour COS passe par **EC2**, pas par un hébergement Replit pour le trafic `leadgen.generads.com` ([WEA-33](./WEA-33-replit-inventory.md)).
- **Repl Replit** : **fermé** (confirmé **2026-05**) — plus d’entrée résiduelle COS dans [WEA-36 §5](./WEA-36-replit-migration-societe.md).
- **Secrets** : rotation ou retrait des entrées Replit encore présentes dans le vault « Replit » / 1Password — suivre [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete).

---

_Document vivant ; création : 2026-05-04 ; mise à jour inventaire : 2026-05-05 ; automation OIDC/SSM : 2026-05 ; dépôt applicatif `WeAdU-ltd/cos` : 2026-05 ; import code initial : 2026-05-08 ; Repl COS fermé : 2026-05._
