# Gmail — accès agents (lecture + envoi) (WEA-24)

Document d’ancrage pour le ticket [WEA-24](https://linear.app/weadu/issue/WEA-24/gmail-acces-agents-lecture-envoi). Il s’aligne sur le runbook OAuth Google ([WEA-20](./GOOGLE_OAUTH_WEA20.md)), le socle secrets ([WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)), la cartographie ([WEA-14](./SECRETS_CARTOGRAPHIE_WEA14.md)) et les notifications humaines ([WEA-19](https://linear.app/weadu/issue/WEA-19/notifications-e-mail-prioritaire-5h-23h-uk-slack-calme-20h-7h-urgence)).

**Dépendance** : [WEA-20](https://linear.app/weadu/issue/WEA-20/google-passe-oauth-gmail-drive-docs-sheets-ads-analytics) doit fournir un client OAuth (type bureau ou web selon le flux), l’écran de consentement et les scopes demandés ; ce document décrit **l’usage agents** une fois le jeton obtenu.

---

## 1. Objectif

Permettre aux agents de **lire** la boîte (threads / libellés utiles) et d’**envoyer** des messages **contrôlés**, avec des règles explicites pour limiter le spam et respecter la charte e-mail.

---

## 2. Scopes OAuth (minimum recommandé)

Croiser avec la table Gmail dans [GOOGLE_OAUTH_WEA20.md](./GOOGLE_OAUTH_WEA20.md). Pour lecture + envoi sans gestion complète des libellés :

| Scope | Rôle |
|-------|------|
| `https://www.googleapis.com/auth/gmail.readonly` | Lecture (messages, threads, pièces selon politique) |
| `https://www.googleapis.com/auth/gmail.send` | Envoi uniquement |

Si les workflows agents doivent **appliquer des libellés** ou gérer des brouillons, ajouter au besoin `gmail.compose` et/ou `gmail.modify` (toujours le **minimum** nécessaire pour limiter la surface de consentement Google).

---

## 3. Secrets — noms canoniques (valeurs hors dépôt et hors Linear)

Les **refresh tokens** et **client secrets** ne sont jamais commités. Les stocker dans GitHub Encrypted Secrets (org ou dépôt), secrets Cursor workspace / cloud, ou coffre d’équipe selon [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh).

| Variable (référence) | Contenu | Où le déposer |
|----------------------|---------|----------------|
| `GMAIL_OAUTH_CLIENT_ID` | Client ID OAuth (Google Cloud Console) | Même canal que les autres secrets Google agents |
| `GMAIL_OAUTH_CLIENT_SECRET` | Client secret OAuth | Idem |
| `GMAIL_OAUTH_REFRESH_TOKEN` | Refresh token du compte / identité utilisée pour l’agent | Idem |

**Alternative** : un fichier JSON **compte de service** ou autre flux documenté dans WEA-20 si l’organisation choisit ce modèle pour une boîte technique ; dans ce cas documenter les noms d’environnement **dans le dépôt consommateur** et rester cohérent avec la grille WEA-20.

---

## 4. Conventions agents (signatures, libellés, ne pas spammer)

| Règle | Détail |
|--------|--------|
| **Signature** | Tout message sortant identifiable comme agent doit inclure une **signature courte** (ex. nom du rôle, lien doc interne, « message automatisé »). Ne pas imiter une signature humaine personnelle. |
| **Libellés** | Utiliser des libellés dédiés (ex. `Agents/…`) pour tracer le traitement ; ne pas retirer des libellés humains sans procédure. |
| **Volume** | Pas d’envoi en rafale ; regrouper les notifications ; **une** vérification smoke par exécution de script suffit pour le critère « envoi contrôlé ». |
| **Destinataires** | En test : **n’envoyer qu’à soi** (adresse du profil `users/me/profile`) sauf procédure explicite ; ne pas utiliser de listes de diffusion pour des essais. |
| **Horaires** | Respecter [WEA-19](https://linear.app/weadu/issue/WEA-19/notifications-e-mail-prioritaire-5h-23h-uk-slack-calme-20h-7h-urgence) pour tout ce qui touche l’humain (fenêtre prioritaire e-mail UK, etc.). |

---

## 5. Critères de fait (WEA-24) — comment les cocher

| Critère | Preuve attendue |
|---------|------------------|
| **Accès testé (lecture + envoi contrôlé)** | Exécution réussie de [`scripts/gmail_oauth_smoke_wea24.py`](../scripts/gmail_oauth_smoke_wea24.py) : par défaut **lecture** (`users/me/profile`) ; avec `--send`, **un** message de test vers l’adresse du compte uniquement (auto-envoi). Capture ou note sur le ticket **sans** exposer les secrets. |
| **Secrets au bon endroit** | Les trois variables (ou équivalent validé équipe) sont dans GitHub/Cursor/coffre, **pas** dans la description Linear ni dans les commentaires. |

---

## 6. Vérification locale ou CI

### 6.1 Dry-run (CI sans secrets)

Le script accepte `--dry-run` : aucun réseau ; utilisé dans [`ci.yml`](../.github/workflows/ci.yml).

### 6.2 Lecture seule (refresh token injecté)

```bash
export GMAIL_OAUTH_CLIENT_ID="***"
export GMAIL_OAUTH_CLIENT_SECRET="***"
export GMAIL_OAUTH_REFRESH_TOKEN="***"
python3 scripts/gmail_oauth_smoke_wea24.py
```

### 6.3 Envoi contrôlé (auto vers `me`)

Même exports qu’en §6.2, puis :

```bash
python3 scripts/gmail_oauth_smoke_wea24.py --send
```

Variables optionnelles :

| Variable | Rôle |
|----------|------|
| `GMAIL_OAUTH_SMOKE_SUBJECT` | Sujet du message de test (défaut : texte neutre « WEA-24 … ») |
| `GMAIL_OAUTH_SMOKE_BODY` | Corps texte brut du message de test |

Pour **désactiver** explicitement l’envoi même si un script tiers passe `--send`, définir `GMAIL_OAUTH_SMOKE_SEND=0`.

---

_Document vivant ; à ajuster si le flux OAuth (desktop vs n8n vs autre) est figé au niveau organisation._
