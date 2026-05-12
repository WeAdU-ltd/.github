# pd-detection — brief agent Replit (infos migration)

**Référent WeAdU** : **rien à faire** sur la fusion des PR du dépôt `.github` (auto-merge après CI). La **section 1** ci-dessous est à exécuter depuis une session **Cursor dans le Repl pd-detection**, pas comme consigne dans le chat au référent — aligné [WEA-35 §7](./WEA-35-weadu-socle-v5-lab-template.md) et [`AGENTS.md`](../../AGENTS.md) (*Zéro friction référent*).

**Linear** : brief [WEA-128](https://linear.app/weadu/issue/WEA-128/pd-detection-brief-agent-replit-infos-migration), synthèse inventaire [WEA-129](https://linear.app/weadu/issue/WEA-129/pd-detection-synthese-inventaire-ticket-a-jour), dépôt GitHub [WEA-130](https://linear.app/weadu/issue/WEA-130) — chaîne [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents). **Ligne inventaire** : [WEA-33](./WEA-33-replit-inventory.md) **#15** (Repl ID préfixe documenté : `3e94a8f8-…`). **Périmètre isolation Finance-RH** : [WEA-37](https://linear.app/weadu/issue/WEA-37/replit-migration-repos-perso-isolation-acces), [WEA-13](./WEA-13-github-access-model.md).

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

### 2 bis. Gabarit GitHub en attendant l’export Repl ([WEA-131](https://linear.app/weadu/issue/WEA-131/pd-detection-code-importe-readme-procedure-de-run))

Arbre **socle WEA-35 + appli Python minimale + CI** : [`templates/pd-detection-app/README.md`](../../templates/pd-detection-app/README.md). **Cible actuelle** : pousser dans **`JeffWeadu/pd-detection`** via **Option A** du README (script [`scripts/init_pd_detection_app_template.sh`](../../scripts/init_pd_detection_app_template.sh) avec `--force` sur un clone du dépôt). Option org **`WeAdU-ltd/pd-detection`** : Option B du même README. Les **noms de secrets** métier restent à reporter depuis l’export Markdown (section 2 ci-dessus) ; [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh).

---

## 3. Synthèse (WEA-129) — inventaire / ticket à jour

| Champ | État (doc dépôt `WeAdU-ltd/.github`) |
|-------|--------------------------------------|
| **Inventaire [WEA-33](./WEA-33-replit-inventory.md) ligne #15** | Colonne **Git** : [`JeffWeadu/pd-detection`](https://github.com/JeffWeadu/pd-detection) — **confirmée** (**2026-05-11**) ; colonnes **Notes** et intro WEA-33 alignées avec ce runbook (sections 3 à 5). Autres colonnes (DB Replit, AO, secrets noms, AWS) : **en attente** export Repl §2 ([WEA-35 §7](./WEA-35-weadu-socle-v5-lab-template.md)). |
| **Réponse agent Repl** | **Non consolidée dans ce fichier** : aucun export Markdown n’a été fusionné dans le §2 depuis une session **dans** le Repl **pd-detection**. La suite reste la consigne §1 + commentaire API sur [WEA-128](https://linear.app/weadu/issue/WEA-128/pd-detection-brief-agent-replit-infos-migration) ([`scripts/linear_issue_comment.py`](../../scripts/linear_issue_comment.py)). |
| **Critère de fait WEA-129** | **Colonnes équivalentes** : **Notes**, intro WEA-33 et **Git** à jour **ou** PR dépôt `.github` fusionnée = preuve ; détail runtime des autres colonnes = **en attente** export Repl. |

---

## 4. Critère de fait WEA-128 (réponse Repl vs inaccessible)

| Exigence | État |
|----------|------|
| Réponse de l’agent Repl **ou** justification documentée si le Repl est inaccessible | **Justification documentée** : même limite que [WEA-35 §7](./WEA-35-weadu-socle-v5-lab-template.md) — l’agent GitHub / Cloud sur `.github` **ne peut pas** substituer l’export runtime. La preuve d’inaccessibilité depuis cet environnement est ce paragraphe + la ligne **#15** [WEA-33](./WEA-33-replit-inventory.md) (vue Socle **sans** ouverture du Repl). **Suite** : exécuter la consigne §1 **dans** le Repl ; poster le résultat sur [WEA-128](https://linear.app/weadu/issue/WEA-128/pd-detection-brief-agent-replit-infos-migration) via [`scripts/linear_issue_comment.py`](../../scripts/linear_issue_comment.py) et/ou compléter le §2 de ce fichier en PR sur `WeAdU-ltd/.github`. |

---

## 5. Dépôt GitHub (WEA-130) — créé ou confirmé

| Rôle | État |
|------|------|
| **URL équivalente GitHub** | **`https://github.com/JeffWeadu/pd-detection`** — dépôt **privé**, compte **perso** ; confirmé **2026-05-11** (propriétaire). **Pas** sous `WeAdU-ltd/` à ce stade — aligné Finance-RH / isolation ([WEA-13](./WEA-13-github-access-model.md), [WEA-37](https://linear.app/weadu/issue/WEA-37/replit-migration-repos-perso-isolation-acces)). Une bascule ultérieure vers `WeAdU-ltd/<repo>` resterait une décision produit / accès. |
| **Vérification API agent** | Le jeton CI utilisé par les agents cloud sur ce dépôt **ne résout pas** `JeffWeadu/pd-detection` via `gh repo view` (**404** attendu sans droit sur le perso) ; la vérité URL est **tracée ici** et sur le ticket **WEA-130**. |
| **`WeAdU-ltd/<repo>`** | **N/A** tant que le code vit sur **JeffWeadu** ; le ticket template « créer sous WeAdU-ltd » est **satisfait** au sens « URL canonique connue » via ce dépôt perso documenté. |
| **Label Linear groupe `repo`** | Aligner sur **`JeffWeadu/pd-detection`** lorsque le label existe dans l’espace Linear ([WEA-17](https://linear.app/weadu/issue/WEA-17/charte-agents-linear-source-interdits-features-nouveaux-projets)). |

---

_Document vivant ; création : 2026-05-11 (WEA-128) ; synthèse WEA-129 / dépôt WEA-130 : **2026-05-11**._
