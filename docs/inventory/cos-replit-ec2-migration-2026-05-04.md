# Chief of Staff Virtuel IA (COS) — Replit, EC2, dépôt Git (WEA-49)

**Linear** : parent [WEA-49](https://linear.app/weadu/issue/WEA-49/repl-2-chief-of-staff-virtuel-ia-cos-migration-replit-github-societe) — chaîne [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents). **Ligne inventaire** : [WEA-33](./WEA-33-replit-inventory.md) #2.

**Secrets** : aucune valeur — [WEA-15](../SECRETS_SOCLE_WEA15.md), 1Password, Windows `C:\ProgramData\.secret_cache\` côté hôte (noms seulement, voir [snapshot Socle](./weadu-socle-v5-lab-replit-snapshot-2026-05-04.md) §4 / §6).

---

## 1. Brief agent Replit (WEA-50) — ce qu’on peut prouver sans ouvrir le Repl

Un **export structuré produit par l’agent Cursor à l’intérieur du Repl** `Chief of Staff Virtuel IA (COS)` n’est **pas** reproductible depuis ce dépôt : l’agent GitHub n’a ni le filesystem Replit ni l’UI Secrets / Deployments.

**Justification documentée (critère de fait)** : même principe que [WEA-44](https://linear.app/weadu/issue/WEA-44/weadu-socle-v5-lab-brief-agent-replit-infos-migration) / §7 de [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md) — ici, la **charge prod** est déjà documentée **hors Replit** (EC2), et le **pont Socle → EC2** est décrit dans le [snapshot Weadu-Socle-V5-Lab](./weadu-socle-v5-lab-replit-snapshot-2026-05-04.md) (§6 *Services externes* : tâches `WeAdU-COS` / `WeAdU-COS-Watchdog` côté Windows, health `localhost:5050`, push config `C:\Scripts\weadu\cos\aws_secrets.env`, secrets dans `C:\ProgramData\.secret_cache\`).

**Consigne** (à coller dans l’agent Cursor **du** Repl COS si un export détaillé du Repl seul est encore nécessaire) : identique au formulaire §7 de [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md) — stack, run local, Git, noms des secrets Replit, DB Replit, déploiement `.replit.app`, externes.

---

## 2. Synthèse migration (WEA-51) — alignement inventaire

| Thème | État documentaire |
|-------|-------------------|
| **Prod** | Trafic public via **EC2** (`leadgen.generads.com` → Caddy → app) — [WEA-33](./WEA-33-replit-inventory.md) ligne #2 ; pas de dépendance Replit pour la prod web décrite là. |
| **Hôte Windows** | Tâches planifiées `\WeAdU\` : `WeAdU-COS`, `WeAdU-COS-Watchdog` — [WEA-29](./WEA-29-aws-ec2-inventory.md) §3.1. |
| **Pont depuis Socle** | SSH / push secrets / health COS — [snapshot Socle](./weadu-socle-v5-lab-replit-snapshot-2026-05-04.md) §6 *AWS Lightsail (EC2)*. |
| **Dépôt GitHub applicatif** | **Non identifié** dans ce dépôt ([snapshot GitHub org](./github-org-repo-snapshot-2026-05-02.json) sans entrée COS évidente). Nom canonique **à trancher** : création future `WeAdU-ltd/<repo-cos>` ou équivalent — voir §4. |

---

## 3. Dépôt GitHub (WEA-52)

| Rôle | URL / statut |
|------|----------------|
| **Doc / procédure (ce dépôt)** | `https://github.com/WeAdU-ltd/.github` — ce fichier. |
| **Code applicatif COS** | **À créer ou à confirmer** — suggestion de nom pour les futurs tickets agents : `WeAdU-ltd/cos` ou `WeAdU-ltd/chief-of-staff` (à valider ; pas de repo créé automatiquement ici). |

Le label Linear groupe **`repo`** ne s’assigne pas directement sur un ticket ; alignement périmètre **`.github`** via le label **`WeAdU-ltd/.github`** jusqu’à ouverture d’un dépôt applicatif dédié.

---

## 4. Code + README + CI (WEA-53)

- **Aujourd’hui** : le run **opérationnel** documenté pour COS est **sur l’instance Windows EC2** (Caddy, tâches WeAdU-COS, secrets poussés depuis Socle). Il n’existe pas encore dans ce dépôt de **clone Git complet** du code COS avec README développeur.
- **Cible** : quand le dépôt applicatif existe, exiger un `README` (prérequis Windows/Linux, secrets **nommés**, commande de build/run) + CI minimale ou alignement [template WEA-35](./WEA-35-weadu-socle-v5-lab-template.md).
- **Référence infra** : [WEA-29](./WEA-29-aws-ec2-inventory.md) §3–4 (hôte, durcissement, sauvegardes).

---

## 5. Cutover Replit + résiduel (WEA-54)

- **Constat** : la **prod décrite** pour COS passe par **EC2**, pas par un hébergement Replit pour le trafic `leadgen.generads.com` ([WEA-33](./WEA-33-replit-inventory.md)).
- **Repl Replit** : peut rester un **espace de dev / archive** tant qu’il existe ; l’entrée correspondante figure dans [WEA-36 §5](./WEA-36-replit-migration-societe.md) tant que le Repl n’est pas fermé ou vidé.
- **Secrets** : toute rotation ou retrait côté Replit après arrêt définitif du Repl — hors périmètre immédiat de ce fichier ; suivre [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete).

---

_Document vivant ; création : 2026-05-04 ; mise à jour inventaire : 2026-05-05._
