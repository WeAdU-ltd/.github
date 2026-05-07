# GitHub Actions ↔ AWS (OIDC) + Systems Manager — WeAdU

**Compte / région principale documentée :** `774180750242`, **`eu-west-2`** (London).

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

## Lightsail — lecture seule (policy JSON dans ce dépôt)

AWS ne fournit **pas** de politique managée du type `AmazonLightsailReadOnlyAccess` à attacher comme les autres services. Le fichier canonique est :

**[`docs/policies/WeAdU-GitHubOIDC-LightsailReadOnly.json`](./policies/WeAdU-GitHubOIDC-LightsailReadOnly.json)** (`lightsail:Get*` sur `*` — lecture / inventaire Lightsail ; sans `List*` pour éviter erreurs de validation IAM sur certains écrans).

### Attacher cette policy au rôle OIDC (une fois)

1. Console **AWS** → **IAM** → **Policies** → **Create policy** → onglet **JSON** → coller le contenu du fichier **`WeAdU-GitHubOIDC-LightsailReadOnly.json`** → **Next** → nom **`WeAdU-GitHubOIDC-LightsailReadOnly`** → **Create policy**.
2. **IAM** → **Roles** → **`WeAdUGitHubOIDC-SSM`** → **Add permissions** → **Attach policies** → cocher **`WeAdU-GitHubOIDC-LightsailReadOnly`** → **Add permissions**.

*(Si tu es déjà au plafond de politiques managées sur le rôle, détache d’abord une policy non indispensable ou demande une augmentation de quota — voir quotas IAM.)*

---

## Vérifier OIDC côté IAM (poste avec AWS CLI)

Si **`aws`** est installé et configuré pour ce compte :

```bash
bash scripts/aws_github_oidc_probe.sh
```

*(Le script est dans ce dépôt ; il liste les fournisseurs OIDC et l’issuer.)*

---

## Ne pas élargir sans besoin

- **Secret org** `AWS_ROLE_ARN` sur **tous** les repos : seulement si tu **élargis aussi** la **trust policy** du rôle avec d’autres `repo:WeAdU-ltd/…` — sinon les workflows des autres repos **échoueront** (`AssumeRoleWithWebIdentity`). Tant que la trust reste à **`WeAdU-ltd/.github`**, le secret **`AWS_ROLE_ARN`** suffit **sur ce dépôt** uniquement.

---

_Fichier vivant ; pas de secrets dans ce fichier._
