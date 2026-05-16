#!/usr/bin/env python3
"""Fetch Marketcall affiliate offers via official API (paginated).

Requires env MC_KEY (X-Api-Key). Do not commit keys; use a local .env or shell export.

Docs: https://www.marketcall.com/affiliate/api/docs
Endpoint: GET https://www.marketcall.com/api/v1/affiliate/offers?per_page=...&page=...

Rate limit: 60 requests/minute per key (sleep between pages).

Usage:
  export MC_KEY='...'
  python3 scripts/marketcall_fetch_offers.py --output /tmp/marketcall_offers_all.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request


def fetch_all_offers(api_key: str, per_page: int = 100, sleep_s: float = 1.1) -> list[dict]:
    base = "https://www.marketcall.com/api/v1/affiliate/offers"
    all_rows: list[dict] = []
    page = 1
    while True:
        url = f"{base}?per_page={per_page}&page={page}"
        req = urllib.request.Request(url, headers={"X-Api-Key": api_key})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            sys.stderr.write(exc.read().decode("utf-8", errors="replace")[:2000])
            sys.stderr.write("\n")
            raise SystemExit(exc.code) from exc
        chunk = payload.get("data") or []
        all_rows.extend(chunk)
        pag = payload.get("paginator") or {}
        total_pages = int(pag.get("total_pages") or 1)
        if page >= total_pages:
            break
        page += 1
        time.sleep(sleep_s)
    return all_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Download Marketcall offers (JSON).")
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write JSON {\"count\": N, \"offers\": [...]}",
    )
    args = parser.parse_args()
    key = os.environ.get("MC_KEY", "").strip()
    if not key:
        sys.stderr.write("Missing MC_KEY in environment.\n")
        raise SystemExit(2)
    offers = fetch_all_offers(key)
    out = {"count": len(offers), "offers": offers}
    path = args.output
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Wrote {path} ({len(offers)} offers)")


if __name__ == "__main__":
    main()
