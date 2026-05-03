# n8n — hébergement < 20 €/mois (WEA-26)

Document d’ancrage pour [WEA-26](https://linear.app/weadu/issue/WEA-26/n8n-hebergement-20-euromois-cloud-vs-vps-mise-en-service). Dépend du socle secrets [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh) ; voir aussi la cartographie [WEA-14](https://linear.app/weadu/issue/WEA-14/secrets-cartographie-1password-github-cursor-regle-chercher-avant-de) ([`SECRETS_CARTOGRAPHIE_WEA14.md`](./SECRETS_CARTOGRAPHIE_WEA14.md)).

---

## Synthèse : décision recommandée

| Critère | **n8n Cloud (Starter)** | **Self-hosted (OVH / Lightsail / VPS)** |
|--------|---------------------------|----------------------------------------|
| **Coût récurrent** | **20 €/mois** si facturation **annuelle** ([tarifs officiels](https://n8n.io/pricing/) — vérifier au moment de la souscription). Hors promo : souvent **24 €/mois** en mensuel. | **~4–15 €/mois** VPS seul (ex. petite instance EU) + **0 €** licence **Community Edition** ([GitHub](https://github.com/n8n-io/n8n)). Option **Business** self-hosted = autre gamme de prix (licence + exécutions). |
| **Budget < 20 €/mois** | Atteint **uniquement** avec engagement annuel Starter (~20 €/mois équivalent). | Facile à tenir avec un VPS modeste. |
| **Charge ops** | **Faible** : mises à jour, disponibilité, sauvegardes gérées par n8n ; données hébergées **UE (Francfort)** selon la page pricing. | **Moyenne à élevée** : OS, Docker/Compose ou équivalent, TLS, sauvegardes DB, mises à jour n8n, monitoring, durcissement réseau. |
| **Limite usage Cloud Starter** | **2 500 exécutions / mois**, 5 exécutions concurrentes, 1 projet partagé (voir [pricing](https://n8n.io/pricing/)). | CE self-hosted : pas de plafond imposé par n8n sur les exécutions ; limites = CPU/RAM/disque du VPS. |

**Recommandation pour minimiser l’ops tout en restant sous 20 €/mois :**

1. **Si** le volume reste modeste et **2 500 exécutions/mois** suffisent : **n8n Cloud Starter en annuel (~20 €/mois)** — meilleur rapport charge ops / coût.
2. **Si** le volume dépasse le Starter ou les données doivent rester sur **un VPS déjà maîtrisé** : **self-hosted Community Edition** sur un petit VPS OVH / Lightsail / équivalent, avec Docker Compose + sauvegardes PostgreSQL documentées.

Les deux options respectent un budget **inférieur à 20 €/mois** si le Cloud est pris en annuel ou si le VPS reste dans la fourchette ci-dessus (vérifier les tarifs fournisseur au moment du choix).

---

## Comparatif détaillé (prix & ops)

### n8n Cloud

- **Prix** : consulter [n8n.io/pricing](https://n8n.io/pricing/) — les montants exacts et la distinction mensuel / annuel évoluent ; la ligne **Starter** « ~20 €/mo en annuel » est la référence pour tenir le budget.
- **Ops** : quasi nul côté infrastructure ; gestion des **credentials** et des workflows dans l’UI Cloud.
- **Secrets** : stockés dans le coffre chiffré de l’instance Cloud ; **ne pas** committer de secrets dans Git. Répliquer les **noms** attendus côté org (voir ci-dessous) dans GitHub/Cursor **sans** valeurs.

### Self-hosted (VPS)

- **Prix** : VPS + éventuellement volume disque / snapshot ; pas de frais de licence pour **Community Edition**.
- **Ops** : installation recommandée via **Docker Compose** ([documentation self-hosted](https://docs.n8n.io/hosting/)), reverse proxy TLS (Caddy, Traefik, nginx), pare-feu, **sauvegardes** de la base (PostgreSQL si utilisée), veille mises à jour de sécurité.
- **Fournisseurs cités dans le ticket** : **OVH** (VPS EU), **AWS Lightsail**, ou tout **petit VPS** équivalent — comparer prix catalogue et transfert au moment du provisioning.

---

## Mise en service — checklist (à cocher une fois fait)

### Option A — n8n Cloud

1. Créer un compte / instance sur [n8n Cloud](https://app.n8n.cloud/register) et choisir le plan Starter (annuel si objectif < 20 €/mo).
2. Noter l’**URL d’accès** (domaine `*.app.n8n.cloud` ou personnalisé si configuré).
3. Enregistrer les secrets selon la [convention secrets (n8n)](#convention-secrets-n8n).

### Option B — Self-hosted sur VPS

1. Provisionner un VPS (budget < 20 €/mois tout compris si possible).
2. Déployer n8n (ex. Compose officiel), TLS, et une base dédiée si besoin.
3. Définir l’**URL publique** (HTTPS) et le **basic auth** ou SSO selon politique interne.
4. Sauvegardes + mise à jour documentées (runbook court suffit dans le wiki ou ce fichier).
5. Enregistrer les secrets selon la convention ci-dessous.

---

## Convention secrets (n8n)

**Ne jamais** mettre les valeurs dans ce dépôt. Stocker les valeurs dans le **socle secrets** ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)) : secrets **organisation** ou **dépôt** GitHub, ou secrets **Cursor** pour les agents, selon ce qui est déjà en place pour WeAdU.

| Nom suggéré (variable / secret) | Usage |
|---------------------------------|--------|
| `N8N_BASE_URL` | URL HTTPS de l’instance (Cloud ou self-hosted), sans slash final superflu. |
| `N8N_API_KEY` | Clé API n8n pour les appels automatisés ([doc API](https://docs.n8n.io/api/)), si utilisée. |
| `N8N_BASIC_AUTH_USER` / `N8N_BASIC_AUTH_PASSWORD` | Si auth basique devant l’UI (surtout self-hosted) ; optionnel si SSO ou autre. |

Après provisioning humain : renseigner ces entrées dans GitHub/Cursor et **une** ligne de statut dans ce fichier ou sur le ticket Linear (faits / écart).

---

## Écart vs critères de fait (état au dernier commit de cette doc)

Les critères Linear pour **Done** sont :

1. **Décision documentée + instance créée ou abo souscrit** — la **décision** et le comparatif sont documentés ici ; **l’instance ou l’abonnement** doit être créé par un humain avec droits de paiement / cloud.
2. **URL d’accès + secrets dans GitHub/Cursor** — **après** mise en service : renseigner les secrets nommés ci-dessus dans les magasins approuvés ; ne pas dupliquer les valeurs dans Git.

Tant que (1) et (2) ne sont pas réalisés opérationnellement, le ticket doit rester ouvert ou porter un commentaire **Écart** sur Linear conformément à la [règle avant Done](https://linear.app/weadu/document/regle-agents-criteres-de-fait-avant-done-tous-projets-2b32aec9e234).

---

_Document vivant : mettre à jour l’URL finale et cocher la checklist lorsque l’instance existe._
