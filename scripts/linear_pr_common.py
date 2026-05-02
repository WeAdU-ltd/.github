"""Shared helpers for Linear ↔ GitHub PR automation (no third-party deps)."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

LINEAR_GRAPHQL = "https://api.linear.app/graphql"

_ISSUE_ID_RE = re.compile(r"\b([A-Za-z][A-Za-z0-9]{1,9})-(\d+)\b")

_DONE_BOX = re.compile(r"\[[xX]\]")
_OPEN_BOX = re.compile(r"\[\s*\]")


def linear_request(api_key: str, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
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


def extract_identifiers_from_text(text: str) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for m in _ISSUE_ID_RE.finditer(text or ""):
        ident = f"{m.group(1).upper()}-{m.group(2)}"
        if ident not in seen:
            seen.add(ident)
            out.append(ident)
    return out


def collect_pr_identifier_sources(pr: dict[str, Any]) -> list[str]:
    head_ref = ((pr.get("head") or {}).get("ref")) or ""
    title = pr.get("title") or ""
    body = pr.get("body") or ""
    parts = [head_ref, title]
    if os.environ.get("LINEAR_DONE_SCAN_BODY", "").strip().lower() in ("1", "true", "yes"):
        parts.append(body)
    return parts


def extract_criteria_section_lines(body: str) -> list[str] | None:
    """Bullet text lines under ## Critères de fait, or None if heading missing."""
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


def extract_criteria_section_raw(body: str) -> str | None:
    """Full Markdown block from ## Critères de fait through the next top-level ## heading."""
    lines = (body or "").splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.lower().startswith("## critères de fait"):
            chunk: list[str] = [lines[i].rstrip()]
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                if nxt.startswith("## ") and not nxt.strip().lower().startswith("## critères de fait"):
                    break
                chunk.append(nxt.rstrip())
                j += 1
            text = "\n".join(chunk).strip()
            return text or None
    return None


def validate_criteria_bullet_lines(section_lines: list[str]) -> tuple[bool, str]:
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
            problems.append(f"Ligne {idx} : pas de case cochée explicite (`[x]`) — {text[:200]}")
    if problems:
        return False, "Critères de fait : preuve insuffisante.\n\n" + "\n".join(f"- {p}" for p in problems)
    return True, ""


def wea_criteria_gate(pr_body: str, linear_issue_description: str | None) -> tuple[bool, str]:
    """
    Done if either the PR or the Linear issue has ## Critères de fait with every bullet [x].
    (You can tick only on Linear after sync, or only in the PR, or both.)
    """
    pr_lines = extract_criteria_section_lines(pr_body)
    lin_lines = extract_criteria_section_lines(linear_issue_description or "")

    pr_has = pr_lines is not None and len(pr_lines) > 0
    lin_has = lin_lines is not None and len(lin_lines) > 0

    msg_pr = ""
    msg_lin = ""
    if pr_has:
        ok_pr, msg_pr = validate_criteria_bullet_lines(pr_lines)
        if ok_pr:
            return True, ""
    if lin_has:
        ok_lin, msg_lin = validate_criteria_bullet_lines(lin_lines)
        if ok_lin:
            return True, ""

    if not pr_has and not lin_has:
        return False, (
            "Aucune section `## Critères de fait` avec puces ni dans la PR ni sur le ticket Linear. "
            "Ajoutez la section sur Linear ; le workflow « sync » peut la recopier dans la PR."
        )

    parts: list[str] = []
    if pr_has:
        parts.append(f"**PR** : {msg_pr}")
    else:
        parts.append("**PR** : pas de section `## Critères de fait` avec puces (ou section vide).")
    if lin_has:
        parts.append(f"**Linear** : {msg_lin}")
    else:
        parts.append("**Linear** : pas de section `## Critères de fait` avec puces (ou section vide).")
    return False, "\n\n".join(parts)


def strip_auto_criteria_blocks(body: str) -> str:
    """Remove previously injected sync blocks (any issue id)."""
    pattern = re.compile(
        r"<!-- linear-auto:criteria:begin [A-Z0-9]+-\d+ -->\r?\n"
        r".*?"
        r"<!-- linear-auto:criteria:end [A-Z0-9]+-\d+ -->\r?\n?",
        re.DOTALL,
    )
    return pattern.sub("", body or "")


def team_completed_state_id(api_key: str, team_key: str) -> str | None:
    data = linear_request(
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


def issue_internal_id(api_key: str, identifier: str, team_key: str, number: int) -> str | None:
    data = linear_request(
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

    data = linear_request(
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


def issue_fetch_description(api_key: str, issue_uuid: str) -> str | None:
    data = linear_request(
        api_key,
        """
        query IssueDesc($id: String!) {
          issue(id: $id) {
            description
          }
        }
        """,
        {"id": issue_uuid},
    )
    issue = data.get("issue") or {}
    desc = issue.get("description")
    return desc if isinstance(desc, str) else None


def issue_update_done(api_key: str, issue_uuid: str, state_id: str) -> tuple[bool, str]:
    data = linear_request(
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


def comment_create(api_key: str, issue_uuid: str, body: str) -> tuple[bool, str]:
    data = linear_request(
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
