#!/usr/bin/env python3
"""
After a PR is merged into the default branch, move linked Linear issues to Done (completed).

Reads the GitHub pull_request event from GITHUB_EVENT_PATH (Actions). Scans the **PR title**
only for issue identifiers like WEA-39 (team key + hyphen + number) so tickets mentioned
only in the PR body are not closed by mistake.

Environment:
  LINEAR_API_KEY  — Linear API key with permission to update issues (required)
  GITHUB_EVENT_PATH — set automatically in GitHub Actions

Exits 0 if the key is missing (workflow configured but secret not set yet).
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from typing import Any

LINEAR_GRAPHQL = "https://api.linear.app/graphql"

# Linear identifiers: leading word boundary, team key (letters/digits), hyphen, number.
_ISSUE_ID_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,9})-(\d+)\b")


def _linear_request(api_key: str, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        LINEAR_GRAPHQL,
        data=payload,
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        raise RuntimeError(f"Linear HTTP {e.code}: {detail}") from e
    if body.get("errors"):
        raise RuntimeError(f"Linear GraphQL errors: {body['errors']}")
    return body["data"]


def _extract_identifiers(title: str) -> list[str]:
    """Identifiers from PR title only (avoids closing tickets cited in body)."""
    text = title or ""
    seen: set[str] = set()
    out: list[str] = []
    for m in _ISSUE_ID_RE.finditer(text):
        ident = f"{m.group(1)}-{m.group(2)}"
        if ident not in seen:
            seen.add(ident)
            out.append(ident)
    return out


def _team_completed_state_id(api_key: str, team_key: str) -> str | None:
    data = _linear_request(
        api_key,
        """
        query TeamCompleted($teamKey: String!) {
          teams(filter: { key: { eq: $teamKey } }, first: 1) {
            nodes {
              states {
                nodes { id name type }
              }
            }
          }
        }
        """,
        {"teamKey": team_key},
    )
    teams = (data.get("teams") or {}).get("nodes") or []
    if not teams:
        return None
    states = ((teams[0].get("states") or {}).get("nodes")) or []
    for s in states:
        if (s.get("type") or "").lower() == "completed":
            return s["id"]
    return None


def _issue_internal_id(api_key: str, identifier: str, team_key: str, number: int) -> str | None:
    """Resolve human id (e.g. WEA-39) to internal UUID via issue(id: …)."""
    data = _linear_request(
        api_key,
        """
        query IssueByKey($identifier: String!) {
          issue(id: $identifier) {
            id
            identifier
          }
        }
        """,
        {"identifier": identifier},
    )
    issue = data.get("issue")
    if issue and issue.get("id"):
        return issue["id"]

    data = _linear_request(
        api_key,
        """
        query IssueByTeamNumber($teamKey: String!, $number: Float!) {
          issues(
            filter: { team: { key: { eq: $teamKey } }, number: { eq: $number } },
            first: 1
          ) {
            nodes { id identifier }
          }
        }
        """,
        {"teamKey": team_key, "number": float(number)},
    )
    nodes = (data.get("issues") or {}).get("nodes") or []
    if nodes and nodes[0].get("id"):
        return nodes[0]["id"]
    return None


def _issue_update_done(api_key: str, issue_uuid: str, state_id: str) -> tuple[bool, str]:
    data = _linear_request(
        api_key,
        """
        mutation IssueDone($id: String!, $stateId: String!) {
          issueUpdate(id: $id, input: { stateId: $stateId }) {
            success
            issue { id identifier state { name type } }
          }
        }
        """,
        {"id": issue_uuid, "stateId": state_id},
    )
    payload = data.get("issueUpdate") or {}
    if payload.get("success"):
        issue = payload.get("issue") or {}
        ident = issue.get("identifier") or issue_uuid
        state = (issue.get("state") or {}).get("name") or "?"
        return True, f"{ident} → {state}"
    return False, f"issueUpdate failed for {issue_uuid}"


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

    title = pr.get("title") or ""
    body = pr.get("body") or ""
    if os.environ.get("LINEAR_DONE_SCAN_BODY", "").strip().lower() in ("1", "true", "yes"):
        identifiers = _extract_identifiers(f"{title}\n{body}")
    else:
        identifiers = _extract_identifiers(title)
    if not identifiers:
        print("linear_mark_done_on_merge: no Linear-style identifiers in PR title/body; nothing to do.")
        return 0

    print(f"linear_mark_done_on_merge: candidates: {', '.join(identifiers)}")

    team_cache: dict[str, str | None] = {}
    errors = 0
    for ident in identifiers:
        m = _ISSUE_ID_RE.match(ident)
        if not m:
            continue
        team_key, num_s = m.group(1), m.group(2)
        number = int(num_s)

        if team_key not in team_cache:
            team_cache[team_key] = _team_completed_state_id(api_key, team_key)
        state_id = team_cache[team_key]
        if not state_id:
            print(f"linear_mark_done_on_merge: no completed state for team {team_key}; skip {ident}", file=sys.stderr)
            errors += 1
            continue

        issue_uuid = _issue_internal_id(api_key, ident, team_key, number)
        if not issue_uuid:
            print(f"linear_mark_done_on_merge: issue not found: {ident}", file=sys.stderr)
            errors += 1
            continue

        ok, msg = _issue_update_done(api_key, issue_uuid, state_id)
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
