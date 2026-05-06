# Repl 01 — Weadu-Socle-V5-Lab — export agent Replit (miroir dépôt)

Date d’intégration : 2026-05-06. **Sans valeurs secrètes** ; les adresses IP et détails machines vivent dans l’inventaire AWS ([WEA-29](./WEA-29-aws-ec2-inventory.md)), pas dans ce fichier.

## Synthèse

| Zone | Contenu |
|------|---------|
| Stack | Python 3.11, FastAPI + Uvicorn, `uv`, `main.py`, `pyproject.toml`, `.replit`, `app/core/config.py`, `config/infra_projects.json` |
| Run local | `bash tools/setup_ssh.sh && python main.py` ; `curl …/health`, `…/aws/status` ; `tools/ask_claude.py` ; `kit/validate_kit.py` |
| Git | Remotes : `gitsafe-backup`, `subrepl-*` (Replit) ; branche `main` ; pas de remote `WeAdU-ltd/*` dans ce workspace au moment de l’export |
| Secrets | Noms uniquement : voir liste dans commentaire Linear associé au ticket Repl 1 — **ne pas** recopier les valeurs |
| PostgreSQL Replit | Oui — tables `kv_state`, `ideas` (council, Ideas Dashboard) ; migration état dynamique envisagée |
| Déploiement | `weadu-socle-v-5-lab.replit.app` ; VM dans `.replit` ; usages prod : council, watcher AWS, auditeurs, dashboards |
| Externes | AWS (SSH, secrets cache, COS `/aws/status`), Slack, Notion, Anthropic, Google (OAuth + APIs), SNS, crons documentés côté Repl |
| GitHub WeAdU-ltd | Non confirmé comme `origin` depuis ce Repl ; vérité migration socle : dépôt **`WeAdU-ltd/.github`** |

## Suite technique

1. Continuer à traiter **WeAdU-ltd/.github** comme socle documentaire + scripts (WEA-35).
2. Planifier migration PG (`kv_state`, `ideas`) ou abandon si fonctionnalités déplacées.
3. Ne pas publier d’IP ou de chemins machine dans les repos publics ; croiser WEA-29.

### Voir aussi (P0 suivant)

Repl 2 — **Chief of Staff (COS)** : prod sur EC2 — [`cos-replit-ec2-migration-2026-05-04.md`](./cos-replit-ec2-migration-2026-05-04.md).

_Preuve Linear : commentaire agent posté via API sur le ticket parent Repl 1 (`scripts/linear_issue_comment.py`)._
