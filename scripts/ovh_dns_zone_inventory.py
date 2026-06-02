#!/usr/bin/env python3
"""List all FQDNs from OVH DNS zones (when hosting API is not granted)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.ovh_inventory_wea28 import _credentials, _get

DEFAULT_BASE = "https://eu.api.ovh.com/1.0"


def collect_fqdns(base: str) -> dict:
    ak, asec, ck = _credentials()
    zones = _get(base, ak, asec, ck, "/domain/zone")
    records_by_zone: dict[str, list[dict]] = {}
    all_fqdns: set[str] = set()
    zone_errors: dict[str, str] = {}
    for zone in zones:
        try:
            rec_ids = _get(base, ak, asec, ck, f"/domain/zone/{zone}/record")
        except RuntimeError as e:
            zone_errors[zone] = str(e)
            continue
        recs = []
        for rid in rec_ids:
            r = _get(base, ak, asec, ck, f"/domain/zone/{zone}/record/{rid}")
            sub = (r.get("subDomain") or "").strip()
            rtype = r.get("fieldType")
            target = r.get("target")
            if sub:
                fqdn = f"{sub}.{zone}".lower()
            else:
                fqdn = zone.lower()
            all_fqdns.add(fqdn)
            recs.append({"fqdn": fqdn, "type": rtype, "target": target, "subDomain": sub or "@"})
        records_by_zone[zone] = recs
    return {
        "zones": zones,
        "zone_errors": zone_errors,
        "fqdn_count": len(all_fqdns),
        "fqdns": sorted(all_fqdns),
        "records_by_zone": records_by_zone,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--write", metavar="FILE")
    p.add_argument("--base", default=DEFAULT_BASE)
    args = p.parse_args()
    try:
        data = collect_fqdns(args.base.rstrip("/"))
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    text = json.dumps(data, indent=2, ensure_ascii=False)
    if args.write:
        with open(args.write, "w", encoding="utf-8") as f:
            f.write(text)
    print(
        json.dumps(
            {
                "zones": data["zones"],
                "zone_errors": data.get("zone_errors"),
                "fqdn_count": data["fqdn_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
