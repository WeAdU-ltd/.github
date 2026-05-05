# wellbots-shopping-ads-checker — Replit → GitHub (Repl 5, WEA-67)

**Linear** : parent [WEA-67](https://linear.app/weadu/issue/WEA-67/repl-5-wellbots-shopping-ads-checker-migration-replit-github-societe) — chaîne [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents). **Ligne inventaire** : [WEA-33](./WEA-33-replit-inventory.md) #5.

**Dépôt GitHub cible (confirmé, 2026-05-06)** : **`https://github.com/WeAdU-ltd/SH-Checker-Bids`** (privé). Les agents sur ce dépôt `.github` ne lisent pas le filesystem Replit.

---

## 1. Brief agent Replit (WEA-68)

Export Markdown **dans** le Repl : non reproductible depuis l’agent GitHub seul — [WEA-35 §7](./WEA-35-weadu-socle-v5-lab-template.md).

**Consigne** à coller dans l’agent Cursor **du** Repl : formulaire §7 [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md).

---

## 2. Synthèse (WEA-69)

| Champ | État (doc dépôt) |
|-------|------------------|
| **Inventaire WEA-33** | Ligne #5 — snapshot mars 2026 ; croiser avec export Repl quand disponible. |
| **Git cible** | `WeAdU-ltd/SH-Checker-Bids` — aligner import depuis Repl. |

---

## 3. Dépôt GitHub (WEA-70)

| Rôle | URL |
|------|-----|
| **Application** | `https://github.com/WeAdU-ltd/SH-Checker-Bids` |

---

## 4. Code + README + CI (WEA-71)

Importer le code depuis le Repl ; README + CI selon le dépôt et [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md) si besoin.

---

## 5. Cutover (WEA-72)

Quand la prod ne dépend plus du Repl : retirer la ligne **#5** dans [WEA-36 §5](./WEA-36-replit-migration-societe.md) ; secrets Replit → [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete).

---

_Document vivant ; création : 2026-05-06._
