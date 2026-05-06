# GitHub Actions — runner self-hosted (automation cloud)

But : exécuter des workflows **sans** passer par ton poste Windows — jobs qui peuvent plus tard parler au réseau interne (VPC, EC2) avec des droits **IAM** ou **réseau** contrôlés, au lieu d’un SSH personnel vers la prod.

**Secrets** : le jeton d’**enregistrement** du runner est à usage unique (interface GitHub). Les credentials du runner vivent **sur la VM** après install — pas dans ce dépôt. Voir [WEA-15](./SECRETS_SOCLE_WEA15.md) pour les secrets **org** utilisés par les workflows classiques.

---

## Principes de sécurité

1. **VM dédiée** uniquement au runner (pas la même instance que COS / prod métier).
2. **Surface réduite** : idéalement **pas de SSH exposé sur Internet** ; préférer **AWS Systems Manager Session Manager** (SSM) pour l’admin shell si l’instance est dans AWS.
3. **Étiquettes** (`labels`) explicites : ex. `weadu-automation`, `linux`, `self-hosted` — les workflows ciblent ces labels, pas `ubuntu-latest`.
4. **Accès repos** : dans GitHub → *Organization settings* → *Actions* → *Runner groups* (si disponible) ou politique **quel repos peuvent utiliser les runners org** — éviter « toute l’Internet peut dispatcher des jobs » par erreur.

---

## Étape 1 — Provisionner une VM Linux

Cible recommandée pour commencer :

| Paramètre | Valeur indicative |
|-----------|-------------------|
| OS | **Ubuntu Server 22.04 ou 24.04 LTS** |
| Taille | **t3.small** ou équivalent (2 vCPU, 2 Go RAM mini ; 4 Go confortable) |
| Disque | **30 Go** gp3 suffisant pour démarrer |
| Région | Alignée sur ton infra existante (ex. **eu-west-2** si déjà utilisée) |
| Réseau | Subnet avec **sortie** Internet (pour joindre `github.com`) ; ingress **non** ouvert au monde si tu utilises SSM |

Ne pas installer le runner sur ton PC : la VM est le produit de cette étape.

---

## Étape 2 — Accès administrateur à la VM

Sans ouvrir le SSH public :

1. Rôle IAM instance avec **`AmazonSSMManagedInstanceCore`** (si AWS).
2. Connexion : **AWS Console** → **Systems Manager** → **Session Manager** → session sur l’instance.

Si tu dois utiliser SSH temporairement pour bootstrap : ouvre le port **22** seulement depuis **ton IP**, installe le runner, puis **retire** la règle SG ou passe à SSM uniquement.

---

## Étape 3 — Créer le runner côté GitHub (jeton)

1. Organisation **WeAdU-ltd** → **Settings** → **Actions** → **Runners**.
2. **New runner** → **New self-hosted runner**.
3. OS : **Linux**, Architecture : **x64**.
4. Copier les commandes affichées (téléchargement `actions-runner`, `./config.sh`, `./run.sh`) — **ne pas** commiter le jeton ; il expire vite.

Enregistrer le runner avec un **nom** explicite : ex. `weadu-automation-eu-west-2-01`.

**Labels** à ajouter lors du `config.sh` : `weadu-automation,self-hosted,linux` (éviter le label réservé `self-hosted` seul si la doc GitHub le permet ; suivre l’invite interactive).

---

## Étape 4 — Service systemd (toujours actif)

Suivre la doc officielle en fin d’installation : `./svc.sh install` puis `./svc.sh start` pour que le runner survive aux reboots.

Vérifier : *Runners* dans les paramètres org affiche le runner **Idle** (vert).

---

## Étape 5 — Workflow de test (dans ce dépôt après merge)

Ajouter un workflow minimal déclenché **manuellement** :

```yaml
on:
  workflow_dispatch:

jobs:
  hello:
    runs-on: [self-hosted, weadu-automation]
    steps:
      - run: echo ok && uname -a
```

Ne pas migrer la **CI principale** (`ci.yml`) tant que ce smoke n’a pas réussi.

---

## Étape 6 — Suite (autonomie agent)

- Workflows **inventory / déploiement / SSH vers environnements internes** : les faire tourner sur `runs-on: [self-hosted, weadu-automation]` avec secrets **org** limités au besoin.
- **Ne pas** stocker de clé SSH prod dans les secrets GitHub si tu peux utiliser **OIDC AWS** ou **SSM Run Command** depuis la VM runner vers les instances cibles.

---

## Références

- [GitHub — Adding self-hosted runners](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/adding-self-hosted-runners)
- Principe « zéro humain » : [ZERO_HUMAN_AUTOMATION_LINEAR.md](./ZERO_HUMAN_AUTOMATION_LINEAR.md)
- Socle secrets : [SECRETS_SOCLE_WEA15.md](./SECRETS_SOCLE_WEA15.md)

---

_Document vivant ; création : agent dépôt WeAdU-ltd/.github._
