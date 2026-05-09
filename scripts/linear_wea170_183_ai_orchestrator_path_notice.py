#!/usr/bin/env python3
"""
Post the canonical « .github/ai-orchestrator/ » strategic notice on Linear issues WEA-170–WEA-183.

Reuses linear_pr_common.issue_internal_id and comment_create (same auth as other scripts).

Environment:
  LINEAR_API_KEY — required for --apply (never committed).

Usage:
  python3 scripts/linear_wea170_183_ai_orchestrator_path_notice.py
      Dry-run: list issues and the comment body (no API writes).

  LINEAR_API_KEY=... python3 scripts/linear_wea170_183_ai_orchestrator_path_notice.py --apply
      Post the same Markdown comment on each issue.

Optional:
  python3 ... --issues WEA-170,WEA-171
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_scripts_dir = str(Path(__file__).resolve().parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from linear_pr_common import comment_create, issue_internal_id  # noqa: E402

DEFAULT_IDENTIFIERS: tuple[str, ...] = tuple(f"WEA-{n}" for n in range(170, 184))

STRATEGIC_NOTICE = """---
Mise à jour stratégique du contexte de développement.

L’orchestrateur IA ne doit pas être développé comme dépôt indépendant. Il doit être implémenté dans le dépôt d’infrastructure existant WeAdU-ltd/.github, sous le chemin de travail canonique suivant :

.github/ai-orchestrator/

Toutes les instructions de codage doivent tenir compte de ce contexte de dépôt partagé :
- utiliser des chemins relatifs depuis .github/ai-orchestrator/ dans les consignes fonctionnelles ;
- si le repo ouvert est directement le dépôt .github, créer/utiliser le dossier local ai-orchestrator/ ;
- ne pas supposer un repo standalone ;
- vérifier et réutiliser les scripts existants du dépôt avant d’en créer de nouveaux ;
- réutiliser notamment linear_pr_common.py quand pertinent ;
- éviter toute duplication de logique déjà présente dans WeAdU-ltd/.github ;
- isoler le code de l’orchestrateur dans .github/ai-orchestrator/ : adaptateurs providers, moteur de routage, serveur MCP, logging, documentation et tests.

Cette contrainte s’applique à ce ticket et à l’ensemble du backlog WEA-170 à WEA-183.
---
"""


def _parse_identifiers(raw: str | None) -> tuple[str, ...]:
    if not raw:
        return DEFAULT_IDENTIFIERS
    parts = [p.strip().upper() for p in raw.split(",") if p.strip()]
    return tuple(parts)


def _resolve_uuid(api_key: str, ident: str) -> str | None:
    if "-" not in ident:
        return None
    team_key, num_s = ident.split("-", 1)
    try:
        num = int(num_s)
    except ValueError:
        return None
    return issue_internal_id(api_key, ident, team_key, num)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Post strategic WeAdU-ltd/.github ai-orchestrator path notice on Linear issues."
    )
    ap.add_argument(
        "--issues",
        help=f"Comma-separated identifiers (default: WEA-170..WEA-183, {len(DEFAULT_IDENTIFIERS)} issues)",
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Actually post comments (requires LINEAR_API_KEY). Without this flag, dry-run only.",
    )
    args = ap.parse_args()

    idents = _parse_identifiers(args.issues)
    api_key = os.environ.get("LINEAR_API_KEY", "").strip()

    print("Mode:", "APPLY (commentCreate)" if args.apply else "DRY-RUN (no writes)")
    print("Issues:", ", ".join(idents))
    print("--- Comment body preview ---")
    print(STRATEGIC_NOTICE.strip())
    print("--- end preview ---\n")

    if not args.apply:
        print(
            "Dry-run complete. To post comments, set LINEAR_API_KEY and run:\n"
            "  LINEAR_API_KEY=<from GitHub org secret or local env> \\\n"
            "  python3 scripts/linear_wea170_183_ai_orchestrator_path_notice.py --apply"
        )
        return 0

    if not api_key:
        print(
            "LINEAR_API_KEY is not set in this environment. Comments were not posted.\n"
            "Configure the key (GitHub Actions secret, local export, or Cursor workspace secret), then run:\n"
            "  python3 scripts/linear_wea170_183_ai_orchestrator_path_notice.py --apply",
            file=sys.stderr,
        )
        return 2

    ok_count = 0
    errors: list[tuple[str, str]] = []
    for ident in idents:
        uuid = _resolve_uuid(api_key, ident)
        if not uuid:
            errors.append((ident, "issue not found or invalid identifier"))
            continue
        ok, msg = comment_create(api_key, uuid, STRATEGIC_NOTICE.strip())
        if ok:
            ok_count += 1
            print(f"OK  {ident}: {msg}")
        else:
            errors.append((ident, msg))
            print(f"ERR {ident}: {msg}", file=sys.stderr)

    print("\n--- Report ---")
    print(f"Method: Linear comment (commentCreate); body unchanged on issues.")
    print(f"Tickets targeted: {len(idents)}")
    print(f"Succeeded: {ok_count}")
    print(f"Failed: {len(errors)}")
    for ident, err in errors:
        print(f"  - {ident}: {err}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
