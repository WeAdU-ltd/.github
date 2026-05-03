#!/usr/bin/env python3
"""
WEA-27 — Inventaire Google Cloud : projets, APIs activées, résumé des doublons inter-projets.

Variables d'environnement optionnelles :
  GCP_PARENT     — ex. organizations/123 ou folders/456 pour restreindre la liste de projets
                   (via `gcloud projects list --filter=parent.id:...` si besoin ; sinon liste globale)
  GCLOUD_PATH    — chemin complet vers gcloud ou gcloud.cmd (Windows : utile si `python` n'a pas
                   le même PATH que la console où `gcloud --version` fonctionne)

Prérequis : `gcloud` installé et session authentifiée (`gcloud auth login`).

Les URIs OAuth détaillées par client ne sont pas exportées ici : voir la console Credentials
ou Cloud Asset Inventory ; ce script aide à repérer les incohérences (même API activée partout,
doublons de configuration à croiser avec AWS/OVH sur WEA-38).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

BEGIN_MARKER = "<!-- WEA27_GCP_INVENTORY_BEGIN -->"
END_MARKER = "<!-- WEA27_GCP_INVENTORY_END -->"

# Défini dans main() après résolution (PATH Python ≠ PATH utilisateur sous Windows).
_GCLOUD_EXE: str = ""


def _resolve_gcloud_executable() -> str | None:
    """Trouve l'exécutable gcloud : PATH, GCLOUD_PATH, puis emplacements types sous Windows."""
    explicit = os.environ.get("GCLOUD_PATH", "").strip().strip('"')
    if explicit:
        if os.path.isfile(explicit):
            return explicit
        for ext in (".cmd", ".exe", ".bat"):
            p = explicit + ext if not explicit.lower().endswith(ext) else explicit
            if os.path.isfile(p):
                return p

    w = shutil.which("gcloud")
    if w:
        return w

    if sys.platform == "win32":
        candidates: list[str] = []
        la = os.environ.get("LOCALAPPDATA", "")
        if la:
            candidates.append(
                os.path.join(la, "Google", "Cloud SDK", "google-cloud-sdk", "bin", "gcloud.cmd")
            )
        for env in ("ProgramFiles", "ProgramFiles(x86)"):
            pf = os.environ.get(env, "")
            if pf:
                candidates.append(
                    os.path.join(pf, "Google", "Cloud SDK", "google-cloud-sdk", "bin", "gcloud.cmd")
                )
        for c in candidates:
            if os.path.isfile(c):
                return c

    return None


def _run_gcloud_json(args: list[str]) -> Any:
    cmd = [_GCLOUD_EXE, *args, "--format=json"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if proc.returncode != 0:
        raise RuntimeError(
            f"gcloud failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr or proc.stdout}"
        )
    out = proc.stdout.strip()
    if not out:
        return [] if args[0] in ("projects", "services", "alpha") else {}
    return json.loads(out)


def _list_projects(parent: str | None) -> list[dict[str, Any]]:
    """
    Liste les projets accessibles. Si GCP_PARENT est défini, filtre par parent (org/folder).
    """
    base = ["projects", "list"]
    extra = os.environ.get("GCP_PARENT", "").strip() or (parent or "").strip()
    if extra:
        org_m = re.match(r"organizations/(\d+)$", extra)
        folder_m = re.match(r"folders/(\d+)$", extra)
        if org_m:
            base.extend(["--filter", f"parent.id:{org_m.group(1)}"])
        elif folder_m:
            base.extend(["--filter", f"parent.id:{folder_m.group(1)}"])
    return _run_gcloud_json(base)


def _list_enabled_services(project_id: str) -> list[str]:
    """Retourne les noms de services activés (ex. compute.googleapis.com)."""
    data = _run_gcloud_json(
        ["services", "list", "--project", project_id, "--enabled"]
    )
    if not isinstance(data, list):
        return []
    return sorted(
        {item.get("config", {}).get("name", "") for item in data if isinstance(item, dict)}
    )


def _build_report(projects: list[dict[str, Any]]) -> tuple[str, list[str]]:
    """Retourne le bloc markdown et la liste des messages d'incohérence."""
    lines: list[str] = []
    issues: list[str] = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S (UTC)")
    lines.append("")
    lines.append(f"_Généré le {now} via `gcloud`._")
    lines.append("")
    lines.append("### Projets (extrait)")
    lines.append("")
    lines.append("| projectId | name | lifecycleState |")
    lines.append("|-----------|------|----------------|")

    proj_rows: list[tuple[str, str, str]] = []
    for p in sorted(projects, key=lambda x: (x.get("projectId") or "").lower()):
        pid = p.get("projectId") or "—"
        name = (p.get("name") or "—").replace("|", "\\|")
        state = p.get("lifecycleState") or "—"
        proj_rows.append((pid, name, state))
        lines.append(f"| `{pid}` | {name} | {state} |")

    if not proj_rows:
        lines.append("| — | _aucun projet listé_ | — |")
        issues.append("Aucun projet retourné par `gcloud projects list` (droits ou filtre parent).")

    service_to_projects: dict[str, list[str]] = defaultdict(list)

    for p in sorted(projects, key=lambda x: (x.get("projectId") or "").lower()):
        pid = p.get("projectId")
        if not pid:
            continue
        try:
            svcs = _list_enabled_services(pid)
        except RuntimeError as e:
            issues.append(f"`{pid}` : impossible de lister les services — {e}")
            continue
        for s in svcs:
            if s:
                service_to_projects[s].append(pid)

    lines.append("")
    lines.append("### APIs activées — résumé")
    lines.append("")
    lines.append("| service | # projets où activé | projets |")
    lines.append("|---------|---------------------|---------|")
    for svc in sorted(service_to_projects.keys(), key=str.lower):
        pids = sorted(set(service_to_projects[svc]))
        n = len(pids)
        proj_cell = ", ".join(f"`{x}`" for x in pids[:12])
        if len(pids) > 12:
            proj_cell += f", … (+{len(pids) - 12})"
        lines.append(f"| `{svc}` | {n} | {proj_cell} |")
    if not service_to_projects:
        lines.append("| — | — | — |")

    lines.append("")
    lines.append("### Incohérences détectées (automatique)")
    lines.append("")
    if issues:
        for i in issues:
            lines.append(f"- {i}")
    else:
        lines.append("- _Lecture complète des projets et services OK._")

    # Heuristique : même service sur plusieurs projets → à croiser avec doublons cloud (WEA-38)
    dup_services = [s for s, pl in service_to_projects.items() if len(set(pl)) > 1]
    if dup_services:
        lines.append(
            f"- **API présente sur plusieurs projets** ({len(dup_services)} services) : "
            "vérifier les doublons fonctionnels avec AWS/OVH ([WEA-38](https://linear.app/weadu/issue/WEA-38/replit-fermeture-apres-bascule-complete))."
        )

    lines.append("")
    return "\n".join(lines), issues


def _inject_into_doc(template: str, generated_block: str) -> str:
    if BEGIN_MARKER not in template or END_MARKER not in template:
        raise ValueError(
            f"Le fichier doit contenir {BEGIN_MARKER} et {END_MARKER} pour insertion."
        )
    before, rest = template.split(BEGIN_MARKER, 1)
    _, after = rest.split(END_MARKER, 1)
    return before + BEGIN_MARKER + generated_block + END_MARKER + after


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventaire WEA-27 Google Cloud (gcloud)")
    parser.add_argument(
        "-o",
        "--output",
        default="docs/inventory/WEA-27-google-cloud.md",
        help="Fichier markdown à mettre à jour",
    )
    parser.add_argument(
        "--parent",
        default="",
        help="ID parent optionnel (organizations/N ou folders/N), sinon env GCP_PARENT",
    )
    args = parser.parse_args()

    global _GCLOUD_EXE
    resolved = _resolve_gcloud_executable()
    if not resolved:
        print(
            "Erreur : Google Cloud SDK (`gcloud`) introuvable ou non exécutable.\n"
            "  Sous Windows : définissez GCLOUD_PATH vers gcloud.cmd, ex. :\n"
            '    $env:GCLOUD_PATH = "$env:LOCALAPPDATA\\Google\\Cloud SDK\\google-cloud-sdk\\bin\\gcloud.cmd"',
            file=sys.stderr,
        )
        return 1
    _GCLOUD_EXE = resolved

    try:
        subprocess.run([_GCLOUD_EXE, "--version"], capture_output=True, check=True, timeout=30)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(
            f"Erreur : `{_GCLOUD_EXE}` ne s'exécute pas correctement : {e}",
            file=sys.stderr,
        )
        return 1

    print(f"Utilisation de : {_GCLOUD_EXE}")

    parent = args.parent.strip() or os.environ.get("GCP_PARENT", "").strip()
    try:
        projects_raw = _list_projects(parent or None)
    except RuntimeError as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1

    projects = [p for p in projects_raw if isinstance(p, dict)]
    block, _issues = _build_report(projects)

    out_path = args.output
    try:
        with open(out_path, encoding="utf-8") as f:
            template = f.read()
    except FileNotFoundError:
        template = f"# WEA-27\n\n{BEGIN_MARKER}\n\n{END_MARKER}\n"

    new_doc = _inject_into_doc(template, "\n" + block + "\n")
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(new_doc)

    print(f"Écrit : {out_path}")
    print(f"  Projets : {len(projects)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
