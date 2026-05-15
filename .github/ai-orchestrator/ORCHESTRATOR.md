# Standard d’utilisation — orchestrateur IA WeAdU

Référence unique pour les agents, scripts et services internes. Ne pas dupliquer ce contenu ailleurs : renvoyer vers ce fichier.

Contrat JSON détaillé des champs : [`specs/api_contract.md`](specs/api_contract.md).

---

## 1. Quand utiliser l’orchestrateur

- Toute tâche IA : extraction, génération, classification, analyse, codage.
- Toute tâche avec des données potentiellement sensibles (toujours choisir un `privacy_level` explicite).
- Tout flux qui fait **plus d’un** appel modèle (centraliser le routage, le budget et la traçabilité).

Objectif : aucun code métier ne parle en direct aux fournisseurs cloud ou à LM Studio ; tout passe par le wrapper et les adaptateurs officiels sous `.github/ai-orchestrator/`.

---

## 2. Comment appeler `POST /ai/run`

**Prérequis :** le serveur FastAPI du wrapper est démarré (voir `requirements.txt` et `main.py` dans ce dossier). Port local par défaut : **8787**.

### Exemple `curl`

```bash
curl -sS -X POST "http://127.0.0.1:8787/ai/run" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "task_type": "extraction",
    "complexity": "low",
    "privacy_level": "local_only",
    "preferred_model": "auto",
    "input": { "prompt": "Exemple de prompt pour un test local." }
  }'
```

### Exemple Python (`httpx`)

```python
import json
import uuid

import httpx

body = {
    "task_id": str(uuid.uuid4()),
    "task_type": "extraction",
    "complexity": "low",
    "privacy_level": "local_only",
    "preferred_model": "auto",
    "input": {"prompt": "Exemple de prompt pour un test local."},
}

r = httpx.post(
    "http://127.0.0.1:8787/ai/run",
    json=body,
    headers={"Content-Type": "application/json"},
    timeout=120.0,
)
print(r.status_code)
print(json.dumps(r.json(), indent=2, ensure_ascii=False))
```

**Confidentialité :** avec `privacy_level: local_only`, le routeur n’envoie pas vers un fournisseur cloud ; toute demande incompatible (ex. `preferred_model` cloud) doit être rejetée avec une erreur explicite.

**Coût :** utiliser `max_cost_usd` lorsque le contrat le prévoit ; la réponse normalisée inclut un bloc `usage` (tokens, `estimated_cost_usd`, et champs d’**estimation d’économie** vis-à-vis d’un équivalent cloud lorsque l’implémentation les renseigne). Voir `specs/api_contract.md` §4.

---

## 3. Comment configurer MCP pour Cursor

Le bloc ci-dessous est la **même** configuration que la section **« AI orchestrator — Cursor MCP »** du [`README.md`](../../README.md) à la racine du dépôt `WeAdU-ltd/.github`.

1. Démarrer le wrapper HTTP sur `127.0.0.1:8787` (port par défaut du code dans ce dossier).
2. Fusionner l’objet suivant dans **`.cursor/mcp.json`** du workspace (ou l’équivalent global `~/.cursor/mcp.json`), puis redémarrer Cursor.

```json
{
  "mcpServers": {
    "weadu-ai-orchestrator": {
      "type": "stdio",
      "command": "python3",
      "args": ["${workspaceFolder}/.github/ai-orchestrator/mcp_server.py"],
      "env": {
        "WEADU_ORCHESTRATOR_URL": "http://127.0.0.1:8787"
      }
    }
  }
}
```

**Outil exposé :** `ai_run` — paramètre `run_request_json` : chaîne JSON du corps `RunRequest` (mêmes champs que l’exemple `curl`).

---

## 4. Comment choisir `complexity`

| Valeur   | Quand l’utiliser |
|----------|------------------|
| `low`    | Tâche simple, court contexte, réponse structurée attendue. |
| `medium` | Analyse multi-étapes, résumé, extraction complexe. |
| `high`   | Raisonnement profond, code complexe, décision critique. |

Le routeur peut s’appuyer sur ce signal ; `privacy_level` et `preferred_model` restent prioritaires pour le choix de fournisseur.

---

## 5. Comment choisir `privacy_level`

| Valeur               | Quand l’utiliser |
|----------------------|------------------|
| `local_only`         | Données client, clés, données personnelles, données produit propriétaires : **aucun** envoi vers un fournisseur cloud. |
| `standard`           | Données internes non sensibles, traitables selon la politique WeAdU sur fournisseurs cloud. |
| `external_allowed`   | Tâches pour lesquelles l’envoi explicite vers un provider cloud est accepté au sens produit / juridique (extensions fines, DPA, régions). |

En cas de doute entre `standard` et `external_allowed`, rester sur le niveau le plus restrictif compatible avec la tâche.

---

## 6. Comment lire les logs

- **Chemin cible (journalisation des appels, WEA-178) :** `logs/ai_orchestrator.jsonl` (à la racine du dépôt applicatif ou du service qui exécute l’orchestrateur, selon déploiement).
- **Format :** JSONL (une ligne JSON par appel).
- **Contenu attendu :** corrélation `task_id`, `provider_used`, `model_used`, métriques `usage` / coût, **sans** stocker le prompt complet ni de secrets.

Tant que le fichier n’est pas encore produit par votre build, s’appuyer sur la réponse HTTP (`provider_used`, `usage`, etc.) pour valider le routage.

---

## 7. Ce qui est interdit

- Aucun appel direct à `https://generativelanguage.googleapis.com` depuis le code métier.
- Aucun appel direct à `https://api.anthropic.com` depuis le code métier.
- Aucun appel direct à LM Studio depuis le code métier **hors** adaptateur officiel de l’orchestrateur.
- Aucune clé API ou secret dans le code source ou les fichiers versionnés.
- Aucun prompt complet ou contenu sensible **en clair** dans les logs.

---

## 8. Checklist d’intégration pour nouvelles fonctions

- [ ] La fonction appelle `POST /ai/run` (ou l’outil MCP `ai_run` qui proxy vers ce endpoint), **pas** un provider directement.
- [ ] `privacy_level` est correctement défini pour la sensibilité réelle des données.
- [ ] `complexity` est correctement défini pour l’effort attendu du modèle.
- [ ] La fonction ne contient plus de logique de **fallback** maison entre fournisseurs (déléguée au routeur).
- [ ] La fonction ne connaît plus de clé API : uniquement configuration d’environnement / secrets hors code.
- [ ] Après déploiement, les logs ou la réponse `RunResponse` montrent le **provider** effectivement utilisé (`provider_used`) de façon cohérente avec la politique de confidentialité.
