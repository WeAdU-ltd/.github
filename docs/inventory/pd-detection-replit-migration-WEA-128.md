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
| Markdown produit par l’agent **dans** le Repl **pd-detection** | **Ingéré** (**2026-05-12**) — copie versionnée : [`pd-detection-replit-export-2026-05-12.md`](./pd-detection-replit-export-2026-05-12.md). **Source unique** : Linear **WEA-128** et le dépôt **`JeffWeadu/pd-detection`** peuvent se contenter d’un **lien** vers ce fichier pour éviter les divergences. |

### 2 bis. Gabarit GitHub en attendant l’export Repl ([WEA-131](https://linear.app/weadu/issue/WEA-131/pd-detection-code-importe-readme-procedure-de-run))

Arbre **socle WEA-35 + appli Python minimale + CI** : [`templates/pd-detection-app/README.md`](../../templates/pd-detection-app/README.md). **Cible actuelle** : pousser dans **`JeffWeadu/pd-detection`** via **Option A** du README (script [`scripts/init_pd_detection_app_template.sh`](../../scripts/init_pd_detection_app_template.sh) avec `--force` sur un clone du dépôt). Option org **`WeAdU-ltd/pd-detection`** : Option B du même README. Les **noms de secrets** métier sont recopiés dans [`pd-detection-replit-export-2026-05-12.md`](./pd-detection-replit-export-2026-05-12.md) ; [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh).

---

## 3. Synthèse (WEA-129) — inventaire / ticket à jour

| Champ | État (doc dépôt `WeAdU-ltd/.github`) |
|-------|--------------------------------------|
| **Inventaire [WEA-33](./WEA-33-replit-inventory.md) ligne #15** | Colonne **Git** : [`JeffWeadu/pd-detection`](https://github.com/JeffWeadu/pd-detection) — **confirmée** ; **URL / déploiement**, **DB**, **AO**, **secrets (noms)**, **AWS** : voir export [**2026-05-12**](./pd-detection-replit-export-2026-05-12.md). |
| **Réponse agent Repl** | **Consolidée** dans [`pd-detection-replit-export-2026-05-12.md`](./pd-detection-replit-export-2026-05-12.md) (**2026-05-12**). |
| **Critère de fait WEA-129** | **Colonnes équivalentes** : **Notes**, intro WEA-33, **Git** + détail runtime via export = **fait** pour l’itération export ; cutover prod : **WEA-132**. |

---

## 4. Critère de fait WEA-128 (réponse Repl vs inaccessible)

| Exigence | État |
|----------|------|
| Réponse de l’agent Repl **ou** justification documentée si le Repl est inaccessible | **Export ingéré** (**2026-05-12**) : [`pd-detection-replit-export-2026-05-12.md`](./pd-detection-replit-export-2026-05-12.md). La justification « agent `.github` seul » ne s’applique plus pour la **précision runtime** ; elle reste valable si le fichier devait être **incomplet** sans session Repl. |

---

## 5. Dépôt GitHub (WEA-130) — créé ou confirmé

| Rôle | État |
|------|------|
| **URL équivalente GitHub** | **`https://github.com/JeffWeadu/pd-detection`** — dépôt **privé**, compte **perso** ; confirmé **2026-05-11** (propriétaire). **Pas** sous `WeAdU-ltd/` à ce stade — aligné Finance-RH / isolation ([WEA-13](./WEA-13-github-access-model.md), [WEA-37](https://linear.app/weadu/issue/WEA-37/replit-migration-repos-perso-isolation-acces)). Une bascule ultérieure vers `WeAdU-ltd/<repo>` resterait une décision produit / accès. |
| **Vérification API agent** | Le jeton CI utilisé par les agents cloud sur ce dépôt **ne résout pas** `JeffWeadu/pd-detection` via `gh repo view` (**404** attendu sans droit sur le perso) ; la vérité URL est **tracée ici** et sur le ticket **WEA-130**. |
| **`WeAdU-ltd/<repo>`** | **N/A** tant que le code vit sur **JeffWeadu** ; le ticket template « créer sous WeAdU-ltd » est **satisfait** au sens « URL canonique connue » via ce dépôt perso documenté. |
| **Label Linear groupe `repo`** | Aligner sur **`JeffWeadu/pd-detection`** lorsque le label existe dans l’espace Linear ([WEA-17](https://linear.app/weadu/issue/WEA-17/charte-agents-linear-source-interdits-features-nouveaux-projets)). |

---

## 6. Cutover (WEA-132) — prod hors Replit + résiduel

Ticket : [WEA-132](https://linear.app/weadu/issue/WEA-132). Liste résiduelle : [WEA-36 §5](./WEA-36-replit-migration-societe.md). Fermeture Replit : [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete).

| Étape | État |
|-------|------|
| Code métier + secrets **noms** dans [`JeffWeadu/pd-detection`](https://github.com/JeffWeadu/pd-detection) (README + CI alignés gabarit **§2 bis** ci-dessus) | **À faire** côté dépôt applicatif |
| **Prod / scheduling** : ne plus dépendre du Repl (ou ligne résiduelle justifiée dans [WEA-36 §5](./WEA-36-replit-migration-societe.md)) | **À valider** — export §2 ingéré (**2026-05-12**) décrit AO / URLs ; bascule effective hors `.replit.app` à confirmer |
| **Secrets** Replit : retirés ou équivalents GitHub / hébergement ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)) | **À faire** quand la prod ne lit plus Replit |
| Preuve **WEA-132** (commentaire API ou PR dépôt avec date + verdict) | **En attente** |

---

_Document vivant ; création : 2026-05-11 (WEA-128) ; synthèse WEA-129 / dépôt WEA-130 : **2026-05-11** ; cutover WEA-132 : **2026-05-12** ; export Repl : **2026-05-12**._
