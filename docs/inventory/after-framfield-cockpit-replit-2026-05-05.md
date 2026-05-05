# after-framfield-cockpit — Replit (Repl 3, WEA-55)

**Linear** : parent [WEA-55](https://linear.app/weadu/issue/WEA-55/repl-3-after-framfield-cockpit-migration-replit-github-persosociete-a-trancher) — chaîne [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents). **Ligne inventaire** : [WEA-33](./WEA-33-replit-inventory.md) #3.

**Blocage produit** : **Perso vs Société** non tranché ([WEA-13](./WEA-13-github-access-model.md)) — aucune création de dépôt `WeAdU-ltd/…` ni bascule OAuth tant que la décision n’est pas écrite sur le ticket parent ou un ticket lié.

---

## 1. Brief agent Replit (WEA-56)

Un export Markdown produit **dans** le Repl `after-framfield-cockpit` n’est pas reproductible depuis l’agent qui ne fait qu’analyser ce dépôt `.github`.

**Justification documentée** : même logique que [WEA-35 §7](./WEA-35-weadu-socle-v5-lab-template.md). Pour la vue **inventaire dépôt** : OAuth redirect sur hostname workspace **éphémère** (instable) — [WEA-33](./WEA-33-replit-inventory.md) ligne #3 ; redirect durables et scopes : [WEA-20](../GOOGLE_OAUTH_WEA20.md).

**Consigne** (à coller dans l’agent Cursor **du** Repl si besoin d’un export Repl-only) : formulaire §7 [WEA-35](./WEA-35-weadu-socle-v5-lab-template.md).

---

## 2. Synthèse inventaire (WEA-57)

| Champ | État (doc dépôt, sans ouverture Repl) |
|-------|--------------------------------------|
| Déploiement | Redirect OAuth **non stable** (hostname workspace éphémère) — photo mars 2026 [WEA-33](./WEA-33-replit-inventory.md). |
| Git / GitHub | **Inconnu** depuis ce dépôt — à compléter depuis le Repl ou inventaire org ([WEA-12](./WEA-12-github-linear.md)). |
| Suite | Après **tranché Perso / Société** : soit repo sous `WeAdU-ltd/…`, soit compte perso + séparation secrets ([WEA-13](./WEA-13-github-access-model.md)). |

---

## 3. Dépôt GitHub cible (WEA-58) — en attente de décision

| Option | Condition |
|--------|-----------|
| `WeAdU-ltd/<repo>` | Décision **Société** + création repo + label agents aligné charte [WEA-17](../CHARTE_AGENTS_LINEAR_WEA17.md). |
| Compte perso GitHub | Décision **Perso** — pas de duplication automatique ici ; pas de nom canonique WeAdU sans arbitrage. |

---

## 4. Code + README + CI (WEA-59) — en attente

Importer le code et ajouter README / CI dans le **dépôt choisi** après §3. Alignement possible avec [template WEA-35](./WEA-35-weadu-socle-v5-lab-template.md) pour un nouveau repo société.

---

## 5. Cutover (WEA-60)

Tant que le périmètre repo et les redirect OAuth **production** ne sont pas fixés, le Repl peut rester dans la [liste résiduelle §5](./WEA-36-replit-migration-societe.md) ; fermeture après cutover + [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete).

---

_Document vivant ; création : 2026-05-05._
