#!/usr/bin/env python3
"""
After a PR is merged into the default branch, move linked Linear issues to Done (completed)
when policy allows it.

Reads the GitHub pull_request event from GITHUB_EVENT_PATH (Actions). Collects Linear-style
identifiers (e.g. WEA-39) from, by default:
  - the PR head branch name (e.g. jeff/wea-39-short-title, cursor/wea-39-foo-d965)
  - the PR title

**WEA-*** issues (team key WEA): Done is applied only if the merged PR description contains a
"## Critères de fait" section (Markdown) where every bullet shows an explicit completed checkbox
(`[x]` or `[X]`). If not, the issue stays open and an **Écart** comment is posted on Linear
listing what is missing (no false "Done").

Other team keys: unchanged — issues are moved to completed when found (no checklist gate).

Optional: set LINEAR_DONE_SCAN_BODY to true to also scan the PR body for extra identifiers
(may match tickets you only mention in prose).

Environment:
  LINEAR_API_KEY     — Linear API key with permission to update issues (required for updates)
  GITHUB_EVENT_PATH  — set automatically in GitHub Actions

Exits 0 if LINEAR_API_KEY is missing (workflow present but secret not available to the job).
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

# Team key (case-insensitive in source) + hyphen + number. Matched id is normalized to uppercase.
_ISSUE_ID_RE = re.compile(r"\b([A-Za-z][A-Za-z0-9]{1,9})-(\d+)\b")

# Checkbox: marked done
_DONE_BOX = re.compile(r"\[[xX]\]")
# Empty checkbox (space or nothing between brackets)
_OPEN_BOX = re.compile(r"\[\s*\]")


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


def _extract_identifiers_from_text(text: str) -> list[str]:
    """Return unique identifiers in order of first appearance (e.g. WEA-39)."""
    seen: set[str] = set()
    out: list[str] = []
    for m in _ISSUE_ID_RE.finditer(text or ""):
        ident = f"{m.group(1).upper()}-{m.group(2)}"
        if ident not in seen:
            seen.add(ident)
            out.append(ident)
    return out


def _collect_identifier_sources(pr: dict[str, Any]) -> list[str]:
    head_ref = ((pr.get("head") or {}).get("ref")) or ""
    title = pr.get("title") or ""
    body = pr.get("body") or ""
    parts = [head_ref, title]
    if os.environ.get("LINEAR_DONE_SCAN_BODY", "").strip().lower() in ("1", "true", "yes"):
        parts.append(body)
    return parts


def _extract_criteria_section_lines(body: str) -> list[str] | None:
    """
    Return bullet text lines under '## Critères de fait' until the next '## ' heading.
    None if the section heading is missing.
    """
    lines = (body or "").splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.lower().startswith("## critères de fait"):
            collected: list[str] = []
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                if nxt.startswith("## ") and not nxt.strip().lower().startswith("## critères de fait"):
                    break
                m = re.match(r"^\s*[*-]\s+(.+)$", nxt)
                if m:
                    collected.append(m.group(1).strip())
                j += 1
            return collected
    return None


def _wea_criteria_gate(pr_body: str) -> tuple[bool, str]:
    """
    For WEA-* tickets: require PR description to prove criteria with explicit [x] on each bullet
    under ## Critères de fait.
    Returns (allowed_to_mark_done, human_reason_for_écart_if_false).
    """
    section_lines = _extract_criteria_section_lines(pr_body)
    if section_lines is None:
        return False, (
            "La description de la PR ne contient pas de section Markdown "
            '`## Critères de fait` (copie depuis Linear, avec une ligne `* [ ]` par critère, '
            "puis cochez chaque `* [x]` quand le critère est réellement couvert avant/après merge)."
        )
    if not section_lines:
        return False, (
            'Section `## Critères de fait` vide ou sans puces (`*` ou `-`). '
            "Listez chaque critère avec une case à cocher."
        )
    problems: list[str] = []
    for idx, text in enumerate(section_lines, start=1):
        if _OPEN_BOX.search(text):
            problems.append(f"Ligne {idx} : case non cochée (`[ ]`) — {text[:200]}")
        elif not _DONE_BOX.search(text):
            problems.append(
                f"Ligne {idx} : pas de case cochée explicite (`[x]`) — {text[:200]}"
            )
    if problems:
        return False, "Critères de fait : preuve insuffisante dans la PR.\n\n" + "\n".join(
            f"- {p}" for p in problems
        )
    return True, ""


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


def _comment_create(api_key: str, issue_uuid: str, body: str) -> tuple[bool, str]:
    data = _linear_request(
        api_key,
        """
        mutation CommentCreate($issueId: String!, $body: String!) {
          commentCreate(input: { issueId: $issueId, body: $body }) {
            success
            comment { id }
          }
        }
        """,
        {"issueId": issue_uuid, "body": body},
    )
    payload = data.get("commentCreate") or {}
    if payload.get("success"):
        return True, "comment posted"
    return False, "commentCreate failed"


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
    for chunk in _collect_identifier_sources(pr):
        for ident in _extract_identifiers_from_text(chunk):
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

        if team_key == "WEA":
            ok_gate, gate_msg = _wea_criteria_gate(pr_body)
            if not ok_gate:
                merge_url = pr.get("html_url") or ""
                cbody = (
                    "## Écart vs critères de fait (automation `.github`)\n\n"
                    f"{gate_msg}\n\n"
                    "Le ticket **n’a pas** été passé en Done automatiquement.\n\n"
                    f"PR fusionnée : {merge_url}\n"
                )
                cok, cmsg = _comment_create(api_key, issue_uuid, cbody)
                if cok:
                    print(f"linear_mark_done_on_merge: {ident}: criteria not met; Écart comment posted.")
                else:
                    print(f"linear_mark_done_on_merge: {ident}: {cmsg}", file=sys.stderr)
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
