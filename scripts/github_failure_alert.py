#!/usr/bin/env python3
"""
Alert on GitHub Actions failures: Slack (optional) + GitHub issue (optional).

Modes:
  1) Event mode (workflow_run): reads GITHUB_EVENT_PATH (standard Actions).
  2) Poll mode (--poll): scans recent failed runs on this repo or whole org.

Secrets (optional): SLACK_CI_ALERT_WEBHOOK_URL (Incoming Webhook).
Org-wide poll: GH_ORG_READ_TOKEN (fine-grained PAT: Actions read + metadata on org repos).
Issues are opened in GITHUB_FAILURE_TRIAGE_REPO (default: current repo) so one `GITHUB_TOKEN`
can triage failures from any detected repo.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

# Allowlist of workflow *names* (must match `name:` in each workflow file)
DEFAULT_WATCH_NAMES = frozenset(
    {
        "CI",
        "Gmail smoke (WEA-24)",
        "Linear sync PR criteria",
        "PR merge status",
        "Auto-merge PR",
        "Linear Done on merge",
    }
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_github_time(s: str) -> datetime:
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s)


def api_get(url: str, token: str) -> Any:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def api_post_json(url: str, token: str, body: dict[str, Any]) -> tuple[int, bytes]:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def slack_webhook(webhook_url: str, text: str) -> None:
    payload = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status >= 400:
            raise RuntimeError(f"Slack webhook HTTP {resp.status}")


def create_issue_if_needed(
    token: str,
    triage_repo: str,
    title: str,
    body: str,
    dedupe_run_id: str | int,
) -> bool:
    """Return True if a new issue was created. Dedupe by run id in search query."""
    rid = str(dedupe_run_id)
    q = urllib.parse.quote(f"repo:{triage_repo} is:issue is:open {rid}")
    search_url = f"https://api.github.com/search/issues?q={q}"
    try:
        data = api_get(search_url, token)
    except urllib.error.HTTPError:
        data = {"items": []}
    items = data.get("items") if isinstance(data, dict) else []
    if isinstance(items, list) and len(items) > 0:
        print(f"Dedupe: issue already open mentioning run {rid}", file=sys.stderr)
        return False

    status, raw = api_post_json(
        f"https://api.github.com/repos/{triage_repo}/issues",
        token,
        {"title": title, "body": body},
    )
    if status not in (200, 201):
        print(f"Create issue failed HTTP {status}: {raw[:1200]!r}", file=sys.stderr)
        return False
    print(f"Created GitHub issue on {triage_repo}.", file=sys.stderr)
    return True


def triage_repo_from_env() -> str:
    return (
        os.environ.get("GITHUB_FAILURE_TRIAGE_REPO", "").strip()
        or os.environ.get("GITHUB_REPOSITORY", "").strip()
    )


def handle_workflow_run_event() -> int:
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path or not os.path.isfile(path):
        print("GITHUB_EVENT_PATH missing", file=sys.stderr)
        return 1
    with open(path, encoding="utf-8") as f:
        event = json.load(f)
    wr = event.get("workflow_run") or {}
    if wr.get("conclusion") != "failure":
        print("Not a failure conclusion; skipping.", file=sys.stderr)
        return 0

    name = wr.get("name") or "unknown-workflow"
    if name not in DEFAULT_WATCH_NAMES:
        print(f"Ignoring unwatched workflow {name!r}", file=sys.stderr)
        return 0

    html_url = wr.get("html_url") or ""
    repo = wr.get("repository", {})
    full_name = repo.get("full_name") or os.environ.get("GITHUB_REPOSITORY", "")
    branch = wr.get("head_branch") or ""
    title_run = wr.get("display_title") or wr.get("name") or ""
    run_id = wr.get("id")

    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        print("GITHUB_TOKEN missing", file=sys.stderr)
        return 1

    triage = triage_repo_from_env()
    if not triage:
        print("No triage repo (GITHUB_FAILURE_TRIAGE_REPO / GITHUB_REPOSITORY)", file=sys.stderr)
        return 1

    slack_url = os.environ.get("SLACK_CI_ALERT_WEBHOOK_URL", "").strip()
    msg = (
        f":rotating_light: *GitHub Actions failure*\n"
        f"*Repo:* `{full_name}`\n"
        f"*Workflow:* `{name}`\n"
        f"*Branch:* `{branch}`\n"
        f"*Run:* {title_run}\n"
        f"{html_url}\n"
        f"_Réaction agent : logs → correctif ou `gh run rerun {run_id} --repo {full_name}`._"
    )
    if slack_url:
        try:
            slack_webhook(slack_url, msg)
            print("Slack notification sent.", file=sys.stderr)
        except OSError as e:
            print(f"Slack failed: {e}", file=sys.stderr)

    skip_issue = os.environ.get("GITHUB_FAILURE_SKIP_ISSUE", "").strip() in ("1", "true", "yes")
    if skip_issue:
        return 0

    issue_title = f"[Actions] {name} failed — `{full_name}` @ {branch}"
    issue_body = (
        f"Échec workflow (alerte automatique).\n\n"
        f"- **Dépôt source:** `{full_name}`\n"
        f"- **Workflow:** `{name}`\n"
        f"- **Branche:** `{branch}`\n"
        f"- **Run ID:** `{run_id}`\n"
        f"- **Lien:** {html_url}\n\n"
        f"### Déblocage\n"
        f"```\ngh run view {run_id} --repo {full_name}\ngh run rerun {run_id} --repo {full_name}\n```\n"
    )
    create_issue_if_needed(token, triage, issue_title, issue_body, run_id or "")
    return 0


def poll_repo_failures(
    token: str,
    repo_full: str,
    lookback_min: int,
    watch_names: frozenset[str],
) -> list[dict[str, Any]]:
    cutoff = utc_now().timestamp() - lookback_min * 60
    url = (
        f"https://api.github.com/repos/{repo_full}/actions/runs"
        f"?per_page=30&status=completed"
    )
    data = api_get(url, token)
    runs = data.get("workflow_runs") if isinstance(data, dict) else None
    if not isinstance(runs, list):
        return []

    bad: list[dict[str, Any]] = []
    for r in runs:
        if r.get("conclusion") != "failure":
            continue
        created = r.get("created_at") or ""
        try:
            ts = parse_github_time(created).timestamp()
        except ValueError:
            continue
        if ts < cutoff:
            continue
        wname = r.get("name") or ""
        if wname not in watch_names:
            continue
        bad.append(r)
    return bad


def poll_org_repos(org: str, token: str) -> list[str]:
    repos: list[str] = []
    page = 1
    while True:
        url = f"https://api.github.com/orgs/{org}/repos?per_page=100&page={page}"
        data = api_get(url, token)
        if not isinstance(data, list) or len(data) == 0:
            break
        for r in data:
            if isinstance(r, dict) and r.get("full_name"):
                repos.append(str(r["full_name"]))
        if len(data) < 100:
            break
        page += 1
        if page > 50:
            break
    return repos


def handle_poll(args: argparse.Namespace) -> int:
    issue_token = os.environ.get("GITHUB_TOKEN", "").strip()
    org_token = os.environ.get("GH_ORG_READ_TOKEN", "").strip()
    lookback = int(os.environ.get("ALERT_LOOKBACK_MIN", "15"))

    slack_url = os.environ.get("SLACK_CI_ALERT_WEBHOOK_URL", "").strip()
    skip_issue = os.environ.get("GITHUB_FAILURE_SKIP_ISSUE", "").strip() in ("1", "true", "yes")
    triage = triage_repo_from_env()
    if not triage:
        print("GITHUB_FAILURE_TRIAGE_REPO or GITHUB_REPOSITORY required", file=sys.stderr)
        return 1

    org = (args.org or os.environ.get("GITHUB_ORG", "WeAdU-ltd")).strip()

    if org_token:
        repos = poll_org_repos(org, org_token)
        token_for_runs = org_token
    else:
        try:
            repos = poll_org_repos(org, issue_token)
            token_for_runs = issue_token
        except (urllib.error.HTTPError, OSError) as e:
            print(f"Org list failed ({e}); scanning current repo only.", file=sys.stderr)
            repo = os.environ.get("GITHUB_REPOSITORY")
            if not repo:
                return 1
            repos = [repo]
            token_for_runs = issue_token

    if not issue_token:
        print("GITHUB_TOKEN missing (needed for triage issues)", file=sys.stderr)
        return 1

    found_any = False
    for full_name in repos:
        try:
            failures = poll_repo_failures(
                token_for_runs, full_name, lookback, DEFAULT_WATCH_NAMES
            )
        except (urllib.error.HTTPError, OSError) as e:
            print(f"Skip {full_name}: {e}", file=sys.stderr)
            continue
        for r in failures:
            found_any = True
            name = r.get("name") or "?"
            html_url = r.get("html_url") or ""
            branch = r.get("head_branch") or ""
            run_id = r.get("id")
            msg = (
                f":rotating_light: *GitHub Actions failure (poll ≤{lookback}min)*\n"
                f"*Repo:* `{full_name}`\n"
                f"*Workflow:* `{name}`\n"
                f"*Branch:* `{branch}`\n"
                f"{html_url}\n"
            )
            if slack_url:
                try:
                    slack_webhook(slack_url, msg)
                except OSError as e:
                    print(f"Slack failed: {e}", file=sys.stderr)

            if not skip_issue:
                issue_title = f"[Actions] {name} failed — `{full_name}` @ {branch} [poll]"
                body = (
                    f"Détecté par poll de secours (≤{lookback} min).\n\n"
                    f"- **Dépôt source:** `{full_name}`\n"
                    f"- **Workflow:** `{name}`\n"
                    f"- **Run ID:** `{run_id}`\n"
                    f"- **Lien:** {html_url}\n\n"
                    f"```\ngh run rerun {run_id} --repo {full_name}\n```\n"
                )
                create_issue_if_needed(issue_token, triage, issue_title, body, run_id or "")
            print(f"Alerted: {full_name} run {run_id}", file=sys.stderr)

    if not found_any:
        print(f"No failures in last {lookback} min (watch list).", file=sys.stderr)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--poll",
        action="store_true",
        help="Poll API instead of workflow_run event",
    )
    parser.add_argument(
        "--org",
        default="",
        help="Organization to scan (with GH_ORG_READ_TOKEN); default WeAdU-ltd",
    )
    args = parser.parse_args()

    if args.poll:
        return handle_poll(args)

    return handle_workflow_run_event()


if __name__ == "__main__":
    raise SystemExit(main())
