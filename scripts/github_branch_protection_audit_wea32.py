#!/usr/bin/env python3
"""
WEA-32 — Vérifie via l’API GitHub les règles de protection sur la branche par défaut
des dépôts d’une organisation (critère « règles appliquées sur au moins la branche principale »).

Variables d’environnement :
  GITHUB_TOKEN  — PAT ou token Actions avec lecture admin:org (repos) ou au minimum
                    lecture des règles de branche sur les dépôts ciblés.
  GITHUB_ORG_AUDIT_TOKEN — (optionnel, CI) si défini, utilisé **à la place** de
                    `GITHUB_TOKEN` pour l’audit org (secret d’organisation dédié WEA-42).

Usage typique (aligné sur WEA-12) :
  export GITHUB_TOKEN=...
  python3 scripts/github_branch_protection_audit_wea32.py --github-org WeAdU-ltd \\
    -o docs/GITHUB_BRANCH_PROTECTION_WEA32.md

Sans --fail : sortie 0 même si des dépôts manquent de protection (audit informatif).
Avec --fail : sortie 1 si au moins un dépôt n’a pas de règle de protection sur la branche par défaut.
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

GITHUB_API = "https://api.github.com"

BEGIN_MARKER = "<!-- WEA32_PROTECTION_BEGIN -->"
END_MARKER = "<!-- WEA32_PROTECTION_END -->"


def _github_request(token: str, path: str, params: list[tuple[str, str]] | None = None) -> Any:
    url = GITHUB_API.rstrip("/") + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
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


def _github_list_org_repos(token: str, org: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    page = 1
    while True:
        chunk = _github_request(
            token,
            f"/orgs/{urllib.parse.quote(org, safe='')}/repos",
            [("per_page", "100"), ("page", str(page)), ("type", "all")],
        )
        if not isinstance(chunk, list) or not chunk:
            break
        out.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
    return out


def _fetch_branch_protection(token: str, owner: str, repo: str, branch: str) -> dict[str, Any] | None:
    path = (
        f"/repos/{urllib.parse.quote(owner, safe='')}/"
        f"{urllib.parse.quote(repo, safe='')}/branches/"
        f"{urllib.parse.quote(branch, safe='')}/protection"
    )
    req = urllib.request.Request(
        GITHUB_API.rstrip("/") + path,
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
        if e.code == 404:
            return None
        detail = e.read().decode(errors="replace")
        raise RuntimeError(f"GitHub HTTP {e.code} {path}: {detail}") from e


def _bool_yn(v: Any) -> str:
    return "oui" if v else "non"


def _summarize_protection(prot: dict[str, Any] | None) -> tuple[str, str, str, str, str]:
    """Returns (status, pr_reviews, status_checks, admins_enforced, signed_commits)."""
    if prot is None:
        return ("aucune", "—", "—", "—", "—")
    pr = prot.get("required_pull_request_reviews") or {}
    pr_on = bool(pr) and (pr.get("required_approving_review_count", 0) or 0) > 0
    pr_detail = f"{pr.get('required_approving_review_count', 0)} approb."
    if not pr_on and pr:
        pr_detail = "règles PR sans nombre d’approbations > 0"
    elif not pr:
        pr_detail = "non"

    sc = prot.get("required_status_checks") or {}
    strict = sc.get("strict")
    contexts = sc.get("contexts") or []
    checks_on = bool(contexts) or bool(strict)
    checks_detail = f"{len(contexts)} check(s)" if contexts else ("strict" if strict else "non")

    admins = prot.get("enforce_admins")
    admins_on = bool(admins and admins.get("enabled"))
    signed = prot.get("required_signatures")
    signed_on = bool(signed and signed.get("enabled"))

    status = "oui" if (pr_on or checks_on) else "minimal"
    return (
        status,
        _bool_yn(pr_on) + (f" ({pr_detail})" if pr_on else ""),
        _bool_yn(checks_on) + (f" ({checks_detail})" if checks_on else ""),
        _bool_yn(admins_on),
        _bool_yn(signed_on),
    )


def _build_markdown_table(rows: list[dict[str, str]], generated_at: str, orgs: list[str]) -> str:
    lines: list[str] = []
    lines.append("")
    lines.append(f"_Généré le {generated_at} (UTC) — organisations : {', '.join(orgs)}._")
    lines.append("")
    lines.append(
        "Lecture API : présence de règles sur la **branche par défaut** "
        "(`GET .../branches/{branch}/protection`). « Aucune » = HTTP 404 / pas de règle."
    )
    lines.append("")
    lines.append("| Dépôt | Branche défaut | Protection | Revues PR requises | Status checks | Admins assujettis | Commits signés |")
    lines.append("|-------|----------------|------------|--------------------|--------------|-------------------|----------------|")
    for r in rows:
        lines.append(
            "| `{full}` | `{defbranch}` | {status} | {pr} | {checks} | {admins} | {signed} |".format(
                full=r["full_name"],
                defbranch=r["default_branch"],
                status=r["protection_status"],
                pr=r["pr_reviews"],
                checks=r["status_checks"],
                admins=r["admins_enforced"],
                signed=r["signed"],
            )
        )
    if not rows:
        lines.append("| — | — | — | — | — | — | — |")
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
    parser = argparse.ArgumentParser(
        description="Audit WEA-32 — protection branche principale (GitHub API)"
    )
    parser.add_argument(
        "--github-org",
        action="append",
        default=[],
        metavar="ORG",
        help="Organisation GitHub (répétable). Ex. --github-org WeAdU-ltd",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="",
        help="Fichier markdown à mettre à jour (section entre marqueurs WEA32_*).",
    )
    parser.add_argument(
        "--fail",
        action="store_true",
        help="Code de sortie 1 si un dépôt n’a aucune protection sur la branche par défaut.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Imprimer le tableau JSON sur stdout au lieu du résumé texte.",
    )
    args = parser.parse_args()

    token = (os.environ.get("GITHUB_ORG_AUDIT_TOKEN") or os.environ.get("GITHUB_TOKEN") or "").strip()
    if not token:
        print(
            "Erreur: définir GITHUB_TOKEN ou GITHUB_ORG_AUDIT_TOKEN (audit API GitHub).",
            file=sys.stderr,
        )
        return 1

    orgs = [o.strip() for o in (args.github_org or []) if o.strip()]
    if not orgs:
        print("Erreur: fournir au moins une --github-org.", file=sys.stderr)
        return 1

    rows: list[dict[str, str]] = []
    for org in orgs:
        for repo in _github_list_org_repos(token, org):
            if repo.get("archived"):
                continue
            full = repo.get("full_name") or ""
            default_branch = repo.get("default_branch") or "main"
            if not full or "/" not in full:
                continue
            owner, name = full.split("/", 1)
            try:
                prot = _fetch_branch_protection(token, owner, name, default_branch)
            except RuntimeError as e:
                print(str(e), file=sys.stderr)
                return 1
            status, pr_s, chk_s, adm_s, sig_s = _summarize_protection(prot)
            rows.append(
                {
                    "full_name": full,
                    "default_branch": default_branch,
                    "protection_status": status if prot is not None else "aucune",
                    "pr_reviews": pr_s,
                    "status_checks": chk_s,
                    "admins_enforced": adm_s,
                    "signed": sig_s,
                    "has_protection": "1" if prot is not None else "0",
                    "has_meaningful": "1" if prot is not None and status != "minimal" else "0",
                }
            )

    rows.sort(key=lambda x: x["full_name"].lower())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    else:
        missing = [r for r in rows if r["has_protection"] == "0"]
        weak = [r for r in rows if r["has_protection"] == "1" and r["has_meaningful"] == "0"]
        print(f"Dépôts scannés : {len(rows)}")
        if missing:
            print(f"Sans règle de protection sur la branche par défaut : {len(missing)}")
            for r in missing:
                print(f"  - {r['full_name']} ({r['default_branch']})")
        if weak:
            print(f"Avec protection « minimale » (ni revues ni checks requis) : {len(weak)}")
            for r in weak:
                print(f"  - {r['full_name']}")

    out_path = (args.output or "").strip()
    if out_path:
        block = _build_markdown_table(rows, now, orgs)
        try:
            with open(out_path, encoding="utf-8") as f:
                template = f.read()
        except OSError as e:
            print(f"Erreur lecture {out_path}: {e}", file=sys.stderr)
            return 1
        try:
            updated = _inject_into_doc(template, block)
        except ValueError as e:
            print(str(e), file=sys.stderr)
            return 1
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(updated)
        except OSError as e:
            print(f"Erreur écriture {out_path}: {e}", file=sys.stderr)
            return 1
        print(f"Mis à jour : {out_path}")

    if args.fail:
        if any(r["has_protection"] == "0" for r in rows):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
