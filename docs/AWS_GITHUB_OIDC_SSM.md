# GitHub Actions ↔ AWS (OIDC) + Systems Manager — WeAdU

**Compte / région principale documentée :** `774180750242`, **`eu-west-2`** (London).

**But :** déclencher **`ssm:SendCommand`** (et besoins dérivés) depuis **GitHub Actions** **sans** clé AWS longue durée dans les repos. Ce fichier est la **référence versionnée** ; pour les humains, les agents peuvent aussi résumer les étapes **inline** dans le chat ou sur Linear — voir [`AGENTS.md`](../AGENTS.md).

---

## Ce qu’un agent dans Cursor **ne peut pas** faire à ta place

La vérification « OIDC GitHub déjà créé dans IAM ? » nécessite **des credentials AWS** (CLI ou console). Dans une session sans AWS CLI ni compte, la réponse est **non vérifiable** — il faut **une** exécution du script ci‑dessous sur une machine où `aws` est installé et connecté au compte **`774180750242`**, ou une lecture IAM dans la console.

---

## Ce qui est en place (`.github`)

| Élément | Valeur |
|---------|--------|
| **Identity provider IAM** | `token.actions.githubusercontent.com` |
| **Rôle OIDC** | `WeAdUGitHubOIDC-SSM` — ARN du type `arn:aws:iam::774180750242:role/WeAdUGitHubOIDC-SSM` |
| **Trust policy** | `repo:WeAdU-ltd/.github:*` (pas les autres dépôts tant que la trust n’est pas élargie) |
| **Secret GitHub (repo `.github`)** | **`AWS_ROLE_ARN`** = ARN complet du rôle ci-dessus |
| **Workflow OIDC (STS)** | [`.github/workflows/aws-oidc-smoke.yml`](../.github/workflows/aws-oidc-smoke.yml) — vérifie `aws sts get-caller-identity` |
| **Workflow SSM (Run Command)** | [`.github/workflows/aws-ssm-send-command-smoke.yml`](../.github/workflows/aws-ssm-send-command-smoke.yml) — PowerShell `hostname` sur l’instance **`mi-08ba03ce367298b11`** (Windows COS / hybrid activation) |

**Instance managée SSM (COS Windows, hybrid)** : **`mi-08ba03ce367298b11`**. Pour changer de cible, éditer la variable **`MANAGED_INSTANCE_ID`** dans **`aws-ssm-send-command-smoke.yml`**.

---

## Vérifier OIDC côté IAM (poste avec AWS CLI)

```bash
bash scripts/aws_github_oidc_probe.sh
```

Le script affiche **`sts get-caller-identity`**, liste les **ARN** des fournisseurs OIDC, puis l’**issuer** (`Url`) de chacun.

**Interprétation rapide :**

- **Liste vide** d’ARN OIDC → **aucun** fournisseur OIDC IAM ; il faudra **créer** celui de GitHub (étape unique compte, doc AWS).
- **Issuer `https://token.actions.githubusercontent.com`** → OIDC GitHub est présent.

Console équivalente : **IAM** → **Identity providers** → chercher **token.actions.githubusercontent.com**.

---

## Lightsail — lecture seule (policy JSON dans ce dépôt)

AWS ne fournit **pas** de politique managée du type `AmazonLightsailReadOnlyAccess` à attacher comme les autres services. Le fichier canonique est :

**[`docs/policies/WeAdU-GitHubOIDC-LightsailReadOnly.json`](./policies/WeAdU-GitHubOIDC-LightsailReadOnly.json)** (`lightsail:Get*`, `lightsail:List*` sur `*`).

### Attacher cette policy au rôle OIDC (une fois)

1. Console **AWS** → **IAM** → **Policies** → **Create policy** → onglet **JSON** → coller le contenu du fichier **`WeAdU-GitHubOIDC-LightsailReadOnly.json`** → **Next** → nom **`WeAdU-GitHubOIDC-LightsailReadOnly`** → **Create policy**.
2. **IAM** → **Roles** → **`WeAdUGitHubOIDC-SSM`** → **Add permissions** → **Attach policies** → cocher **`WeAdU-GitHubOIDC-LightsailReadOnly`** → **Add permissions**.

*(Si tu es déjà au plafond de politiques managées sur le rôle, détache d’abord une policy non indispensable ou demande une augmentation de quota — voir quotas IAM.)*

---

## Création incrémentale (référence, une fois par compte)

1. **Identity provider OIDC GitHub** dans IAM (issuer `token.actions.githubusercontent.com`, audience `sts.amazonaws.com`) — voir [Configuring OpenID Connect in Amazon Web Services](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services).
2. **Rôle IAM** dont la **trust policy** limite le **`sub`** au périmètre voulu (repo, environnement, branche) — aligné avec ce qui est déjà documenté dans le tableau ci‑dessus pour **`WeAdUGitHubOIDC-SSM`**.
3. **Permissions** du rôle : au minimum ce dont les workflows ont besoin (`ssm:SendCommand`, etc.) — **conditionnées** par instance (`mi-*`) ou par **tag** sur les ressources que SSM gère, plutôt que `Resource: "*"` sur tout le compte.

---

## Ne pas élargir sans besoin

- **Secret org** `AWS_ROLE_ARN` sur **tous** les repos : seulement si tu **élargis aussi** la **trust policy** du rôle avec d’autres `repo:WeAdU-ltd/…` — sinon les workflows des autres repos **échoueront** (`AssumeRoleWithWebIdentity`). Tant que la trust reste à **`WeAdU-ltd/.github`**, le secret **`AWS_ROLE_ARN`** suffit **sur ce dépôt** uniquement.

En cas de workflow ou dépôt compromis, un rôle trop large pourrait envoyer des commandes à **n’importe quelle** machine du compte. Élargir le périmètre = **ajouter des tags** sur plus de serveurs ou des conditions IAM explicites, pas ouvrir `*` sans réflexion.

---

## Suite (automation dans ce dépôt)

Les workflows listés dans le tableau ci‑dessus utilisent déjà **`aws-actions/configure-aws-credentials`** avec **`role-to-assume`**. Pour de nouveaux cas : réutiliser le même rôle et les mêmes garde-fous, ou documenter ici toute nouvelle policy / trust.

---

_Fichier vivant ; pas de secrets dans ce fichier._
