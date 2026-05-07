# WEA-33 — Replit : inventaire (~15 projets) et dépendances

Document d’ancrage pour le ticket [WEA-33](https://linear.app/weadu/issue/WEA-33/replit-inventaire-15-projets-et-dependances) dans le dépôt **`WeAdU-ltd/.github`**.

**Dépendances Linear** : [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces) (inventaire GitHub), [WEA-13](https://linear.app/weadu/issue/WEA-13/github-modele-dacces-interne-partage-perso-finance-rh-isole) (modèle d’accès perso / société / finance-RH). Chaîne suite migration : [WEA-35](https://linear.app/weadu/issue/WEA-35/weadu-socle-v5-lab-audit-template-github-cursor) ([doc dépôt](./WEA-35-weadu-socle-v5-lab-template.md)) → [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents) ([doc dépôt](./WEA-36-replit-migration-societe.md)) → [WEA-37](https://linear.app/weadu/issue/WEA-37/replit-migration-repos-perso-isolation-acces) → [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete).

**Secrets** : ne pas copier de valeurs dans ce fichier. Les jetons vivent dans **Secrets** de chaque Repl, le **socle secrets** ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)) et 1Password si besoin. Ici : **noms de variables ou nature**, pas les contenus.

**Source des lignes ci-dessous** : export consolidé **Socle V5.1** (Repl *Weadu-Socle-V5-Lab*), **2026-03-29**, croisé avec `config/infra_projects.json`, snapshot CSV équipe **2026-03-17**, et docs internes Socle. **Mise à jour Socle (2026-05-04)** : export agent Repl sans valeurs de secrets → [`weadu-socle-v5-lab-replit-snapshot-2026-05-04.md`](./weadu-socle-v5-lab-replit-snapshot-2026-05-04.md) (ticket [WEA-44](https://linear.app/weadu/issue/WEA-44/weadu-socle-v5-lab-brief-agent-replit-infos-migration)). **Mise à jour COS / EC2 (2026-05-05)** : runbook sans accès Repl → [`cos-replit-ec2-migration-2026-05-04.md`](./cos-replit-ec2-migration-2026-05-04.md) (chaîne [WEA-49](https://linear.app/weadu/issue/WEA-49/repl-2-chief-of-staff-virtuel-ia-cos-migration-replit-github-societe)). **Repl COS fermé (2026-05)** : ligne #2 du tableau — repo GitHub + fermeture Repl ; même runbook. **Mise à jour Linear (2026-05-05)** : la chaîne d’épique **[Repl 11] suspended accounts clean up** a été **retirée** sur Linear (pas de migration GitHub prévue pour ce Repl) ; la ligne **#11** reste dans l’inventaire Socle pour traçabilité. Les autres lignes du tableau restent sur la photo mars 2026 jusqu’à passage équivalent.

**Limite de fraîcheur** : si Replit n’est **plus utilisé** depuis un moment, les changements faits **ailleurs** (GitHub, poste local, EC2, secrets hors Repl) **ne sont pas** reflétés dans Socle ni dans l’UI Replit. Ce tableau reste une **photo à fin mars 2026** utile pour la chaîne migration / fermeture ([WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents) → [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete)) ; la **vérité opérationnelle actuelle** se lit plutôt dans les **dépôts GitHub** et les **hébergements** réellement en prod (croiser [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces), [WEA-29](https://linear.app/weadu/issue/WEA-29/aws-inventaire-ec2-ubuntu-windows-taches-selenium)).

---

## 1. Comment compléter ou régénérer

1. **Replit** : nom, déploiement `.replit.app`, onglet Git, Database, Deployments (Always On / Autoscale), Secrets (**noms** uniquement).
2. **Git** : aligner avec [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces) (`org/repo`).
3. **AWS** : croiser avec [WEA-29](https://linear.app/weadu/issue/WEA-29/aws-inventaire-ec2-ubuntu-windows-taches-selenium) ; ne pas recopier d’IP ou de clés API dans ce dépôt.
4. **Automatisation** : token Replit d’équipe (secret [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)) + script API pour remplir les colonnes encore `inconnu`.

---

## 2. Synthèse

| Indicateur | Valeur |
|------------|--------|
| Lignes inventoriées (principales) | **21** |
| Statut **Vérifié** (colonnes complètes depuis le Repl courant) | **1** (Socle) |
| Statut **Partiel** | **20** |
| Entrées exclues / à réconcilier (hors tableau) | **4** (voir §4) |

---

## 3. Tableau des Repls + statut

| # | Nom Repl | Replit ID (réf.) | URL / déploiement (aperçu) | Statut inventaire | Git | Replit DB | Always On | Secrets (noms / nature) | Lien AWS | Priorité migration | Perso / Société / Finance-RH (WEA-13) | Notes |
|---|----------|------------------|----------------------------|-------------------|-----|-----------|------------|-------------------------|----------|---------------------|---------------------------------------|-------|
| 1 | Weadu-Socle-V5-Lab | `3194f6df-…` | `weadu-socle-v-5-lab.replit.app` ; VM (`.replit`) — état **Always On** non confirmé (voir snapshot §6) | **Vérifié** | pas de remote GitHub ; `gitsafe-backup` + remotes `subrepl-*` (détail §3 [snapshot 2026-05-04](./weadu-socle-v5-lab-replit-snapshot-2026-05-04.md)) | **Oui** (PostgreSQL : tables `kv_state`, `ideas` — snapshot §5) | **non confirmé** | noms §4 [snapshot 2026-05-04](./weadu-socle-v5-lab-replit-snapshot-2026-05-04.md) ; `DATABASE_*` injectés par Replit | **Oui** — SSH EC2 + DynamoDB `eu-west-2` (noms tables snapshot §5 ; pas d’IP ici — [WEA-29](./WEA-29-aws-ec2-inventory.md)) | **P0** | Société | Hub — synthèse fraîche agent Repl : [WEA-44](https://linear.app/weadu/issue/WEA-44/weadu-socle-v5-lab-brief-agent-replit-infos-migration) / [WEA-45](https://linear.app/weadu/issue/WEA-45/weadu-socle-v5-lab-synthese-inventaire-ticket-a-jour) |
| 2 | Chief of Staff Virtuel IA (COS) | `cfe38994-…` | Trafic prod via **EC2** (`leadgen.generads.com` → Caddy → app), pas hébergement Replit ; tâches `WeAdU-COS` / `WeAdU-COS-Watchdog` — [WEA-29](./WEA-29-aws-ec2-inventory.md) §3.1 | **Partiel** | [`WeAdU-ltd/cos`](https://github.com/WeAdU-ltd/cos) — **confirmé** ; Repl **fermé** (**2026-05**) — [runbook COS](./cos-replit-ec2-migration-2026-05-04.md) | inconnu (charge sur EC2) | **Oui (EC2)** — pas AO Replit pour la prod décrite | pont Socle → EC2 + chemins caches — [snapshot Socle](./weadu-socle-v5-lab-replit-snapshot-2026-05-04.md) §6 ; **plus de Repl COS** | **Oui** — EC2 Lightsail Windows ; pas d’IP dans ce tableau — [WEA-29](./WEA-29-aws-ec2-inventory.md) | **P0** | Société | Chaîne migration : [WEA-49](https://linear.app/weadu/issue/WEA-49/repl-2-chief-of-staff-virtuel-ia-cos-migration-replit-github-societe) ; doc [`cos-replit-ec2-migration-2026-05-04.md`](./cos-replit-ec2-migration-2026-05-04.md) ; **Repl fermé 2026-05** |
| 3 | after-framfield-cockpit | `6514c921-…` | Repl **supprimé** (**2026-05-05**) ; prod = **Google Sheet** + API (compte de service / GitHub Actions) | **Partiel** (inventaire figé hors Replit) | [`JeffWeadu/after-framfield-cockpit`](https://github.com/JeffWeadu/after-framfield-cockpit) — privé, **code + README** + workflow smoke Sheets sur `main` | inconnu | **N/A** (Repl supprimé) | GitHub Secrets + 1Password ; plus de Secrets Replit pour ce projet | inconnu | **P1** | **Perso** | Repl supprimé — [runbook](./after-framfield-cockpit-replit-2026-05-05.md), chaîne [WEA-55](https://linear.app/weadu/issue/WEA-55/repl-3-after-framfield-cockpit-migration-replit-github-persosociete-a-trancher) **Done** |
| 4 | negative-search-terms-tool | `5ffebe14-…` | non déployé (snapshot 2026-03-17) ; cutover GitHub en cours | **Partiel** | [`WeAdU-ltd/Negative-Terms`](https://github.com/WeAdU-ltd/Negative-Terms) — **confirmé** (privé) | inconnu | inconnu | probable Google Ads + kit | inconnu | **P1** | Société | [WEA-61](https://linear.app/weadu/issue/WEA-61/repl-4-negative-search-terms-tool-migration-replit-github-societe) — [runbook](./negative-search-terms-replit-migration-2026-05-06.md) |
| 5 | wellbots-shopping-ads-checker | `79eb34c6-…` | **Prod** : CI GitHub → **EC2 Windows** ([runbook](./wellbots-shopping-ads-checker-replit-migration-2026-05-06.md) §5) ; chaîne **[WEA-67](https://linear.app/weadu/issue/WEA-67/repl-5-wellbots-shopping-ads-checker-migration-replit-github-societe)** **terminée** (**2026-05**) | **Partiel** | [`WeAdU-ltd/SH-Checker-Bids`](https://github.com/WeAdU-ltd/SH-Checker-Bids) — **confirmé** (privé) | inconnu | inconnu | probable Google Ads + kit | **aligné EC2** (déploiement doc dépôt) | **P1** | Société | [WEA-67](https://linear.app/weadu/issue/WEA-67/repl-5-wellbots-shopping-ads-checker-migration-replit-github-societe) — [runbook](./wellbots-shopping-ads-checker-replit-migration-2026-05-06.md) ; **migration terminée 2026-05** |
| 6 | WeAdU LeadGen | `345d8dd5-…` | idem ; ne pas confondre URL prod avec COS | **Partiel** | inconnu | inconnu | inconnu | probable kit | inconnu | **P2** | Société | |
| 7 | Max Conv Val Budget Mngt | `d32b27a6-…` | absent CSV 2026-03-17 | **Partiel** | inconnu | inconnu | inconnu | probable Google Ads + kit | inconnu | **P2** | Société | |
| 8 | Waste Watcher | `f09a27de-…` | idem | **Partiel** | inconnu | inconnu | inconnu | probable Google Ads + kit | inconnu | **P2** | Société | |
| 9 | Automatic Google Ads tracking monitoring | `7fc2b09c-…` (infra *Brand-crea-bids*) | idem | **Partiel** | inconnu | inconnu | inconnu | probable Google Ads + kit | inconnu | **P2** | Société | **À réconcilier** avec UUID `6b3e66a1-…` (CSV équipe, autre Repl / rename) |
| 10 | Wellbots real-time figures | `6301f251-…` | idem | **Partiel** | inconnu | inconnu | inconnu | probable Google Ads + kit | inconnu | **P2** | Société | |
| 11 | suspended accounts clean up | `139389d0-…` | idem | **Partiel** | inconnu | inconnu | inconnu | probable Google Ads + kit | inconnu | **P2** | Société | **Hors migration Linear** : épique `[Repl 11] …` supprimée sur Linear (**2026-05-05**) — pas de ticket de chaîne WEA-36 ; le Repl peut rester sur Replit ou être archivé hors projet migration. |
| 12 | Dashboard — Carmino & monPL | `89725b9e-…` | possible passage par hub dashboard EC2 ; à confirmer | **Partiel** | inconnu | inconnu | inconnu | inconnu (clés dashboard côté vault Socle) | inconnu | **P2** | Société | Absent CSV 2026-03-17 |
| 13 | Recommandations mngt | `ad9b5532-…` | idem | **Partiel** | inconnu | inconnu | inconnu | probable Google Ads + kit | inconnu | **P2** | Société | |
| 14 | Ads Performance Analyze | `cb5cc4be-…` | absent CSV 2026-03-17 | **Partiel** | inconnu | inconnu | inconnu | probable Google Ads + kit | inconnu | **P2** | Société | |
| 15 | pd-detection | `3e94a8f8-…` | idem | **Partiel** | inconnu | inconnu | inconnu | probable kit | inconnu | **P2** | **Finance-RH** | Suivi COS selon Socle |
| 16 | bad performers | `8ae0b387-…` | idem | **Partiel** | inconnu | inconnu | inconnu | probable Google Ads + kit | inconnu | **P3** | Société | |
| 17 | Feed Optimizer | `cb7bc686-…` | idem | **Partiel** | inconnu | inconnu | inconnu | probable Google Ads + kit | inconnu | **P3** | Société | |
| 18 | Dashboard — Epic Extender | `bc1c605a-…` | idem | **Partiel** | inconnu | inconnu | inconnu | probable kit | inconnu | **P3** | Société | |
| 19 | Bad Performer labels | `67b17d9b-…` | absent CSV 2026-03-17 | **Partiel** | inconnu | inconnu | inconnu | probable Google Ads + kit | inconnu | **P3** | Société | |
| 20 | Test tracker | `62ce3ea8-…` | idem | **Partiel** | inconnu | inconnu | inconnu | probable kit | inconnu | **P3** | Société | |
| 21 | Divers | `d6bcecff-…` | présent CSV équipe ; absent `infra_projects.json` | **Partiel** | inconnu | inconnu | inconnu | inconnu | inconnu | **À décider** | Société (probable) | Scratch / archivage ? |

_UUID complets : voir source dans le Repl Socle ; seuls les préfixes sont repris ici pour lisibilité._

---

## 4. Exclus / à réconcilier (hors tableau principal)

| Sujet | ID / ref. | Action |
|-------|-----------|--------|
| **Obsolete** | `8a0d25c6-…` | Archivé / exclu inventaire actif |
| **Doublon nom « Automatic Google Ads… »** | `7fc2b09c-…` vs `6b3e66a1-…` | Vérifier dans le dashboard équipe : un ou deux Repls |
| **Divers** | `d6bcecff-…` | Déjà ligne 21 ; décider enregistrement infra ou archivage |
| **suspended accounts clean up (ligne #11)** | `139389d0-…` | **Hors périmètre migration GitHub** (décision **2026-05-05**) : pas d’épique Linear `[Repl 11]` ; ne pas recréer via `linear_create_wea36_repl_issues.py` |

---

## 5. Écart vs critères de fait ([règle Done](https://linear.app/weadu/document/regle-agents-criteres-de-fait-avant-done-tous-projets-2b32aec9e234))

| Critère ticket | État |
|----------------|------|
| Tableau des Repls + statut | **Rempli** : 21 lignes avec noms, priorités, classification, statut **Vérifié** / **Partiel** (état Replit / Socle **figé** ~mars 2026 — voir encadré *Limite de fraîcheur* ci-dessus). |
| Détail Git / DB Replit / AO / secrets / AWS par Repl | **Partiel** : 20 lignes encore largement `inconnu` sur plusieurs colonnes (données non visibles depuis Socle sans ouvrir chaque Repl ou API équipe). |

**Suite pour un Done « strict »** : pour chaque ligne **Partiel**, compléter depuis le dashboard Replit (ou script API) les colonnes Git, DB, AO, noms de secrets, AWS ; réconcilier l’UUID #9 ; *after-framfield-cockpit* **tranché Perso** → [`JeffWeadu/after-framfield-cockpit`](https://github.com/JeffWeadu/after-framfield-cockpit) ; décision sur *Divers* / *Obsolete*.

**Suite pour un Done « vague 1 » acceptée par l’humain** : si l’équipe accepte que l’inventaire **Socle + statuts Partiel explicites** satisfait le critère « tableau + statut » pour cette itération, documenter cette acceptation **sur le ticket Linear** puis passer **Done**.

---

_Document vivant ; dernière intégration dépôt : données Socle 2026-03-29 ; alignement chaîne Linear 2026-05-05 (Repl #11 hors migration)._
