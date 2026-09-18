#!/usr/bin/env python3
"""
WEA-28 — Audit Agency Plus: classify attached multisites (DNS + HTTP).

Reads inventory JSON from ovh_inventory_wea28.py (--export-domains) or fetches live.
Writes summary JSON + optional CSV under /tmp (never commit FQDN lists).

Usage:
  python3 scripts/ovh_inventory_wea28.py --export-domains --write /tmp/ovh-snapshot.json
  python3 scripts/ovh_audit_agency_plus.py --inventory /tmp/ovh-snapshot.json --write /tmp/ovh-audit-summary.json
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import socket
import ssl
import sys
import urllib.error
import urllib.request
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# Known production IPs (AWS Lightsail/EC2 eu-west-2 from WEA-29 / DNS checks)
AWS_PROD_IPS = frozenset({"18.135.12.229"})
OVH_HOSTING_IPS = frozenset({"213.186.33.5", "213.186.33.19", "213.186.33.10"})
GOOGLE_SITES_IPS = frozenset({"198.202.211.1"})

OVH_DEFAULT_PAGE_MARKERS = (
    b"site en construction",
    b"under construction",
    b"coming soon",
    b"default web site page",
    b"page par defaut",
)


@dataclass
class SiteCheck:
    fqdn: str
    category: str
    a_records: list[str]
    http_status: int | None
    https_status: int | None
    final_url: str | None
    notes: str


def _resolve_a(fqdn: str) -> list[str]:
    try:
        infos = socket.getaddrinfo(fqdn, None, type=socket.SOCK_STREAM)
        return sorted({item[4][0] for item in infos})
    except (socket.gaierror, OSError):
        return []


def _http_probe(url: str, timeout: float = 8.0) -> tuple[int | None, str | None, bytes]:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "WeAdU-ovh-audit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.status, resp.geturl(), b""
    except urllib.error.HTTPError as e:
        return e.code, url, b""
    except Exception:
        req_get = urllib.request.Request(url, method="GET", headers={"User-Agent": "WeAdU-ovh-audit/1.0"})
        try:
            with urllib.request.urlopen(req_get, timeout=timeout, context=ctx) as resp:
                return resp.status, resp.geturl(), resp.read(4096)
        except urllib.error.HTTPError as e:
            try:
                body = e.read(4096)
            except Exception:
                body = b""
            return e.code, url, body
        except Exception:
            return None, None, b""


def _classify(fqdn: str, ips: list[str], status: int | None, body: bytes) -> tuple[str, str]:
    if not ips:
        return "dns_none", "no A/AAAA resolution"
    if any(ip in AWS_PROD_IPS for ip in ips):
        return "duplicate_aws", f"A points to AWS prod ({','.join(ips)})"
    if any(ip in GOOGLE_SITES_IPS for ip in ips):
        return "off_ovh_hosting", f"A points off OVH cluster ({','.join(ips)})"
    if ips and not any(ip in OVH_HOSTING_IPS for ip in ips):
        return "off_ovh_hosting", f"A not on OVH hosting IP ({','.join(ips)})"
    if status is None:
        return "unknown", "no HTTP response"
    if status >= 500:
        return "dead", f"HTTP {status}"
    if status in (404, 410):
        return "dead", f"HTTP {status}"
    if status in (401, 403):
        return "active_restricted", f"HTTP {status} (auth/walled)"
    if body and any(m in body.lower() for m in OVH_DEFAULT_PAGE_MARKERS):
        return "placeholder", "default/under construction page"
    if 200 <= status < 400:
        return "active", f"HTTP {status}"
    return "unknown", f"HTTP {status}"


def _check_one(fqdn: str) -> SiteCheck:
    ips = _resolve_a(fqdn)
    https_status, final_url, body = _http_probe(f"https://{fqdn}/")
    http_status = None
    if https_status is None:
        http_status, final_url, body = _http_probe(f"http://{fqdn}/")
    status = https_status if https_status is not None else http_status
    category, notes = _classify(fqdn, ips, status, body)
    return SiteCheck(
        fqdn=fqdn,
        category=category,
        a_records=ips,
        http_status=http_status,
        https_status=https_status,
        final_url=final_url,
        notes=notes,
    )


def _fetch_billing_summary() -> dict[str, Any]:
    from scripts.ovh_inventory_wea28 import _credentials, _get

    base = "https://eu.api.ovh.com/1.0"
    ak, asec, ck = _credentials()
    out: dict[str, Any] = {"bills": [], "orders_recent": [], "services_hosting": []}
    try:
        bill_ids = _get(base, ak, asec, ck, "/me/bill") or []
        for bid in bill_ids[:8]:
            try:
                bill = _get(base, ak, asec, ck, f"/me/bill/{bid}")
                out["bills"].append(
                    {
                        "billId": bid,
                        "date": bill.get("date"),
                        "priceWithTax": bill.get("priceWithTax"),
                        "tax": bill.get("tax"),
                        "url": bill.get("url"),
                    }
                )
            except RuntimeError:
                continue
    except RuntimeError as e:
        out["bills_error"] = str(e)
    try:
        order_ids = _get(base, ak, asec, ck, "/me/order") or []
        for oid in order_ids[:8]:
            try:
                order = _get(base, ak, asec, ck, f"/me/order/{oid}")
                out["orders_recent"].append(
                    {
                        "orderId": oid,
                        "date": order.get("date"),
                        "expiration": order.get("expiration"),
                        "status": order.get("status"),
                        "url": order.get("url"),
                    }
                )
            except RuntimeError:
                continue
    except RuntimeError as e:
        out["orders_error"] = str(e)
    try:
        hosting_ids = _get(base, ak, asec, ck, "/hosting/web") or []
        for hid in hosting_ids:
            h = _get(base, ak, asec, ck, f"/hosting/web/{hid}")
            out["services_hosting"].append(
                {
                    "serviceName": h.get("serviceName"),
                    "offer": h.get("offer"),
                    "state": h.get("state"),
                    "quotaUsed": h.get("quotaUsed"),
                    "quotaSize": h.get("quotaSize"),
                    "hasCdn": h.get("hasCdn"),
                }
            )
    except RuntimeError as e:
        out["hosting_error"] = str(e)
    return out


def run_audit(domains: list[str], workers: int = 24) -> dict[str, Any]:
    domains = sorted({d.strip().lower() for d in domains if d.strip()})
    results: list[SiteCheck] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        for item in pool.map(_check_one, domains):
            results.append(item)
    counts = Counter(r.category for r in results)
    return {
        "total": len(results),
        "category_counts": dict(counts),
        "top_suffixes_by_category": {
            cat: Counter(
                ".".join(r.fqdn.split(".")[-2:]) for r in results if r.category == cat
            ).most_common(15)
            for cat in sorted(counts)
        },
        "samples": {cat: [r.fqdn for r in results if r.category == cat][:8] for cat in sorted(counts)},
        "sites": [asdict(r) for r in results],
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Audit OVH Agency Plus attached domains")
    p.add_argument("--inventory", help="JSON from ovh_inventory_wea28.py")
    p.add_argument("--write", metavar="FILE", help="Write audit summary JSON")
    p.add_argument("--csv", metavar="FILE", help="Write per-site CSV (local only)")
    p.add_argument("--workers", type=int, default=24)
    p.add_argument("--skip-billing", action="store_true")
    p.add_argument("--billing-only", action="store_true")
    args = p.parse_args()

    if args.billing_only:
        billing = _fetch_billing_summary()
        payload = {"billing": billing}
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        if args.write:
            Path(args.write).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return 0

    if not args.inventory:
        print("error: --inventory required unless --billing-only", file=sys.stderr)
        return 1

    inv_path = Path(args.inventory)
    if not inv_path.is_file():
        print(f"error: inventory not found: {inv_path}", file=sys.stderr)
        return 1

    inv = json.loads(inv_path.read_text(encoding="utf-8"))
    domains = inv.get("attached_domains") or []
    if not domains:
        print("error: inventory missing attached_domains; re-run with --export-domains", file=sys.stderr)
        return 1

    audit = run_audit(domains, workers=args.workers)
    audit["hosting_summary"] = inv.get("hosting_summary")
    audit["attached_domains_count"] = inv.get("attached_domains_count")
    audit["invoice_context"] = {
        "reference": "FR78255331",
        "date": "2026-06-01",
        "agency_plus_ht_annual": 695.88,
        "total_ttc": 853.98,
        "note": "Agency Plus = gamme Agencies 2027 (ex Performance 3 catalogue)",
    }
    if not args.skip_billing:
        try:
            audit["billing"] = _fetch_billing_summary()
        except Exception as e:
            audit["billing_error"] = str(e)

    summary = {k: v for k, v in audit.items() if k != "sites"}
    if args.write:
        Path(args.write).write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        Path(str(args.write).replace(".json", "-full.json")).write_text(
            json.dumps(audit, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    if args.csv:
        with Path(args.csv).open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(
                f,
                fieldnames=["fqdn", "category", "a_records", "http_status", "https_status", "final_url", "notes"],
            )
            w.writeheader()
            for row in audit["sites"]:
                r = dict(row)
                r["a_records"] = ",".join(r["a_records"])
                w.writerow(r)

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
