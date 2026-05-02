#!/usr/bin/env python3
"""
After a PR is merged into the default branch, move linked Linear issues to Done (completed)
when policy allows it.

Reads the GitHub pull_request event from GITHUB_EVENT_PATH (Actions). Collects Linear-style
identifiers (e.g. WEA-39) from, by default:
  - the PR head branch name (e.g. jeff/wea-39-short-title, cursor/wea-39-foo-d965)
  - the PR title

**WEA-*** issues: Done only if every bullet under `## Critères de fait` has `[x]`, using in order:
  1) that section in the merged PR body (if it has checklist bullets), else
  2) the same section on the Linear issue description.

Otherwise an **Écart** comment is posted (no false Done). Other team keys: no checklist gate.

Optional: set LINEAR_DONE_SCAN_BODY to true to also scan the PR body for identifiers.

Environment:
  LINEAR_API_KEY     — Linear API key (required for updates)
  GITHUB_EVENT_PATH  — set automatically in GitHub Actions

Exits 0 if LINEAR_API_KEY is missing.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

_scripts_dir = str(Path(__file__).resolve().parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from linear_pr_common import (
    collect_pr_identifier_sources,
    comment_create,
    extract_identifiers_from_text,
    issue_fetch_description,
    issue_internal_id,
    issue_update_done,
    team_completed_state_id,
    wea_criteria_gate,
)


def main() -> int:
    api_key = os.environ.get("LINEAR_API_KEY", "").strip()
    if not api_key:
        print("linear_mark_done_on_merge: LINEAR_API_KEY not set; skipping.", file=sys.stderr)
        return 0

    event_path = os.environ.get("GITHUB_EVENT_PATH", "").strip()
    if not event_path:
        print("linear_mark_done_on_merge: GITHUB_EVENT_PATH missing; not running in Actions?", file=sys.stderr)
        return 1

    with open(event_path, encoding="utf-8") as f:
        event = json.load(f)

    pr = event.get("pull_request") or {}
    if not pr.get("merged"):
        print("linear_mark_done_on_merge: PR not merged; nothing to do.")
        return 0

    pr_body = pr.get("body") or ""

    seen: set[str] = set()
    identifiers: list[str] = []
    for chunk in collect_pr_identifier_sources(pr):
        for ident in extract_identifiers_from_text(chunk):
            if ident not in seen:
                seen.add(ident)
                identifiers.append(ident)

    if not identifiers:
        print(
            "linear_mark_done_on_merge: no Linear-style identifiers in head branch name or PR title "
            "(enable LINEAR_DONE_SCAN_BODY to include PR body); nothing to do.",
            file=sys.stderr,
        )
        return 0

    print(f"linear_mark_done_on_merge: candidates: {', '.join(identifiers)}")

    team_cache: dict[str, str | None] = {}
    errors = 0
    for ident in identifiers:
        m = re.match(r"^([A-Z][A-Z0-9]{1,9})-(\d+)$", ident)
        if not m:
            continue
        team_key, num_s = m.group(1), m.group(2)
        number = int(num_s)

        if team_key not in team_cache:
            team_cache[team_key] = team_completed_state_id(api_key, team_key)
        state_id = team_cache[team_key]
        if not state_id:
            print(f"linear_mark_done_on_merge: no completed state for team {team_key}; skip {ident}", file=sys.stderr)
            errors += 1
            continue

        issue_uuid = issue_internal_id(api_key, ident, team_key, number)
        if not issue_uuid:
            print(f"linear_mark_done_on_merge: issue not found: {ident}", file=sys.stderr)
            errors += 1
            continue

        if team_key == "WEA":
            linear_desc = issue_fetch_description(api_key, issue_uuid)
            ok_gate, gate_msg = wea_criteria_gate(pr_body, linear_desc)
            if not ok_gate:
                merge_url = pr.get("html_url") or ""
                cbody = (
                    "## Écart vs critères de fait (automation `.github`)\n\n"
                    f"{gate_msg}\n\n"
                    "Le ticket **n’a pas** été passé en Done automatiquement.\n\n"
                    f"PR fusionnée : {merge_url}\n"
                )
                cok, cmsg = comment_create(api_key, issue_uuid, cbody)
                if cok:
                    print(f"linear_mark_done_on_merge: {ident}: criteria not met; Écart comment posted.")
                else:
                    print(f"linear_mark_done_on_merge: {ident}: {cmsg}", file=sys.stderr)
                    errors += 1
                continue

        ok, msg = issue_update_done(api_key, issue_uuid, state_id)
        if ok:
            print(f"linear_mark_done_on_merge: {msg}")
        else:
            print(f"linear_mark_done_on_merge: {msg}", file=sys.stderr)
            errors += 1

    return 1 if errors else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as e:
        print(f"linear_mark_done_on_merge: {e}", file=sys.stderr)
        raise SystemExit(1) from e
