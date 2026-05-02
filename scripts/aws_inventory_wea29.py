#!/usr/bin/env python3
"""
WEA-29 — Inventaire EC2 (Ubuntu / Windows), ENI, volumes liés, security groups,
coûts indicatifs à partir du catalogue public On-Demand (approximatif).

Prérequis :
  pip install boto3
  Profil ou variables AWS (voir AWS CLI) : AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
  AWS_SESSION_TOKEN (optionnel), AWS_DEFAULT_REGION (optionnel).

Usage :
  python3 scripts/aws_inventory_wea29.py -o docs/inventory/WEA-29-aws-ec2-inventory.md
  AWS_PROFILE=mon-profil python3 scripts/aws_inventory_wea29.py --regions eu-west-1,us-east-1

Les sections « OS invité » (tâches planifiées Windows, Selenium, systemd Linux) ne sont pas
visibles via l’API EC2 : compléter manuellement ou via SSM dans la zone MANUEL du Markdown.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Any

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    print(
        "Missing boto3. Install with: pip install boto3",
        file=sys.stderr,
    )
    sys.exit(1)

BEGIN_MARKER = "<!-- WEA29_INVENTORY_BEGIN -->"
END_MARKER = "<!-- WEA29_INVENTORY_END -->"

# Approximate USD/month On-Demand (us-east-1 style, 730h) — pour ordre de grandeur uniquement.
# Mis à jour ponctuellement ; pour facturation réelle utiliser Cost Explorer / factures.
ROUGH_MONTHLY_USD: dict[str, float] = {
    "t3.micro": 7.5,
    "t3.small": 15.0,
    "t3.medium": 30.0,
    "t3.large": 60.0,
    "t3.xlarge": 120.0,
    "t3a.micro": 7.0,
    "t3a.small": 14.0,
    "t3a.medium": 28.0,
    "m5.large": 70.0,
    "m5.xlarge": 140.0,
    "c5.large": 62.0,
    "r5.large": 91.0,
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S (UTC)")


def _regions(client_args: dict[str, Any], explicit: list[str] | None) -> list[str]:
    if explicit:
        return sorted(set(explicit))
    ec2 = boto3.client("ec2", **client_args)
    resp = ec2.describe_regions()
    return sorted(r["RegionName"] for r in resp["Regions"])


def _rough_cost(instance_type: str | None) -> str:
    if not instance_type:
        return "—"
    base = ROUGH_MONTHLY_USD.get(instance_type, None)
    if base is None:
        return f"— (type `{instance_type}` non cartographié ; voir tarifs AWS)"
    return f"~{base:.0f} USD/mois (On-Demand indicatif, région variable)"


def _collect_region(client_args: dict[str, Any], region: str) -> dict[str, Any]:
    ec2 = boto3.client("ec2", region_name=region, **{k: v for k, v in client_args.items() if k != "region_name"})
    instances: list[dict[str, Any]] = []
    paginator = ec2.get_paginator("describe_instances")
    for page in paginator.paginate():
        for res in page.get("Reservations", []):
            for inst in res.get("Instances", []):
                instances.append(inst)

    eips: list[dict[str, Any]] = []
    try:
        eips = ec2.describe_addresses().get("Addresses", [])
    except ClientError:
        pass

    return {"region": region, "instances": instances, "eips": eips}


def _platform_label(inst: dict[str, Any]) -> str:
    # Windows instances have PlatformDetails / Platform
    plat = inst.get("Platform")
    details = inst.get("PlatformDetails") or ""
    if plat == "windows" or "Windows" in details:
        return "Windows"
    return "Linux/Unix (souvent Ubuntu en prod — confirmer via AMI / SSM)"


def _instance_row(region: str, inst: dict[str, Any]) -> str:
    iid = inst.get("InstanceId", "?")
    typ = inst.get("InstanceType", "?")
    state = inst.get("State", {}).get("Name", "?")
    priv = inst.get("PrivateIpAddress") or "—"
    pub = inst.get("PublicIpAddress") or "—"
    vpc = inst.get("VpcId") or "—"
    subnet = inst.get("SubnetId") or "—"
    az = inst.get("Placement", {}).get("AvailabilityZone") or "—"
    key = inst.get("KeyName") or "—"
    lt = inst.get("LaunchTime")
    lt_s = lt.strftime("%Y-%m-%d %H:%M UTC") if lt else "—"

    sgs = []
    for sg in inst.get("SecurityGroups", []):
        sgs.append(f"`{sg.get('GroupId')}` ({sg.get('GroupName', '')})")
    sg_txt = ", ".join(sgs) if sgs else "—"

    tags = {t["Key"]: t["Value"] for t in inst.get("Tags", [])}
    name = tags.get("Name", "—")
    tag_preview = json.dumps(tags, ensure_ascii=False) if tags else "—"

    vol_lines = []
    for bdm in inst.get("BlockDeviceMappings", []):
        ebs = bdm.get("Ebs", {})
        vid = ebs.get("VolumeId")
        if vid:
            vol_lines.append(vid)
    platform = _platform_label(inst)
    cost = _rough_cost(typ)

    lines = [
        f"#### `{iid}` — {name}",
        "",
        "| Champ | Valeur |",
        "|--------|--------|",
        f"| Région | `{region}` |",
        f"| AZ | `{az}` |",
        f"| Type | `{typ}` |",
        f"| État | `{state}` |",
        f"| Plateforme (API) | {platform} |",
        f"| IP privée | `{priv}` |",
        f"| IP publique | `{pub or '—'}` |",
        f"| VPC / sous-réseau | `{vpc}` / `{subnet}` |",
        f"| Key pair | `{key}` |",
        f"| Security groups | {sg_txt} |",
        f"| Volumes (IDs) | {', '.join(f'`{v}`' for v in vol_lines) or '—'} |",
        f"| Lancée le | {lt_s} |",
        f"| Tags | {tag_preview} |",
        f"| Coût indicatif instance | {cost} |",
        "",
    ]
    return "\n".join(lines)


def _eip_section(region: str, eips: list[dict[str, Any]]) -> str:
    if not eips:
        return f"_Aucune Elastic IP allouée dans `{region}`._\n"
    rows = ["| IP publique | AllocationId | Instance associée |", "|---|---|---|"]
    for a in eips:
        pub = a.get("PublicIp", "—")
        aid = a.get("AllocationId", "—")
        iid = a.get("InstanceId") or a.get("NetworkInterfaceId") or "—"
        rows.append(f"| `{pub}` | `{aid}` | `{iid}` |")
    return "\n".join(rows) + "\n"


def build_markdown_payload(blocks: list[dict[str, Any]]) -> str:
    parts: list[str] = [
        f"_Généré le {_utc_now_iso()}._",
        "",
        "> Les montants « coût indicatif » sont des ordres de grandeur (On-Demand public, région variable).",
        "> Pour le réel : **Cost Explorer**, factures, ou **Pricing API**.",
        "",
        "## Synthèse par région",
        "",
    ]

    for block in blocks:
        region = block["region"]
        insts = block["instances"]
        eips = block["eips"]
        parts.append(f"### Région `{region}`")
        parts.append("")
        if not insts:
            parts.append("_Aucune instance EC2 dans cette région._")
            parts.append("")
            parts.append("#### Elastic IPs")
            parts.append("")
            parts.extend([_eip_section(region, eips)])
            continue

        parts.append("| InstanceId | Name (tag) | Type | État | OS (API) | IP privée | IP publique |")
        parts.append("|------------|------------|------|------|----------|-----------|-------------|")
        for inst in insts:
            tags = {t["Key"]: t["Value"] for t in inst.get("Tags", [])}
            name = tags.get("Name", "—")
            parts.append(
                "| `{id}` | {nm} | `{typ}` | `{st}` | {os} | `{pip}` | `{pub}` |".format(
                    id=inst.get("InstanceId"),
                    nm=name.replace("|", "\\|"),
                    typ=inst.get("InstanceType"),
                    st=inst.get("State", {}).get("Name"),
                    os=_platform_label(inst),
                    pip=inst.get("PrivateIpAddress") or "—",
                    pub=inst.get("PublicIpAddress") or "—",
                )
            )
        parts.append("")
        parts.append("### Détail des instances")
        parts.append("")
        for inst in insts:
            parts.append(_instance_row(region, inst))

        parts.append("### Elastic IPs")
        parts.append("")
        parts.append(_eip_section(region, eips))

    parts.append("---")
    parts.append("")
    parts.append(
        "**Accès SSH / RDP / SSM :** dépend des security groups, du sous-réseau (public/privé), "
        "des clés et de [WEA-15](https://linear.app/weadu/issue/WEA-15/secrets-socle-partage-org-github-cursor-isolation-finance-rh). "
        "Ne pas dupliquer les secrets dans ce dépôt."
    )
    return "\n".join(parts)


def _patch_file(path: str, new_inner: str) -> None:
    from pathlib import Path

    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if BEGIN_MARKER not in text or END_MARKER not in text:
        raise SystemExit(
            f"{path} doit contenir {BEGIN_MARKER} et {END_MARKER} pour insertion."
        )
    before, rest = text.split(BEGIN_MARKER, 1)
    _, after = rest.split(END_MARKER, 1)
    updated = before + BEGIN_MARKER + "\n\n" + new_inner.strip() + "\n\n" + END_MARKER + after
    p.write_text(updated, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="WEA-29 — inventaire EC2 AWS → Markdown")
    parser.add_argument(
        "-o",
        "--output",
        default="docs/inventory/WEA-29-aws-ec2-inventory.md",
        help="Fichier Markdown à mettre à jour",
    )
    parser.add_argument(
        "--regions",
        help="Liste de régions séparées par des virgules (sinon toutes les régions activées du compte)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="N'écrase pas le fichier : affiche le Markdown sur stdout",
    )
    args = parser.parse_args()

    region_list = None
    if args.regions:
        region_list = [r.strip() for r in args.regions.split(",") if r.strip()]

    session_kw: dict[str, Any] = {}
    try:
        regions = _regions(session_kw, region_list)
    except (BotoCoreError, ClientError) as e:
        print(f"Erreur AWS (credentials / STS): {e}", file=sys.stderr)
        sys.exit(2)

    blocks: list[dict[str, Any]] = []
    for region in regions:
        try:
            blocks.append(_collect_region(session_kw, region))
        except ClientError as e:
            print(f"Avertissement région {region}: {e}", file=sys.stderr)
            blocks.append({"region": region, "instances": [], "eips": []})

    md = build_markdown_payload(blocks)
    if args.dry_run:
        print(md)
        return
    _patch_file(args.output, md)
    print(f"Mis à jour : {args.output}")


if __name__ == "__main__":
    main()
