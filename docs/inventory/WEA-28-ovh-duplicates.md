# WEA-28 — OVH : inventaire et doublons (vs AWS, GCP…)

Document d’ancrage pour le ticket [WEA-28](https://linear.app/weadu/issue/WEA-28/ovh-inventaire-et-doublons-vs-aws-gcp) dans le dépôt **`WeAdU-ltd/.github`**.

**Dépendance** : le ticket indique une dépendance à [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh) (socle secrets). Les identifiants OVH et les clés API ne doivent **pas** figurer dans ce fichier ; ils restent dans le coffre (1Password / gestionnaire) une fois WEA-15 stabilisé. Ici : **noms de services, IDs publics, décisions**.

**Constat agent / CI** : aucun accès OVH, AWS ou GCP n’est disponible depuis ce dépôt. Les tableaux ci-dessous sont des **gabarits** à remplir par un **administrateur compte** (console OVH, facturation, DNS). Pour le parallèle multi-cloud, croiser avec [WEA-27](https://linear.app/weadu/issue/WEA-27/google-cloud-inventaire-projets-uris-oauth-doublons) et les inventaires AWS / autres lorsqu’ils existent.

---

## 1. Actifs OVH (liste à compléter)

### 1.1 Noms de domaine

| Domaine / zone | Produit (Web / DNS / transfert) | Date / contrat | Contact / renouvellement | Notes |
|-----------------|----------------------------------|----------------|---------------------------|-------|
| *À compléter* | | | | |

### 1.2 VPS / instances / Public Cloud

| Nom / hostname | Région | Rôle (prod, lab, mail relay…) | IP publique (si pertinent) | OS / stack | Notes |
|----------------|--------|-------------------------------|----------------------------|--------------|-------|
| *À compléter* | | | | | |

### 1.3 E-mail (MXplan, E-mail Pro, Hosted Exchange…)

| Offre | Domaine(s) | Boîtes / alias clés | Redondance / sauvegardes | Notes |
|-------|------------|---------------------|--------------------------|-------|
| *À compléter* | | | | |

### 1.4 Hébergement web / bases / fichiers

| Hébergement (Perso / Pro / Cloud Web) | Sites / apps | Bases de données | Liens vers déploiements (ex. GitHub Actions) | Notes |
|----------------------------------------|----------------|------------------|-----------------------------------------------|-------|
| *À compléter* | | | | |

### 1.5 Autres (Load Balancer, Kubernetes, stockage objet, réseau)

| Service OVH | Identifiant / nom | Usage | Notes |
|---------------|-------------------|-------|-------|
| *À compléter* | | | |

---

## 2. Doublons et chevauchements (vs AWS, GCP, autres)

Pour chaque ligne, indiquer si le même besoin est couvert ailleurs (risque de double facturation ou de divergence DNS / TLS).

| Actif OVH (réf. §1) | Recouvrement possible | Fournisseur / ressource cible | Gravité (coût, SPOF, sécurité) | Action proposée (voir §3) |
|---------------------|------------------------|-------------------------------|--------------------------------|---------------------------|
| *Ex. site statique* | *Même contenu sur S3 + CloudFront* | AWS | *À évaluer* | *Migrer / couper un des deux* |
| *À compléter* | | | | |

**Références internes** : inventaire Google Cloud [WEA-27](https://linear.app/weadu/issue/WEA-27/google-cloud-inventaire-projets-uris-oauth-doublons) ; inventaire GitHub / déploiements [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces).

---

## 3. Décisions brouillon — garder / migrer / couper

| Actif ou groupe | Décision | Cible si migration | Échéance / dépendances | Responsable |
|-----------------|----------|--------------------|------------------------|---------------|
| *À compléter* | **Garder** / **Migrer** / **Couper** | | | |

**Légende**

- **Garder** : OVH reste la source de vérité pour ce besoin.
- **Migrer** : bascule documentée (DNS, secrets, runbook) vers un autre fournisseur.
- **Couper** : résiliation après bascule ou abandon du besoin (vérifier sauvegardes et MX).

---

## 4. Suite opérationnelle (hors agent)

1. Exporter ou relever les factures / manager OVH et remplir les §1–3.
2. Aligner les secrets (comptes OVH, API application) avec [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh).
3. Mettre à jour ce fichier dans une PR ; cocher les critères de fait sur le ticket Linear uniquement lorsque les tableaux sont **réellement** remplis (pas de Done « sur gabarit vide »).
