# WEA-20 — Google OAuth : clients, scopes, redirect URIs, écran de consentement

Runbook pour le ticket [WEA-20](https://linear.app/weadu/issue/WEA-20/google-passe-oauth-gmail-drive-docs-sheets-ads-analytics). Il **documente** ce que l’équipe doit créer ou mettre à jour dans **Google Cloud Console** ; les **Client ID / Client Secret** ne doivent pas figurer dans ce dépôt (stockage selon [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh) : coffre, secrets GitHub, etc.).

**Dépendances Linear** : WEA-20 est **bloqué par** WEA-15 (socle secrets). Les tickets [WEA-21](https://linear.app/weadu/issue/WEA-21/google-ads-analytics-api-agents-autonomie-note-risque) (Ads / Analytics) et [WEA-24](https://linear.app/weadu/issue/WEA-24/gmail-acces-agents-lecture-envoi) (Gmail) sont **bloqués par** WEA-20 ; l’inventaire projets GCP / doublons est couvert par [WEA-27](https://linear.app/weadu/issue/WEA-27/google-cloud-inventaire-projets-uris-oauth-doublons).

---

## 1. Création ou mise à jour des clients OAuth (GCP)

1. **Google Cloud Console** → projet cible (voir alignement WEA-27) → **APIs & Services** → **Credentials** → **Create credentials** → **OAuth client ID**.
2. Si demandé, configurer d’abord l’**OAuth consent screen** (section 3).
3. Choisir le **type d’application** adapté au consommateur du jeton :
   - **Application Web** : backends, n8n, outils hébergés avec callback HTTPS fixe.
   - **Desktop** (ou flux « installed app » / loopback) : CLIs et agents locaux qui ouvrent le navigateur puis reçoivent le code sur `http://127.0.0.1` ou `http://localhost` (voir [OAuth 2.0 pour les applications de bureau](https://developers.google.com/identity/protocols/oauth2/native-app)).
4. Activer les **APIs** correspondantes dans le même projet (Gmail API, Google Drive API, Google Docs API, Google Sheets API, Google Ads API, Google Analytics API / Admin API selon le besoin).

Après création : noter le **Client ID** et enregistrer le **Client Secret** dans le canal secrets validé par WEA-15 ; ne pas committer ces valeurs.

---

## 2. Liste de scopes (référence « large » pour agents)

À **ajouter uniquement** ce qui est réellement utilisé ; les scopes sensibles ou restreints prolongent la revue Google. Les chaînes ci-dessous sont les **scope URLs** standard OAuth 2.0.

### Gmail

| Scope | Usage typique |
|-------|----------------|
| `https://www.googleapis.com/auth/gmail.readonly` | Lecture seule |
| `https://www.googleapis.com/auth/gmail.modify` | Libellés, brouillons, corbeille (pas envoi seul) |
| `https://www.googleapis.com/auth/gmail.compose` | Créer / modifier brouillons |
| `https://www.googleapis.com/auth/gmail.send` | Envoyer des messages (souvent combiné avec compose) |
| `https://mail.google.com/` | Accès complet au compte Gmail (très sensible ; éviter si un ensemble plus fin suffit) |

### Google Drive

| Scope | Usage typique |
|-------|----------------|
| `https://www.googleapis.com/auth/drive.readonly` | Lecture de tous les fichiers |
| `https://www.googleapis.com/auth/drive.file` | Fichiers créés ou ouverts par l’app uniquement |
| `https://www.googleapis.com/auth/drive` | Accès complet Drive (sensible) |

### Google Docs & Sheets

| Scope | Usage typique |
|-------|----------------|
| `https://www.googleapis.com/auth/documents` | Docs créés par l’app ou auxquels l’utilisateur a accédé (selon modèle d’accès) |
| `https://www.googleapis.com/auth/documents.readonly` | Lecture seule |
| `https://www.googleapis.com/auth/spreadsheets` | Sheets lecture/écriture |
| `https://www.googleapis.com/auth/spreadsheets.readonly` | Lecture seule |

### Google Ads

| Scope | Usage typique |
|-------|----------------|
| `https://www.googleapis.com/auth/adwords` | API Google Ads (comptes liés au Google Ads utilisateur / MCC selon configuration) |

### Google Analytics (Universal / GA4 selon API utilisée)

| Scope | Usage typique |
|-------|----------------|
| `https://www.googleapis.com/auth/analytics.readonly` | Données Analytics en lecture |
| `https://www.googleapis.com/auth/analytics` | Lecture + configuration (selon API) |
| `https://www.googleapis.com/auth/analytics.edit` | Modification des ressources de propriété (sensible) |

### Optionnel (souvent utile avec les suites ci-dessus)

| Scope | Usage typique |
|-------|----------------|
| `https://www.googleapis.com/auth/userinfo.email` | Email de l’utilisateur connecté (profil) |
| `https://www.googleapis.com/auth/userinfo.profile` | Nom / photo de profil |
| `openid` | OpenID Connect (souvent avec `email`, `profile`) |

Pour les **combinaisons exactes** par produit (Ads vs Analytics Admin, etc.), croiser avec WEA-21 et la doc officielle de chaque API au moment de l’implémentation.

---

## 3. Écran de consentement et utilisateurs test

1. **APIs & Services** → **OAuth consent screen**.
2. Choisir **Interne** (Workspace uniquement) si tout le monde est sur le même domaine Google Workspace ; sinon **Externe**.
3. En mode **Testing** (app non publiée) : ajouter chaque compte Google qui doit autoriser l’app dans **Test users** (max 100 en test).
4. Les scopes **sensibles** ou **restreints** peuvent exiger une **vérification** Google avant diffusion large ; prévoir délais et justificatifs minimisation des données.
5. Documenter le **Support email** et les **domaines autorisés** si l’app utilise des liens ou hébergements de marque.

---

## 4. Redirect URIs et origines JavaScript (modèles à compléter)

Renseigner dans le client OAuth **Web** :

- **Authorized JavaScript origins** : origines **HTTPS** (sans chemin) du front qui initie le flux implicitement ou charge la bibliothèque Google Identity ; ex. `https://app.votredomaine.tld`, `https://votre-org.github.io` (Pages), origine du **Cloud Agent / IDE** si un flux navigateur y est ancré (à figer avec l’équipe infra).
- **Authorized redirect URIs** : URLs **exactes** (schéma, hôte, port, chemin) qui reçoivent le `code` OAuth 2.0 ; une variante d’URL = une ligne supplémentaire.

Modèles fréquents (remplacer les placeholders par les URLs réelles de l’organisation) :

| Contexte | Exemple d’origine JS | Exemple de redirect URI |
|----------|----------------------|---------------------------|
| Développement local (web) | `http://localhost:3000` | `http://localhost:3000/api/auth/callback/google` |
| Agent / CLI (loopback) | *(souvent vide pour pure server-side)* | `http://127.0.0.1:8085/` ou port documenté par l’outil |
| Backend SaaS (n8n, etc.) | Domaine public du service | Callback documenté par le fournisseur (ex. `/rest/oauth2-credential/callback`) |
| GitHub Actions / sans navigateur | — | Préférer **compte de service** ou **Workload Identity** plutôt qu’un client « desktop » dans la CI |

**Règles Google** : pas d’URI en HTTP sauf `localhost` ; pas d’espaces ni de wildcard dans les redirect URIs ; aligner **exactement** ce que l’application envoie dans la requête `redirect_uri`.

Après stabilisation des URLs : dupliquer la liste dans l’inventaire [WEA-27](https://linear.app/weadu/issue/WEA-27/google-cloud-inventaire-projets-uris-oauth-doublons) pour éviter les doublons entre projets GCP.

---

## 5. Critères de fait (WEA-20) — comment les cocher

| Critère | Preuve attendue |
|---------|------------------|
| Client(s) OAuth créés ou mis à jour ; liste des scopes | Capture ou export console GCP + liste des scopes **effectivement** demandés par l’app (ce document sert de grille) ; identifiants dans le canal WEA-15. |
| Écran de consentement / test users si nécessaire | Type d’app (interne / externe) documenté ; liste des test users à jour si l’app est en testing ; vérification Google lancée ou N/A. |

---

_Document vivant : à ajuster quand les URLs d’hébergement des agents (Cursor Cloud, n8n, apps internes) sont figées._
