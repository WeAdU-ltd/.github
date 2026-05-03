# Slack — app agents et règles anti-notification (WEA-25)

Document d’ancrage pour le ticket [WEA-25](https://linear.app/weadu/issue/WEA-25/slack-app-agents-regles-anti-notification). Il s’aligne sur la cartographie des secrets ([WEA-14](./SECRETS_CARTOGRAPHIE_WEA14.md)), le socle secrets ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)) et les règles de notification [WEA-19](https://linear.app/weadu/issue/WEA-19/notifications-e-mail-prioritaire-5h-23h-uk-slack-calme-20h-7h-urgence).

---

## 1. Objectif

Une **app Slack** (ou bot) permet aux agents et à l’automation de **publier** dans l’espace de travail, avec **mentions individuelles** (`@personne`) lorsque c’est utile, tout en **réduisant le bruit** : canaux dédiés, fils de discussion, pas de `@here` / `@channel` pour du routage générique.

---

## 2. Critère : app installée ; jeton dans les secrets

### 2.1 Création et installation (côté Slack / administrateurs)

1. Créer une **Slack app** sur [api.slack.com/apps](https://api.slack.com/apps) (workspace WeAdU).
2. **OAuth & Permissions** : ajouter les scopes **Bot Token Scopes** nécessaires au minimum pour votre usage, typiquement :
   - `chat:write` — publier des messages ;
   - si vous utilisez des fils / réponses explicites : `chat:write.public` peut être requis pour poster dans des canaux où le bot n’est pas membre (selon politique du workspace) ;
   - ajoutez d’autres scopes uniquement si un workflow documenté en a besoin (fichiers, réactions, etc.).
3. Installer l’app dans le workspace ; récupérer le **Bot User OAuth Token** (`xoxb-…`).
4. Inviter le bot dans les **canaux agents** concernés (ou s’appuyer sur une politique « join channels » si vous l’activez).

### 2.2 Stockage du secret (aligné WEA-15)

| Nom canonique (référence) | Contenu | Où le déposer |
|---------------------------|---------|----------------|
| `SLACK_BOT_TOKEN` | Jeton bot `xoxb-…` | Secret **organisation** ou **dépôt** GitHub autorisé pour les workflows / automation qui appellent Slack ; ou emplacement défini par le socle secrets ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)). Les agents Cursor Cloud / postes locaux suivent la même convention **nommée**, sans commit dans le dépôt. |

- Ne **jamais** committer le jeton ; ne pas le coller dans les tickets Linear ni dans les PR.
- Les workflows qui consomment ce secret doivent le référencer explicitement (`secrets.SLACK_BOT_TOKEN` ou variable d’environnement injectée par la CI), comme pour les autres intégrations (voir [README principal](../README.md) et [cartographie secrets](./SECRETS_CARTOGRAPHIE_WEA14.md)).

**Preuve « token dans secrets » pour marquer le critère fait sur Linear :** capture ou note dans le ticket indiquant que `SLACK_BOT_TOKEN` (ou nom équivalent approuvé par l’équipe) est présent au bon niveau (org / repo / environnement) **sans** exposer la valeur.

---

## 3. Critère : règles documentées (lien WEA-19)

Les règles **produit / humain** (fuseau UK, e-mail prioritaire, fenêtre Slack calme) sont dans [WEA-19 — Notifications](https://linear.app/weadu/issue/WEA-19/notifications-e-mail-prioritaire-5h-23h-uk-slack-calme-20h-7h-urgence). Pour **ce dépôt et les agents**, appliquer en complément :

| Règle | Détail |
|--------|--------|
| **Canaux dédiés** | Utiliser des canaux réservés aux sorties agents / automation, pas le canal général « tout le monde ». |
| **Fils (threads)** | Répondre dans le fil d’un message plutôt que des messages top-level en rafale sur le canal. |
| **Mentions** | `@utilisateur` acceptable pour une action ciblée ; **éviter** `@here`, `@channel`, et toute mention de masse sauf procédure d’urgence validée côté [WEA-19](https://linear.app/weadu/issue/WEA-19/notifications-e-mail-prioritaire-5h-23h-uk-slack-calme-20h-7h-urgence). |
| **Horaires Slack** | Respecter la fenêtre **calme 20h–7h (UK)** pour Slack sauf **blocage total sans action humaine** (voir description WEA-19). L’e-mail reste le canal prioritaire pour l’humain dans les plages définies là-bas. |
| **Intégrations (n8n, CI, etc.)** | Même logique : router les événements non urgents vers canaux/fils dédiés ; ne pas dupliquer massivement e-mail + Slack pour le même événement sans besoin. |

---

## 4. Dépendance WEA-15

Tant que le [socle secrets WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh) n’est pas stabilisé, l’**emplacement exact** du jeton (quel coffre, quel préfixe d’environnement) peut suivre la décision d’équipe ; le nom **`SLACK_BOT_TOKEN`** reste la référence dans ce dépôt pour les scripts et docs.

---

_Document statique ; mise à jour si les scopes Slack, les canaux ou le socle secrets évoluent._
