#!/usr/bin/env python3
"""
WEA-22 — Smoke test Brave Search API (Web Search).

Exige une clé API via l'environnement : BRAVE_SEARCH_API_KEY (préféré) ou Brave_API (alias équipe / Cursor).

Variables optionnelles :
  BRAVE_SEARCH_QUERY  — requête de test (défaut : Brave Search API)
  BRAVE_SEARCH_COUNT  — nombre de résultats (défaut : 3)

Référence : docs/BRAVE_SEARCH_API_WEA22.md
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BRAVE_WEB_SEARCH = "https://api.search.brave.com/res/v1/web/search"

# Order: preferred canonical name, then team alias (1Password / GitHub / Cursor).
_KEY_ENV_NAMES = ("BRAVE_SEARCH_API_KEY", "Brave_API")


def _api_key_from_env() -> str:
    for name in _KEY_ENV_NAMES:
        v = os.environ.get(name, "").strip()
        if v:
            return v
    return ""


def main() -> int:
    api_key = _api_key_from_env()
    if not api_key:
        names = " or ".join(_KEY_ENV_NAMES)
        print(
            f"Missing API key: set {names} from 1Password / GitHub / Cursor (never commit the value).",
            file=sys.stderr,
        )
        return 2

    query = os.environ.get("BRAVE_SEARCH_QUERY", "Brave Search API").strip() or "Brave Search API"
    count_raw = os.environ.get("BRAVE_SEARCH_COUNT", "3").strip()
    try:
        count = max(1, min(20, int(count_raw)))
    except ValueError:
        count = 3

    params = urllib.parse.urlencode({"q": query, "count": str(count)})
    url = f"{BRAVE_WEB_SEARCH}?{params}"

    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "X-Subscription-Token": api_key,
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read()
            status = resp.status
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.reason}", file=sys.stderr)
        try:
            err_body = e.read().decode("utf-8", errors="replace")
            if err_body:
                print(err_body[:2000], file=sys.stderr)
        except OSError:
            pass
        return 1
    except urllib.error.URLError as e:
        print(f"Request failed: {e.reason}", file=sys.stderr)
        return 1

    if status != 200:
        print(f"Unexpected status {status}", file=sys.stderr)
        return 1

    try:
        data = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as e:
        print(f"Invalid JSON response: {e}", file=sys.stderr)
        return 1

    web = data.get("web") or {}
    results = web.get("results") if isinstance(web, dict) else None
    n = len(results) if isinstance(results, list) else 0
    print(f"OK: Brave Search API returned HTTP {status}; web.results count = {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
