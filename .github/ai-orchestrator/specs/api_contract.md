# Contrat d’API universel — orchestrateur IA

**Ticket :** [WEA-170](https://linear.app/weadu/issue/WEA-170/definir-le-contrat-dapi-universel-de-lorchestrateur-ia)  
**Emplacement canonique :** tout le code et la doc de l’orchestrateur vivent sous **`WeAdU-ltd/.github`** dans le dossier **`.github/ai-orchestrator/`** (dans un checkout du dépôt `.github`, le chemin local équivalent est `ai-orchestrator/`). Ce document est la source de vérité pour le format d’échange entre les appelants (API interne, MCP, scripts) et l’orchestrateur.

**Objectif :** une interface unique pour toutes les requêtes IA, quel que soit le fournisseur derrière : **LM Studio** (local), **Gemini Flash**, **Claude Haiku**.

## Résumé (contrat en une lecture)

| Racine — obligatoire | Racine — optionnel |
|----------------------|-------------------|
| `task_id`, `task_type`, `complexity`, `privacy_level`, `preferred_model`, `input` | `max_cost_usd`, `options` |

| Sous `input` — obligatoire | Sous `input` — optionnel (défauts) |
|----------------------------|-----------------------------------|
| `prompt` (chaîne non vide) | `context` (`{}`), `data` (`[]`) |

**Réponse** — `task_id`, `status`, `provider_used`, `model_used`, `output`, `usage` (§4.3), `routing_reason`, `error` ; le bloc `usage` inclut au minimum tokens, coût estimé USD, durée ms, et peut inclure les champs optionnels d’**économie** (`estimated_cloud_equivalent_cost_usd`, `estimated_savings_usd`).

---

## 1. Principes

1. **Indépendance vis-à-vis du provider** — les appelants ne choisissent pas les endpoints propres à chaque fournisseur ; ils envoient un `RunRequest` et reçoivent un `RunResponse` normalisé.
2. **Confidentialité prioritaire** — `privacy_level` et `preferred_model` sont des contraintes dures pour le routeur (voir règles ci-dessous).
3. **Traçabilité** — chaque réponse expose `provider_used`, `model_used`, `routing_reason` et un bloc `usage` exploitable pour coût, performance et **estimation d’économie** (sans stocker le prompt complet par défaut ; les logs détaillés sont hors scope de ce fichier).
4. **Évolution** — champs optionnels et clés d’extension dans `input.context` / `output` : les appelants doivent ignorer les champs inconnus (tolérance lecture).

Représentation logique : **JSON** (UTF-8). Les exemples utilisent des objets JSON ; les types indiqués décrivent la sémantique attendue après parsing.

---

## 2. Énumérations

### 2.1 `task_type`

| Valeur           | Usage indicatif                                      |
|------------------|------------------------------------------------------|
| `classification` | Étiquetage, scoring binaire ou multi-classe          |
| `generation`     | Texte, plan, brouillon structuré                   |
| `extraction`     | Données structurées depuis texte / documents         |
| `coding`         | Génération ou transformation de code                 |
| `analysis`       | Raisonnement, synthèse, revue                        |

### 2.2 `complexity`

| Valeur   | Rôle |
|----------|------|
| `low`    | Tâches simples, peu de raisonnement multi-étapes   |
| `medium` | Tâches standards, équilibre coût / qualité         |
| `high`   | Tâches exigeantes, raisonnement poussé             |

*Le routeur peut utiliser `complexity` comme signal par défaut ; `preferred_model` et `privacy_level` restent prioritaires.*

### 2.3 `privacy_level`

| Valeur              | Signification |
|---------------------|---------------|
| `local_only`        | Aucun envoi vers un fournisseur cloud : exécution **LM Studio** uniquement (ou erreur si indisponible). |
| `standard`          | Données traitables sur fournisseurs cloud selon politique WeAdU. |
| `external_allowed`  | Même famille que `standard` pour ce contrat ; réservé aux extensions (politiques fines, régions, DPA). Les implémentations v1 peuvent traiter `standard` et `external_allowed` de façon identique tant que la politique produit n’est pas différenciée. |

### 2.4 `preferred_model`

Le champ **`preferred_model`** est une **chaîne JSON** (`string`) qui peut prendre **deux formes** :

1. **Valeur prédéfinie (enum)** — l’une des constantes ci-dessous ;
2. **Identifiant libre** — toute autre chaîne **non vide** : nom **exact** du modèle tel qu’exposé par le **provider effectivement ciblé** après routage (ex. id LM Studio dans `GET /v1/models`, id modèle côté Google ou Anthropic selon l’adaptateur invoqué).

| Valeur (enum)    | Signification |
|------------------|----------------|
| `auto`           | Délégation complète au routeur (sous contraintes `privacy_level` et `max_cost_usd`). |
| `local`          | Forcer **LM Studio** (équivalent `lm_studio` côté `provider_used`). |
| `gemini_flash`   | Forcer l’adaptateur **Gemini Flash** si compatible avec `privacy_level`. |
| `claude_haiku`   | Forcer l’adaptateur **Claude Haiku** si compatible avec `privacy_level`. |

**Identifiant libre** — lorsque la valeur n’est **pas** l’une des quatre constantes ci-dessus, elle **ne** doit **pas** être interprétée comme un alias d’enum : c’est l’**identifiant canonique du modèle** pour le provider choisi (sensible à la casse selon les APIs cibles). Le routeur / l’adaptateur vérifie la présence du modèle lorsque l’API du fournisseur l’expose (ex. liste des modèles LM Studio).

*Si une valeur **enum** est incompatible avec `privacy_level` (ex. `claude_haiku` + `local_only`), le serveur renvoie une erreur explicite (voir §5). Une chaîne libre qui désigne un modèle **cloud** alors que `privacy_level = local_only` est également incohérente : à rejeter côté routeur ou adaptateur avec une erreur claire (`privacy_violation` ou `validation_error` selon l’implémentation).*

### 2.5 `status` (réponse)

| Valeur     | Signification |
|------------|----------------|
| `success`  | Exécution terminée ; résultat dans `output`. |
| `error`    | Échec sans secours utile ; détails dans `error`. |
| `fallback` | Échec ou refus du provider demandé, mais une exécution de repli a réussi. |

### 2.6 `provider_used`

| Valeur          | Fournisseur |
|-----------------|-------------|
| `lm_studio`     | LM Studio (local) |
| `gemini_flash`  | Google Gemini Flash |
| `claude_haiku`  | Anthropic Claude Haiku |

---

## 3. Requête — `RunRequest`

### 3.1 Schéma cible

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_type": "classification",
  "complexity": "low",
  "privacy_level": "standard",
  "preferred_model": "auto",
  "max_cost_usd": 0.01,
  "input": {
    "prompt": "string",
    "context": {},
    "data": []
  },
  "options": {
    "temperature": 0.2,
    "max_tokens": 1000,
    "timeout_ms": 30000
  }
}
```

### 3.2 Champs obligatoires (racine)

| Champ | Type | Description |
|-------|------|-------------|
| `task_id` | `string` (UUID v4 recommandé) | Corrélation requête / réponse et journaux. |
| `task_type` | `string` | Une valeur de §2.1. |
| `complexity` | `string` | Une valeur de §2.2. |
| `privacy_level` | `string` | Une valeur de §2.3. |
| `preferred_model` | `string` | Non vide : une **valeur enum** de §2.4 **ou** un **identifiant libre** de modèle pour le provider cible (voir §2.4). |
| `input` | `object` | Voir §3.3 : au minimum `prompt` non vide. |

### 3.3 Sous-objet `input`

| Champ | Obligatoire | Type | Défaut | Description |
|-------|-------------|------|--------|-------------|
| `prompt` | **oui** | `string` | — | Texte principal de la tâche ; longueur minimale > 0. |
| `context` | non | `object` | `{}` | Données structurées additionnelles (non loggées en clair par défaut côté orchestrateur). |
| `data` | non | `array` | `[]` | Pièces structurées (ex. blocs à classer) ; sémantique métier. |

### 3.4 Champs optionnels (racine)

| Champ | Type | Défaut | Description |
|-------|------|--------|-------------|
| `max_cost_usd` | `number` | comportement impl. | Plafond de coût estimé pour **cette** requête (USD). Si absent, le routeur applique une limite configurée côté serveur. |
| `options` | `object` | voir §3.5 | Paramètres transmis aux adaptateurs quand supportés. |

### 3.5 Sous-objet `options` (tous optionnels si `options` absent)

| Champ | Type | Défaut indicatif | Description |
|-------|------|-----------------|-------------|
| `temperature` | `number` | config serveur | 0–2 typiquement ; sémantique alignée sur le provider sous-jacent. |
| `max_tokens` | `integer` | config serveur | Limite haute de tokens de sortie. |
| `timeout_ms` | `integer` | config serveur | Délai max pour l’appel provider + normalisation. |

---

## 4. Réponse — `RunResponse`

### 4.1 Schéma cible

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "success",
  "provider_used": "lm_studio",
  "model_used": "string",
  "output": {},
  "usage": {
    "input_tokens": 0,
    "output_tokens": 0,
    "estimated_cost_usd": 0,
    "duration_ms": 0,
    "estimated_cloud_equivalent_cost_usd": null,
    "estimated_savings_usd": null
  },
  "routing_reason": "string",
  "error": null
}
```

### 4.2 Champs obligatoires

| Champ | Type | Description |
|-------|------|-------------|
| `task_id` | `string` | **Identique** à la requête. |
| `status` | `string` | Valeur de §2.5. |
| `provider_used` | `string` | Valeur de §2.6 (ou erreur si aucun provider n’a été sollicité). |
| `model_used` | `string` | Identifiant lisible du modèle (ex. nom OpenAI-compatible, id Anthropic, id Google). |
| `output` | `object` | Résultat normalisé ; vide `{}` autorisé si toute l’information est portée par erreur / logs uniquement pour les cas d’erreur métier documentés. |
| `usage` | `object` | Bloc coût / performance (§4.3). |
| `routing_reason` | `string` | Justification courte et stable pour l’audit (ex. `privacy_local_only`, `complexity_low_default_local`, `user_preferred_gemini`, `fallback_cloud_after_local_failure`). |

### 4.3 Sous-objet `usage` (champs requis pour coût et économie)

| Champ | Type | Oblig. | Description |
|-------|------|--------|-------------|
| `input_tokens` | `integer` | oui | Entrée ; `0` si inconnu. |
| `output_tokens` | `integer` | oui | Sortie ; `0` si inconnu. |
| `estimated_cost_usd` | `number` | oui | Coût **réel estimé** de l’appel (USD). **LM Studio : toujours `0`**. |
| `duration_ms` | `integer` | oui | Temps mesuré côté adaptateur (boucle locale ou aller-retour API). |

Champs **optionnels** pour le calcul d’économie (alignés sur les objectifs de logging backlog ; remplissage recommandé dès que le routeur peut les estimer) :

| Champ | Type | Description |
|-------|------|-------------|
| `estimated_cloud_equivalent_cost_usd` | `number` \| `null` | Coût **hypothétique** si la même charge avait été traitée par un référent cloud (définition de la référence : config serveur, ex. « équivalent Gemini Flash »). |
| `estimated_savings_usd` | `number` \| `null` | `estimated_cloud_equivalent_cost_usd - estimated_cost_usd` lorsque les deux sont connus ; sinon `null`. |

Ces champs permettent d’alimenter tableaux de bord et agrégations (ex. rapport quotidien) **sans** dupliquer le prompt dans les journaux.

### 4.4 `error`

- Type : `object` \| `null`
- `null` si `status` est `success` ou `fallback` sans erreur terminale.
- En cas d’`error`, structure recommandée (contrat stable minimal) :

```json
{
  "code": "string_machine_readable",
  "message": "message humain court",
  "retryable": false
}
```

Les codes précis (`provider_timeout`, `privacy_violation`, `cost_cap_exceeded`, etc.) seront listés dans une évolution de ce document ou dans le code du routeur.

---

## 5. Règles de validation transverses

1. **UUID** — `task_id` doit être un UUID RFC 4122 (v4 recommandé) ; sinon erreur `validation_error`.
2. **Énumérations contrôlées** — `task_type`, `complexity`, `privacy_level` doivent être dans les ensembles §2.1–§2.3 ; sinon `validation_error`. Pour `preferred_model`, se reporter à §2.4 : enum **ou** chaîne libre ; chaîne vide interdite.
3. **`local_only`** — interdit tout `provider_used` autre que `lm_studio` ; `preferred_model` cloud ⇒ erreur `privacy_violation` sans appel cloud.
4. **`auto` + `standard`** — le routeur choisit parmi les trois providers selon règles produit (documentées dans le moteur de routage, hors ce fichier).
5. **`max_cost_usd`** — si le coût estimé avant appel dépasse la limite, erreur ou statut métier `error` avec `code: cost_cap_exceeded` (comportement exact : implémentation WEA-171+).

---

## 6. Métadonnées de routage

| Source | Champ | Rôle |
|--------|-------|------|
| Requête | `complexity`, `privacy_level`, `preferred_model`, `max_cost_usd` | Entrées du routeur. |
| Réponse | `provider_used`, `routing_reason` | Preuve de décision et conformité. |
| Réponse | `usage` | Mesure coût / durée / économie estimée. |

---

## 7. Compatibilité fournisseurs

| Provider | `provider_used` | Remarques contractuelles |
|----------|-----------------|---------------------------|
| LM Studio | `lm_studio` | `usage.estimated_cost_usd === 0` ; tokens optionnels selon capacité de l’API locale. |
| Gemini Flash | `gemini_flash` | Tokens / coût selon réponse API ; arrondi et estimation documentés côté adaptateur. |
| Claude Haiku | `claude_haiku` | Idem ; `model_used` reflète la variante exacte. |

---

## 8. Critères d’acceptation (WEA-170)

| Critère | Couvert par |
|---------|----------------|
| Document court entrée / sortie | Résumé en tête + sections 3–4 et schémas JSON. |
| Champs obligatoires / optionnels | §3.2–3.5 et §4.2–4.3. |
| Support LM Studio, Gemini Flash, Claude Haiku | §2.6 et §7. |
| Forcer le local via `local_only` | §2.3 et §5.3. |
| Laisser l’orchestrateur choisir via `auto` | §2.4 et §5.4. |
| Données pour calcul d’économie | §4.3 (`estimated_cost_usd`, `estimated_cloud_equivalent_cost_usd`, `estimated_savings_usd`, tokens, durée). |

---

## 9. Hors scope (ce document)

- Endpoints HTTP précis (`POST /ai/run`, etc.) — ticket wrapper WEA-171.
- Schéma interne des adaptateurs — tickets adaptateurs.
- Format des fichiers de log et intégration Larridin — WEA-178+.

---

*Dernière mise à jour : 2026-05-13 — WEA-170 (résumé exécutif, clarification champs `input`, renumérotation §3.5 `options`).*
