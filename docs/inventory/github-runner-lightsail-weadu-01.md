# GitHub Actions — runner Lightsail `github-runner-weadu-01`

**Mise à jour** : 2026-05-06. Données **non secrètes** (réseau public documentaire). La **clé privée SSH** ne doit **jamais** figurer ici.

| Champ | Valeur |
|--------|--------|
| **Rôle** | Runner GitHub Actions **self-hosted** ([procédure](../GITHUB_SELF_HOSTED_RUNNER.md)) |
| **Fournisseur** | Amazon Lightsail |
| **Région / zone** | `eu-west-2` — Londres, zone **A** (`eu-west-2a`) |
| **Nom instance** | `github-runner-weadu-01` |
| **OS** | Ubuntu 24.04 LTS |
| **Plan** | 2 Go RAM, 2 vCPU, 60 Go SSD (dual-stack) |
| **IPv4 publique** | `13.135.161.59` |
| **IPv4 privée** | `172.26.7.238` |
| **IPv6 publique** | `2a05:d01c:8cd:f200:a6d6:1136:71da:8cef` |
| **Utilisateur SSH** | `ubuntu` |
| **Nom logique clé Lightsail** | `weadu-github-runner-london` (paire générée dans la console ; **fichier `.pem` uniquement chez le référent**) |

## Ce qui reste hors dépôt

- **Fichier `.pem`** : conservé sur le poste du référent (chemin local) **et/ou** copie dans **1Password** en pièce jointe sécurisée ou note — pour récupération si le poste change.
- **Jeton d’enregistrement du runner GitHub** : usage unique dans l’UI ; pas stocké dans ce fichier.

## Connexion SSH (rappel)

```bash
ssh -i chemin/vers/weadu-github-runner-london.pem ubuntu@13.135.161.59
```

Sous **Windows** : après avoir restreint les ACL sur le `.pem` (voir [GITHUB_SELF_HOSTED_RUNNER.md § Windows](../GITHUB_SELF_HOSTED_RUNNER.md) si présent ; sinon `icacls` comme dans le README du même dossier).

---

_Voir aussi : [GITHUB_SELF_HOSTED_RUNNER.md](../GITHUB_SELF_HOSTED_RUNNER.md), smoke [`.github/workflows/self-hosted-runner-smoke.yml`](../../.github/workflows/self-hosted-runner-smoke.yml)._
