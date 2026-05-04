# Notifications — e-mail prioritaire, Slack calme (WEA-19)

Document d’ancrage pour le ticket [WEA-19](https://linear.app/weadu/issue/WEA-19/notifications-e-mail-prioritaire-5h-23h-uk-slack-calme-20h-7h-urgence). Il complète [WEA-17 — Charte agents](./CHARTE_AGENTS_LINEAR_WEA17.md), le runbook Slack ([WEA-25](./SLACK_APP_AGENTS_WEA25.md)), Gmail agents ([WEA-24](./GMAIL_AGENTS_WEA24.md)), l’hébergement n8n ([WEA-26](./WEA-26-n8n-hebergement.md)) et le ticket n8n e-mails [WEA-31](https://linear.app/weadu/issue/WEA-31/n8n-files-e-mail-humain-etalement-5h-23h-uk-integrations).

---

## 1. Fuseau et référence horaire

Toutes les fenêtres ci-dessous sont en **Europe/London** (UK : heure d’été / hiver gérée par le fuseau, pas par une heure UTC fixe).

| Fenêtre | Plage (heure locale UK) | Usage |
|---------|-------------------------|--------|
| **E-mail humain — envois étalés** | **05:00–23:00** inclus | Canal **principal** pour tout ce qui doit être lu par l’humain ; pas d’envoi **hors** cette plage sauf exception §3. |
| **Slack — calme** | **20:00–07:00** | Pas de messages Slack **non urgents** ; voir §3 pour l’exception **blocage total**. |

Les automatisations (GitHub Actions, bots) qui **ne ciblent pas** un humain directement (ex. logs internes) ne sont pas couvertes par ce tableau ; dès qu’un canal touche Jeff ou une personne, appliquer ce document.

---

## 2. Qui reçoit quoi, quand

### 2.1 E-mail (prioritaire pour l’humain)

| Destinataire / canal | Contenu typique | Quand | Responsable technique |
|----------------------|-----------------|-------|------------------------|
| **Jeff (humain)** | Résumés agents, digest, actions requises, confirmations importantes | **05:00–23:00 UK** ; regrouper / étaler les envois (pas de rafale) | **n8n** pour les flux « humain » ([WEA-31](https://linear.app/weadu/issue/WEA-31/n8n-files-e-mail-humain-etalement-5h-23h-uk-integrations)) ; scripts Gmail ([WEA-24](./GMAIL_AGENTS_WEA24.md)) en secours si pas encore branchés |
| **Boîte technique / agents** | Smoke tests, traces, libellés `Agents/…` | Hors fenêtre humaine **autorisé** si aucun humain n’est en copie et aucune règle métier ne l’interdit | Workflows CI / scripts documentés |

Règles agents complémentaires : signature courte, pas de listes de diffusion pour des essais, une vérification smoke par run quand c’est du test — voir [GMAIL_AGENTS_WEA24.md](./GMAIL_AGENTS_WEA24.md).

### 2.2 Slack

| Canal / mode | Contenu typique | Quand | Notes |
|--------------|-----------------|-------|--------|
| **Canaux agents / automation** | Statut, liens vers PR ou runs, fils sur un message parent | **07:00–20:00 UK** pour le bruit courant | Préférer **canaux dédiés** et **threads** ; pas de `@here` / `@channel` pour du routage générique ([WEA-25](./SLACK_APP_AGENTS_WEA25.md)) |
| **Mention individuelle** (`@personne`) | Action ciblée, question bloquante | Dans la fenêtre **07:00–20:00** si possible | Éviter les mentions de masse |
| **Urgence — exception fenêtre calme** | **Blocage total sans action humaine** (ex. prod / sécurité / credential expiré bloquant toute progression) | **20:00–07:00** : **un seul** message clair (fil ou canal d’urgence convenu), pas de spam | Définir le canal ou le fil d’urgence dans le workspace ; ne pas dupliquer le même événement sur 3 canaux |

**Webhooks** (ex. `SLACK_CI_ALERT_WEBHOOK_URL`, [alertes CI](./GITHUB_CI_FAILURE_ALERT.md)) : même logique — en fenêtre calme, **router** vers un canal qui ne notifie pas massivement ou **bufferiser** via n8n ([WEA-31](https://linear.app/weadu/issue/WEA-31/n8n-files-e-mail-humain-etalement-5h-23h-uk-integrations)) si l’événement n’est pas une urgence §3.

### 2.3 Doublon e-mail + Slack

Éviter d’envoyer le **même** événement non critique sur les deux canaux sans besoin. Ordre par défaut : **e-mail** pour l’humain (dans 05:00–23:00) ; **Slack** pour l’équipe technique / agents dans la journée UK.

---

## 3. Définition courte : « blocage total sans action humaine »

À utiliser **uniquement** pour déroger à la fenêtre Slack calme (20:00–07:00 UK) ou, si vraiment nécessaire, pour un **e-mail** hors 05:00–23:00 UK :

- Aucun agent ni automation **ne peut** débloquer (pas de contournement documenté, pas de secret de repli, pas de merge possible sans humain).
- L’**impact** est majeur (sécurité, perte de données, arrêt complet d’un service critique) **ou** la fenêtre de correction expire avant 07:00 UK.

Sinon : **attendre** 07:00 UK pour Slack, ou mettre en **file** e-mail / n8n ([WEA-31](https://linear.app/weadu/issue/WEA-31/n8n-files-e-mail-humain-etalement-5h-23h-uk-integrations)) jusqu’à 05:00 UK.

---

## 4. Alignement n8n (WEA-26 / WEA-31)

| Sujet | Ticket / doc | Rôle |
|--------|----------------|------|
| Instance, secrets `N8N_*` | [WEA-26](https://linear.app/weadu/issue/WEA-26/n8n-hebergement-20-euromois-cloud-vs-vps-mise-en-service), [`WEA-26-n8n-hebergement.md`](./WEA-26-n8n-hebergement.md) | Hébergement et noms de secrets |
| Files e-mail, étalement 05:00–23:00 UK, routage Slack calme | [WEA-31](https://linear.app/weadu/issue/WEA-31/n8n-files-e-mail-humain-etalement-5h-23h-uk-integrations), [`WEA-31-n8n-human-email-queue.md`](./WEA-31-n8n-human-email-queue.md) | **Implémentation** des règles de ce document (schedules, IF sur heure UK, files d’attente) et workflow importable |

Les workflows n8n doivent appliquer **explicitement** `Europe/London` dans les nœuds de date/heure ou équivalent, et centraliser ici toute **décision** de politique ; les détails de graphes vivent sur WEA-31 et dans l’instance n8n.

---

## 5. Critères de fait (WEA-19) — preuve attendue

| Critère | Preuve |
|---------|--------|
| **Document opérationnel (qui / quoi / quand)** | Ce fichier dans le dépôt `WeAdU-ltd/.github` + lien depuis le README. |
| **Aligné avec n8n (tickets n8n)** | Références croisées [WEA-26](https://linear.app/weadu/issue/WEA-26/n8n-hebergement-20-euromois-cloud-vs-vps-mise-en-service) et [WEA-31](https://linear.app/weadu/issue/WEA-31/n8n-files-e-mail-humain-etalement-5h-23h-uk-integrations) ; implémentation effective suivie sur WEA-31. |

---

_Document vivant : ajuster les noms de canaux Slack et les exemples d’urgence quand le workspace est figé._
