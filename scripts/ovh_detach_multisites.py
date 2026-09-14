#!/usr/bin/env python3
"""Detach OVH hosting multisites except cluster hostname (WEA-28)."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.ovh_inventory_wea28 import _credentials, _get, _request

DEFAULT_KEEP = "weadufu.cluster028.hosting.ovh.net"
DEFAULT_BASE = "https://eu.api.ovh.com/1.0"


def detach_all(base: str, keep: str, dry_run: bool, delay: float) -> dict:
    ak, asec, ck = _credentials()
    svc = _get(base, ak, asec, ck, "/hosting/web")[0]
    attached = _get(base, ak, asec, ck, f"/hosting/web/{svc}/attachedDomain")
    to_detach = sorted(d for d in attached if d != keep)

    result = {
        "service": svc,
        "keep": keep,
        "initial_count": len(attached),
        "queued": [],
        "failed": [],
        "dry_run": dry_run,
    }

    for fqdn in to_detach:
        if dry_run:
            result["queued"].append(fqdn)
            continue
        path = f"/hosting/web/{svc}/attachedDomain/{fqdn}"
        status, data = _request(base, ak, asec, ck, "DELETE", path)
        if status == 200:
            result["queued"].append({"fqdn": fqdn, "task": data})
        else:
            result["failed"].append({"fqdn": fqdn, "status": status, "error": data})
        time.sleep(delay)

    if not dry_run:
        # OVH deletes are async; poll until stable or timeout
        for _ in range(60):
            time.sleep(10)
            remaining = _get(base, ak, asec, ck, f"/hosting/web/{svc}/attachedDomain")
            result["remaining_count"] = len(remaining)
            result["remaining"] = remaining
            if len(remaining) <= 1 and keep in remaining:
                break
        else:
            result["timeout"] = True

    return result


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--keep", default=DEFAULT_KEEP)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--delay", type=float, default=0.3, help="Seconds between DELETE calls")
    p.add_argument("--write", metavar="FILE")
    args = p.parse_args()

    try:
        result = detach_all(DEFAULT_BASE, args.keep, args.dry_run, args.delay)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.write:
        Path(args.write).write_text(text, encoding="utf-8")
    print(text)
    return 0 if not result.get("failed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
