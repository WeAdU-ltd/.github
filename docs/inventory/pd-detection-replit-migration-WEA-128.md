# pd-detection — brief agent Replit (infos migration)

**Linear** : [WEA-128](https://linear.app/weadu/issue/WEA-128/pd-detection-brief-agent-replit-infos-migration) — chaîne [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents). **Ligne inventaire** : [WEA-33](./WEA-33-replit-inventory.md) **#15** (Repl ID préfixe documenté : `3e94a8f8-…`). **Périmètre isolation Finance-RH** : [WEA-37](https://linear.app/weadu/issue/WEA-37/replit-migration-repos-perso-isolation-acces), [WEA-13](./WEA-13-github-access-model.md).

Les agents Cursor exécutés **uniquement** sur le dépôt **`WeAdU-ltd/.github`** n’ont pas le workspace Replit **pd-detection** : pas de `ls` du Repl, pas de lecture des Secrets Replit, pas de vérité runtime sans session **dans** ce Repl.

---

## 1. Consigne à coller vers l’agent Cursor **du** Repl **pd-detection**

Produire un export structuré (**Markdown**, **aucune valeur de secret**) avec :

1. **Stack** : langage, frameworks, fichiers d’entrée (`main`, `package.json`, `requirements.txt`, etc.).
2. **Run local** : commandes exactes pour lancer en dev.
3. **Git** : remote(s) connus, branche par défaut, dernier commit court.
4. **Secrets** : liste des **noms** de variables (pas les valeurs) dans Replit Secrets.
5. **Base Replit** : oui/non ; tables ou usage si pertinent.
6. **Déploiement** : URL `.replit.app`, Always On / autoscale, charge prod vs expérimentation.
7. **Externes** : AWS/GCP/API/OAuth redirect si visible dans le code ou la config.

Ne pas coller de secrets dans Linear ; résumer sur le ticket ou dans le dépôt cible après revue.

**Norme commune (autres Repls)** : le même gabarit est rappelé dans [WEA-35 §7](./WEA-35-weadu-socle-v5-lab-template.md) (ticket [WEA-44](https://linear.app/weadu/issue/WEA-44/weadu-socle-v5-lab-brief-agent-replit-infos-migration)).

---

## 2. Export ingéré (miroir dépôt)

| Bloc | État |
|------|------|
| Markdown produit par l’agent **dans** le Repl **pd-detection** | **À produire** — remplacer ce tableau par le corps de l’export (ou ajouter une sous-section) lorsque l’agent Repl aura répondu. |

---

## 3. Critère de fait WEA-128 (réponse Repl vs inaccessible)

| Exigence | État |
|----------|------|
| Réponse de l’agent Repl **ou** justification documentée si le Repl est inaccessible | **Justification documentée** : même limite que [WEA-35 §7](./WEA-35-weadu-socle-v5-lab-template.md) — l’agent GitHub / Cloud sur `.github` **ne peut pas** substituer l’export runtime. La preuve d’inaccessibilité depuis cet environnement est ce paragraphe + la ligne **#15** [WEA-33](./WEA-33-replit-inventory.md) (vue Socle **sans** ouverture du Repl). **Suite** : exécuter la consigne §1 **dans** le Repl ; poster le résultat sur [WEA-128](https://linear.app/weadu/issue/WEA-128/pd-detection-brief-agent-replit-infos-migration) via [`scripts/linear_issue_comment.py`](../../scripts/linear_issue_comment.py) et/ou compléter le §2 de ce fichier en PR sur `WeAdU-ltd/.github`. |

---

_Document vivant ; création : 2026-05-11 (WEA-128)._
