#!/usr/bin/env python3
"""
WEA-21 — Smoke tests lecture (REST) Google Ads + Google Analytics Admin.

Prérequis flux OAuth : voir docs/GOOGLE_OAUTH_WEA20.md et docs/GOOGLE_ADS_ANALYTICS_API_WEA21.md.
Les valeurs secrètes ne doivent jamais être commitées (WEA-15).

Variables d'environnement (noms seulement dans la doc ; valeurs hors dépôt) :
  GOOGLE_OAUTH_ACCESS_TOKEN   — jeton porteur OAuth 2.0 (scopes Ads + Analytics Admin en lecture)
  GOOGLE_ADS_DEVELOPER_TOKEN  — developer token Google Ads (obligatoire pour l'appel Ads ci-dessous)

Optionnel :
  GOOGLE_ADS_API_VERSION      — segment de version dans l'URL Ads (défaut : v21)
  GOOGLE_ADS_LOGIN_CUSTOMER_ID — sans tirets, si accès via MCC (en-tête login-customer-id)

Comportement :
  --dry-run   Aucun appel réseau ; pour CI (comme ibkr_smoke_wea30).

Sans --dry-run : effectue un GET Analytics Admin (accountSummaries) ; si GOOGLE_ADS_DEVELOPER_TOKEN
est défini, effectue aussi customers:listAccessibleCustomers (Google Ads).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

GA_ADMIN_ACCOUNT_SUMMARIES = "https://analyticsadmin.googleapis.com/v1beta/accountSummaries"


def _ads_list_accessible_url(version: str) -> str:
    v = version.strip().lstrip("v") or "21"
    if not v[0].isdigit():
        v = "21"
    return f"https://googleads.googleapis.com/v{v}/customers:listAccessibleCustomers"


def _request_json(url: str, headers: dict[str, str], method: str = "GET") -> tuple[int, dict]:
    req = urllib.request.Request(url, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=45) as resp:
        body = resp.read()
        status = resp.status
    data = json.loads(body.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("response JSON root is not an object")
    return status, data


def run_dry_run() -> int:
    print("google_ads_analytics_smoke_wea21: dry-run OK (no network).")
    print(
        "Live: export GOOGLE_OAUTH_ACCESS_TOKEN; optional GOOGLE_ADS_DEVELOPER_TOKEN "
        "for Ads; see docs/GOOGLE_ADS_ANALYTICS_API_WEA21.md"
    )
    return 0


def run_live() -> int:
    token = os.environ.get("GOOGLE_OAUTH_ACCESS_TOKEN", "").strip()
    if not token:
        print(
            "Missing GOOGLE_OAUTH_ACCESS_TOKEN. Obtain an OAuth 2.0 access token with the "
            "required scopes (never commit it). See docs/GOOGLE_OAUTH_WEA20.md.",
            file=sys.stderr,
        )
        return 2

    auth_header = f"Bearer {token}"
    errors = 0

    # --- Google Analytics Admin API (read) ---
    ga_url = f"{GA_ADMIN_ACCOUNT_SUMMARIES}?{urllib.parse.urlencode({'pageSize': '1'})}"
    try:
        status, data = _request_json(
            ga_url,
            headers={
                "Authorization": auth_header,
                "Accept": "application/json",
            },
        )
    except urllib.error.HTTPError as e:
        print(f"Analytics Admin API HTTP {e.code}: {e.reason}", file=sys.stderr)
        try:
            err_body = e.read().decode("utf-8", errors="replace")
            if err_body:
                print(err_body[:2000], file=sys.stderr)
        except OSError:
            pass
        errors += 1
    except urllib.error.URLError as e:
        print(f"Analytics Admin API request failed: {e.reason}", file=sys.stderr)
        errors += 1
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Analytics Admin API invalid JSON: {e}", file=sys.stderr)
        errors += 1
    else:
        summaries = data.get("accountSummaries")
        n = len(summaries) if isinstance(summaries, list) else 0
        print(f"OK: Analytics Admin API HTTP {status}; accountSummaries page (size≤1) returned {n} row(s).")

    # --- Google Ads API (read) ---
    dev_token = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", "").strip()
    if not dev_token:
        print(
            "Skipping Google Ads REST smoke (GOOGLE_ADS_DEVELOPER_TOKEN unset). "
            "Set it to exercise customers:listAccessibleCustomers.",
            file=sys.stderr,
        )
        return 0 if errors == 0 else 1

    version = os.environ.get("GOOGLE_ADS_API_VERSION", "v21").strip() or "v21"
    ads_url = _ads_list_accessible_url(version)
    ads_headers: dict[str, str] = {
        "Authorization": auth_header,
        "developer-token": dev_token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    login_cid = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").strip().replace("-", "")
    if login_cid:
        ads_headers["login-customer-id"] = login_cid

    try:
        status, data = _request_json(ads_url, headers=ads_headers)
    except urllib.error.HTTPError as e:
        print(f"Google Ads API HTTP {e.code}: {e.reason}", file=sys.stderr)
        try:
            err_body = e.read().decode("utf-8", errors="replace")
            if err_body:
                print(err_body[:2000], file=sys.stderr)
        except OSError:
            pass
        errors += 1
    except urllib.error.URLError as e:
        print(f"Google Ads API request failed: {e.reason}", file=sys.stderr)
        errors += 1
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Google Ads API invalid JSON: {e}", file=sys.stderr)
        errors += 1
    else:
        names = data.get("resourceNames")
        n = len(names) if isinstance(names, list) else 0
        print(f"OK: Google Ads API HTTP {status}; resourceNames count = {n}")

    return 0 if errors == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="WEA-21 smoke: Google Analytics Admin + optional Google Ads REST read.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="No HTTP calls; for CI.",
    )
    args = parser.parse_args()
    if args.dry_run:
        return run_dry_run()
    return run_live()


if __name__ == "__main__":
    raise SystemExit(main())
