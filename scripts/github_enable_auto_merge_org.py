#!/usr/bin/env python3
"""
Enable GitHub « Allow auto-merge » on every repository in an organization.

Prerequisite for `gh pr merge --auto` / reusable workflow auto-merge across repos.
Requires `gh` CLI authenticated (`gh auth login`) with permission to admin repos.

Usage:
  gh auth login   # once
  python3 scripts/github_enable_auto_merge_org.py --org WeAdU-ltd
  python3 scripts/github_enable_auto_merge_org.py --org WeAdU-ltd --dry-run

Does not store secrets; uses your existing gh session.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys


def gh_json(args: list[str]) -> object:
    try:
        out = subprocess.check_output(["gh", *args], text=True)
    except subprocess.CalledProcessError as e:
        print(e.stderr or str(e), file=sys.stderr)
        raise SystemExit(1)
    if not out.strip():
        return []
    return json.loads(out)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="PATCH allow_auto_merge=true on all org repos via gh api.",
    )
    parser.add_argument(
        "--org",
        default="WeAdU-ltd",
        help="GitHub organization name (default: WeAdU-ltd)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions only, no PATCH.",
    )
    args = parser.parse_args()

    # Paginated list of repos (name + current flag)
    repos = gh_json(
        [
            "api",
            f"orgs/{args.org}/repos",
            "--paginate",
            "-q",
            "[.[] | {name: .name, full_name: .full_name, allow_auto_merge: .allow_auto_merge}]",
        ]
    )
    if not isinstance(repos, list):
        print("Unexpected API response", file=sys.stderr)
        return 1

    enabled = 0
    skipped = 0
    failed = 0
    for r in repos:
        name = r.get("name")
        full = r.get("full_name")
        already = r.get("allow_auto_merge")
        if not name or not full:
            continue
        if already is True:
            skipped += 1
            continue
        if args.dry_run:
            print(f"[dry-run] would enable auto-merge: {full}")
            enabled += 1
            continue
        try:
            subprocess.run(
                [
                    "gh",
                    "api",
                    f"repos/{full}",
                    "-X",
                    "PATCH",
                    "-f",
                    "allow_auto_merge=true",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"OK: allow_auto_merge enabled — {full}")
            enabled += 1
        except subprocess.CalledProcessError as e:
            err = (e.stderr or e.stdout or "").strip()
            if "403" in err or "not accessible" in err.lower():
                err += "\n  (Hint: use `gh auth login` with a user that has **admin** on the repo, not only a fine-grained token without admin.)"
            print(f"FAIL: {full} — {err}", file=sys.stderr)
            failed += 1

    print(
        f"Done: enabled={enabled}, already_on={skipped}, failed={failed}, total_repos={len(repos)}",
        file=sys.stderr,
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
