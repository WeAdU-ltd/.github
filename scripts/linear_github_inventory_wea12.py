#!/usr/bin/env python3
"""
WEA-12 — Croise les labels Linear du groupe parent « repo » avec GitHub,
liste les dépôts sans label correspondant et les tickets ouverts récents sans enfant « repo ».

Variables d'environnement :
  LINEAR_API_KEY   — jeton API Linear (obligatoire)
  GITHUB_TOKEN     — PAT GitHub avec lecture org/repos (obligatoire)
  LINEAR_TEAM_KEY  — clé d'équipe Linear (défaut : WEA)

Contenu aligné sur la proposition Negative-Terms#638 (ticket WEA-12).

Option --markdown-label-prefix : restreindre le tableau des labels dans le MD
(ex. WeAdU-ltd/) tout en gardant tous les labels pour les tickets sans repo.
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

LINEAR_GRAPHQL = "https://api.linear.app/graphql"
GITHUB_API = "https://api.github.com"

BEGIN_MARKER = "<!-- WEA12_INVENTORY_BEGIN -->"
END_MARKER = "<!-- WEA12_INVENTORY_END -->"


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


def _github_request(token: str, path: str, params: list[tuple[str, str]] | None = None) -> Any:
    url = GITHUB_API.rstrip("/") + path
    if params:
        from urllib.parse import urlencode

        url += "?" + urlencode(params)
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        raise RuntimeError(f"GitHub HTTP {e.code} {path}: {detail}") from e


def _linear_repo_parent_id(api_key: str) -> str | None:
    """Retourne l'id du label parent nommé « repo », ou None."""
    data = _linear_request(
        api_key,
        """
        query RepoParentLabel {
          issueLabels(filter: { name: { eq: "repo" } }, first: 10) {
            nodes { id name }
          }
        }
        """,
    )
    nodes = (data.get("issueLabels") or {}).get("nodes") or []
    for n in nodes:
        if (n.get("name") or "").strip().lower() == "repo":
            return n["id"]
    return None


def _linear_repo_child_labels(api_key: str, parent_id: str) -> list[dict[str, str]]:
    """Labels enfants du groupe repo (nom attendu : owner/repo)."""
    out: list[dict[str, str]] = []
    cursor: str | None = None
    while True:
        data = _linear_request(
            api_key,
            """
            query RepoChildren($parentId: ID!, $after: String) {
              issueLabels(
                filter: { parent: { id: { eq: $parentId } } }
                first: 100
                after: $after
              ) {
                pageInfo { hasNextPage endCursor }
                nodes { id name }
              }
            }
            """,
            {"parentId": parent_id, "after": cursor},
        )
        conn = data.get("issueLabels") or {}
        for n in conn.get("nodes") or []:
            name = (n.get("name") or "").strip()
            if "/" in name:
                out.append({"id": n["id"], "name": name})
        page = conn.get("pageInfo") or {}
        if not page.get("hasNextPage"):
            break
        cursor = page.get("endCursor")
    return sorted(out, key=lambda x: x["name"].lower())


def _linear_open_issues_without_repo_child(
    api_key: str,
    team_key: str,
    repo_child_label_ids: set[str],
    max_issues: int,
) -> list[dict[str, str]]:
    """Tickets ouverts de l'équipe sans label enfant du groupe repo (par id)."""
    rows: list[dict[str, str]] = []
    cursor: str | None = None
    while len(rows) < max_issues:
        data = _linear_request(
            api_key,
            """
            query TeamIssues($teamKey: String!, $after: String) {
              teams(filter: { key: { eq: $teamKey } }) {
                nodes {
                  issues(
                    first: 50
                    after: $after
                    filter: {
                      state: { type: { nin: ["completed", "canceled"] } }
                    }
                  ) {
                    pageInfo { hasNextPage endCursor }
                    nodes {
                      identifier
                      title
                      updatedAt
                      labels { nodes { id } }
                    }
                  }
                }
              }
            }
            """,
            {"teamKey": team_key, "after": cursor},
        )
        teams_conn = (data.get("teams") or {}).get("nodes") or []
        if not teams_conn:
            raise RuntimeError(f"Aucune équipe Linear avec la clé « {team_key} ».")
        conn = (teams_conn[0].get("issues") or {}) if teams_conn else {}
        for node in conn.get("nodes") or []:
            labels = ((node.get("labels") or {}).get("nodes")) or []
            has_repo_child = any(
                (lab.get("id") or "") in repo_child_label_ids for lab in labels
            )
            if not has_repo_child:
                rows.append(
                    {
                        "identifier": node.get("identifier") or "",
                        "title": (node.get("title") or "").replace("|", "\\|"),
                        "updatedAt": node.get("updatedAt") or "",
                    }
                )
                if len(rows) >= max_issues:
                    break
        page = conn.get("pageInfo") or {}
        if not page.get("hasNextPage"):
            break
        cursor = page.get("endCursor")
    rows.sort(key=lambda r: r.get("updatedAt") or "", reverse=True)
    return rows[:max_issues]


def _github_list_org_repos(token: str, org: str) -> list[str]:
    names: list[str] = []
    page = 1
    while True:
        chunk = _github_request(
            token,
            f"/orgs/{urllib.parse.quote(org, safe='')}/repos",
            [("per_page", "100"), ("page", str(page)), ("type", "all")],
        )
        if not isinstance(chunk, list) or not chunk:
            break
        for repo in chunk:
            fn = repo.get("full_name")
            if fn:
                names.append(fn)
        if len(chunk) < 100:
            break
        page += 1
    return sorted(set(names), key=str.lower)


def _orgs_from_labels(labels: list[dict[str, str]]) -> list[str]:
    owners: set[str] = set()
    for lb in labels:
        name = lb.get("name", "")
        if "/" in name:
            owners.add(name.split("/", 1)[0].strip())
    return sorted(owners)


def _build_markdown_tables(
    repo_labels: list[dict[str, str]],
    github_orgs: list[str],
    missing_repo_labels: list[str],
    orphan_issues: list[dict[str, str]],
    generated_at: str,
    markdown_label_prefix: str | None = None,
) -> str:
    lines: list[str] = []
    lines.append("")
    lines.append(f"_Généré le {generated_at} (UTC)._")
    if markdown_label_prefix:
        lines.append(
            f"_Tableau des labels `repo` **filtré** : noms commençant par `{markdown_label_prefix}` "
            "(périmètre société WeAdU-ltd). Les calculs « dépôts sans label » et « tickets sans repo » "
            "restent basés sur **tous** les enfants du groupe `repo` dans Linear._"
        )
    lines.append("")
    lines.append("### Labels Linear (groupe `repo`) → dépôt GitHub")
    lines.append("")
    lines.append("| Label Linear (`owner/repo`) | URL GitHub |")
    lines.append("|----------------------------|------------|")
    table_labels = repo_labels
    if markdown_label_prefix:
        pfx = markdown_label_prefix.strip()
        table_labels = [lb for lb in repo_labels if (lb.get("name") or "").startswith(pfx)]
    for lb in table_labels:
        name = lb["name"]
        url = f"https://github.com/{name}"
        lines.append(f"| `{name}` | {url} |")
    if len(table_labels) == 0:
        lines.append("| — | — |")
    lines.append("")
    lines.append("### Dépôts GitHub sans label Linear correspondant")
    lines.append("")
    lines.append(f"_Organisations scannées : {', '.join(github_orgs) or '—'}._")
    lines.append("")
    lines.append("| Dépôt | Note |")
    lines.append("|-------|------|")
    for full in missing_repo_labels:
        lines.append(f"| `{full}` | Aucun label enfant `repo` avec ce nom exact |")
    if not missing_repo_labels:
        lines.append("| — | Aucun trou dans le périmètre scanné |")
    lines.append("")
    lines.append("### Tickets Linear ouverts (équipe configurée), sans sous-label `repo`")
    lines.append("")
    lines.append("| Issue | Mis à jour | Titre |")
    lines.append("|-------|------------|-------|")
    for row in orphan_issues:
        ident = row["identifier"]
        url = f"https://linear.app/weadu/issue/{ident}"
        updated = row.get("updatedAt", "")[:10]
        title = row.get("title", "")[:120]
        lines.append(f"| [{ident}]({url}) | {updated} | {title} |")
    if not orphan_issues:
        lines.append("| — | — | — |")
    lines.append("")
    return "\n".join(lines)


def _inject_into_doc(template: str, generated_block: str) -> str:
    if BEGIN_MARKER not in template or END_MARKER not in template:
        raise ValueError(
            f"Le fichier doit contenir {BEGIN_MARKER} et {END_MARKER} pour insertion."
        )
    before, rest = template.split(BEGIN_MARKER, 1)
    _, after = rest.split(END_MARKER, 1)
    return before + BEGIN_MARKER + generated_block + END_MARKER + after


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventaire WEA-12 Linear ↔ GitHub")
    parser.add_argument(
        "-o",
        "--output",
        default="docs/GITHUB_LINEAR_INVENTORY_WEA12.md",
        help="Fichier markdown à mettre à jour (défaut: docs/GITHUB_LINEAR_INVENTORY_WEA12.md)",
    )
    parser.add_argument(
        "--github-org",
        action="append",
        default=[],
        metavar="ORG",
        help="Organisation GitHub à scanner (répétable). Sinon déduit des labels repo.",
    )
    parser.add_argument(
        "--team-key",
        default=os.environ.get("LINEAR_TEAM_KEY", "WEA"),
        help="Clé d'équipe Linear (défaut: env LINEAR_TEAM_KEY ou WEA)",
    )
    parser.add_argument(
        "--max-issues",
        type=int,
        default=50,
        help="Nombre max de tickets sans repo à lister (défaut: 50)",
    )
    parser.add_argument(
        "--markdown-label-prefix",
        default=None,
        metavar="PREFIX",
        help=(
            "Si défini (ex. WeAdU-ltd/), le tableau « Labels repo » du markdown "
            "ne liste que les labels dont le nom commence par ce préfixe. "
            "Les autres calculs utilisent toujours tous les labels enfants `repo`."
        ),
    )
    args = parser.parse_args()

    linear_key = os.environ.get("LINEAR_API_KEY", "").strip()
    gh_token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not linear_key:
        print("Erreur: définir LINEAR_API_KEY.", file=sys.stderr)
        return 1
    if not gh_token:
        print("Erreur: définir GITHUB_TOKEN.", file=sys.stderr)
        return 1

    parent_id = _linear_repo_parent_id(linear_key)
    if not parent_id:
        print(
            "Impossible de trouver le label parent nommé « repo » dans Linear.",
            file=sys.stderr,
        )
        return 1

    repo_labels = _linear_repo_child_labels(linear_key, parent_id)
    label_names = {lb["name"] for lb in repo_labels}

    github_orgs = args.github_org if args.github_org else _orgs_from_labels(repo_labels)
    if not github_orgs:
        print(
            "Aucune organisation GitHub : passez --github-org WeAdU-ltd ou créez des labels repo owner/repo.",
            file=sys.stderr,
        )
        return 1

    all_full_names: list[str] = []
    for org in github_orgs:
        try:
            all_full_names.extend(_github_list_org_repos(gh_token, org))
        except RuntimeError as e:
            print(f"Avertissement ({org}): {e}", file=sys.stderr)

    missing = sorted({r for r in all_full_names if r not in label_names}, key=str.lower)

    repo_child_ids = {lb["id"] for lb in repo_labels}
    orphan_issues = _linear_open_issues_without_repo_child(
        linear_key, args.team_key, repo_child_ids, args.max_issues
    )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    block = _build_markdown_tables(
        repo_labels,
        github_orgs,
        missing,
        orphan_issues,
        now,
        markdown_label_prefix=args.markdown_label_prefix,
    )

    out_path = args.output
    try:
        with open(out_path, encoding="utf-8") as f:
            template = f.read()
    except FileNotFoundError:
        template = (
            f"# Inventaire WEA-12\n\n{BEGIN_MARKER}\n\n{END_MARKER}\n"
        )

    new_doc = _inject_into_doc(template, "\n" + block + "\n")
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(new_doc)

    print(f"Écrit : {out_path}")
    print(f"  Labels repo : {len(repo_labels)}")
    print(f"  Dépôts sans label : {len(missing)}")
    print(f"  Tickets sans repo : {len(orphan_issues)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
