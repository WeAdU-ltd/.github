#!/usr/bin/env python3
"""
On pull_request opened/reopened/synchronize: inject or refresh a "## Critères de fait" block
from each linked Linear WEA-* issue into the PR body (GitHub API).

Uses GITHUB_EVENT_PATH + GITHUB_TOKEN (default in Actions). Requires LINEAR_API_KEY.

The injected block is wrapped in HTML comments so it can be replaced idempotently.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

_scripts_dir = str(Path(__file__).resolve().parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from linear_pr_common import (
    collect_pr_identifier_sources,
    extract_criteria_section_raw,
    extract_identifiers_from_text,
    issue_fetch_description,
    issue_internal_id,
)


def _has_auto_block(body: str, issue_id: str) -> bool:
    return f"<!-- linear-auto:criteria:begin {issue_id} -->" in (body or "")


def _github_request(method: str, url: str, token: str, body: dict[str, Any] | None = None) -> Any:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "weadu-linear-sync-pr-criteria",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        raise RuntimeError(f"GitHub HTTP {e.code}: {detail}") from e


def _build_block(issue_id: str, section_md: str) -> str:
    inner = section_md.strip()
    if not inner:
        return ""
    return (
        f"<!-- linear-auto:criteria:begin {issue_id} -->\n"
        f"{inner}\n"
        f"<!-- linear-auto:criteria:end {issue_id} -->\n"
    )


def main() -> int:
    api_key = os.environ.get("LINEAR_API_KEY", "").strip()
    if not api_key:
        print("linear_sync_pr_criteria: LINEAR_API_KEY not set; skipping.", file=sys.stderr)
        return 0

    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        print("linear_sync_pr_criteria: GITHUB_TOKEN missing.", file=sys.stderr)
        return 1

    event_path = os.environ.get("GITHUB_EVENT_PATH", "").strip()
    if not event_path:
        print("linear_sync_pr_criteria: GITHUB_EVENT_PATH missing.", file=sys.stderr)
        return 1

    with open(event_path, encoding="utf-8") as f:
        event = json.load(f)

    pr = event.get("pull_request") or {}
    if pr.get("draft"):
        print("linear_sync_pr_criteria: draft PR; skip.")
        return 0

    repo = event.get("repository") or {}
    full_name = repo.get("full_name")
    if not full_name:
        print("linear_sync_pr_criteria: repository.full_name missing.", file=sys.stderr)
        return 1

    pr_number = pr.get("number")
    if pr_number is None:
        print("linear_sync_pr_criteria: pull_request.number missing.", file=sys.stderr)
        return 1

    seen: set[str] = set()
    identifiers: list[str] = []
    for chunk in collect_pr_identifier_sources(pr):
        for ident in extract_identifiers_from_text(chunk):
            if ident not in seen:
                seen.add(ident)
                identifiers.append(ident)

    wea_ids = [i for i in identifiers if i.startswith("WEA-")]
    if not wea_ids:
        print("linear_sync_pr_criteria: no WEA-* in branch/title; nothing to do.")
        return 0

    blocks: list[str] = []
    for ident in wea_ids:
        m = re.match(r"^WEA-(\d+)$", ident)
        if not m:
            continue
        number = int(m.group(1))
        issue_uuid = issue_internal_id(api_key, ident, "WEA", number)
        if not issue_uuid:
            print(f"linear_sync_pr_criteria: issue not found: {ident}", file=sys.stderr)
            continue
        if _has_auto_block(body, ident):
            print(f"linear_sync_pr_criteria: auto block already present for {ident}; skip.")
            continue
        desc = issue_fetch_description(api_key, issue_uuid) or ""
        raw = extract_criteria_section_raw(desc)
        if not raw:
            print(f"linear_sync_pr_criteria: no ## Critères de fait on Linear for {ident}; skip block.")
            continue
        blocks.append(_build_block(ident, raw))

    if not blocks:
        print("linear_sync_pr_criteria: nothing to inject.")
        return 0

    note = (
        "\n---\n"
        "*Bloc ci-dessous synchronisé depuis Linear (workflow). "
        "Cochez les critères sur le ticket **ou** dans la PR ; le merge Done automatique accepte l’un ou l’autre.*\n"
    )
    new_body = (body.rstrip() + "\n\n" + note + "\n".join(blocks).rstrip() + "\n").strip() + "\n"

    if new_body.strip() == (body or "").strip():
        print("linear_sync_pr_criteria: PR body already up to date; skip PATCH.")
        return 0

    url = f"https://api.github.com/repos/{full_name}/pulls/{pr_number}"
    _github_request("PATCH", url, token, {"body": new_body})
    print(f"linear_sync_pr_criteria: updated PR #{pr_number} body ({len(blocks)} new block(s)).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as e:
        print(f"linear_sync_pr_criteria: {e}", file=sys.stderr)
        raise SystemExit(1) from e

