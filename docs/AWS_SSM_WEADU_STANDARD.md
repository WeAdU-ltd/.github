# AWS Systems Manager — norme WeAdU (serveurs)

**But :** tout contrôle répétitif sur une VM AWS **sans RDP/SSH personnel** ni secrets dans le chat — même schéma pour **tous** les projets.

## Norme

| Élément | Règle |
|---------|--------|
| **Vérité « managée ou non »** | Console **Systems Manager → Fleet Manager → Managed nodes** ; statut **Online** = prêt pour automation. |
| **Automation** | **GitHub Actions** + rôle IAM (**OIDC** org `WeAdU-ltd`, pas de clés longues durée dans les repos) avec droits **`ssm:SendCommand`** (et dérivés) **limités** aux instances / tags concernés. Détail OIDC + vérif : [`AWS_GITHUB_OIDC_SSM.md`](./AWS_GITHUB_OIDC_SSM.md). |
| **RDP / SSH** | **Dépannage humain** ou bootstrap — pas la voie par défaut pour checks planifiés. |

## EC2 Linux / Windows (compte déjà avec Default Host Management)

Si la bannière **Default Host Management Configuration** apparaît dans Fleet Manager : **Configure** selon la doc AWS pour enrôler automatiquement les instances EC2 compatibles dans la région.

## Lightsail ou serveur sans profil EC2 « classique »

Les instances **Lightsail** ou hors défaut EC2 suivent souvent la doc **Hybrid Activation** ou la doc **Lightsail + Systems Manager** (installation agent + permissions IAM — détail **variable selon l’OS et l’offre**).

Liens officiels (à suivre dans l’ordre du wizard AWS affiché pour ta situation) :

- [Systems Manager — Managed instances](https://docs.aws.amazon.com/systems-manager/latest/userguide/managed_instances.html)
- [Setting up hybrid activations](https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-managed-instance-activation.html)
- [Using AWS Systems Manager with Lightsail](https://lightsail.aws.amazon.com/ls/docs/en_us/articles/amazon-lightsail-using-systems-manager)

## Première chose à faire (toi, une fois par machine qui manque dans Fleet Manager)

1. Ouvre **Systems Manager** (région où tourne le serveur, ex. **eu-west-2**) → **Fleet Manager** → **Managed nodes**.
2. Si la machine **n’apparaît pas** ou n’est pas **Online** : applique **une** des docs ci-dessus jusqu’à ce qu’elle soit **listée et Online** — puis les agents peuvent enchaîner sur workflows / commandes documentées ailleurs.

## Pour ne pas refaire la même confusion

- **Ne pas** confondre « instance visible dans **Lightsail** » et « instance **managée** par SSM » : tant que Fleet Manager ne la montre pas **Online**, l’agent `.github` **ne peut pas** l’atteindre via SSM.
- Les **mots de passe Administrator** / clés : **1Password** (vault interne éventuellement nommé « Replit ») — **jamais** dans Linear ni dans le chat.

---

_Miroir procédural ; pas de secrets dans ce fichier._ Les agents **WeAdU** doivent, quand ils guident un humain, **reproduire dans le chat ou sur Linear** les étapes utiles de ce document — pas seulement renvoyer vers ce fichier ([`AGENTS.md`](../AGENTS.md) section *Communication*).
