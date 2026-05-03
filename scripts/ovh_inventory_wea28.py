#!/usr/bin/env python3
"""
WEA-28 — read-only inventory via OVHcloud EU API (v1).

Credentials: set OVH_APPLICATION_KEY, OVH_APPLICATION_SECRET, OVH_CONSUMER_KEY
or run under `op run` with those variables pointing at 1Password references, e.g.:

  op run --no-masking --env-file=scripts/ovh_inventory_wea28.op.env -- \\
    python3 scripts/ovh_inventory_wea28.py --json

Where `ovh_inventory_wea28.op.env` contains lines like:
  OVH_APPLICATION_KEY=op://VaultName/OVH_APPLICATION_KEY/credential

Does not print secrets. Output is JSON on stdout (or --write path).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from collections import Counter
from typing import Any

DEFAULT_BASE = "https://eu.api.ovh.com/1.0"


def _env_or_op(name: str, op_ref: str) -> str:
    v = (os.environ.get(name) or "").strip()
    if v and not v.startswith("op://"):
        return v
    ref = v if v.startswith("op://") else op_ref
    try:
        return subprocess.check_output(["op", "read", ref], text=True, timeout=30).strip()
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        raise RuntimeError(
            f"Missing {name} and `op read {ref}` failed ({e}). "
            "Export the three OVH_* variables or use `op run` with op:// references."
        ) from e


def _credentials() -> tuple[str, str, str]:
    return (
        _env_or_op("OVH_APPLICATION_KEY", "op://Replit/OVH_APPLICATION_KEY/credential"),
        _env_or_op("OVH_APPLICATION_SECRET", "op://Replit/OVH_APPLICATION_SECRET/credential"),
        _env_or_op("OVH_CONSUMER_KEY", "op://Replit/OVH_CONSUMER_KEY/credential"),
    )


def _api_time(base: str) -> int:
    with urllib.request.urlopen(base + "/auth/time", timeout=30) as r:
        return int(r.read().decode().strip())


def _sign(app_secret: str, consumer_key: str, method: str, url: str, body: str, t: int) -> str:
    pre = "+".join([app_secret, consumer_key, method.upper(), url, body, str(t)])
    return "$1$" + hashlib.sha1(pre.encode()).hexdigest()


def _request(
    base: str,
    app_key: str,
    app_secret: str,
    consumer_key: str,
    method: str,
    path: str,
    body: str | None = None,
) -> tuple[int, Any]:
    body = body or ""
    full_url = base + path
    t = _api_time(base)
    sig = _sign(app_secret, consumer_key, method, full_url, body, t)
    req = urllib.request.Request(full_url, method=method, data=body.encode() if body else None)
    req.add_header("X-Ovh-Application", app_key)
    req.add_header("X-Ovh-Consumer", consumer_key)
    req.add_header("X-Ovh-Signature", sig)
    req.add_header("X-Ovh-Timestamp", str(t))
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        err = e.read().decode(errors="replace")
        try:
            parsed = json.loads(err)
        except json.JSONDecodeError:
            parsed = err
        return e.code, parsed


def _get(
    base: str,
    ak: str,
    asec: str,
    ck: str,
    path: str,
) -> Any:
    status, data = _request(base, ak, asec, ck, "GET", path)
    if status != 200:
        raise RuntimeError(f"GET {path} -> HTTP {status}: {data!r}")
    return data


def _suffix_counts(domains: list[str], min_labels: int = 2) -> list[tuple[str, int]]:
    c: Counter[str] = Counter()
    for d in domains:
        parts = d.lower().strip().split(".")
        if len(parts) >= min_labels:
            c[".".join(parts[-2:])] += 1
        else:
            c[d] += 1
    return c.most_common(25)


def build_report(base: str) -> dict[str, Any]:
    ak, asec, ck = _credentials()
    me = _get(base, ak, asec, ck, "/me")
    zones = _get(base, ak, asec, ck, "/domain/zone")
    hosting_ids = _get(base, ak, asec, ck, "/hosting/web")
    email_domains = _get(base, ak, asec, ck, "/email/domain")
    vps = _get(base, ak, asec, ck, "/vps")
    dedi = _get(base, ak, asec, ck, "/dedicated/server")
    cloud = _get(base, ak, asec, ck, "/cloud/project")
    ips = _get(base, ak, asec, ck, "/ip")

    hosting_summary: dict[str, Any] | None = None
    attached: list[str] = []
    if hosting_ids:
        svc = hosting_ids[0]
        hosting_summary = _get(base, ak, asec, ck, f"/hosting/web/{svc}")
        attached = _get(base, ak, asec, ck, f"/hosting/web/{svc}/attachedDomain")

    safe_me = {k: me.get(k) for k in ("nichandle", "country", "ovhSubsidiary", "customerCode") if k in me}

    return {
        "api_base": base,
        "me": safe_me,
        "dns_zones": zones,
        "email_domains": email_domains,
        "hosting_services": hosting_ids,
        "hosting_summary": (
            {k: hosting_summary.get(k) for k in ("serviceName", "state", "offer", "datacenter", "quotaSize", "quotaUsed", "hasCdn")}
            if hosting_summary
            else None
        ),
        "attached_domains_count": len(attached),
        "attached_domains_top_suffixes": _suffix_counts(attached),
        "vps": vps,
        "dedicated_servers": dedi,
        "public_cloud_projects": cloud,
        "ips": ips,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="OVH read-only inventory for WEA-28")
    p.add_argument("--base", default=os.environ.get("OVH_API_BASE", DEFAULT_BASE), help="API base URL")
    p.add_argument("--write", metavar="FILE", help="Write JSON report to this file")
    p.add_argument("--json", action="store_true", help="Print JSON to stdout (default)")
    args = p.parse_args()

    try:
        report = build_report(args.base.rstrip("/"))
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.write:
        with open(args.write, "w", encoding="utf-8") as f:
            f.write(text)
    if args.json or not args.write:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
