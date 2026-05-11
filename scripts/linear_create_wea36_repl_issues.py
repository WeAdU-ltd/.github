#!/usr/bin/env python3
"""
Create one Linear parent issue per Repl (WEA-33 société scope) + ordered sub-issues,
with issueRelationCreate(blocks) chains and Repl-parent -> blocks -> WEA-36.

Prerequisites: LINEAR_API_KEY in the environment (same as other scripts/linear_*.py).

Default is dry-run (no API writes). Use --apply to create issues.

Example:
  export LINEAR_API_KEY=...
  python3 scripts/linear_create_wea36_repl_issues.py
  python3 scripts/linear_create_wea36_repl_issues.py --apply

Optional: --only-slug weadu-socle-v5-lab  (single Repl for testing)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

_scripts_dir = str(Path(__file__).resolve().parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from linear_pr_common import linear_request  # noqa: E402

LINEAR_GRAPHQL = "https://api.linear.app/graphql"

WEA_TEAM_KEY = "WEA"
WEA_TEAM_ID = "27f364a1-8f38-4eee-83fb-9d8cde85e192"
PROJECT_AUTONOMIE_ID = "c5b40805-76a2-411d-955a-149666d2a7a2"
LABEL_DOT_GITHUB_ID = "0d0f8c49-8e38-4889-82a5-3f38534743b5"

BRIEF_CHILD_BODY = """## Objectif

Obtenir **depuis l’agent Cursor du Repl** (pas seulement Socle) les infos nécessaires à la migration : dépendances réelles, secrets (**noms** uniquement), commandes de run, déploiement `.replit.app`, lien Git existant, volumétrie DB, ce qui est obsolete.

## Consigne à coller vers l’agent Replit

Demander à l’agent du Repl de produire un export structuré (Markdown) avec :

1. **Stack** : langage, frameworks, fichiers d’entrée (`main`, `package.json`, `requirements.txt`, etc.).
2. **Run local** : commandes exactes pour lancer en dev.
3. **Git** : remote(s) connus, branche par défaut, dernier commit court.
4. **Secrets** : liste des **noms** de variables (pas les valeurs) dans Replit Secrets.
5. **Base Replit** : oui/non, tables ou usage si pertinent.
6. **Déploiement** : URL `.replit.app`, Always On / autoscale, charge prod vs expérimentation.
7. **Externes** : AWS/GCP/API/OAuth redirect si visible dans le code ou la config.

Ne pas coller de secrets dans Linear ; résumer dans le ticket ou dans le dépôt cible plus tard.

## Exécution (référent WeAdU — routine sans friction)

- **Merge PR** sur `WeAdU-ltd/.github` : **auto-merge** quand la PR n’est pas brouillon et la CI requise est verte — **pas** de procédure *Merge* manuelle pour le référent (workflow `auto-merge-pr.yml`).
- **Coller cette consigne** : depuis une session **Cursor (ou équivalent) ouverte dans ce Repl**, ou tout opérateur avec le workspace Repl — **pas** comme liste d’actions pour le référent dans le chat.
- **Consigne canonique** (à préférer pour éviter les doubles) : [WEA-35 §7 — Brief agent dans le Repl](https://github.com/WeAdU-ltd/.github/blob/main/docs/inventory/WEA-35-weadu-socle-v5-lab-template.md#7-wea-44--brief-agent-cursor-dans-le-repl-export-migration).

## Critères de fait

- [ ] Réponse de l’agent Repl ou justification documentée si le Repl est inaccessible.
"""


def _repl_slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80] or "repl"


# WEA-33 table rows 1–21 (main); replit id prefix for traceability in description.
REPL_EPICS: list[dict[str, Any]] = [
    {"num": 1, "name": "Weadu-Socle-V5-Lab", "id_prefix": "3194f6df", "prio": "P0", "scope": "société", "note": "Hub Socle — cible doc WeAdU-ltd/.github + WEA-35"},
    {"num": 2, "name": "Chief of Staff Virtuel IA (COS)", "id_prefix": "cfe38994", "prio": "P0", "scope": "société", "note": "Prod EC2 — pas hébergement Replit"},
    {"num": 3, "name": "after-framfield-cockpit", "id_prefix": "6514c921", "prio": "P1", "scope": "perso/société à trancher", "note": "OAuth redirect instable"},
    {"num": 4, "name": "negative-search-terms-tool", "id_prefix": "5ffebe14", "prio": "P1", "scope": "société", "note": "Probable équivalent WeAdU-ltd/Negative-Terms"},
    {"num": 5, "name": "wellbots-shopping-ads-checker", "id_prefix": "79eb34c6", "prio": "P1", "scope": "société", "note": "Probable équivalent WeAdU-ltd/SH-Checker-Bids"},
    {"num": 6, "name": "WeAdU LeadGen", "id_prefix": "345d8dd5", "prio": "P2", "scope": "société", "note": ""},
    {"num": 7, "name": "Max Conv Val Budget Mngt", "id_prefix": "d32b27a6", "prio": "P2", "scope": "société", "note": ""},
    {"num": 8, "name": "Waste Watcher", "id_prefix": "f09a27de", "prio": "P2", "scope": "société", "note": ""},
    {"num": 9, "name": "Automatic Google Ads tracking monitoring", "id_prefix": "7fc2b09c", "prio": "P2", "scope": "société", "note": "Réconcilier UUID 6b3e66a1 / Brand-crea-bids"},
    {"num": 10, "name": "Wellbots real-time figures", "id_prefix": "6301f251", "prio": "P2", "scope": "société", "note": ""},
    {
        "num": 11,
        "name": "suspended accounts clean up",
        "id_prefix": "139389d0",
        "prio": "P2",
        "scope": "société",
        "note": "Hors migration GitHub : épique Linear [Repl 11] supprimée 2026-05-05 (WEA-33 §4).",
        "skip_linear_epic": True,
    },
    {"num": 12, "name": "Dashboard — Carmino & monPL", "id_prefix": "89725b9e", "prio": "P2", "scope": "société", "note": "Possible hub EC2"},
    {"num": 13, "name": "Recommandations mngt", "id_prefix": "ad9b5532", "prio": "P2", "scope": "société", "note": ""},
    {"num": 14, "name": "Ads Performance Analyze", "id_prefix": "cb5cc4be", "prio": "P2", "scope": "société", "note": ""},
    {"num": 15, "name": "pd-detection", "id_prefix": "3e94a8f8", "prio": "P2", "scope": "finance-rh", "note": "Isolation / WEA-37"},
    {"num": 16, "name": "bad performers", "id_prefix": "8ae0b387", "prio": "P3", "scope": "société", "note": ""},
    {"num": 17, "name": "Feed Optimizer", "id_prefix": "cb7bc686", "prio": "P3", "scope": "société", "note": ""},
    {"num": 18, "name": "Dashboard — Epic Extender", "id_prefix": "bc1c605a", "prio": "P3", "scope": "société", "note": ""},
    {"num": 19, "name": "Bad Performer labels", "id_prefix": "67b17d9b", "prio": "P3", "scope": "société", "note": ""},
    {"num": 20, "name": "Test tracker", "id_prefix": "62ce3ea8", "prio": "P3", "scope": "société", "note": ""},
    {"num": 21, "name": "Divers", "id_prefix": "d6bcecff", "prio": "—", "scope": "à décider", "note": "Scratch / archivage ?"},
]


def _issue_create(
    api_key: str,
    title: str,
    description: str,
    *,
    parent_id: str | None = None,
    priority: int | None = None,
) -> dict[str, Any]:
    """priority: 0 = none, 1 = urgent ... Linear scale."""
    inp: dict[str, Any] = {
        "teamId": WEA_TEAM_ID,
        "projectId": PROJECT_AUTONOMIE_ID,
        "title": title[:255],
        "description": description,
        "labelIds": [LABEL_DOT_GITHUB_ID],
    }
    if parent_id:
        inp["parentId"] = parent_id
    if priority is not None:
        inp["priority"] = priority
    data = linear_request(
        api_key,
        """
        mutation IssueCreate($input: IssueCreateInput!) {
          issueCreate(input: $input) {
            success
            issue { id identifier title parent { id } }
          }
        }
        """,
        {"input": inp},
    )
    payload = data.get("issueCreate") or {}
    if not payload.get("success"):
        raise RuntimeError(f"issueCreate failed: {payload}")
    return payload["issue"]


def _relation_create(api_key: str, blocking_id: str, blocked_id: str) -> None:
    data = linear_request(
        api_key,
        """
        mutation Rel($input: IssueRelationCreateInput!) {
          issueRelationCreate(input: $input) {
            success
            issueRelation { id type }
          }
        }
        """,
        {
            "input": {
                "issueId": blocking_id,
                "relatedIssueId": blocked_id,
                "type": "blocks",
            }
        },
    )
    payload = data.get("issueRelationCreate") or {}
    if not payload.get("success"):
        raise RuntimeError(f"issueRelationCreate failed: {payload}")


def _existing_repl_parent(api_key: str, repl_num: int) -> dict[str, Any] | None:
    """Return an existing parent issue if this script was already run for that line number."""
    frag = f"[Repl {repl_num}]"
    data = linear_request(
        api_key,
        """
        query Q($teamKey: String!, $frag: String!) {
          issues(
            filter: { team: { key: { eq: $teamKey } }, title: { containsIgnoreCase: $frag } }
            first: 3
          ) {
            nodes { id identifier title }
          }
        }
        """,
        {"teamKey": WEA_TEAM_KEY, "frag": frag},
    )
    nodes = (data.get("issues") or {}).get("nodes") or []
    for n in nodes:
        t = n.get("title") or ""
        if t.strip().startswith(frag):
            return n
    return None


def _fetch_issue_id(api_key: str, identifier: str) -> str:
    data = linear_request(
        api_key,
        """
        query I($id: String!) {
          issue(id: $id) { id identifier }
        }
        """,
        {"id": identifier},
    )
    issue = data.get("issue")
    if not issue or not issue.get("id"):
        raise RuntimeError(f"Issue {identifier!r} not found")
    return issue["id"]


def _parent_description(meta: dict[str, Any], slug: str) -> str:
    return f"""## Repl source (WEA-33)

- **Ligne inventaire** : #{meta["num"]}
- **Nom Replit** : {meta["name"]}
- **ID (préfixe)** : `{meta["id_prefix"]}-…`
- **Priorité migration** : {meta["prio"]}
- **Périmètre** : {meta["scope"]}
- **Notes** : {meta.get("note") or "—"}

## Programme

Ticket parent pour la migration **Replit → GitHub** (chaîne [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents)). Les sous-tickets ci-dessous sont ordonnés : chaque étape **bloque** la suivante.

**Règle** : avant tout export ou cutover, passer par le sous-ticket **Brief agent Replit** — Socle n’a pas la même précision que l’agent du Repl.

## Liens dépôt

- Inventaire : [`docs/inventory/WEA-33-replit-inventory.md`](https://github.com/WeAdU-ltd/.github/blob/main/docs/inventory/WEA-33-replit-inventory.md)
- Migration vagues : [`docs/inventory/WEA-36-replit-migration-societe.md`](https://github.com/WeAdU-ltd/.github/blob/main/docs/inventory/WEA-36-replit-migration-societe.md)

_Slug ticket : `{slug}`_
"""


def _child_titles(slug: str, display_name: str) -> list[tuple[str, str]]:
    return [
        (
            f"{display_name} — brief agent Replit (infos migration)",
            BRIEF_CHILD_BODY,
        ),
        (
            f"{display_name} — synthèse : inventaire / ticket à jour",
            f"""## Objectif

Consolider la réponse de l’agent Repl dans ce ticket (ou lien vers doc dépôt `.github` si PR).

## Critères de fait

- [ ] Colonnes équivalentes WEA-33 mises à jour ou lien vers PR dépôt.
""",
        ),
        (
            f"{display_name} — dépôt GitHub `WeAdU-ltd/…` créé ou confirmé",
            """## Objectif

Créer le dépôt sous `WeAdU-ltd` **ou** confirmer l’URL existante (croiser [WEA-12](https://linear.app/weadu/issue/WEA-12/github-inventaire-orgs-comptes-repos-et-acces)).

## Critères de fait

- [ ] URL `https://github.com/WeAdU-ltd/<repo>` connue et notée sur ce ticket.
- [ ] Label Linear groupe `repo` aligné si besoin ([WEA-17](https://linear.app/weadu/issue/WEA-17/charte-agents-linear-source-interdits-features-nouveaux-projets)).
""",
        ),
        (
            f"{display_name} — code importé + README procédure de run",
            """## Objectif

Pousser le code (historique si possible) et documenter **comment** lancer / tester / déployer.

## Critères de fait

- [ ] `README` avec prérequis, commandes, secrets **nommés** (valeurs hors repo, [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh)).
- [ ] CI minimale ou alignement template [WEA-35](https://linear.app/weadu/issue/WEA-35/weadu-socle-v5-lab-audit-template-github-cursor) si nouveau dépôt.
""",
        ),
        (
            f"{display_name} — cutover : prod hors Replit + résiduel",
            """## Objectif

Basculer la charge utile hors Replit ; ne garder le Repl **que** si cutover non fini ([liste résiduelle](https://github.com/WeAdU-ltd/.github/blob/main/docs/inventory/WEA-36-replit-migration-societe.md)).

## Critères de fait

- [ ] Prod / scheduling ne dépend plus du Repl **ou** entrée explicite dans la liste résiduelle avec justification.
- [ ] Secrets retirés ou tournés côté GitHub / hébergement cible si applicable.
""",
        ),
    ]


def main() -> int:
    api_key = os.environ.get("LINEAR_API_KEY", "").strip()
    if not api_key:
        print("LINEAR_API_KEY not set.", file=sys.stderr)
        return 1

    ap = argparse.ArgumentParser(description="Create WEA Repl migration Linear issues.")
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Actually create issues (default is dry-run).",
    )
    ap.add_argument(
        "--only-slug",
        help="Only process one Repl slug (e.g. weadu-socle-v5-lab).",
    )
    args = ap.parse_args()

    epics = REPL_EPICS
    if args.only_slug:
        slug_f = args.only_slug.strip().lower()
        epics = [e for e in REPL_EPICS if _repl_slugify(e["name"]) == slug_f]
        if not epics:
            print(f"No Repl matching slug {args.only_slug!r}", file=sys.stderr)
            return 1
        if epics[0].get("skip_linear_epic"):
            print(
                f"Repl {args.only_slug!r} is excluded from Linear migration epics (see WEA-33 §4).",
                file=sys.stderr,
            )
            return 1

    epics = [e for e in epics if not e.get("skip_linear_epic")]
    if not epics:
        print("No Repl epics to process after skip_linear_epic filter.", file=sys.stderr)
        return 0

    wea36_id = _fetch_issue_id(api_key, "WEA-36")

    print(f"WEA-36 id: {wea36_id}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
    print(f"Repl epics to process: {len(epics)}")

    if not args.apply:
        for meta in epics:
            slug = _repl_slugify(meta["name"])
            kids = _child_titles(slug, meta["name"])
            print(f"- {slug}: 1 parent + {len(kids)} children; cutover (last child) blocks WEA-36")
        print("\nRun with --apply to create issues on Linear.")
        return 0

    created_parents = 0
    skipped = 0
    for meta in epics:
        slug = _repl_slugify(meta["name"])
        existing = _existing_repl_parent(api_key, meta["num"])
        if existing:
            print(f"Skip Repl {meta['num']} ({slug}): already exists {existing.get('identifier')}")
            skipped += 1
            continue

        parent_title = f"[Repl {meta['num']}] {meta['name']} — migration Replit → GitHub ({meta['scope']})"
        parent_desc = _parent_description(meta, slug)

        parent = _issue_create(api_key, parent_title, parent_desc)
        parent_id = parent["id"]
        created_parents += 1
        print(f"Created parent {parent.get('identifier')} {parent_title[:60]}…")

        child_ids: list[str] = []
        for title, body in _child_titles(slug, meta["name"]):
            time.sleep(0.15)
            ch = _issue_create(api_key, title, body, parent_id=parent_id)
            child_ids.append(ch["id"])
            print(f"  child {ch.get('identifier')} {title[:50]}…")

        for i in range(len(child_ids) - 1):
            time.sleep(0.1)
            _relation_create(api_key, child_ids[i], child_ids[i + 1])

        # Last step (cutover) blocks WEA-36 so the epic unblocks only when every Repl cutover is Done.
        time.sleep(0.1)
        _relation_create(api_key, child_ids[-1], wea36_id)

        time.sleep(0.25)

    print(
        f"\nDone. Created {created_parents} parent epics (+ sub-issues); skipped {skipped} already present; "
        "each Repl chain ends with cutover -> blocks -> WEA-36."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
