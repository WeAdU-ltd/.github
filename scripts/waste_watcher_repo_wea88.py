#!/usr/bin/env python3
"""
WEA-88 — Create or confirm WeAdU-ltd/waste-watcher, bootstrap WEA-35 minimal socle, align Linear.

Prerequisites (when using --apply):
  GITHUB_TOKEN or GH_TOKEN — PAT/app token with repo create + push on WeAdU-ltd/waste-watcher
  LINEAR_API_KEY — Linear API (comment + issue update + label)

Default is dry-run (no GitHub/Linear writes).

Examples:
  python3 scripts/waste_watcher_repo_wea88.py
  python3 scripts/waste_watcher_repo_wea88.py --apply
  python3 scripts/waste_watcher_repo_wea88.py --apply --skip-github
  python3 scripts/waste_watcher_repo_wea88.py --apply --skip-linear
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

_scripts_dir = str(Path(__file__).resolve().parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from linear_pr_common import comment_create, issue_internal_id, linear_request  # noqa: E402

ORG = "WeAdU-ltd"
REPO = "waste-watcher"
FULL = f"{ORG}/{REPO}"
REPO_URL = f"https://github.com/{ORG}/{REPO}"
ISSUE_IDENT = "WEA-88"  # Repl #8 — Waste Watcher
TEAM_KEY = "WEA"
ISSUE_NUM = 88
LABEL_DOT_GITHUB_ID = "0d0f8c49-8e38-4889-82a5-3f38534743b5"
REPO_LABEL_NAME = FULL


def _gh_token() -> str:
    for key in (
        "GITHUB_ORG_REPO_CREATE_TOKEN",
        "GITHUB_TOKEN",
        "GH_TOKEN",
        "GH_ORG_READ_TOKEN",
    ):
        val = os.environ.get(key, "").strip()
        if val:
            return val
    return ""


def _run(cmd: list[str], *, env: dict[str, str] | None = None, cwd: str | None = None) -> None:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    token = _gh_token()
    if token:
        merged["GH_TOKEN"] = token
        merged["GITHUB_TOKEN"] = token
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, env=merged, cwd=cwd)


def github_repo_exists() -> bool:
    token = _gh_token()
    if not token:
        return False
    import urllib.error
    import urllib.request

    req = urllib.request.Request(
        f"https://api.github.com/repos/{FULL}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise


def github_create_repo(apply: bool) -> bool:
    if github_repo_exists():
        print(f"GitHub: {REPO_URL} already exists.")
        return True
    if not apply:
        print(f"GitHub: would create private repo {FULL}")
        return False
    token = _gh_token()
    if not token:
        print("GitHub: no GITHUB_TOKEN/GH_TOKEN — cannot create repo.", file=sys.stderr)
        return False
    try:
        _run(
            [
                "gh",
                "repo",
                "create",
                FULL,
                "--private",
                "--description",
                "Waste Watcher / Waste Controller — migration Replit (WEA-88, WEA-33 #8)",
            ]
        )
    except subprocess.CalledProcessError:
        print(
            "GitHub: createRepository refused (enable org Actions repo creation "
            "or set GITHUB_ORG_REPO_CREATE_TOKEN with admin:org / repo create).",
            file=sys.stderr,
        )
        return github_repo_exists()
    return github_repo_exists()


def github_bootstrap_socle(apply: bool) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    init_script = repo_root / "scripts" / "init_wea35_socle_template.sh"
    if not init_script.is_file():
        raise FileNotFoundError(init_script)

    if not apply:
        print("GitHub: would bootstrap WEA-35 minimal + README on main")
        return

    if not github_repo_exists():
        raise RuntimeError(f"Repo {FULL} missing — create first.")

    with tempfile.TemporaryDirectory(prefix="wea88-waste-watcher-") as tmp:
        tmp_path = Path(tmp)
        _run(["git", "clone", f"https://github.com/{FULL}.git", str(tmp_path / "repo")])
        work = tmp_path / "repo"
        _run(["bash", str(init_script), str(work)], cwd=str(repo_root))

        readme = work / "README.md"
        readme.write_text(
            f"""# Waste Watcher (Waste Controller)

Application **Google Ads waste control** — migration depuis Replit (*Waste Watcher*, inventaire [WEA-33 #8](https://github.com/WeAdU-ltd/.github/blob/main/docs/inventory/WEA-33-replit-inventory.md)).

- **Prod actuelle (2026-05)** : `waste-controller.replit.app` (autoscale) — voir cutover [WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents).
- **Export Repl** : [`waste-watcher-replit-export-2026-05-26.md`](https://github.com/WeAdU-ltd/.github/blob/main/docs/inventory/waste-watcher-replit-export-2026-05-26.md) dans `WeAdU-ltd/.github`.
- **Linear dépôt** : [WEA-88](https://linear.app/weadu/issue/WEA-88/waste-watcher-depot-github-wead-u-ltd-cree-ou-confirme).

## Run local (depuis l'export Repl)

```bash
pnpm --filter @workspace/api-server run dev
pnpm --filter @workspace/waste-controller run dev
```

Stack : Node 24, pnpm monorepo, React 19 + Vite, Express 5, PostgreSQL 16 (Drizzle). Importer le code depuis le Repl avant prod hors Replit.

## Socle agent

Fichiers minimaux WEA-35 — doc complète : [WEA-35 template](https://github.com/WeAdU-ltd/.github/blob/main/docs/inventory/WEA-35-weadu-socle-v5-lab-template.md).
""",
            encoding="utf-8",
        )

        _run(["git", "add", "-A"], cwd=str(work))
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(work),
            capture_output=True,
            text=True,
            check=True,
        )
        if not status.stdout.strip():
            print("GitHub: bootstrap — nothing to commit (already present).")
            return
        _run(["git", "commit", "-m", "chore: WEA-35 minimal socle + README (WEA-88)"], cwd=str(work))
        _run(["git", "push", "origin", "HEAD:main"], cwd=str(work))


def _linear_repo_parent_id(api_key: str) -> str | None:
    data = linear_request(
        api_key,
        """
        query RepoParentLabel {
          issueLabels(filter: { name: { eq: "repo" } }, first: 10) {
            nodes { id name }
          }
        }
        """,
    )
    for n in (data.get("issueLabels") or {}).get("nodes") or []:
        if (n.get("name") or "").strip().lower() == "repo":
            return n["id"]
    return None


def _linear_label_id_by_name(api_key: str, name: str) -> str | None:
    data = linear_request(
        api_key,
        """
        query LabelByName($name: String!) {
          issueLabels(filter: { name: { eq: $name } }, first: 5) {
            nodes { id name }
          }
        }
        """,
        {"name": name},
    )
    nodes = (data.get("issueLabels") or {}).get("nodes") or []
    if nodes:
        return nodes[0]["id"]
    return None


def _linear_ensure_repo_label(api_key: str, apply: bool) -> str | None:
    existing = _linear_label_id_by_name(api_key, REPO_LABEL_NAME)
    if existing:
        print(f"Linear: label {REPO_LABEL_NAME} exists ({existing})")
        return existing
    if not apply:
        print(f"Linear: would create child label {REPO_LABEL_NAME}")
        return None
    parent_id = _linear_repo_parent_id(api_key)
    if not parent_id:
        print("Linear: parent label 'repo' not found.", file=sys.stderr)
        return None
    data = linear_request(
        api_key,
        """
        mutation CreateRepoLabel($input: IssueLabelCreateInput!) {
          issueLabelCreate(input: $input) {
            success
            issueLabel { id name }
          }
        }
        """,
        {
            "input": {
                "name": REPO_LABEL_NAME,
                "parentId": parent_id,
                "color": "#4cb782",
            }
        },
    )
    payload = data.get("issueLabelCreate") or {}
    if payload.get("success"):
        label = payload.get("issueLabel") or {}
        print(f"Linear: created label {label.get('name')} ({label.get('id')})")
        return label.get("id")
    print("Linear: issueLabelCreate failed.", file=sys.stderr)
    return None


def linear_align_issue(api_key: str, apply: bool, repo_confirmed: bool) -> bool:
    issue_uuid = issue_internal_id(api_key, ISSUE_IDENT, TEAM_KEY, ISSUE_NUM)
    if not issue_uuid:
        print(f"Linear: issue {ISSUE_IDENT} not found.", file=sys.stderr)
        return False

    repo_label_id = _linear_ensure_repo_label(api_key, apply)
    description_block = f"""## Dépôt GitHub (WEA-88)

| Champ | Valeur |
|-------|--------|
| **URL canonique** | **`{REPO_URL}`** |
| **Slug** | `{REPO}` (aligné inventaire *Waste Watcher*, UI *Waste Controller*) |
| **État** | {"**confirmé** (API GitHub)" if repo_confirmed else "*à créer* — exécuter `python3 scripts/waste_watcher_repo_wea88.py --apply` ou workflow `waste-watcher-repo-wea88.yml`"} |
| **Label Linear `repo`** | `{REPO_LABEL_NAME}` ([WEA-17](https://linear.app/weadu/issue/WEA-17/charte-agents-linear-source-interdits-features-nouveaux-projets)) |

## Critères de fait

- [x] URL `https://github.com/WeAdU-ltd/{REPO}` connue et notée sur ce ticket.
- [x] Label Linear groupe `repo` aligné : `{REPO_LABEL_NAME}`.

Runbook : [`waste-watcher-replit-migration-WEA-88.md`](https://github.com/WeAdU-ltd/.github/blob/main/docs/inventory/waste-watcher-replit-migration-WEA-88.md).
"""

    if not apply:
        print(f"Linear: would update {ISSUE_IDENT} description + labels + comment")
        return True

    label_ids: list[str] = []
    if repo_label_id:
        label_ids.append(repo_label_id)

    data = linear_request(
        api_key,
        """
        mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
          issueUpdate(id: $id, input: $input) {
            success
            issue { identifier }
          }
        }
        """,
        {
            "id": issue_uuid,
            "input": {
                "description": description_block,
                "labelIds": label_ids,
            },
        },
    )
    if not (data.get("issueUpdate") or {}).get("success"):
        print("Linear: issueUpdate failed.", file=sys.stderr)
        return False

    comment_body = f"""## WEA-88 — dépôt GitHub

- **URL** : {REPO_URL}
- **Label `repo`** : `{REPO_LABEL_NAME}`
- **Runbook** : https://github.com/WeAdU-ltd/.github/blob/main/docs/inventory/waste-watcher-replit-migration-WEA-88.md

Critères de fait couverts côté procédure ; suite migration : import code Repl ([WEA-36](https://linear.app/weadu/issue/WEA-36/replit-migration-vagues-repos-societe-agents)) / runbook §3.
"""
    ok, msg = comment_create(api_key, issue_uuid, comment_body)
    print(f"Linear: {msg}")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="WEA-88 waste-watcher GitHub repo + Linear alignment.")
    ap.add_argument("--apply", action="store_true", help="Perform writes (default: dry-run).")
    ap.add_argument("--skip-github", action="store_true")
    ap.add_argument("--skip-linear", action="store_true")
    args = ap.parse_args()

    repo_ok = github_repo_exists()
    if not args.skip_github:
        if not repo_ok:
            repo_ok = github_create_repo(args.apply)
        if repo_ok and args.apply:
            github_bootstrap_socle(args.apply)
    else:
        print("GitHub: skipped.")

    linear_done = args.skip_linear
    if not args.skip_linear:
        api_key = os.environ.get("LINEAR_API_KEY", "").strip()
        if not api_key:
            print("Linear: LINEAR_API_KEY not set in this session.", file=sys.stderr)
            if args.apply:
                return 1
        elif not linear_align_issue(api_key, args.apply, repo_ok):
            return 1
        else:
            linear_done = True

    if not args.apply:
        print("Dry-run complete. Re-run with --apply to execute.")
        return 0

    if repo_ok:
        print(f"Done: {REPO_URL}")
        return 0
    if linear_done:
        print(
            f"Linear updated; GitHub repo still missing — add GITHUB_ORG_REPO_CREATE_TOKEN "
            f"or create {REPO_URL} manually, then re-run.",
            file=sys.stderr,
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
