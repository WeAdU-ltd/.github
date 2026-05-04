# WEA-33 — Replit : inventaire (~15 projets) et dépendances

Document d’ancrage pour le ticket [WEA-33](https://linear.app/weadu/issue/WEA-33/replit-inventaire-15-projets-et-dependances) dans le dépôt **`WeAdU-ltd/.github`**.

**Dépendances Linear** : [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces) (inventaire GitHub), [WEA-13](https://linear.app/weadu/issue/WEA-13/github-modele-dacces-interne-partage-perso-finance-rh-isole) (modèle d’accès perso / société / finance-RH). Chaîne suite migration : [WEA-35](https://linear.app/weadu/issue/WEA-35/weadu-socle-v5-lab-audit-template-github-cursor) ([doc dépôt](./WEA-35-weadu-socle-v5-lab-template.md)) → [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents) ([doc dépôt](./WEA-36-replit-migration-societe.md)) → [WEA-37](https://linear.app/weadu/issue/WEA-37/replit-migration-repos-perso-isolation-acces) → [WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete).

**Secrets** : ne pas copier de valeurs dans ce fichier. Les jetons vivent dans **Secrets** de chaque Repl, le **socle secrets** ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)) et 1Password si besoin. Ici : **noms de variables ou nature**, pas les contenus.

**Source des lignes ci-dessous** : export consolidé **Socle V5.1** (Repl *Weadu-Socle-V5-Lab*), **2026-03-29**, croisé avec `config/infra_projects.json`, snapshot CSV équipe **2026-03-17**, et docs internes Socle. Les détails narratifs (listes complètes de noms de secrets, notes techniques) restent dans le Repl Socle ; ce fichier garde la **vue dépôt** alignée WEA-33.

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
| Entrées exclues / à réconcilier (hors tableau) | **3** (voir §4) |

---

## 3. Tableau des Repls + statut

| # | Nom Repl | Replit ID (réf.) | URL / déploiement (aperçu) | Statut inventaire | Git | Replit DB | Always On | Secrets (noms / nature) | Lien AWS | Priorité migration | Perso / Société / Finance-RH (WEA-13) | Notes |
|---|----------|------------------|----------------------------|-------------------|-----|-----------|------------|-------------------------|----------|---------------------|---------------------------------------|-------|
| 1 | Weadu-Socle-V5-Lab | `3194f6df-…` | Workspace dev Replit ; pas de prod stable `.replit.app` (au 2026-03-17) | **Vérifié** | inconnu (pas de `github_repo` dans infra export) | **Oui** (PostgreSQL managé) | inconnu | oui — voir Repl Socle (liste noms : vault 1P, Slack, AWS, DB, etc.) | **Oui** — SSH vers EC2 (monitoring COS) ; DynamoDB `eu-west-2` (stacks Portfolio / registry, noms tables côté Socle) | **P0** | Société | Hub orchestration / secrets |
| 2 | Chief of Staff Virtuel IA (COS) | `cfe38994-…` | Trafic prod via **EC2** (`leadgen.generads.com` → Caddy → app), pas hébergement Replit | **Partiel** | inconnu | inconnu (charge sur EC2) | **Oui (EC2)** — tâche planifiée Windows, pas AO Replit | partiel — secrets poussés par Socle documentés côté Socle ; liste complète dans Repl COS | **Oui** — déploiement sur EC2 Lightsail | **P0** | Société | |
| 3 | after-framfield-cockpit | `6514c921-…` | OAuth redirect sur hostname workspace éphémère (non stable) | **Partiel** | inconnu | inconnu | inconnu | probable kit V5.1 | inconnu | **P1** | Société / Perso à trancher | Absent CSV 2026-03-17 |
| 4 | negative-search-terms-tool | `5ffebe14-…` | non déployé (snapshot 2026-03-17) | **Partiel** | inconnu | inconnu | inconnu | probable Google Ads + kit | inconnu | **P1** | Société | |
| 5 | wellbots-shopping-ads-checker | `79eb34c6-…` | idem | **Partiel** | inconnu | inconnu | inconnu | probable Google Ads + kit | inconnu | **P1** | Société | |
| 6 | WeAdU LeadGen | `345d8dd5-…` | idem ; ne pas confondre URL prod avec COS | **Partiel** | inconnu | inconnu | inconnu | probable kit | inconnu | **P2** | Société | |
| 7 | Max Conv Val Budget Mngt | `d32b27a6-…` | absent CSV 2026-03-17 | **Partiel** | inconnu | inconnu | inconnu | probable Google Ads + kit | inconnu | **P2** | Société | |
| 8 | Waste Watcher | `f09a27de-…` | idem | **Partiel** | inconnu | inconnu | inconnu | probable Google Ads + kit | inconnu | **P2** | Société | |
| 9 | Automatic Google Ads tracking monitoring | `7fc2b09c-…` (infra *Brand-crea-bids*) | idem | **Partiel** | inconnu | inconnu | inconnu | probable Google Ads + kit | inconnu | **P2** | Société | **À réconcilier** avec UUID `6b3e66a1-…` (CSV équipe, autre Repl / rename) |
| 10 | Wellbots real-time figures | `6301f251-…` | idem | **Partiel** | inconnu | inconnu | inconnu | probable Google Ads + kit | inconnu | **P2** | Société | |
| 11 | suspended accounts clean up | `139389d0-…` | idem | **Partiel** | inconnu | inconnu | inconnu | probable Google Ads + kit | inconnu | **P2** | Société | |
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

---

## 5. Écart vs critères de fait ([règle Done](https://linear.app/weadu/document/regle-agents-criteres-de-fait-avant-done-tous-projets-2b32aec9e234))

| Critère ticket | État |
|----------------|------|
| Tableau des Repls + statut | **Rempli** : 21 lignes avec noms, priorités, classification, statut **Vérifié** / **Partiel** (état Replit / Socle **figé** ~mars 2026 — voir encadré *Limite de fraîcheur* ci-dessus). |
| Détail Git / DB Replit / AO / secrets / AWS par Repl | **Partiel** : 20 lignes encore largement `inconnu` sur plusieurs colonnes (données non visibles depuis Socle sans ouvrir chaque Repl ou API équipe). |

**Suite pour un Done « strict »** : pour chaque ligne **Partiel**, compléter depuis le dashboard Replit (ou script API) les colonnes Git, DB, AO, noms de secrets, AWS ; réconcilier l’UUID #9 ; trancher *after-framfield-cockpit* Perso vs Société ; décision sur *Divers* / *Obsolete*.

**Suite pour un Done « vague 1 » acceptée par l’humain** : si l’équipe accepte que l’inventaire **Socle + statuts Partiel explicites** satisfait le critère « tableau + statut » pour cette itération, documenter cette acceptation **sur le ticket Linear** puis passer **Done**.

---

_Document vivant ; dernière intégration dépôt : données Socle 2026-03-29._
