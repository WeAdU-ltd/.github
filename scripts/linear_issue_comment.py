#!/usr/bin/env python3
"""
Post a Markdown comment on a Linear issue by identifier (e.g. WEA-43).

Uses LINEAR_API_KEY (same as scripts/linear_pr_common.py). Reads body from
stdin by default, or from --file.

Examples:
  printf '%s\\n' 'Hello' | python3 scripts/linear_issue_comment.py WEA-43
  python3 scripts/linear_issue_comment.py WEA-43 --file /tmp/note.md

Agents must use this instead of asking the human to paste into Linear.
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


def main() -> int:
    ap = argparse.ArgumentParser(description="Post a comment on a Linear issue.")
    ap.add_argument("issue", help="Linear identifier, e.g. WEA-43")
    ap.add_argument(
        "-f",
        "--file",
        help="Read comment body from file (default: stdin)",
    )
    args = ap.parse_args()

    api_key = os.environ.get("LINEAR_API_KEY", "").strip()
    if not api_key:
        print("linear_issue_comment: LINEAR_API_KEY not set.", file=sys.stderr)
        return 1

    ident = args.issue.strip().upper()
    if "-" not in ident:
        print("linear_issue_comment: expected identifier like WEA-43", file=sys.stderr)
        return 1
    team_key, num_s = ident.split("-", 1)
    try:
        num = int(num_s)
    except ValueError:
        print("linear_issue_comment: invalid issue number", file=sys.stderr)
        return 1

    body = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
    body = body.strip()
    if not body:
        print("linear_issue_comment: empty body", file=sys.stderr)
        return 1

    issue_uuid = issue_internal_id(api_key, ident, team_key, num)
    if not issue_uuid:
        print(f"linear_issue_comment: issue {ident} not found", file=sys.stderr)
        return 1

    ok, msg = comment_create(api_key, issue_uuid, body)
    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
