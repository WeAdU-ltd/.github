#!/usr/bin/env python3
"""
WEA-30 — Smoke minimal pour la connexion socket TWS / IB Gateway (API classique).

  --dry-run     Aucune connexion ; utilisé en CI (pas de dépendance ibapi).

Variables pour une tentative réelle (local uniquement ; secrets hors Git, cf. WEA-15) :
  IBKR_HOST       — hôte du Gateway/TWS (défaut : 127.0.0.1)
  IBKR_PORT       — port socket (ex. paper 7497)
  IBKR_CLIENT_ID  — entier non nul (défaut : 1)

Installation optionnelle : pip install ibapi
"""

from __future__ import annotations

import argparse
import os
import sys
import threading
import time


def run_dry_run() -> int:
    print("ibkr_smoke_wea30: dry-run OK (no network, no ibapi import).")
    print("Optional live check: set IBKR_HOST, IBKR_PORT, IBKR_CLIENT_ID; pip install ibapi; run without --dry-run.")
    return 0


def run_connect(host: str, port: int, client_id: int, timeout_s: float = 5.0) -> int:
    try:
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper
    except ImportError:
        print(
            "Missing package 'ibapi'. Install with: pip install ibapi",
            file=sys.stderr,
        )
        return 2

    connected = threading.Event()
    errors: list[str] = []

    class App(EWrapper, EClient):
        def __init__(self) -> None:
            EClient.__init__(self, self)

        def connectAck(self) -> None:  # noqa: N802 — IB API naming
            connected.set()

        def error(self, reqId, errorCode, errorString, advancedOrderRejectJson="") -> None:  # noqa: N802
            if errorCode not in (2104, 2106, 2158):  # informational "market data farm connected" etc.
                errors.append(f"code={errorCode} {errorString}")

    app = App()
    app.connect(host, port, client_id)
    thread = threading.Thread(target=app.run, daemon=True)
    thread.start()
    if not connected.wait(timeout_s):
        print(f"No connectAck within {timeout_s}s (host={host!r} port={port}). Is Gateway/TWS running?", file=sys.stderr)
        app.disconnect()
        return 1
    app.disconnect()
    time.sleep(0.2)
    if errors:
        print("Errors during session:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    print(f"ibkr_smoke_wea30: connectAck received from {host}:{port} (clientId={client_id}).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="WEA-30 IBKR socket smoke (optional ibapi).")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip network and ibapi; for CI.",
    )
    args = parser.parse_args()
    if args.dry_run:
        return run_dry_run()

    host = os.environ.get("IBKR_HOST", "127.0.0.1")
    port_s = os.environ.get("IBKR_PORT", "")
    client_s = os.environ.get("IBKR_CLIENT_ID", "1")
    if not port_s:
        print("IBKR_PORT is required for live connect (e.g. 7497 for paper).", file=sys.stderr)
        return 2
    try:
        port = int(port_s)
        client_id = int(client_s)
    except ValueError:
        print("IBKR_PORT and IBKR_CLIENT_ID must be integers.", file=sys.stderr)
        return 2
    return run_connect(host, port, client_id)


if __name__ == "__main__":
    sys.exit(main())
