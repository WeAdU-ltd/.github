#!/usr/bin/env python3
"""
Ensure the Linear project « Autonomie agents » links to the canonical charter doc on GitHub.

Idempotent: if the project content already contains the target URL and the charter heading,
only the short description is topped up when the URL line is missing.

Environment:
  LINEAR_API_KEY                 — required
  LINEAR_AUTONOMIE_PROJECT_ID    — optional UUID (default: WeAdU project Autonomie agents)
  LINEAR_CHARTE_DOC_URL         — optional full URL to the markdown on default branch
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_scripts_dir = str(Path(__file__).resolve().parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from linear_pr_common import linear_request

DEFAULT_PROJECT_ID = "c5b40805-76a2-411d-955a-149666d2a7a2"
DEFAULT_DOC_URL = (
    "https://github.com/WeAdU-ltd/.github/blob/main/docs/CHARTE_AGENTS_LINEAR_WEA17.md"
)
CHARTE_HEADING = "## Charte agents (WEA-17)"
ORDER_MARKER = "## Ordre d'exécution recommandé"


def _fetch_project(api_key: str, project_id: str) -> tuple[str, str]:
    data = linear_request(
        api_key,
        """
        query P($id: String!) {
          project(id: $id) {
            description
            content
          }
        }
        """,
        {"id": project_id},
    )
    p = data.get("project") or {}
    desc = p.get("description") if isinstance(p.get("description"), str) else ""
    content = p.get("content") if isinstance(p.get("content"), str) else ""
    return desc or "", content or ""


def _build_charter_block(doc_url: str) -> str:
    return (
        "\n\n---\n\n"
        f"{CHARTE_HEADING}\n\n"
        "Document dépôt **WeAdU-ltd/.github** : "
        f"[Charte agents — Linear source, interdits, règle Cursor]({doc_url}).\n"
    )


def _ensure_description(desc: str, doc_url: str) -> str | None:
    """Return new description if an update is needed, else None."""
    line = f"Charte agents (WEA-17) : {doc_url}"
    if doc_url in desc and "Charte agents (WEA-17)" in desc:
        return None
    base = desc.strip()
    if not base:
        return line
    return f"{base}\n\n{line}"


def _ensure_content(content: str, doc_url: str) -> str | None:
    """Return new project content if an update is needed, else None."""
    if doc_url in content and CHARTE_HEADING in content:
        return None
    block = _build_charter_block(doc_url)
    if ORDER_MARKER in content:
        if block.strip() in content:
            return None
        return content.replace(ORDER_MARKER, block + ORDER_MARKER, 1)
    if CHARTE_HEADING in content:
        return None
    return content.rstrip() + block


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions only; do not call projectUpdate.",
    )
    args = parser.parse_args()

    api_key = os.environ.get("LINEAR_API_KEY", "").strip()
    if not api_key:
        print("linear_sync_autonomie_project_doc: LINEAR_API_KEY not set; skipping.", file=sys.stderr)
        return 0

    project_id = os.environ.get("LINEAR_AUTONOMIE_PROJECT_ID", DEFAULT_PROJECT_ID).strip()
    doc_url = os.environ.get("LINEAR_CHARTE_DOC_URL", DEFAULT_DOC_URL).strip()

    desc, content = _fetch_project(api_key, project_id)
    new_desc = _ensure_description(desc, doc_url)
    new_content = _ensure_content(content, doc_url)

    if new_desc is None and new_content is None:
        print("linear_sync_autonomie_project_doc: project already in sync; nothing to do.")
        return 0

    if args.dry_run:
        print("linear_sync_autonomie_project_doc: would update project", project_id)
        if new_desc is not None:
            print("--- description (preview) ---\n", new_desc[:500])
        if new_content is not None:
            print("--- content: insert or replace before order section ---")
        return 0

    input_payload: dict[str, str] = {}
    if new_desc is not None:
        input_payload["description"] = new_desc
    if new_content is not None:
        input_payload["content"] = new_content

    data = linear_request(
        api_key,
        """
        mutation U($id: String!, $input: ProjectUpdateInput!) {
          projectUpdate(id: $id, input: $input) {
            success
            project { id name }
          }
        }
        """,
        {"id": project_id, "input": input_payload},
    )
    pu = data.get("projectUpdate") or {}
    if not pu.get("success"):
        print("linear_sync_autonomie_project_doc: projectUpdate failed", file=sys.stderr)
        return 1
    proj = pu.get("project") or {}
    print(
        f"linear_sync_autonomie_project_doc: updated {proj.get('name')!r} ({proj.get('id')})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
