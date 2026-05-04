# n8n — files e-mail humain (UK 05:00–23:00) et intégrations (WEA-31)

Document d’ancrage pour [WEA-31](https://linear.app/weadu/issue/WEA-31/n8n-files-e-mail-humain-etalement-5h-23h-uk-integrations). La politique fuseau et canaux est dans [`NOTIFICATIONS_EMAIL_SLACK_WEA19.md`](./NOTIFICATIONS_EMAIL_SLACK_WEA19.md) ([WEA-19](https://linear.app/weadu/issue/WEA-19/notifications-e-mail-prioritaire-5h-23h-uk-slack-calme-20h-7h-urgence)) ; l’instance n8n et les secrets d’accès à l’UI / API dans [`WEA-26-n8n-hebergement.md`](./WEA-26-n8n-hebergement.md) ([WEA-26](https://linear.app/weadu/issue/WEA-26/n8n-hebergement-20-euromois-cloud-vs-vps-mise-en-service)).

---

## 1. Workflow livré dans ce dépôt (digest / alerte)

| Élément | Rôle |
|---------|------|
| [`n8n/workflows/WEA-31-human-digest-uk-window.json`](../n8n/workflows/WEA-31-human-digest-uk-window.json) | Export JSON **importable** dans n8n (« Import from File »). Graphe minimal **fonctionnel** : déclencheur planifié, construction d’un sujet + corps, **If** sur l’heure UK (champs `Hour` issus du *Schedule Trigger* en `Europe/London`), envoi *Send Email* (SMTP) si 05:00–23:00 UK, sinon *No Operation*. |

**Après import** : attacher un credential **SMTP** au nœud *Send digest email*, remplacer les adresses d’exemple (`noreply@example.com`, `you@example.com`) ou les expressions `$env.N8N_DIGEST_FROM_EMAIL` / `$env.N8N_HUMAN_EMAIL_TO` si tu exposes ces variables sur l’instance self-hosted, publier le workflow et l’activer.

Le nœud *Build digest text* est un **canevas** : le remplacer ou le faire précéder par des nœuds **Linear**, **Slack**, **HTTP Request**, **Gmail**, etc., tout en gardant le **filtre horaire UK** et l’e-mail aval pour rester aligné avec [WEA-19](https://linear.app/weadu/issue/WEA-19/notifications-e-mail-prioritaire-5h-23h-uk-slack-calme-20h-7h-urgence).

**Étalement** : le fichier utilise un déclenchement **toutes les 2 heures** comme exemple (réduit les rafales). Pour un digest quotidien à une heure fixe, remplacer la règle du *Schedule Trigger* (ex. *Days* à une heure donnée) tout en conservant le filtre 05:00–23:00 si des déclencheurs externes (webhooks) peuvent arriver hors plage.

**File persistante** : ce graphe **ne stocke pas** les messages ; hors fenêtre il **n’envoie pas**. Pour une vraie file (retry différé, persistance), ajouter base de données, sous-workflow avec *Wait*, ou source événementielle qui ne délivre l’e-mail qu’à l’intérieur de la fenêtre.

---

## 2. Secrets et credentials — **noms uniquement** (valeurs hors Git)

### Accès instance et API n8n

Aligné sur [WEA-26](https://linear.app/weadu/issue/WEA-26/n8n-hebergement-20-euromois-cloud-vs-vps-mise-en-service) : `N8N_BASE_URL`, `N8N_API_KEY`, et si besoin `N8N_BASIC_AUTH_USER` / `N8N_BASIC_AUTH_PASSWORD`.

### Envoi e-mail (SMTP dans n8n)

Les paramètres réels vivent dans le **credential SMTP** de l’instance n8n (UI), pas dans ce dépôt. Côté convention de variables pour **documentation / infra** (self-hosted ou injection d’env) :

| Nom (documentation) | Usage |
|---------------------|--------|
| `N8N_SMTP_HOST` | Hôte du relais SMTP |
| `N8N_SMTP_PORT` | Port (souvent 465 TLS ou 587 STARTTLS) |
| `N8N_SMTP_USER` | Utilisateur SMTP si requis |
| `N8N_SMTP_PASS` | Mot de passe ou secret du relais |
| `N8N_SMTP_SENDER` | Adresse d’expéditeur par défaut (peut compléter le nœud *Send Email*) |
| `N8N_DIGEST_FROM_EMAIL` | Expéditeur du digest humain (optionnel ; utilisé dans le workflow exemple si défini en env) |
| `N8N_HUMAN_EMAIL_TO` | Destinataire humain principal (optionnel ; idem) |

*(Les noms exacts des champs du credential SMTP dans l’UI n8n suivent la doc officielle « SMTP » ; l’important est de ne **jamais** committer les valeurs.)*

### API mail non-SMTP (alternative)

Si tu envoies via **Gmail OAuth** dans n8n plutôt que SMTP, réutiliser les noms du runbook [`GMAIL_AGENTS_WEA24.md`](./GMAIL_AGENTS_WEA24.md) : `GMAIL_OAUTH_CLIENT_ID`, `GMAIL_OAUTH_CLIENT_SECRET`, `GMAIL_OAUTH_REFRESH_TOKEN` (côté Google Cloud + credential Gmail dans n8n).

### Ponts optionnels (rappel)

| Intégration | Nom courant documenté ailleurs |
|-------------|-------------------------------|
| Linear API | `LINEAR_API_KEY` (scripts / agents — [`SECRETS_CARTOGRAPHIE_WEA14.md`](./SECRETS_CARTOGRAPHIE_WEA14.md)) |
| Slack | `SLACK_BOT_TOKEN` ; webhooks type `SLACK_CI_ALERT_WEBHOOK_URL` — [`SLACK_APP_AGENTS_WEA25.md`](./SLACK_APP_AGENTS_WEA25.md) |

---

## 3. Critères de fait (WEA-31) — preuve dans ce dépôt

| Critère | Preuve |
|---------|--------|
| Au moins un workflow « digest / alerte » fonctionnel | Fichier importable [`n8n/workflows/WEA-31-human-digest-uk-window.json`](../n8n/workflows/WEA-31-human-digest-uk-window.json) + instructions §1 ci-dessus. |
| Secrets n8n + SMTP ou API mail documentés (noms seulement) | Tableaux §2 ; pas de valeurs dans Git. |

_L’import et la connexion SMTP sur l’instance réelle restent une action opérationnelle sur l’instance ([WEA-26](https://linear.app/weadu/issue/WEA-26/n8n-hebergement-20-euromois-cloud-vs-vps-mise-en-service))._

---

_Document vivant : ajuster les noms d’env si le socle secrets [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh) fige une variante canonique._
